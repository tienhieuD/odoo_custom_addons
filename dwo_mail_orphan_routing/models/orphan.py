# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import logging
import re
from datetime import timedelta

from markupsafe import Markup, escape

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import email_normalize, email_split, html2plaintext, html_sanitize

_logger = logging.getLogger(__name__)

PARAM = "dwo_orphan."
DEFAULT_TARGET_MODELS = [
    "res.partner", "crm.lead", "sale.order", "purchase.order", "account.move",
    "project.task", "helpdesk.ticket", "hr.applicant", "stock.picking", "mrp.production",
]
CODE_FIELDS = ("name", "ref", "number", "client_order_ref", "reference", "partner_ref", "code")
MSG_ID_RE = re.compile(r"<[^<>\s]+>")
CODE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9/\-.]*[A-Za-z0-9]")


class DwoMailOrphan(models.Model):
    _name = "dwo.mail.orphan"
    _description = "Orphan mail"
    _order = "date desc, id desc"
    _rec_name = "subject"

    subject = fields.Char(index=True, readonly=True)
    email_from = fields.Char("From", index=True, readonly=True)
    author_id = fields.Many2one("res.partner", "Sender contact", ondelete="set null", readonly=True)
    email_to = fields.Char("To", readonly=True)
    email_cc = fields.Char("Cc", readonly=True)
    rcpt_address = fields.Char("Received at", index=True, readonly=True,
                               help="The address the email was sent to (the alias or the catch-all).")
    alias_id = fields.Many2one("mail.alias", "Alias", ondelete="set null", index=True, readonly=True)
    message_id = fields.Char("Message-Id", index=True, readonly=True)
    in_reply_to = fields.Char("In-Reply-To", readonly=True)
    references = fields.Text("References", readonly=True)
    date = fields.Datetime(default=fields.Datetime.now, index=True, readonly=True)
    body_html = fields.Html("Body", readonly=True, sanitize=True)
    body_preview = fields.Char("Preview", compute="_compute_body_preview", store=True)
    attachment_ids = fields.Many2many("ir.attachment", "dwo_mail_orphan_attachment_rel", "orphan_id", "attachment_id",
                                      string="Attachments", readonly=True)
    attachment_count = fields.Integer(compute="_compute_attachment_count")
    reason = fields.Char("Why it was not routed", readonly=True)
    state = fields.Selection(
        [("new", "New"), ("routed", "Routed"), ("ignored", "Ignored")],
        default="new", required=True, index=True)
    res_model = fields.Char("Target model", readonly=True)
    res_id = fields.Many2oneReference("Target record", model_field="res_model", readonly=True)
    target_display = fields.Char("Target", compute="_compute_target_display")
    routed_message_id = fields.Many2one("mail.message", "Posted message", ondelete="set null", readonly=True)
    routed_user_id = fields.Many2one("res.users", "Routed by", ondelete="set null", readonly=True)
    routed_date = fields.Datetime(readonly=True)
    rule_id = fields.Many2one("dwo.mail.orphan.rule", "Rule", ondelete="set null", readonly=True)
    suggestion_ids = fields.One2many("dwo.mail.orphan.suggestion", "orphan_id", "Suggestions", readonly=True)
    suggestion_count = fields.Integer(compute="_compute_suggestion_count")

    # ------------------------------------------------------------
    # compute
    # ------------------------------------------------------------

    @api.depends("body_html")
    def _compute_body_preview(self):
        for rec in self:
            text = html2plaintext(rec.body_html or "") if rec.body_html else ""
            text = " ".join(text.split())
            rec.body_preview = text[:160]

    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    def _compute_suggestion_count(self):
        for rec in self:
            rec.suggestion_count = len(rec.suggestion_ids)

    @api.depends("res_model", "res_id", "state")
    def _compute_target_display(self):
        for rec in self:
            name = False
            if rec.res_model and rec.res_id and rec.res_model in self.env:
                try:
                    record = self.env[rec.res_model].browse(rec.res_id)
                    if record.exists():
                        record._dwo_check_access("read")
                        name = "%s: %s" % (self.env["ir.model"]._get(rec.res_model).name, record.display_name)
                except AccessError:
                    name = _("(no access)")
            rec.target_display = name

    # ------------------------------------------------------------
    # settings helpers
    # ------------------------------------------------------------

    @api.model
    def _icp(self, key, default=None):
        icp = self.env["ir.config_parameter"].sudo()
        value = icp.get_str(PARAM + key) if hasattr(icp, "get_str") else icp.get_param(PARAM + key)
        return default if value is False or value is None else value

    @api.model
    def _icp_set(self, key, value):
        icp = self.env["ir.config_parameter"].sudo()
        return icp.set_str(PARAM + key, value) if hasattr(icp, "set_str") else icp.set_param(PARAM + key, value)

    @api.model
    def _capture_enabled(self):
        return self._icp("enabled", "1") in ("1", "True", "true")

    @api.model
    def _target_models(self):
        """Models the orphan emails can be routed to (settings)."""
        raw = self._icp("target_models")
        names = DEFAULT_TARGET_MODELS if raw is None else [n for n in raw.split(",") if n and n != "-"]
        return [n for n in names if n in self.env and hasattr(self.env[n], "message_post")]

    # ------------------------------------------------------------
    # capture (called from mail.thread.message_route)
    # ------------------------------------------------------------

    @api.model
    def _short_reason(self, exc):
        text = str(exc)
        if text.startswith("No possible route"):
            return "No alias or record accepts this address"
        return text

    @api.model
    def _capture(self, message, message_dict, reason):
        """Store an incoming email that could not be routed. Returns the orphan, or False when it could not be stored
        (the caller then keeps the standard behaviour)."""
        message_id = message_dict.get("message_id")
        try:
            with self.env.cr.savepoint():
                existing = self.search([("message_id", "=", message_id)], limit=1) if message_id else self.browse()
                if existing:
                    return existing
                orphan = self.create(self._capture_values(message_dict, reason))
                orphan._store_attachments(message_dict.get("attachments") or [])
        except Exception:  # never lose the standard behaviour because of this module
            _logger.exception("Orphan Mail Router: could not store the email %s", message_id)
            return False
        try:
            with self.env.cr.savepoint():
                if not orphan._apply_rules():
                    orphan._compute_suggestions()
        except Exception:
            _logger.exception("Orphan Mail Router: rules or suggestions failed for %s", message_id)
        return orphan

    @api.model
    def _capture_values(self, d, reason):
        email_from = d.get("email_from") or ""
        to_list = [e.lower() for e in email_split(d.get("to") or "")]
        rcpt_list = [e.lower() for e in email_split(d.get("recipients") or d.get("to") or "")]
        alias = self.env["mail.alias"].browse()
        for address in to_list + rcpt_list:
            alias = self.env["mail.alias"].sudo().search([("alias_full_name", "=", address)], limit=1)
            if alias:
                break
        rcpt = alias.alias_full_name if alias else ((to_list or rcpt_list or [False])[0])
        normalized = email_normalize(email_from)
        author = self.env["res.partner"].browse()
        if normalized:
            author = self.env["res.partner"].sudo().search([("email_normalized", "=", normalized)], limit=1)
        body = d.get("body") or ""
        return {
            "subject": (d.get("subject") or "")[:500],
            "email_from": email_from,
            "author_id": author.id,
            "email_to": d.get("to") or "",
            "email_cc": d.get("cc") or "",
            "rcpt_address": rcpt or False,
            "alias_id": alias.id or False,
            "message_id": d.get("message_id") or False,
            "in_reply_to": d.get("in_reply_to") or False,
            "references": d.get("references") or False,
            "date": d.get("date") or fields.Datetime.now(),
            "body_html": html_sanitize(str(body)),
            "reason": (reason or "")[:300],
        }

    def _store_attachments(self, attachments):
        Attachment = self.env["ir.attachment"].sudo()
        for att in attachments:
            fname, content = att[0], att[1]
            if isinstance(content, str):
                content = content.encode("utf-8")
            if not content:
                continue
            attachment = Attachment.create({
                "name": fname or "attachment",
                "raw": content,
                "res_model": self._name,
                "res_id": self.id,
            })
            self.sudo().write({"attachment_ids": [(4, attachment.id)]})

    # ------------------------------------------------------------
    # suggestions
    # ------------------------------------------------------------

    def action_refresh_suggestions(self):
        self._compute_suggestions()
        return True

    def _compute_suggestions(self):
        Suggestion = self.env["dwo.mail.orphan.suggestion"].sudo()
        for orphan in self.sudo():
            found = orphan._find_candidates()
            top = sorted(found.items(), key=lambda kv: -kv[1][0])[:3]
            orphan.suggestion_ids.unlink()
            for sequence, ((model, res_id), (score, reasons)) in enumerate(top):
                record = self.env[model].browse(res_id)
                Suggestion.create({
                    "orphan_id": orphan.id,
                    "sequence": sequence,
                    "res_model": model,
                    "res_id": res_id,
                    "name": record.display_name,
                    "score": min(score, 100),
                    "reason": "; ".join(reasons),
                })

    def _add_candidate(self, found, model, res_id, score, reason, allowed):
        if model not in allowed or not res_id or model not in self.env:
            return
        key = (model, res_id)
        if key not in found:
            if not self.env[model].browse(res_id).exists():
                return
            found[key] = [0, []]
        found[key][0] += score
        if reason not in found[key][1]:
            found[key][1].append(reason)

    def _find_candidates(self):
        self.ensure_one()
        allowed = self._target_models()
        found = {}
        refs = MSG_ID_RE.findall("%s %s" % (self.references or "", self.in_reply_to or ""))[-32:]
        # 1. reply headers: a message of a record, or an orphan already routed
        if refs:
            for msg in self.env["mail.message"].sudo().search(
                    [("message_id", "in", refs), ("model", "in", allowed), ("res_id", "!=", 0)], limit=20):
                self._add_candidate(found, msg.model, msg.res_id, 100, _("Replies to a message of this record"), allowed)
            for sibling in self.sudo().search([("id", "!=", self.id), ("state", "=", "routed"), ("message_id", "in", refs)]):
                self._add_candidate(found, sibling.res_model, sibling.res_id, 90, _("Same thread as a routed email"), allowed)
        # 2. codes in the subject
        tokens = [t for t in CODE_RE.findall(self.subject or "") if len(t) >= 3 and any(c.isdigit() for c in t)]
        for token in tokens[:8]:
            for model in allowed:
                Model = self.env[model].sudo()
                names = [f for f in CODE_FIELDS if f in Model._fields and Model._fields[f].store
                         and Model._fields[f].type == "char"]
                if not names:
                    continue
                domain = ["|"] * (len(names) - 1) + [(f, "=ilike", token) for f in names]
                for record in Model.search(domain, limit=3):
                    self._add_candidate(found, model, record.id, 80, _("Code %s in the subject", token), allowed)
        # 3. the alias parent record
        alias = self.alias_id.sudo()
        if alias and alias.alias_parent_model_id and alias.alias_parent_thread_id:
            self._add_candidate(found, alias.alias_parent_model_id.model, alias.alias_parent_thread_id, 50,
                                _("Parent record of the alias %s", alias.alias_full_name), allowed)
        # 4. the sender
        partner = self.author_id.sudo()
        if partner:
            if "res.partner" in allowed:
                self._add_candidate(found, "res.partner", partner.id, 30, _("The sender is this contact"), allowed)
            seen = set()
            for msg in self.env["mail.message"].sudo().search(
                    [("author_id", "=", partner.id), ("model", "in", allowed), ("res_id", "!=", 0)],
                    order="id desc", limit=40):
                key = (msg.model, msg.res_id)
                if key in seen:
                    continue
                seen.add(key)
                self._add_candidate(found, msg.model, msg.res_id, 40, _("Recent record of the sender"), allowed)
                if len(seen) >= 5:
                    break
        return found

    # ------------------------------------------------------------
    # rules
    # ------------------------------------------------------------

    def _apply_rules(self):
        """Apply the automatic rules to the new orphans. Returns True when a rule handled the email."""
        Rule = self.env["dwo.mail.orphan.rule"].sudo()
        rules = Rule.search([])
        handled = False
        for orphan in self.sudo():
            if orphan.state != "new":
                continue
            for rule in rules:
                if not rule._match(orphan):
                    continue
                try:
                    with self.env.cr.savepoint():
                        rule._apply(orphan)
                    handled = True
                    break
                except Exception:
                    _logger.exception("Orphan Mail Router: rule %s failed on %s", rule.id, orphan.message_id)
        return handled

    # ------------------------------------------------------------
    # routing
    # ------------------------------------------------------------

    def _route_to(self, model, res_id, follow=False, sudo=False):
        """Move the emails into the chatter of the record. Access to write the record is checked unless sudo."""
        if model not in self._target_models():
            raise UserError(_("The model %s is not allowed as a target (Settings).", model))
        record = self.env[model].sudo().browse(res_id).exists()
        if not record:
            raise UserError(_("The target record does not exist."))
        if not sudo:
            record.with_env(self.env)._dwo_check_access("write")
        else:
            record = record.sudo()
        record = record.with_env(self.env(su=True)) if sudo else record.with_env(self.env)
        for orphan in self:
            orphan._route_one(record, follow=follow)
        return True

    def _route_one(self, record, follow=False):
        self.ensure_one()
        message = self.routed_message_id.sudo().exists()
        if message:
            # routed before: move the posted message
            message.write({"model": record._name, "res_id": record.id, "parent_id": False})
            message.attachment_ids.write({"res_model": record._name, "res_id": record.id})
        else:
            refs = MSG_ID_RE.findall("%s %s" % (self.references or "", self.in_reply_to or ""))
            parent = self.env["mail.message"].sudo().search(
                [("message_id", "in", refs), ("model", "=", record._name), ("res_id", "=", record.id)],
                limit=1) if refs else self.env["mail.message"]
            kwargs = {}
            if self.message_id:
                kwargs["message_id"] = self.message_id
            if self.date:
                kwargs["date"] = self.date
            message = record.with_context(mail_post_autofollow_author_skip=True).message_post(
                body=Markup(self.body_html or ""),
                subject=self.subject,
                message_type="email",
                subtype_xmlid="mail.mt_comment",
                email_from=self.email_from,
                author_id=self.author_id.id or False,
                parent_id=parent.id or False,
                attachments=[(a.name, a.raw or b"") for a in self.attachment_ids.sudo()],
                **kwargs)
        if follow and self.author_id and hasattr(record, "message_subscribe"):
            record.message_subscribe(partner_ids=self.author_id.ids)
        self.write({
            "state": "routed",
            "res_model": record._name,
            "res_id": record.id,
            "routed_message_id": message.id,
            "routed_user_id": self.env.uid,
            "routed_date": fields.Datetime.now(),
        })
        self.suggestion_ids.sudo().unlink()

    def action_ignore(self):
        for orphan in self:
            if orphan.state == "routed":
                raise UserError(_("A routed email cannot be ignored. Route it again to another record instead."))
        self.write({"state": "ignored"})
        return True

    def action_restore(self):
        for orphan in self:
            if orphan.state != "ignored":
                raise UserError(_("Only an ignored email can be restored."))
        self.write({"state": "new"})
        self._compute_suggestions()
        return True

    def action_route_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Route emails"),
            "res_model": "dwo.mail.orphan.route.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_orphan_ids": self.ids},
        }

    def action_open_target(self):
        self.ensure_one()
        if not (self.res_model and self.res_id):
            raise UserError(_("This email is not routed."))
        return {
            "type": "ir.actions.act_window",
            "res_model": self.res_model,
            "res_id": self.res_id,
            "view_mode": "form",
            "views": [(False, "form")],
        }

    def action_view_attachments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Attachments"),
            "res_model": "ir.attachment",
            "view_mode": "list,form",
            "domain": [("id", "in", self.attachment_ids.ids)],
        }

    def _related_orphans(self, same_sender=False, same_thread=False):
        """New orphans from the same sender / in the same thread as these ones."""
        related = self.browse()
        pool = self.search([("state", "=", "new")], limit=1000)
        senders = {email_normalize(o.email_from) for o in self if o.email_from}
        ids = {o.message_id for o in self if o.message_id}
        roots = set()
        for o in self:
            refs = MSG_ID_RE.findall("%s %s" % (o.references or "", o.in_reply_to or ""))
            roots.update(refs[:1])
        for o in pool:
            if same_sender and o.email_from and email_normalize(o.email_from) in senders:
                related |= o
            if same_thread:
                refs = set(MSG_ID_RE.findall("%s %s" % (o.references or "", o.in_reply_to or "")))
                if refs & ids or (o.message_id and o.message_id in roots) or (refs & roots):
                    related |= o
        return related

    # ------------------------------------------------------------
    # crons
    # ------------------------------------------------------------

    @api.model
    def _cron_daily(self):
        self._cron_purge()
        self._cron_digest()

    @api.model
    def _cron_purge(self):
        days = int(self._icp("keep_days", "0") or 0)
        if days > 0:
            limit = fields.Datetime.now() - timedelta(days=days)
            self.sudo().search([("state", "!=", "new"), ("date", "<", limit)]).unlink()

    @api.model
    def _cron_digest(self):
        if self._icp("digest", "0") not in ("1", "True", "true"):
            return
        group = self.env.ref("dwo_mail_orphan_routing.group_dwo_orphan_manager")
        since = self._icp("last_digest") or False
        if not since:
            since = fields.Datetime.to_string(fields.Datetime.now() - timedelta(days=1))
        now = fields.Datetime.now()
        icp = self.env["ir.config_parameter"].sudo()
        base = (icp.get_str("web.base.url") if hasattr(icp, "get_str") else icp.get_param("web.base.url")) or ""
        company = self.env.company
        for user in group.sudo().all_user_ids if "all_user_ids" in group._fields else group.sudo().users:
            if not user.email or not user.active:
                continue
            orphans = self.with_user(user).search([("state", "=", "new"), ("create_date", ">", since)], order="date desc")
            if not orphans:
                continue
            by_address = {}
            for o in orphans:
                by_address[o.rcpt_address or _("(unknown)")] = by_address.get(o.rcpt_address or _("(unknown)"), 0) + 1
            rows = Markup("").join(
                Markup("<li>%s: <b>%s</b></li>") % (a, n) for a, n in sorted(by_address.items()))
            items = Markup("").join(
                Markup("<li>%s - %s</li>") % (escape(o.email_from or ""), escape(o.subject or _("(no subject)")))
                for o in orphans[:15])
            more = Markup("<p>... %s</p>") % _("and %s more", len(orphans) - 15) if len(orphans) > 15 else Markup("")
            action = self.env.ref("dwo_mail_orphan_routing.action_dwo_mail_orphan")
            link = "%s/odoo/action-%s" % (base, action.id)
            body = Markup(
                "<p>%s</p><ul>%s</ul><p>%s</p><ul>%s</ul>%s<p><a href=\"%s\">%s</a></p>"
            ) % (
                _("%s new orphan emails could not be attached to any record since the last digest.", len(orphans)),
                rows, _("Latest:"), items, more, link, _("Open the orphan inbox"))
            self.env["mail.mail"].sudo().create({
                "subject": _("Orphan emails: %s new", len(orphans)),
                "body_html": body,
                "email_to": user.email,
                "email_from": company.email_formatted or user.email_formatted,
                "auto_delete": True,
            })
        self._icp_set("last_digest", fields.Datetime.to_string(now))


class DwoMailOrphanSuggestion(models.Model):
    _name = "dwo.mail.orphan.suggestion"
    _description = "Orphan mail suggestion"
    _order = "sequence, score desc, id"

    orphan_id = fields.Many2one("dwo.mail.orphan", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer()
    res_model = fields.Char("Model")
    res_id = fields.Many2oneReference("Record ID", model_field="res_model")
    model_name = fields.Char("Document", compute="_compute_model_name")
    name = fields.Char("Record")
    score = fields.Integer("Match")
    reason = fields.Char("Why")

    def _compute_model_name(self):
        for rec in self:
            rec.model_name = rec.res_model in self.env and self.env["ir.model"]._get(rec.res_model).name or rec.res_model

    def action_route(self):
        self.ensure_one()
        follow = self.env["dwo.mail.orphan"]._icp("follow_sender", "0") in ("1", "True", "true")
        self.orphan_id._route_to(self.res_model, self.res_id, follow=follow)
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self.res_model,
            "res_id": self.res_id,
            "view_mode": "form",
            "views": [(False, "form")],
        }


class MailThreadAccess(models.AbstractModel):
    _inherit = "mail.thread"

    def _dwo_check_access(self, operation):
        """check_access / check_access_rights + check_access_rule across versions."""
        if hasattr(self, "check_access"):
            return self.check_access(operation)
        self.check_access_rights(operation)
        return self.check_access_rule(operation)
