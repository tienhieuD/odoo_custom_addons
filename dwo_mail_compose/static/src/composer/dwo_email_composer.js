/* @odoo-module */

import {
    Component,
    markup,
    onMounted,
    onWillStart,
    onWillUnmount,
    useEffect,
    useExternalListener,
    useState,
} from "@odoo/owl";
import { getWysiwygClass } from "web_editor.loader";
import { toInline, getCSSRules } from "web_editor.convertInline";
import { HtmlFieldWysiwygAdapterComponent } from "@web_editor/js/backend/html_field";
import { registerMessagingComponent } from "@mail/utils/messaging_component";
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { deserializeDateTime, formatDateTime } from "@web/core/l10n/dates";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { localization } from "@web/core/l10n/localization";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

import { DwoAddressInput } from "./dwo_address_input";
import { DwoApprovalDialog } from "./dwo_approval_dialog";
import { DwoSaveTemplateDialog } from "./dwo_save_template_dialog";
import { DwoTemplateConflictDialog } from "./dwo_template_conflict_dialog";
import { DwoTemplateDropdown } from "./dwo_template_dropdown";

const SAVE_DELAY = 1500;

/** Text of an HTML string, without loading anything (a parsed document is inert). */
function textOf(html) {
    const doc = new DOMParser().parseFromString(html || "", "text/html");
    return (doc.body.textContent || "").replace(/\s+/g, " ").trim();
}

/**
 * Cut a body in what the user writes (above) and the quoted email (from the quote block on).
 */
export function splitBody(html) {
    const doc = new DOMParser().parseFromString(html || "", "text/html");
    const root = doc.body;
    const quote = root.querySelector("#divRplyFwdMsg");
    if (!quote) {
        return { above: root.innerHTML, quote: "" };
    }
    let top = quote;
    while (top.parentElement && top.parentElement !== root) {
        top = top.parentElement;
    }
    const nodes = [...root.childNodes];
    const index = nodes.indexOf(top);
    const serialize = (list) => {
        const holder = doc.createElement("div");
        list.forEach((node) => holder.appendChild(node.cloneNode(true)));
        return holder.innerHTML;
    };
    return { above: serialize(nodes.slice(0, index)), quote: serialize(nodes.slice(index)) };
}

/**
 * The body without the empty lines at its start: the lines a user finds to write in when an email
 * is started. What remains is the signature (and nothing else when there is none).
 */
export function withoutLeadingBlankLines(html) {
    const doc = new DOMParser().parseFromString(html || "", "text/html");
    const root = doc.body;
    const isBlank = (node) =>
        node.nodeType === Node.TEXT_NODE
            ? !node.textContent.trim()
            : ["P", "DIV"].includes(node.tagName) &&
              !node.textContent.trim() &&
              ![...node.children].some((child) => child.tagName !== "BR");
    while (root.firstChild && isBlank(root.firstChild)) {
        root.removeChild(root.firstChild);
    }
    return root.innerHTML;
}

/**
 * Inline form of the Send email button. All the rules (defaults, quote,
 * subject, reply-all, sending) come from the server model dwo.mail.composer;
 * this component displays, edits and autosaves the draft.
 */
export class DwoEmailComposer extends Component {
    static template = "dwo_mail_compose.EmailComposer";
    static components = {
        HtmlFieldWysiwygAdapterComponent,
        DwoAddressInput,
        DwoTemplateDropdown,
        AutoComplete,
        Dropdown,
        DropdownItem,
    };
    static props = {
        thread: Object,
        mode: { type: [String, Boolean], optional: true },
        refMessageId: { type: [Number, Boolean], optional: true },
        // the email opened last on this screen, and how the chatter is told when it changes
        preferredEmailId: { type: [Number, Boolean], optional: true },
        onEmailChange: { type: Function, optional: true },
        onClose: Function,
        onSent: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.http = useService("http");
        // the service without the wrapper that refuses a call after the form is gone: the last save can end after it
        this.rawRpc = this.env.services.rpc;
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            editorKey: 0,
            // the message fills the whole screen (only the body is edited)
            expanded: false,
            // the content an editor is created with: set together with editorKey, never read
            // from bodyHtml which the editor itself keeps rewriting while the user types
            editorContent: "",
            from: "",
            to: [],
            cc: [],
            bcc: [],
            showCc: false,
            showBcc: false,
            showReplyTo: false,
            subject: "",
            templateId: 0,
            templateName: "",
            templateDropdownKey: 0,
            fromKey: 0,
            replyTo: "",
            replyToDefault: "",
            replyToCustom: false,
            replyToManaged: true,
            attachments: [],
            fromOptions: [],
            mode: "new",
            refMessageId: false,
            savedAt: "",
            hasDraft: false,
            // the stored email being edited: it has an id after the first save
            emailId: false,
            emailState: "draft",
            approvers: [],
            requestComment: "",
            decisionComment: "",
            decidedBy: "",
            editedAfterRequest: false,
            // the unsent emails of the user on this record
            emails: [],
            // from the server: which buttons to show and who can approve (see _dwo_policy)
            policy: {
                require_approval: false, can_send_now: true, can_request_approval: false,
                allow_self_approval: true, approver_ids: [], user_id: 0,
            },
            newerEmail: false,
            sending: false,
            uploading: 0,
        });
        this.bodyHtml = "";
        // what the editor holds right after it was loaded, i.e. the HTML tidied by the editor itself
        this.baselineHtml = null;
        // what the form held when it was loaded or last filled by a template: used to know
        // whether the user wrote something of their own since
        this.snapshot = { subject: "", aboveText: "" };
        this.snapshotMode = "capture";
        // what the current template added, so choosing another template can take it back
        this.templateAdded = { to: [], cc: [], bcc: [], attachments: [] };
        this.editor = null;
        this.dirty = false;
        this.destroyed = false;
        this.closing = false;
        // set when the email was approved and sent while the form was open: nothing is saved anymore
        this.locked = false;
        this.saveTimer = null;
        this.savePromise = null;
        onWillStart(async () => {
            await this.loadWysiwyg();
            await this.load();
        });
        // Esc brings the expanded body back, wherever the focus is
        useExternalListener(window, "keydown", (ev) => this.onKeydown(ev));
        // The sticky statusbar of a form (z-index 1020) covers the body shown on the whole screen,
        // whose fixed position lives in the stacking context of the form: while it is expanded the
        // page tells the statusbar to go down (see the scss)
        useEffect(
            (expanded) => {
                if (!expanded) {
                    return;
                }
                document.body.classList.add("o-dwo-composeExpanded");
                return () => document.body.classList.remove("o-dwo-composeExpanded");
            },
            () => [this.state.expanded]
        );
        useEffect(
            () => this.captureSnapshot(),
            () => [this.state.editorKey, this.state.loading]
        );
        onMounted(() => {
            if (this.props.mode) {
                // a Reply or Forward is a new email: it is stored now, not at the first edit
                this.dirty = true;
                this.saveNow();
            }
        });
        onWillUnmount(() => {
            // last save of the pending change; after this the component must not touch its state
            this.closing = true;
            clearTimeout(this.saveTimer);
            if (this.dirty) {
                this.saveNow();
            }
            this.destroyed = true;
        });
    }

    get model() {
        return this.props.thread.model;
    }

    get resId() {
        return this.props.thread.id;
    }

    /** The subject of the email; before there is one, what the form is. */
    get title() {
        return (this.state.subject || "").trim() || _t("Compose email");
    }

    async load() {
        const state = await this.orm.call("dwo.mail.composer", "get_state", [
            this.model,
            this.resId,
            this.props.mode ? false : this.props.preferredEmailId || false,
        ]);
        this.state.fromOptions = state.from_options;
        this.state.emails = state.emails;
        this.state.policy = state.policy;
        let data;
        if (this.props.mode) {
            data = await this.orm.call("dwo.mail.composer", "get_defaults", [
                this.model,
                this.resId,
                this.props.refMessageId || false,
                this.props.mode,
            ]);
        } else if (state.current) {
            data = state.current;
            this.state.newerEmail = state.newer_email;
        } else {
            data = state.defaults;
        }
        this.applyData(data);
        this.state.loading = false;
        this.refreshReplyTo();
    }

    applyData(data) {
        this.state.from = data.from || "";
        this.state.to = data.to || [];
        this.state.cc = data.cc || [];
        this.state.bcc = data.bcc || [];
        // Cc and Bcc are shown when they have a value, else behind their button
        this.state.showCc = this.state.cc.length > 0;
        this.state.showBcc = this.state.bcc.length > 0;
        this.state.subject = data.subject || "";
        this.state.templateId = data.template_id || 0;
        this.state.templateName = data.template_name || "";
        this.state.replyTo = data.reply_to || "";
        this.state.replyToCustom = Boolean(data.reply_to_custom);
        this.state.replyToDefault = data.reply_to_custom ? "" : data.reply_to || "";
        this.state.replyToManaged = data.reply_to_managed ?? true;
        this.state.showReplyTo = this.state.replyToCustom;
        this.snapshot.subject = data.subject || "";
        this.snapshotMode = "capture";
        this.state.attachments = data.attachments || [];
        this.state.mode = data.mode || "new";
        this.state.refMessageId = data.ref_message_id || false;
        this.state.emailId = data.id || false;
        this.state.emailState = data.state || "draft";
        this.locked = false;
        this.state.approvers = data.approvers || [];
        this.state.requestComment = data.request_comment || "";
        this.state.decisionComment = data.decision_comment || "";
        this.state.decidedBy = data.decided_by || "";
        this.state.editedAfterRequest = Boolean(data.edited_after_request);
        this.state.hasDraft = Boolean(data.id);
        this.state.savedAt = data.id ? this.timeLabel(data.saved_at) : "";
        this.bodyHtml = data.body || "";
        this.state.editorContent = this.bodyHtml;
        this.templateAdded = { to: [], cc: [], bcc: [], attachments: [] };
    }

    // --- editor -----------------------------------------------------------

    /**
     * The editor is the standard Odoo HTML editor, configured like the html_mail
     * field: no columns, links open in a new tab. Images can be inserted from the
     * toolbar or pasted: both end as an attachment of the record and a link with an
     * access token in the body (see uploadPendingImages), never as a base64 blob.
     */
    get editorConfig() {
        // the options of the legacy Wysiwyg widget of Odoo 16 (web_editor)
        return {
            value: this.state.editorContent || "",
            autostart: false,
            height: "auto",
            allowCommandImage: true,
            allowCommandVideo: false,
            recordInfo: { res_model: this.model, res_id: this.resId },
        };
    }

    /**
     * In Odoo 16 the editor is a jQuery widget whose assets are not in the backend bundle: they are loaded
     * when they are needed, like the html field does (the form shows the editor after this).
     */
    async loadWysiwyg() {
        // the legacy widget of Odoo 16, with its assets loaded when they are needed
        this.Wysiwyg = await getWysiwygClass();
    }

    /**
     * The editor of web_editor builds its editable and its helpers itself, next to the component, so Owl does
     * not remove them when the component is replaced (a new template, a new email, an email chosen in the
     * list): the old editable could stay in the page under the new one. Whatever is not the current editor's
     * is removed.
     */
    removeStaleEditor(wysiwyg) {
        const current = wysiwyg.$editable[0];
        const box = current.closest(".o-dwo-editorBox");
        if (!box) {
            return;
        }
        for (const editable of box.querySelectorAll(".note-editable")) {
            if (editable !== current) {
                editable.remove();
            }
        }
        // the containers of the table menus of an editor that is gone are empty
        for (const container of box.querySelectorAll(".o_table_ui_container")) {
            if (!container.children.length) {
                container.remove();
            }
        }
    }

    /** Called by the Wysiwyg once it is mounted: it starts the editor and gives the adapter below. */
    async onStartWysiwyg(wysiwyg) {
        await wysiwyg.startEdition();
        wysiwyg.odooEditor.addEventListener("historyStep", () => this.onEditorChange());
        wysiwyg.$editable[0].classList.add("o-dwo-editor", "p-2");
        this.removeStaleEditor(wysiwyg);
        // the few things the form needs from an editor, as the html_editor of 18 offers them
        this.editor = {
            wysiwyg,
            get editable() {
                return wysiwyg.$editable?.[0];
            },
            document: wysiwyg.odooEditor.document,
            getContent: () => wysiwyg.getValue(),
            getElContent: () => {
                const el = document.createElement("div");
                el.innerHTML = wysiwyg.getValue();
                return el;
            },
        };
        // the editor starts after the form is mounted: what it holds now is the baseline of the changes
        this.captureSnapshot();
    }

    onEditorChange() {
        // the editor reports a last change while it is being closed, with a content that
        // must not replace the draft
        if (this.closing || this.destroyed || !this.editor?.editable?.isConnected) {
            return;
        }
        this.bodyHtml = this.editor.getContent();
        this.scheduleSave();
    }

    /**
     * Read the content straight from the editor. Its change event comes one step late, so a
     * text typed just before Close or Send would otherwise be missing from the draft.
     */
    syncBody() {
        if (this.destroyed || !this.editor?.editable?.isConnected) {
            return;
        }
        const html = this.editor.getContent();
        if (html !== this.bodyHtml) {
            this.bodyHtml = html;
            // The editor tidies the HTML it is given, so it differs from the server's HTML before
            // anyone typed. Only a difference with what the editor held when it loaded is an edit:
            // otherwise merely opening the form and closing it, or clicking a row of the list,
            // would store a draft nobody wrote.
            if (this.baselineHtml === null || html !== this.baselineHtml) {
                this.dirty = true;
            }
        }
    }

    /** Load a new content in the editor: the editor is created again with it. */
    renderBody() {
        this.editor = null;
        this.state.editorContent = this.bodyHtml;
        this.state.editorKey++;
    }

    /**
     * Upload the images pasted or dropped in the editor (kept as base64 until now) as
     * attachments of the record, and point them to a link with an access token. Done
     * before each save and before sending, so neither the draft nor the email carries
     * a base64 image.
     */
    async uploadPendingImages() {
        const editable = this.editor && this.editor.editable;
        if (!editable || !editable.isConnected) {
            return;
        }
        // Odoo 16 keeps a pasted or dropped image as a base64 blob in the page: it becomes an attachment of
        // the record, and the image points to it, so neither the draft nor the email carries base64
        for (const img of editable.querySelectorAll('img[src^="data:"]')) {
            const [head, data] = img.getAttribute("src").split(",");
            const mimetype = (head.match(/^data:([^;]+)/) || [])[1] || "image/png";
            const attachment = await this.rawRpc("/web_editor/attachment/add_data", {
                name: img.dataset.fileName || `image.${mimetype.split("/")[1] || "png"}`,
                data,
                is_image: true,
                res_model: this.model,
                res_id: this.resId,
                generate_access_token: true,
            });
            if (attachment && attachment.id && attachment.image_src) {
                // Odoo 16 gives no access token with the attachment: the people who receive the email have
                // no session, the token is what lets them see the image
                const [token] = await this.rawRpc("/web/dataset/call_kw/ir.attachment/generate_access_token", {
                    model: "ir.attachment",
                    method: "generate_access_token",
                    args: [[attachment.id]],
                    kwargs: {},
                });
                img.setAttribute("src", attachment.image_src + (token ? `?access_token=${token}` : ""));
                img.classList.remove("o_b64_image_to_save", "o_modified_image_to_save");
            }
        }
    }

    /**
     * The content with its CSS turned into inline styles, as mail clients ignore stylesheets.
     * It is what is stored on every save, like the html_mail field does, so a send from the
     * browser and a send made later by the server use the same HTML.
     */
    async getInlinedBody() {
        if (!this.editor?.editable?.isConnected) {
            return this.bodyHtml;
        }
        await this.uploadPendingImages();
        const el = this.editor.getElContent();
        const cssRules = getCSSRules(this.editor.document);
        this.editor.editable.after(el);
        await toInline($(el), cssRules, this.editor.wysiwyg.$iframe);
        el.remove();
        return el.innerHTML;
    }

    timeLabel(datetimeString) {
        const date = datetimeString ? new Date(datetimeString.replace(" ", "T") + "Z") : new Date();
        return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    payload(body = this.bodyHtml) {
        return {
            from: this.state.from,
            to: this.state.to,
            cc: this.state.cc,
            bcc: this.state.bcc,
            subject: this.state.subject,
            reply_to: this.state.replyTo,
            reply_to_custom: this.state.replyToCustom,
            body,
            template_id: this.state.templateId || false,
            attachment_ids: this.state.attachments.map((a) => a.id),
            mode: this.state.mode,
            ref_message_id: this.state.refMessageId,
            email_id: this.state.emailId,
        };
    }

    // --- autosave ---------------------------------------------------------

    scheduleSave() {
        if (this.destroyed || this.locked) {
            return;
        }
        this.dirty = true;
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => this.saveNow(), SAVE_DELAY);
    }

    /** Saves are chained: a save never starts before the previous one is stored. */
    saveNow() {
        clearTimeout(this.saveTimer);
        const previous = this.savePromise || Promise.resolve();
        this.savePromise = previous.catch(() => {}).then(() => this.doSave());
        return this.savePromise;
    }

    async doSave() {
        this.syncBody();
        if (this.state.sending || !this.dirty) {
            return;
        }
        this.dirty = false;
        const body = await this.getInlinedBody();
        // global rpc: the save can finish after the form is gone, which a service bound to the component forbids
        // each save carries the id the first one got: saves are chained, so there is never a second record
        const saved = await this.rawRpc("/web/dataset/call_kw/dwo.mail.composer/save_email", {
            model: "dwo.mail.composer",
            method: "save_email",
            args: [this.model, this.resId, this.state.emailId, this.payload(body)],
            kwargs: {},
        });
        if (this.destroyed) {
            return;
        }
        const stateChanged = saved.state !== this.state.emailState;
        if (saved.id !== this.state.emailId) {
            this.props.onEmailChange?.(saved.id);
        }
        this.state.emailId = saved.id;
        this.state.emailState = saved.state;
        this.state.hasDraft = true;
        this.state.savedAt = this.timeLabel();
        if (saved.state === "sent") {
            // an approver approved it while it was open: it left, the server did not write the edit
            this.locked = true;
            this.dirty = false;
            clearTimeout(this.saveTimer);
            this.notification.add(_t("This email was approved and sent. Your last changes were not saved."), {
                type: "warning",
            });
        }
        if (stateChanged) {
            // approved, rejected or reassigned meanwhile: show who decided and what they wrote
            await this.refreshMeta();
        }
        this.refreshList();
    }

    /** The approval data of the stored email, without touching what the user is writing. */
    async refreshMeta() {
        const data = await this.orm.call("dwo.mail.composer", "load_email", [this.state.emailId]);
        if (this.destroyed) {
            return;
        }
        this.state.emailState = data.state;
        this.state.approvers = data.approvers;
        this.state.requestComment = data.request_comment;
        this.state.decisionComment = data.decision_comment;
        this.state.decidedBy = data.decided_by;
        this.state.editedAfterRequest = data.edited_after_request;
    }

    // --- editing ----------------------------------------------------------

    onFieldChange(field, value) {
        this.state[field] = value;
        this.scheduleSave();
    }

    showCcField() {
        this.state.showCc = true;
    }

    showBccField() {
        this.state.showBcc = true;
    }

    // --- From -------------------------------------------------------------

    get fromLabel() {
        const option = this.state.fromOptions.find((o) => o.email === this.state.from);
        return option ? `${option.name} <${option.email}>` : "";
    }

    get fromSources() {
        return [
            {
                options: (term) => {
                    const needle = (term || "").trim().toLowerCase();
                    return this.state.fromOptions
                        .filter((o) => !needle || `${o.name} ${o.email}`.toLowerCase().includes(needle))
                        .map((o) => ({
                            label: `${o.name} <${o.email}>`,
                            value: o.email,
                        }));
                },
            },
        ];
    }

    /** Odoo 18: the AutoComplete calls one onSelect for every option. */
    onFromSelect(option) {
        this.onFromPicked(option.value);
    }

    onFromPicked(email) {
        this.state.from = email;
        this.scheduleSave();
        if (!this.state.replyToCustom) {
            this.refreshReplyTo();
        }
    }

    /** Only a listed sender is accepted: any other text goes back to the current one. */
    onFromTyped({ inputValue }) {
        const typed = (inputValue || "").trim().toLowerCase();
        const match = this.state.fromOptions.find(
            (o) => `${o.name} <${o.email}>`.toLowerCase() === typed
        );
        if (match) {
            this.onFromPicked(match.email);
        } else {
            this.state.fromKey++;
        }
    }

    // --- Advanced: Reply-To -----------------------------------------------

    /** The default comes from the model of the record (the sales team address in CRM). */
    async refreshReplyTo() {
        if (this.destroyed) {
            return;
        }
        const result = await this.orm.call("dwo.mail.composer", "get_reply_to", [
            this.model,
            this.resId,
            this.state.from || false,
            this.state.replyToCustom ? this.state.replyTo : false,
        ]);
        if (this.destroyed) {
            return;
        }
        this.state.replyToDefault = result.default.email;
        this.state.replyToManaged = result.managed;
        if (!this.state.replyToCustom) {
            this.state.replyTo = result.default.email;
        }
    }

    addReplyTo() {
        this.state.showReplyTo = true;
    }

    /** The row only goes away while it holds the default: a custom value stays visible. */
    hideReplyTo() {
        if (!this.state.replyToCustom) {
            this.state.showReplyTo = false;
        }
    }

    onReplyToInput(ev) {
        this.state.replyTo = ev.target.value;
        this.state.replyToCustom = this.state.replyTo.trim().toLowerCase() !== this.state.replyToDefault;
        this.scheduleSave();
    }

    resetReplyTo() {
        this.state.replyToCustom = false;
        this.refreshReplyTo();
        this.scheduleSave();
    }

    // --- template ---------------------------------------------------------

    /** What the user wrote, compared to what the form held when it was filled. */
    isContentDirty() {
        const subjectDirty = (this.state.subject || "").trim() !== (this.snapshot.subject || "").trim();
        const html = this.editor?.editable?.isConnected ? this.editor.getContent() : this.bodyHtml;
        const bodyDirty = textOf(splitBody(html).above) !== this.snapshot.aboveText;
        return subjectDirty || bodyDirty;
    }

    captureSnapshot() {
        if (this.state.loading) {
            return;
        }
        this.baselineHtml = this.editor?.editable?.isConnected ? this.editor.getContent() : null;
        if (this.snapshotMode === "keep") {
            // the template text was added after the user's: still the user's content
            this.snapshotMode = "capture";
            return;
        }
        const html = this.editor?.editable?.isConnected ? this.editor.getContent() : this.bodyHtml;
        this.snapshot.aboveText = textOf(splitBody(html).above);
    }

    /** A template chosen in the menu. */
    async onTemplatePicked(record) {
        if (!record || record.id === this.state.templateId) {
            return;
        }
        if (!this.isContentDirty()) {
            // nothing written yet: the template goes into the empty lines, the signature stays
            return this.applyTemplate(record, "fill");
        }
        this.dialog.add(DwoTemplateConflictDialog, {
            onOverwrite: () => this.applyTemplate(record, "overwrite"),
            onAppend: () => this.applyTemplate(record, "append"),
        });
    }

    /** Take back what the current template added; the text of the user stays. */
    clearTemplate() {
        this.state.templateId = 0;
        this.state.templateName = "";
        this.removeTemplateAdditions();
        this.scheduleSave();
    }

    /**
     * Apply a template: subject, body (above the quote), From, recipients and
     * attachments, all computed on this record by the server. Recipients of the
     * template are added to the ones already there (a reply-all keeps its people),
     * and choosing another template first takes back what the previous one added.
     * "append" keeps the user's subject and message and puts the template text after it.
     * "fill" is for a form nothing was written in: the text takes the place of the empty lines
     * and the signature stays under it. "overwrite" replaces everything above the quote.
     */
    async applyTemplate(record, mode) {
        this.removeTemplateAdditions();
        const result = await this.orm.call("dwo.mail.composer", "apply_template", [
            record.id,
            this.model,
            this.resId,
        ]);
        this.state.templateId = record.id;
        this.state.templateName = record.display_name || record.name || "";
        if (result.subject && (mode !== "append" || !this.state.subject.trim())) {
            this.state.subject = result.subject;
        }
        if (mode !== "append") {
            this.snapshot.subject = this.state.subject;
        }
        if (result.from) {
            this.onFromPicked(result.from);
        }
        this.mergeRecipients(result);
        this.state.attachments = [...this.state.attachments, ...result.attachments];
        this.templateAdded.attachments = result.attachments.map((a) => a.id);
        if (result.body) {
            const html = this.editor?.editable?.isConnected ? this.editor.getContent() : this.bodyHtml;
            const { above, quote } = splitBody(html);
            let newAbove = result.body;
            if (mode === "append") {
                newAbove = above + result.body;
            } else if (mode === "fill") {
                // into the empty lines: what follows them (the signature) is kept
                newAbove = result.body + withoutLeadingBlankLines(above);
            }
            this.bodyHtml = newAbove + (quote ? "<br/>" + quote : "");
            this.snapshotMode = mode === "append" ? "keep" : "capture";
            this.renderBody();
        }
        for (const warning of result.warnings) {
            this.notification.add(warning, { type: "warning" });
        }
        this.scheduleSave();
    }

    mergeRecipients(result) {
        for (const field of ["to", "cc", "bcc"]) {
            // no limit between the fields; an address is not added twice in the same one
            const used = new Set(this.state[field].map((a) => a.email));
            const added = [];
            for (const address of result[field]) {
                if (!used.has(address.email)) {
                    used.add(address.email);
                    added.push({ email: address.email, name: address.name });
                }
            }
            this.state[field] = [...this.state[field], ...added];
            this.templateAdded[field] = added.map((a) => a.email);
        }
        if (result.cc.length) {
            this.state.showCc = true;
        }
        if (result.bcc.length) {
            this.state.showBcc = true;
        }
    }

    removeTemplateAdditions() {
        for (const field of ["to", "cc", "bcc"]) {
            this.state[field] = this.state[field].filter(
                (a) => !this.templateAdded[field].includes(a.email)
            );
        }
        this.state.attachments = this.state.attachments.filter(
            (a) => !this.templateAdded.attachments.includes(a.id)
        );
        this.templateAdded = { to: [], cc: [], bcc: [], attachments: [] };
    }

    /** Save the email being written as a template of this kind of record. */
    onSaveTemplate() {
        this.dialog.add(DwoSaveTemplateDialog, {
            onSave: async (name) => {
                this.syncBody();
                const template = await this.orm.call("dwo.mail.composer", "save_as_template", [
                    this.model,
                    this.resId,
                    name,
                    {
                        subject: this.state.subject,
                        body: this.bodyHtml,
                        attachment_ids: this.state.attachments.map((a) => a.id),
                    },
                ]);
                this.notification.add(_t("Template saved: %s", template.name), { type: "success" });
                this.state.templateDropdownKey++;
            },
        });
    }

    // --- attachments ------------------------------------------------------

    async onFilesSelected(ev) {
        for (const file of ev.target.files) {
            this.state.uploading++;
            try {
                const response = await this.http.post("/mail/attachment/upload", {
                    csrf_token: odoo.csrf_token,
                    ufile: file,
                    thread_id: this.resId,
                    thread_model: this.model,
                    is_pending: true,
                });
                if (response.error) {
                    this.notification.add(response.error, { type: "danger" });
                } else {
                    this.state.attachments.push({
                        id: response.data.attachment_id,
                        name: file.name,
                        size: file.size,
                    });
                    this.scheduleSave();
                }
            } finally {
                this.state.uploading--;
            }
        }
        ev.target.value = "";
    }

    /** Every deletion asks first. */
    confirmDelete({ title, body, confirmLabel, confirm }) {
        this.dialog.add(ConfirmationDialog, {
            title,
            body,
            confirmLabel: confirmLabel || _t("Delete"),
            confirm,
            cancel: () => {},
        });
    }

    askRemoveAttachment(attachment) {
        this.confirmDelete({
            title: _t("Remove the file?"),
            body: _t("%s will no longer be attached to this email.", attachment.name),
            confirmLabel: _t("Remove"),
            confirm: () => this.removeAttachment(attachment),
        });
    }

    removeAttachment(attachment) {
        this.state.attachments = this.state.attachments.filter((a) => a.id !== attachment.id);
        this.scheduleSave();
    }

    // --- actions ----------------------------------------------------------

    /** A save already on the wire could land after the draft is deleted: wait for it. */
    async settleSave() {
        clearTimeout(this.saveTimer);
        try {
            await this.savePromise;
        } catch {
            // a failed autosave does not matter here
        }
    }

    async onSend() {
        this.state.sending = true;
        await this.settleSave();
        try {
            this.bodyHtml = await this.getInlinedBody();
            const result = await this.orm.call("dwo.mail.composer", "send", [
                this.model,
                this.resId,
                this.payload(),
            ]);
            this.dirty = false;
            this.notification.add(_t("Email sent"), { type: "success" });
            this.props.onSent(result.message_id);
        } finally {
            this.state.sending = false;
        }
    }

    deleteBody(state) {
        if (state === "pending") {
            return _t("The approval request is closed and the people who were asked are told. The email is deleted.");
        }
        if (state === "rejected") {
            return _t("The email and what the approver wrote about it are deleted.");
        }
        return _t("This draft is deleted. This cannot be undone.");
    }

    /** The Delete draft button: asks, then deletes the email in the form. */
    askDeleteCurrent() {
        this.confirmDelete({
            title: _t("Delete this email?"),
            body: this.deleteBody(this.state.emailState),
            confirm: () => this.onDeleteDraft(),
        });
    }

    /** Remove the draft and go back to the initial content of the form. */
    async onDeleteDraft() {
        this.dirty = false;
        await this.settleSave();
        const defaults = await this.orm.call("dwo.mail.composer", "delete_email", [
            this.model,
            this.resId,
            this.state.emailId,
        ]);
        this.applyData(defaults);
        this.renderBody();
        this.state.newerEmail = false;
        this.props.onEmailChange?.(false);
        this.refreshList();
    }

    async onApplyDefaults() {
        const defaults = await this.orm.call("dwo.mail.composer", "get_defaults", [
            this.model,
            this.resId,
            false,
            "reply",
        ]);
        // same stored email, new content
        const { emailId, emailState } = this.state;
        this.applyData(defaults);
        this.state.emailId = emailId;
        this.state.emailState = emailState;
        this.state.hasDraft = Boolean(emailId);
        this.renderBody();
        this.state.newerEmail = false;
        this.scheduleSave();
    }

    onDismissBanner() {
        this.state.newerEmail = false;
    }

    // --- the stored emails of the user on this record --------------------

    async refreshList() {
        if (this.destroyed) {
            return;
        }
        this.state.emails = await this.orm.call("dwo.mail.composer", "list_emails", [this.model, this.resId]);
    }

    /** Open an email of the list in the form, after saving the one being written. */
    async onOpenEmail(email) {
        if (email.id === this.state.emailId) {
            return;
        }
        await this.saveNow();
        const data = await this.orm.call("dwo.mail.composer", "load_email", [email.id]);
        this.applyData(data);
        this.renderBody();
        this.state.newerEmail = false;
        this.props.onEmailChange?.(email.id);
        this.refreshReplyTo();
        this.refreshList();
    }

    /** Delete an email of the list (always after a question): the one in the form goes back to the defaults. */
    onDeleteListed(email) {
        this.confirmDelete({
            title: _t("Delete this email?"),
            body: this.deleteBody(email.state),
            confirm: async () => {
                if (email.id === this.state.emailId) {
                    return this.onDeleteDraft();
                }
                await this.orm.call("dwo.mail.composer", "delete_email", [this.model, this.resId, email.id]);
                this.refreshList();
            },
        });
    }

    formatListDate(serialized) {
        return serialized ? formatDateTime(deserializeDateTime(serialized)) : "";
    }

    // --- the message on the whole screen ------------------------------------

    toggleExpanded() {
        this.state.expanded = !this.state.expanded;
    }

    onKeydown(ev) {
        // a dialog opened from the editor (a link, an image) has its own Esc
        if (ev.key === "Escape" && this.state.expanded && !document.querySelector(".modal")) {
            this.state.expanded = false;
        }
    }

    async onNewEmail() {
        await this.saveNow();
        const defaults = await this.orm.call("dwo.mail.composer", "get_defaults", [
            this.model,
            this.resId,
            false,
            "reply",
        ]);
        this.applyData(defaults);
        this.renderBody();
        this.state.newerEmail = false;
        // the new email is created in the database right away: it is in the list, remembered, and
        // shows up when the form is opened again, even if nothing was typed yet
        this.dirty = true;
        await this.saveNow();
        this.refreshReplyTo();
    }

    // --- approval -----------------------------------------------------------

    onRequestApproval() {
        const { approver_ids, allow_self_approval, user_id } = this.state.policy;
        this.dialog.add(DwoApprovalDialog, {
            // empty list: everybody can approve
            allowedIds: approver_ids,
            excludedId: allow_self_approval ? false : user_id,
            onConfirm: async ({ approverIds, comment }) => {
                this.state.sending = true;
                try {
                    await this.settleSave();
                    this.syncBody();
                    this.bodyHtml = await this.getInlinedBody();
                    const result = await this.orm.call("dwo.mail.composer", "request_approval", [
                        this.model,
                        this.resId,
                        this.state.emailId,
                        this.payload(),
                        approverIds,
                        comment || null,
                    ]);
                    this.dirty = false;
                    this.state.emailId = result.id;
                    this.state.emailState = result.state;
                    this.state.hasDraft = true;
                    this.state.emails = result.emails;
                    const loaded = await this.orm.call("dwo.mail.composer", "load_email", [result.id]);
                    this.state.approvers = loaded.approvers;
                    this.state.requestComment = loaded.request_comment;
                    this.state.decisionComment = "";
                    this.state.editedAfterRequest = false;
                    this.notification.add(_t("The approval was requested"), { type: "success" });
                } finally {
                    this.state.sending = false;
                }
            },
        });
    }

    get stateLabel() {
        return {
            draft: _t("Draft"),
            pending: _t("Waiting for approval"),
            rejected: _t("Rejected"),
            sent: _t("Approved and sent"),
        }[this.state.emailState];
    }

    get approverNames() {
        return this.state.approvers.map((u) => u.name).join(", ");
    }

    /** An address typed but not yet turned into a badge is committed first, so the draft keeps it. */
    async commitTypedAddresses() {
        const typing = [...document.querySelectorAll(".o-dwo-emailComposer .o-dwo-addressText")].filter(
            (input) => input.value.trim()
        );
        if (typing.length) {
            // blur() sends nothing when the window has no focus (a headless browser): the event is sent too
            typing.forEach((input) => {
                input.blur();
                input.dispatchEvent(new FocusEvent("blur"));
            });
            // the badge is made a moment after the blur
            await new Promise((resolve) => setTimeout(resolve, 200));
        }
    }

    async onClose() {
        // wait for the draft to be stored, so the Send email button can show it; the form
        // closes even when the save fails
        try {
            await this.commitTypedAddresses();
            await this.saveNow();
        } finally {
            this.closing = true;
            this.props.onClose();
        }
    }
}

registerMessagingComponent(DwoEmailComposer);
