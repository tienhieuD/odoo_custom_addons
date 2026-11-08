# -*- coding: utf-8 -*-
import base64
import hashlib
import mimetypes
import re

from lxml import html as lxml_html
from markupsafe import Markup

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError

# Reply and forward prefixes in several languages (Re, Fw, Fwd, Tr, Aw, Sv, Rv)
PREFIX_RE = re.compile(r"^\s*((re|fwd?|tr|aw|sv|rv)\s*:\s*)+", re.IGNORECASE)


# <img src="data:image/png;base64,..."> pasted in the editor
B64_IMAGE_RE = re.compile(r"(<img\b[^>]*?\bsrc=)([\"'])data:(image/[\w.+-]+);base64,([^\"']+)\2", re.IGNORECASE)


class DwoMailComposer(models.AbstractModel):
    """Backend of the inline email composer: defaults, draft, suggestions and sending.

    All the business rules (who is in To and Cc, subject prefix, quote) live
    here so the JavaScript side only displays and edits.
    """
    _name = "dwo.mail.composer"
    _description = "Email Composer Backend"

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------

    @api.model
    def _check_internal(self):
        """The whole API is for internal users: it reads messages in sudo and
        proposes addresses, so a portal or public user must never reach it."""
        if not self.env.user._is_internal():
            raise AccessError(self.env._("Only internal users can use the email composer."))

    @api.model
    def _get_thread(self, res_model, res_id, access="read"):
        self._check_internal()
        if res_model not in self.env or not hasattr(self.env[res_model], "message_post"):
            raise UserError(self.env._("This record has no chatter."))
        thread = self.env[res_model].browse(res_id).exists()
        if not thread:
            raise UserError(self.env._("The record does not exist anymore."))
        thread.check_access(access)
        return thread

    @api.model
    def _parse(self, text):
        """'A <a@x.com>, b@x.com' -> [{'email': 'a@x.com', 'name': 'A'}, ...] (no duplicates)."""
        result, index = [], {}
        for name, email in tools.mail.email_split_tuples(text or ""):
            normalized = tools.email_normalize(email)
            if not normalized:
                continue
            if normalized not in index:
                index[normalized] = {"email": normalized, "name": name or ""}
                result.append(index[normalized])
            elif name and not index[normalized]["name"]:
                # the same address written twice, once with a name: keep the name, at the first place
                index[normalized]["name"] = name
        return result

    @api.model
    def _format_list(self, items):
        return ", ".join(
            tools.formataddr((i.get("name") or "", i["email"])) if isinstance(i, dict) else str(i)
            for i in items)

    @api.model
    def _stored_recipients(self, items):
        """What is kept in a stored email: a list of {email, name}, whatever the client gave (a plain
        address or a dict). Anything that is not an address is dropped; sending checks again."""
        result = []
        for item in items or []:
            raw = item.get("email") if isinstance(item, dict) else item
            email = tools.email_normalize(raw or "")
            if email:
                result.append({
                    "email": email,
                    "name": (item.get("name") or "") if isinstance(item, dict) else "",
                    **({"isNew": True} if isinstance(item, dict) and item.get("isNew") else {}),
                })
        return result

    @api.model
    def _system_emails(self, thread=None):
        """Addresses that must never be proposed as recipients (aliases of the system)."""
        emails = set()
        for domain in self.env["mail.alias.domain"].sudo().search([]):
            for fname in ("catchall_email", "bounce_email", "default_from_email"):
                emails.update(tools.email_normalize_all(domain[fname] or ""))
        if thread is not None and "alias_id" in thread._fields and thread.alias_id:
            emails.update(tools.email_normalize_all(thread.alias_id.sudo().alias_full_name or ""))
        return emails

    @api.model
    def _dwo_allowed_from_addresses(self):
        """Senders the user may pick. Override to extend or restrict."""
        user = self.env.user
        result = []
        if user.email_normalized:
            result.append({"email": user.email_normalized, "name": user.name})
        company = self.env.company
        company_email = tools.email_normalize(company.email or "")
        if company_email:
            result.append({"email": company_email, "name": company.name})
        for domain in self.env["mail.alias.domain"].sudo().search([("company_ids", "in", self.env.company.ids)]):
            for email in tools.email_normalize_all(domain.default_from_email or ""):
                result.append({"email": email, "name": company.name})
        unique, seen = [], set()
        for item in result:
            if item["email"] not in seen:
                seen.add(item["email"])
                unique.append(item)
        return unique

    @api.model
    def _default_from(self):
        allowed = self._dwo_allowed_from_addresses()
        return allowed[0] if allowed else {"email": "", "name": ""}

    @api.model
    def _own_pending_attachments(self, attachment_ids):
        """Attachments the caller may attach: pending ones (uploaded for a composer) created by the caller.
        Core links any id it is given, in sudo, so the check has to be made here."""
        attachments = self.env["ir.attachment"].sudo().browse([int(a) for a in attachment_ids or []]).exists()
        return attachments.filtered(
            lambda a: a.res_model == "mail.compose.message" and a.create_uid.id == self.env.uid)

    @api.model
    def _get_ref_message(self, thread, ref_message_id=False):
        """The message answered or forwarded: the given one, else the latest official email
        (incoming email or email sent with this module). Notes and discussion are ignored."""
        Message = self.env["mail.message"].sudo()
        if ref_message_id:
            message = Message.browse(ref_message_id).exists()
            # only emails can be answered or forwarded: never an internal note or a discussion message
            if message and message.model == thread._name and message.res_id == thread.id \
                    and (message.message_type == "email" or message.dwo_is_from_compose):
                return message
        return Message.search([
            ("model", "=", thread._name), ("res_id", "=", thread.id),
            "|", ("message_type", "=", "email"), ("dwo_is_from_compose", "=", True),
        ], order="date desc, id desc", limit=1)

    @api.model
    def _subject_with_prefix(self, subject, prefix):
        base = PREFIX_RE.sub("", subject or "").strip()
        return f"{prefix}: {base}" if base else f"{prefix}:"

    @api.model
    def _tz_date_label(self, dt):
        """Date in the timezone of the author of the new email: 'YYYY-MM-DD HH:MM (JST)'.
        Zones without a letter abbreviation (tzdata gives '+07') use 'UTC+07:00'."""
        tz = self.env.user.tz or self.env.context.get("tz") or "UTC"
        local = fields.Datetime.context_timestamp(self.with_context(tz=tz), dt)
        abbreviation = local.strftime("%Z")
        if not re.fullmatch(r"[A-Za-z]{2,5}", abbreviation or ""):
            offset = local.strftime("%z") or "+0000"
            abbreviation = f"UTC{offset[:3]}:{offset[3:]}"
        return f"{local.strftime('%Y-%m-%d %H:%M')} ({abbreviation})"

    @api.model
    def _message_addresses(self, ref):
        """(from, to, cc) of a message as lists of dicts, from incoming or outgoing fields."""
        from_ = self._parse(ref.email_from)
        if not from_ and ref.author_id.email_normalized:
            from_ = [{"email": ref.author_id.email_normalized, "name": ref.author_id.name}]
        if ref.dwo_is_from_compose:
            return from_, self._parse(ref.outgoing_email_to), self._parse(ref.outgoing_email_cc)
        # the To as received keeps the aliases (catchall) that the core removes from incoming_email_to
        to = self._parse(ref.dwo_incoming_email_to_all) or self._parse(ref.incoming_email_to)
        return from_, to, self._parse(ref.incoming_email_cc)

    @api.model
    def _quote_block(self, ref, label):
        """Outlook style quote. The meta never contains Bcc. To and Cc lines are
        written only when they have a value."""
        from_, to, cc = self._message_addresses(ref)
        lines = []
        if from_:
            lines.append(Markup("<b>From:</b> %s") % self._format_list(from_[:1]))
        if to:
            lines.append(Markup("<b>To:</b> %s") % self._format_list(to))
        if cc:
            lines.append(Markup("<b>Cc:</b> %s") % self._format_list(cc))
        lines.append(Markup("<b>Date:</b> %s") % self._tz_date_label(ref.date or fields.Datetime.now()))
        return Markup(
            '<div id="divRplyFwdMsg" dir="ltr"><div>---------- %s ----------</div>'
            "<div>%s</div><br/><div>%s</div></div>"
        ) % (label, Markup("<br/>").join(lines), ref.body or "")

    @api.model
    def _initial_body(self, quote=Markup("")):
        """What the editor holds when an email is started: three empty lines to write in, then the
        signature, then the quote of the email answered. A template chosen on this untouched body
        is written into those lines."""
        return Markup("<p><br></p>") * 3 + self._signature_html() + quote

    @api.model
    def _signature_html(self):
        signature = self.env.user.signature
        return Markup("<br/>") + signature if signature and not tools.is_html_empty(signature) else Markup("")

    # ------------------------------------------------------------
    # REPLY-TO
    # ------------------------------------------------------------

    @api.model
    def _dwo_is_odoo_address(self, email):
        """True if Odoo receives the mail sent to this address (catchall or an alias), so a
        reply to it comes back to the record."""
        email = tools.email_normalize(email or "")
        if not email:
            return False
        if email in self._system_emails():
            return True
        return bool(self.env["mail.alias"].sudo().search_count([("alias_full_name", "=ilike", email)], limit=1))

    @api.model
    def _default_reply_to(self, thread, from_email=None):
        """The Reply-To that Odoo gives to a message posted on the record. It is the logic of the
        model: the alias of the record, or of its team in CRM, else the company catchall, else the
        sender. Using the same method as ``message_post`` keeps the default and the real header equal."""
        sender = from_email or self._default_from()["email"]
        default = tools.formataddr((self.env.user.name, sender)) if sender else False
        formatted = thread._notify_get_reply_to(
            default=default, author_id=self.env.user.partner_id.id)[thread.id]
        parsed = self._parse(formatted)
        return parsed[0] if parsed else {"email": sender or "", "name": ""}

    @api.model
    def get_reply_to(self, res_model, res_id, from_email=False, reply_to=False):
        """Default Reply-To for a sender, and whether the checked address (the given one, else
        the default) is handled by Odoo."""
        thread = self._get_thread(res_model, res_id)
        default = self._default_reply_to(thread, tools.email_normalize(from_email or "") or None)
        checked = tools.email_normalize(reply_to or "") or default["email"]
        return {"default": default, "managed": self._dwo_is_odoo_address(checked)}

    # ------------------------------------------------------------
    # DEFAULTS
    # ------------------------------------------------------------

    @api.model
    def _compute_defaults(self, thread, ref=None, mode="reply"):
        """Content of the form plus the Reply-To that Odoo computes for the record."""
        result = self._compute_content_defaults(thread, ref, mode)
        default = self._default_reply_to(thread, result["from"] or None)
        result.update(
            reply_to=default["email"],
            reply_to_custom=False,
            reply_to_managed=self._dwo_is_odoo_address(default["email"]),
        )
        return result

    @api.model
    def _compute_content_defaults(self, thread, ref=None, mode="reply"):
        """Initial content of the form.

        A. no official email in the thread: only From (the user) is set.
        B. reference is an incoming email: reply-all (From = the address that received it).
        C. reference is an email we sent: same From, To, Cc and Bcc, subject RE.
        D. forward: From is the user, recipients are empty, subject FW.
        """
        me = self.env.user.email_normalized
        system = self._system_emails(thread)
        allowed = self._dwo_allowed_from_addresses()
        allowed_emails = {a["email"] for a in allowed}
        default_from = self._default_from()
        result = {
            "mode": "new", "ref_message_id": False, "from": default_from["email"],
            "to": [], "cc": [], "bcc": [], "subject": "",
            "body": str(self._initial_body()), "template_id": False, "attachments": [],
        }
        if not ref:
            return result

        sender, to_list, cc_list = self._message_addresses(ref)
        result["ref_message_id"] = ref.id

        if mode == "forward":
            result.update(
                mode="forward",
                subject=self._subject_with_prefix(ref.subject or ref.record_name, "FW"),
                body=str(self._initial_body(self._quote_block(ref, "Forwarded message"))),
                attachments=self._copy_attachments_for_forward(ref),
            )
            return result

        # "reply_sender" is the Reply button: only the person who wrote, no Cc. Anything else is
        # reply-all, which is also what the Send email button starts with.
        only_sender = mode == "reply_sender"
        result["mode"] = "reply"
        result["subject"] = self._subject_with_prefix(ref.subject or ref.record_name, "RE")
        result["body"] = str(self._initial_body(self._quote_block(ref, "Original message")))

        if ref.dwo_is_from_compose:
            # C. we wrote the last email: continue with the same people
            if sender and sender[0]["email"] in allowed_emails:
                result["from"] = sender[0]["email"]
            result["to"] = to_list
            if not only_sender:
                result["cc"] = cc_list
                result["bcc"] = self._parse(ref.outgoing_email_bcc)
            return result

        # B. incoming email: reply-all
        excluded = {me} | system
        reply_to = [a for a in sender if a["email"] not in excluded] or [a for a in to_list if a["email"] not in excluded][:1]
        if not reply_to:
            # The user wrote to the system himself (the catchall, the alias of the record) and nobody
            # else is in To: the answer still goes to the address the email came from.
            reply_to = [a for a in sender if a["email"] not in system][:1]
        to_emails = {a["email"] for a in reply_to}
        for address in to_list + cc_list:
            if address["email"] in allowed_emails:
                result["from"] = address["email"]
                break
        others = []
        for address in to_list + cc_list:
            email = address["email"]
            if email in excluded or email in to_emails or email in allowed_emails:
                continue
            if email not in {o["email"] for o in others}:
                others.append(address)
        result["to"] = reply_to
        result["cc"] = [] if only_sender else others
        return result

    @api.model
    def _copy_attachments_for_forward(self, ref):
        """Pending copies of the attachments of the forwarded email (the original ones stay with it)."""
        attachments = []
        for attachment in ref.sudo().attachment_ids:
            copy = attachment.sudo().copy({"res_model": "mail.compose.message", "res_id": 0})
            attachments.append({
                "id": copy.id, "name": copy.name, "mimetype": copy.mimetype, "size": copy.file_size})
        return attachments

    # ------------------------------------------------------------
    # PUBLIC API (called by the web client)
    # ------------------------------------------------------------

    @api.model
    def get_defaults(self, res_model, res_id, ref_message_id=False, mode="reply"):
        thread = self._get_thread(res_model, res_id)
        ref = self._get_ref_message(thread, ref_message_id)
        return self._compute_defaults(thread, ref, mode)

    @api.model
    def _dwo_require_approval(self):
        """True when the company forbids sending directly: every email goes through an approver."""
        return bool(self.env.company.dwo_mail_require_approval)

    @api.model
    def _unsent_domain(self, res_model, res_id):
        return [
            ("user_id", "=", self.env.uid), ("res_model", "=", res_model), ("res_id", "=", res_id),
            ("state", "in", ("draft", "pending", "rejected")),
        ]

    @api.model
    def has_draft(self, res_model, res_id):
        """Cheap check used to show the dot on the Send email button: an email is still unsent."""
        return bool(self.env["dwo.mail.email"].search_count(self._unsent_domain(res_model, res_id), limit=1))

    @api.model
    def list_emails(self, res_model, res_id):
        """The emails of the user on this record that did not leave yet (draft, waiting, rejected)."""
        self._get_thread(res_model, res_id)
        # newest created first
        emails = self.env["dwo.mail.email"].search(
            self._unsent_domain(res_model, res_id), order="create_date desc, id desc")
        return [email._dwo_summary() for email in emails]

    @api.model
    def _own_email(self, email_id, res_model=None, res_id=None):
        email = self.env["dwo.mail.email"].browse(email_id).exists()
        if not email or email.user_id != self.env.user:
            raise AccessError(self.env._("You can only use your own emails."))
        if res_model is not None and (email.res_model, email.res_id) != (res_model, res_id):
            raise AccessError(self.env._("This email belongs to another record."))
        self._get_thread(email.res_model, email.res_id)
        return email

    @api.model
    def get_state(self, res_model, res_id, preferred_email_id=False):
        """Everything the form needs when it opens.

        The email shown is the one the user opened last on this screen (``preferred_email_id``, kept
        by the client until the screen changes or the page is reloaded), else the **newest created**
        of their unsent emails on this record (whatever its state), else the defaults. The list of the
        unsent emails comes with it."""
        thread = self._get_thread(res_model, res_id)
        Email = self.env["dwo.mail.email"]
        unsent = Email.search(self._unsent_domain(res_model, res_id), order="create_date desc, id desc")
        current = unsent.filtered(lambda email: email.id == preferred_email_id)[:1] or unsent[:1]
        latest = self._get_ref_message(thread)
        newer_email = False
        if current and latest and latest.date and current.write_date and latest.date > current.write_date \
                and latest.id != current.ref_message_id:
            from_, _to, _cc = self._message_addresses(latest)
            newer_email = {
                "id": latest.id,
                "from": self._format_list(from_[:1]),
                "date": self._tz_date_label(latest.date),
            }
        return {
            "current": current._dwo_to_dict() if current else False,
            "emails": self.list_emails(res_model, res_id),
            "defaults": self._compute_defaults(thread, latest, "reply"),
            "newer_email": newer_email,
            "from_options": self._dwo_allowed_from_addresses(),
            "policy": {"require_approval": self._dwo_require_approval()},
        }

    @api.model
    def load_email(self, email_id):
        return self._own_email(email_id)._dwo_to_dict()

    @api.model
    def _externalize_images(self, res_model, res_id, body):
        """Turn the images pasted in the body (base64) into attachments of the record, linked by
        ``/web/image/<id>?access_token=...`` like the Odoo editor does. A mail client does not show
        a base64 image reliably and a big one makes the email heavy. Done on the server, before the
        draft is stored and before sending, so the stored draft, a direct send and an approved send
        all get the same body. The same picture is stored once: autosave sends it again and again."""
        if not body or "base64," not in body:
            return body
        Attachment = self.env["ir.attachment"]

        def replace(match):
            prefix, quote, mimetype, data = match.groups()
            try:
                raw = base64.b64decode(data)
            except ValueError:
                return match.group(0)
            checksum = hashlib.sha1(raw).hexdigest()
            attachment = Attachment.search([
                ("res_model", "=", res_model), ("res_id", "=", res_id),
                ("checksum", "=", checksum), ("create_uid", "=", self.env.uid),
            ], limit=1)
            if not attachment:
                extension = mimetypes.guess_extension(mimetype) or ""
                attachment = Attachment.create({
                    "name": "image-%s%s" % (checksum[:8], extension),
                    "raw": raw,
                    "mimetype": mimetype,
                    "res_model": res_model,
                    "res_id": res_id,
                })
            return "%s%s/web/image/%d?access_token=%s%s" % (
                prefix, quote, attachment.id, attachment.generate_access_token()[0], quote)

        return B64_IMAGE_RE.sub(replace, body)

    @api.model
    def _email_values(self, vals, res_model=False, res_id=False):
        return {
            "mode": vals.get("mode") or "new",
            "ref_message_id": vals.get("ref_message_id") or 0,
            "email_from": vals.get("from") or False,
            "to_json": self._stored_recipients(vals.get("to")),
            "cc_json": self._stored_recipients(vals.get("cc")),
            "bcc_json": self._stored_recipients(vals.get("bcc")),
            "reply_to": vals.get("reply_to") or False,
            "reply_to_custom": bool(vals.get("reply_to_custom")),
            "subject": vals.get("subject") or False,
            "body": self._externalize_images(res_model, res_id, vals.get("body")) or False,
            "template_id": vals.get("template_id") or False,
            "attachment_ids": [(6, 0, self._own_pending_attachments(vals.get("attachment_ids")).ids)],
        }

    @api.model
    def save_email(self, res_model, res_id, email_id, vals):
        """Create or update the stored email. The client sends the id it got from the first save."""
        self._get_thread(res_model, res_id)
        values = self._email_values(vals, res_model, res_id)
        if email_id:
            email = self._own_email(email_id, res_model, res_id)
            if email.state == "sent":
                # approved and sent while the author kept the form open: nothing is written, the
                # client learns the state and stops saving
                return {"id": email.id, "state": email.state, "saved_at": fields.Datetime.to_string(email.write_date)}
            email.write(values)
        else:
            email = self.env["dwo.mail.email"].create(dict(
                values, res_model=res_model, res_id=res_id, company_id=self.env.company.id))
        return {"id": email.id, "state": email.state, "saved_at": fields.Datetime.to_string(email.write_date)}

    @api.model
    def delete_email(self, res_model, res_id, email_id=False):
        """Delete the stored email (whoever waited for it is told) and return the initial content."""
        thread = self._get_thread(res_model, res_id)
        if email_id:
            self._own_email(email_id, res_model, res_id)._withdraw_and_unlink()
        return self._compute_defaults(thread, self._get_ref_message(thread), "reply")

    @api.model
    def request_approval(self, res_model, res_id, email_id, vals, approver_ids, comment=None):
        """Store the email and ask the approvers to approve and send it. Anyone of them can."""
        thread = self._get_thread(res_model, res_id)
        self._prepare_post(thread, vals)  # an email that cannot be sent is not worth an approval
        approvers = self.env["res.users"].browse([int(u) for u in approver_ids or []]).exists().filtered(
            lambda user: user.active and not user.share)
        if not approvers:
            raise UserError(self.env._("Choose at least one approver."))
        saved = self.save_email(res_model, res_id, email_id, vals)
        email = self.env["dwo.mail.email"].browse(saved["id"])
        email.request_approval(approvers, comment)
        return {"id": email.id, "state": email.state, "emails": self.list_emails(res_model, res_id)}

    @api.model
    def apply_template(self, template_id, res_model, res_id):
        """Render a template on the record and return what the form must take:
        From, To, Cc, Bcc, subject, body and attachments, with every placeholder computed.

        Only a template made for the model of the record is accepted. Attachments are
        returned as pending copies owned by the caller, so they can be sent and removed
        like any file the user attached by hand.
        """
        thread = self._get_thread(res_model, res_id)
        template = self.env["mail.template"].browse(template_id).exists()
        if not template:
            raise UserError(self.env._("This template does not exist anymore."))
        template.check_access("read")
        if template.model != res_model:
            raise UserError(self.env._("This template is not made for this kind of record."))

        values = template._generate_template(
            [thread.id],
            ("subject", "body_html", "email_from", "email_to", "email_cc", "email_bcc",
             "partner_to", "attachment_ids", "report_template_ids"),
            find_or_create_partners=False,
        )[thread.id]

        warnings = []
        allowed = {a["email"] for a in self._dwo_allowed_from_addresses()}
        sender = self._parse(values.get("email_from"))
        from_email = False
        if sender:
            if sender[0]["email"] in allowed:
                from_email = sender[0]["email"]
            else:
                warnings.append(self.env._(
                    "The template sends from %s, which you are not allowed to use. The From address is unchanged.",
                    sender[0]["email"]))

        partners = self.env["res.partner"].browse(values.get("partner_ids") or []).exists()
        to = self._parse(values.get("email_to"))
        to_emails = {a["email"] for a in to}
        for partner in partners:
            for email in tools.email_normalize_all(partner.email or ""):
                if email not in to_emails:
                    to_emails.add(email)
                    to.append({"email": email, "name": partner.name or ""})

        attachments = []
        Attachment = self.env["ir.attachment"].sudo()
        for attachment in Attachment.browse(values.get("attachment_ids") or []).exists():
            copy = attachment.copy({"res_model": "mail.compose.message", "res_id": 0})
            attachments.append(copy)
        for name, content in values.get("attachments") or []:
            attachments.append(Attachment.create({
                "name": name, "datas": content, "res_model": "mail.compose.message", "res_id": 0}))

        body = values.get("body_html")
        return {
            "template_id": template.id,
            "subject": values.get("subject") or False,
            "body": str(body) if body and not tools.is_html_empty(body) else False,
            "from": from_email,
            "to": to,
            "cc": self._parse(values.get("email_cc")),
            "bcc": self._parse(values.get("email_bcc")),
            "attachments": [
                {"id": a.id, "name": a.name, "mimetype": a.mimetype, "size": a.file_size}
                for a in attachments
            ],
            "warnings": warnings,
        }

    @api.model
    def _body_without_quote(self, html):
        """The message the user wrote, without the quoted email: a template must not carry the
        last customer's email."""
        if not html or tools.is_html_empty(html):
            return ""
        root = lxml_html.fragment_fromstring(str(html), create_parent="div")
        for quote in root.xpath('.//*[@id="divRplyFwdMsg"]'):
            tail = quote.tail
            parent = quote.getparent()
            if tail and tail.strip():
                # keep text that followed the quote
                previous = quote.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or "") + tail
                else:
                    parent.text = (parent.text or "") + tail
            parent.remove(quote)
        # the empty lines left to write in are not part of the template
        for child in list(root):
            if child.tag in ("p", "div") and not (child.text or "").strip() \
                    and all(grandchild.tag == "br" for grandchild in child) and not (child.tail or "").strip():
                root.remove(child)
            else:
                break
        return (root.text or "") + "".join(lxml_html.tostring(child, encoding="unicode") for child in root)

    @api.model
    def save_as_template(self, res_model, res_id, name, vals):
        """Save the email being written as a template of the model, owned by the caller, like
        "Save as Template" of the core composer. The subject is kept without its RE:/FW: prefix, the
        body without the quote. Attachments are copied: the originals stay pending for the email."""
        self._get_thread(res_model, res_id)
        name = (name or "").strip()
        if not name:
            raise UserError(self.env._("Give a name to the template."))
        subject = PREFIX_RE.sub("", vals.get("subject") or "").strip()
        template = self.env["mail.template"].create({
            "name": name,
            "model_id": self.env["ir.model"]._get_id(res_model),
            "subject": subject or False,
            "body_html": self._body_without_quote(vals.get("body")),
            "use_default_to": True,
            "user_id": self.env.uid,
        })
        copies = [
            attachment.copy({"res_model": "mail.template", "res_id": template.id}).id
            for attachment in self._own_pending_attachments(vals.get("attachment_ids"))
        ]
        if copies:
            template.attachment_ids = [(6, 0, copies)]
        return {"id": template.id, "name": template.name}

    @api.model
    def suggest(self, query="", exclude=None, limit=8):
        self._check_internal()
        return self.env["dwo.mail.address"].dwo_suggest(query, limit=limit, exclude=exclude)

    # ------------------------------------------------------------
    # SENDING
    # ------------------------------------------------------------

    @api.model
    def _clean_recipients(self, items, label):
        result, seen = [], set()
        for item in items or []:
            raw = item.get("email") if isinstance(item, dict) else item
            name = item.get("name", "") if isinstance(item, dict) else ""
            email = tools.email_normalize(raw or "")
            if not email:
                raise UserError(self.env._("%(label)s: %(value)s is not a valid email address.", label=label, value=raw))
            if email not in seen:
                seen.add(email)
                result.append({"email": email, "name": name or ""})
        return result

    @api.model
    def _prepare_post(self, thread, vals):
        """Check an email and return what ``message_post`` needs. Raise if it cannot be sent."""
        to = self._clean_recipients(vals.get("to"), self.env._("To"))
        cc = self._clean_recipients(vals.get("cc"), self.env._("Cc"))
        bcc = self._clean_recipients(vals.get("bcc"), self.env._("Bcc"))
        if not to:
            raise UserError(self.env._("Add at least one recipient in To."))

        from_email = tools.email_normalize(vals.get("from") or "")
        allowed = {a["email"]: a for a in self._dwo_allowed_from_addresses()}
        if not from_email:
            raise UserError(self.env._("Choose the From address."))
        if from_email not in allowed:
            raise AccessError(self.env._("You are not allowed to send from %s.", from_email))
        email_from = tools.formataddr((allowed[from_email]["name"] or "", from_email))

        body = self._externalize_images(thread._name, thread.id, vals.get("body") or "")
        requested_ids = [int(a) for a in (vals.get("attachment_ids") or [])]
        attachment_ids = self._own_pending_attachments(requested_ids).ids
        if set(requested_ids) != set(attachment_ids):
            raise AccessError(self.env._("Some attachments cannot be sent: upload them again."))
        if tools.is_html_empty(body) and not attachment_ids:
            raise UserError(self.env._("The email is empty."))

        ref = self._get_ref_message(thread, vals.get("ref_message_id") or False)
        subject = (vals.get("subject") or "").strip() or (ref.subject if ref else False) or thread.display_name

        extra = {}
        if vals.get("reply_to_custom"):
            reply_to = tools.email_normalize(vals.get("reply_to") or "")
            if not reply_to:
                raise UserError(self.env._("Reply-To: %s is not a valid email address.", vals.get("reply_to")))
            extra["reply_to"] = reply_to

        return {
            "recipients": to + cc + bcc,
            "post": dict(
                body=Markup(body),
                subject=subject,
                message_type="email_outgoing",
                subtype_xmlid="mail.mt_comment",
                email_from=email_from,
                author_id=self.env.user.partner_id.id,
                parent_id=ref.id if ref else False,
                outgoing_email_to=self._format_list(to),
                outgoing_email_cc=self._format_list(cc) or False,
                outgoing_email_bcc=self._format_list(bcc) or False,
                dwo_is_from_compose=True,
                attachment_ids=attachment_ids,
                email_add_signature=False,
                email_layout_xmlid="dwo_mail_compose.mail_layout_official",
                notify_skip_followers=True,
                # an official email is kept in the mail queue after sending: proof of what left
                mail_auto_delete=False,
                **extra,
            ),
        }

    @api.model
    def _send_email(self, res_model, res_id, vals):
        """Send the email as the current user. This is the one place that sends; the approval
        calls it as the author, ``send`` calls it as the user who clicked. It does not check the
        "approval required" setting: ``send`` does."""
        thread = self._get_thread(res_model, res_id, getattr(self.env[res_model], "_mail_post_access", "write"))
        prepared = self._prepare_post(thread, vals)
        message = thread.message_post(**prepared["post"])
        self.env["dwo.mail.address"].dwo_register(prepared["recipients"])
        return message

    @api.model
    def send(self, res_model, res_id, vals):
        """Send now. When the company requires approval this is refused, whatever the client shows."""
        if self._dwo_require_approval():
            raise UserError(self.env._(
                "Emails must be approved before they are sent. Ask for an approval instead."))
        email = False
        if vals.get("email_id"):
            email = self._own_email(vals["email_id"], res_model, res_id)
            # the lock keeps an approver and the author from sending the same email twice
            email._lock(("draft", "pending", "rejected"))
        message = self._send_email(res_model, res_id, vals)
        if email:
            email._close_after_direct_send()
        thread = self._get_thread(res_model, res_id)
        return {"message_id": message.id, "defaults": self._compute_defaults(thread, self._get_ref_message(thread), "reply")}
