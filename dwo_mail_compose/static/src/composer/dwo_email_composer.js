/** @odoo-module **/

import { toInline, getCSSRules } from 'web_editor.convertInline';
import { ComponentAdapter } from 'web.OwlCompatibility';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { _t } from '@web/core/l10n/translation';

import { DwoAddressInput } from './dwo_address_input';
import {
    DwoApprovalDialog,
    DwoConfirmDialog,
    DwoSaveTemplateDialog,
    DwoTemplateConflictDialog,
} from './dwo_dialogs';
import { DwoEditorHost } from './dwo_editor_host';
import { DwoTemplateDropdown } from './dwo_template_dropdown';
import { formatListDate, notify, orm, splitBody, textOf, withoutLeadingBlankLines } from './dwo_utils';

const { Component } = owl;
const { useExternalListener, useState } = owl.hooks;

const SAVE_DELAY = 1500;

/**
 * Inline form of the Send email button. All the rules (defaults, quote,
 * subject, reply-all, sending) come from the server model dwo.mail.composer;
 * this component displays, edits and autosaves the draft.
 */
export class DwoEmailComposer extends Component {

    setup() {
        super.setup();
        this.state = useState({
            loading: true,
            editorKey: 0,
            // the message fills the whole screen (only the body is edited)
            expanded: false,
            // the content an editor is created with: set together with editorKey, never read
            // from bodyHtml which the editor itself keeps rewriting while the user types
            editorContent: '',
            from: '',
            to: [],
            cc: [],
            bcc: [],
            showCc: false,
            showBcc: false,
            showReplyTo: false,
            subject: '',
            templateId: 0,
            templateName: '',
            templateDropdownKey: 0,
            replyTo: '',
            replyToDefault: '',
            replyToCustom: false,
            replyToManaged: true,
            attachments: [],
            fromOptions: [],
            mode: 'new',
            refMessageId: false,
            savedAt: '',
            hasDraft: false,
            // the stored email being edited: it has an id after the first save
            emailId: false,
            emailState: 'draft',
            approvers: [],
            requestComment: '',
            decisionComment: '',
            decidedBy: '',
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
            // the menu of the form that is open (advanced, send), a dialog and what it needs
            menu: '',
            dialog: '',
        });
        this.dialogProps = {};
        this.bodyHtml = '';
        // what the editor holds right after it was loaded, i.e. the HTML tidied by the editor itself
        this.baselineHtml = null;
        // what the form held when it was loaded or last filled by a template: used to know
        // whether the user wrote something of their own since
        this.snapshot = { subject: '', aboveText: '' };
        this.snapshotMode = 'capture';
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
        this.snapshotKey = '';
        this.editorArgsValue = null;
        for (const name of [
            'onTemplatePicked', 'onSaveTemplate', 'closeDialog', 'onKeydown', 'onStartWysiwyg', 'onChangeTo', 'onChangeCc', 'onChangeBcc',
        ]) {
            this[name] = this[name].bind(this);
        }
        // Esc brings the expanded body back, wherever the focus is
        useExternalListener(window, 'keydown', this.onKeydown);
        // a click outside a menu closes it
        useExternalListener(document, 'click', (ev) => {
            if (this.state.menu && !ev.target.closest('.o-dwo-menuHost')) {
                this.state.menu = '';
            }
        });
    }

    async willStart() {
        await this.load();
    }

    mounted() {
        this.afterRender();
        if (this.chatter.dwoMode) {
            // a Reply or Forward is a new email: it is stored now, not at the first edit
            this.dirty = true;
            this.saveNow();
        }
    }

    patched() {
        this.afterRender();
    }

    willUnmount() {
        // last save of the pending change; after this the component must not touch its state
        this.closing = true;
        clearTimeout(this.saveTimer);
        if (this.dirty) {
            this.saveNow();
        }
        this.destroyed = true;
        document.body.classList.remove('o-dwo-composeExpanded');
    }

    /**
     * What Owl 16 does with effects: The sticky statusbar of a form covers the body shown on the whole screen, whose
     * fixed position lives in the stacking context of the form: while it is expanded the page tells the statusbar to
     * go down (see the scss). And the snapshot of the content is taken again when the editor or the loading changes.
     */
    afterRender() {
        document.body.classList.toggle('o-dwo-composeExpanded', this.state.expanded);
        const key = `${this.state.editorKey}:${this.state.loading}`;
        if (key !== this.snapshotKey) {
            this.snapshotKey = key;
            this.captureSnapshot();
        }
    }

    // --- the chatter and its record ----------------------------------------

    /** @returns {mail.chatter} */
    get chatter() {
        return this.messaging.models['mail.chatter'].get(this.props.chatterLocalId);
    }

    get model() {
        return this.chatter.thread.model;
    }

    get resId() {
        return this.chatter.thread.id;
    }

    /** The subject of the email; before there is one, what the form is. */
    get title() {
        return (this.state.subject || '').trim() || this.env._t('Compose email');
    }

    async load() {
        const chatter = this.chatter;
        const mode = chatter.dwoMode;
        const state = await orm(this.env, 'dwo.mail.composer', 'get_state', [
            this.model,
            this.resId,
            mode ? false : chatter.dwoRememberedEmailId || false,
        ]);
        this.state.fromOptions = state.from_options;
        this.state.emails = state.emails;
        this.state.policy = state.policy;
        let data;
        if (mode) {
            data = await orm(this.env, 'dwo.mail.composer', 'get_defaults', [
                this.model,
                this.resId,
                chatter.dwoRefMessageId || false,
                mode,
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
        this.state.from = data.from || '';
        this.state.to = data.to || [];
        this.state.cc = data.cc || [];
        this.state.bcc = data.bcc || [];
        // Cc and Bcc are shown when they have a value, else behind their button
        this.state.showCc = this.state.cc.length > 0;
        this.state.showBcc = this.state.bcc.length > 0;
        this.state.subject = data.subject || '';
        this.state.templateId = data.template_id || 0;
        this.state.templateName = data.template_name || '';
        this.state.replyTo = data.reply_to || '';
        this.state.replyToCustom = Boolean(data.reply_to_custom);
        this.state.replyToDefault = data.reply_to_custom ? '' : data.reply_to || '';
        this.state.replyToManaged = data.reply_to_managed === undefined ? true : data.reply_to_managed;
        this.state.showReplyTo = this.state.replyToCustom;
        this.snapshot.subject = data.subject || '';
        this.snapshotMode = 'capture';
        this.state.attachments = data.attachments || [];
        this.state.mode = data.mode || 'new';
        this.state.refMessageId = data.ref_message_id || false;
        this.state.emailId = data.id || false;
        this.state.emailState = data.state || 'draft';
        this.locked = false;
        this.state.approvers = data.approvers || [];
        this.state.requestComment = data.request_comment || '';
        this.state.decisionComment = data.decision_comment || '';
        this.state.decidedBy = data.decided_by || '';
        this.state.editedAfterRequest = Boolean(data.edited_after_request);
        this.state.hasDraft = Boolean(data.id);
        this.state.savedAt = data.id ? this.timeLabel(data.saved_at) : '';
        this.bodyHtml = data.body || '';
        this.state.editorContent = this.bodyHtml;
        this.buildEditorArgs();
        this.templateAdded = { to: [], cc: [], bcc: [], attachments: [] };
    }

    // --- editor -----------------------------------------------------------

    get EditorHost() {
        return DwoEditorHost;
    }

    get ComponentAdapter() {
        return ComponentAdapter;
    }

    /**
     * The arguments of the editor widget. Owl 1 renders a template with an object made from the component
     * (Object.create): what the template reads is read there, and what it writes is lost. The arguments are
     * built here, by the component, each time a new editor is wanted (a new key), so the adapter does not see
     * a change at every render.
     */
    get editorArgs() {
        return this.editorArgsValue;
    }

    buildEditorArgs() {
        // the options of the Wysiwyg widget of Odoo 15 (web_editor): the content is the body of the draft; images
        // pasted in it stay in the body as base64 and the server turns them into attachments of the record
        const options = {
            value: this.state.editorContent || '',
            recordInfo: { res_model: this.model, res_id: this.resId },
            allowCommandVideo: false,
            linkForceNewWindow: true,
            tabsize: 0,
            resizable: false,
            mediaModalParams: { noVideos: true, res_model: this.model, res_id: this.resId, useMediaLibrary: false },
        };
        this.editorArgsValue = [options, this.onStartWysiwyg];
    }

    /** Called by the widget once the editor is started. */
    async onStartWysiwyg(wysiwyg) {
        wysiwyg.odooEditor.addEventListener('historyStep', () => this.onEditorChange());
        wysiwyg.$editable[0].classList.add('o-dwo-editor', 'p-2');
        // the few things the form needs from an editor
        this.editor = {
            wysiwyg,
            get editable() {
                return wysiwyg.$editable && wysiwyg.$editable[0];
            },
            document: wysiwyg.odooEditor.document,
            getContent: () => wysiwyg.getValue(),
            getElContent: () => {
                const el = document.createElement('div');
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
        if (this.closing || this.destroyed || !this.editorConnected()) {
            return;
        }
        this.bodyHtml = this.editor.getContent();
        this.scheduleSave();
    }

    editorConnected() {
        return Boolean(this.editor && this.editor.editable && this.editor.editable.isConnected);
    }

    /**
     * Read the content straight from the editor. Its change event comes one step late, so a
     * text typed just before Close or Send would otherwise be missing from the draft.
     */
    syncBody() {
        if (this.destroyed || !this.editorConnected()) {
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
        this.buildEditorArgs();
        this.state.editorKey++;
    }

    /**
     * The content with its CSS turned into inline styles, as mail clients ignore stylesheets.
     * It is what is stored on every save, like the html_mail field does, so a send from the
     * browser and a send made later by the server use the same HTML. Images pasted in the editor
     * (base64) are turned into attachments by the server.
     */
    async getInlinedBody() {
        if (!this.editorConnected()) {
            return this.bodyHtml;
        }
        const el = this.editor.getElContent();
        const cssRules = getCSSRules(this.editor.document);
        this.editor.editable.after(el);
        await toInline($(el), cssRules, this.editor.wysiwyg.$iframe);
        el.remove();
        return el.innerHTML;
    }

    timeLabel(datetimeString) {
        const date = datetimeString ? new Date(datetimeString.replace(' ', 'T') + 'Z') : new Date();
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
        // each save carries the id the first one got: saves are chained, so there is never a second record
        const saved = await orm(this.env, 'dwo.mail.composer', 'save_email', [
            this.model, this.resId, this.state.emailId, this.payload(body),
        ]);
        if (this.destroyed) {
            if (saved.id !== this.state.emailId) {
                this.chatter.dwoOnEmailChange(saved.id);
            }
            return;
        }
        const stateChanged = saved.state !== this.state.emailState;
        if (saved.id !== this.state.emailId) {
            this.chatter.dwoOnEmailChange(saved.id);
        }
        this.state.emailId = saved.id;
        this.state.emailState = saved.state;
        this.state.hasDraft = true;
        this.state.savedAt = this.timeLabel();
        if (saved.state === 'sent') {
            // an approver approved it while it was open: it left, the server did not write the edit
            this.locked = true;
            this.dirty = false;
            clearTimeout(this.saveTimer);
            this.notify(this.env._t('This email was approved and sent. Your last changes were not saved.'), 'warning');
        }
        if (stateChanged) {
            // approved, rejected or reassigned meanwhile: show who decided and what they wrote
            await this.refreshMeta();
        }
        this.refreshList();
    }

    notify(message, type) {
        notify(this.env, message, { type });
    }

    /** The approval data of the stored email, without touching what the user is writing. */
    async refreshMeta() {
        const data = await orm(this.env, 'dwo.mail.composer', 'load_email', [this.state.emailId]);
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

    onChangeTo(value) {
        this.onFieldChange('to', value);
    }

    onChangeCc(value) {
        this.onFieldChange('cc', value);
    }

    onChangeBcc(value) {
        this.onFieldChange('bcc', value);
    }

    onInputSubject(ev) {
        this.onFieldChange('subject', ev.target.value);
    }

    showCcField() {
        this.state.showCc = true;
    }

    showBccField() {
        this.state.showBcc = true;
    }

    toggleMenu(ev) {
        const name = ev.currentTarget.dataset.menu;
        this.state.menu = this.state.menu === name ? '' : name;
    }

    // --- From -------------------------------------------------------------

    get hasFromOption() {
        return this.state.fromOptions.some((o) => o.email === this.state.from);
    }

    /** Only the addresses of the sender list can be chosen: a plain list (Odoo 15 has no autocomplete component). */
    onChangeFrom(ev) {
        this.onFromPicked(ev.target.value);
    }

    onFromPicked(email) {
        this.state.from = email;
        this.scheduleSave();
        if (!this.state.replyToCustom) {
            this.refreshReplyTo();
        }
    }

    // --- Advanced: Reply-To -----------------------------------------------

    /** The default comes from the model of the record (the sales team address in CRM). */
    async refreshReplyTo() {
        if (this.destroyed) {
            return;
        }
        const result = await orm(this.env, 'dwo.mail.composer', 'get_reply_to', [
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
        this.state.menu = '';
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
        const subjectDirty = (this.state.subject || '').trim() !== (this.snapshot.subject || '').trim();
        const html = this.editorConnected() ? this.editor.getContent() : this.bodyHtml;
        const bodyDirty = textOf(splitBody(html).above) !== this.snapshot.aboveText;
        return subjectDirty || bodyDirty;
    }

    captureSnapshot() {
        if (this.state.loading) {
            return;
        }
        this.baselineHtml = this.editorConnected() ? this.editor.getContent() : null;
        if (this.snapshotMode === 'keep') {
            // the template text was added after the user's: still the user's content
            this.snapshotMode = 'capture';
            return;
        }
        const html = this.editorConnected() ? this.editor.getContent() : this.bodyHtml;
        this.snapshot.aboveText = textOf(splitBody(html).above);
    }

    /** A template chosen in the menu. */
    async onTemplatePicked(record) {
        if (!record || record.id === this.state.templateId) {
            return;
        }
        if (!this.isContentDirty()) {
            // nothing written yet: the template goes into the empty lines, the signature stays
            return this.applyTemplate(record, 'fill');
        }
        this.openDialog('conflict', {
            onOverwrite: () => this.applyTemplate(record, 'overwrite'),
            onAppend: () => this.applyTemplate(record, 'append'),
        });
    }

    /** Take back what the current template added; the text of the user stays. */
    clearTemplate() {
        this.state.templateId = 0;
        this.state.templateName = '';
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
        const result = await orm(this.env, 'dwo.mail.composer', 'apply_template', [
            record.id,
            this.model,
            this.resId,
        ]);
        this.state.templateId = record.id;
        this.state.templateName = record.display_name || record.name || '';
        if (result.subject && (mode !== 'append' || !this.state.subject.trim())) {
            this.state.subject = result.subject;
        }
        if (mode !== 'append') {
            this.snapshot.subject = this.state.subject;
        }
        if (result.from) {
            this.onFromPicked(result.from);
        }
        this.mergeRecipients(result);
        this.state.attachments = [...this.state.attachments, ...result.attachments];
        this.templateAdded.attachments = result.attachments.map((a) => a.id);
        if (result.body) {
            const html = this.editorConnected() ? this.editor.getContent() : this.bodyHtml;
            const { above, quote } = splitBody(html);
            let newAbove = result.body;
            if (mode === 'append') {
                newAbove = above + result.body;
            } else if (mode === 'fill') {
                // into the empty lines: what follows them (the signature) is kept
                newAbove = result.body + withoutLeadingBlankLines(above);
            }
            this.bodyHtml = newAbove + (quote ? '<br/>' + quote : '');
            this.snapshotMode = mode === 'append' ? 'keep' : 'capture';
            this.renderBody();
        }
        for (const warning of result.warnings) {
            this.notify(warning, 'warning');
        }
        this.scheduleSave();
    }

    mergeRecipients(result) {
        for (const field of ['to', 'cc', 'bcc']) {
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
        for (const field of ['to', 'cc', 'bcc']) {
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
        this.openDialog('saveTemplate', {
            onSave: async (name) => {
                this.syncBody();
                const template = await orm(this.env, 'dwo.mail.composer', 'save_as_template', [
                    this.model,
                    this.resId,
                    name,
                    {
                        subject: this.state.subject,
                        body: this.bodyHtml,
                        attachment_ids: this.state.attachments.map((a) => a.id),
                    },
                ]);
                this.notify(this.env._t('Template saved: ') + template.name, 'success');
                this.state.templateDropdownKey++;
            },
        });
    }

    // --- dialogs ----------------------------------------------------------

    openDialog(name, props) {
        this.dialogProps = props;
        this.state.dialog = name;
    }

    closeDialog() {
        this.state.dialog = '';
    }

    /** Every deletion asks first. */
    confirmDelete({ title, body, confirmLabel, confirm }) {
        this.openDialog('confirm', {
            title,
            body,
            confirmLabel: confirmLabel || this.env._t('Delete'),
            onConfirm: confirm,
        });
    }

    // --- attachments ------------------------------------------------------

    async onFilesSelected(ev) {
        const input = ev.target;
        for (const file of [...input.files]) {
            this.state.uploading++;
            try {
                const data = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(String(reader.result).split(',')[1] || '');
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                });
                const attachment = await orm(this.env, 'dwo.mail.composer', 'upload_attachment', [
                    file.name, file.type, data,
                ]);
                this.state.attachments.push(attachment);
                this.scheduleSave();
            } catch (error) {
                this.notify(this.env._t('The file could not be attached.'), 'danger');
            } finally {
                this.state.uploading--;
            }
        }
        input.value = '';
    }

    askRemoveAttachment(ev) {
        const id = Number(ev.currentTarget.dataset.id);
        const attachment = this.state.attachments.find((a) => a.id === id);
        this.confirmDelete({
            title: this.env._t('Remove the file?'),
            body: attachment.name + this.env._t(' will no longer be attached to this email.'),
            confirmLabel: this.env._t('Remove'),
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
        } catch (_error) {
            // a failed autosave does not matter here
        }
    }

    async onSend() {
        this.state.menu = '';
        this.state.sending = true;
        await this.settleSave();
        try {
            this.bodyHtml = await this.getInlinedBody();
            const result = await orm(this.env, 'dwo.mail.composer', 'send', [
                this.model,
                this.resId,
                this.payload(),
            ]);
            this.dirty = false;
            this.notify(this.env._t('Email sent'), 'success');
            this.chatter.dwoOnEmailSent(result.message_id);
        } finally {
            if (!this.destroyed) {
                this.state.sending = false;
            }
        }
    }

    deleteBody(state) {
        if (state === 'pending') {
            return this.env._t('The approval request is closed and the people who were asked are told. The email is deleted.');
        }
        if (state === 'rejected') {
            return this.env._t('The email and what the approver wrote about it are deleted.');
        }
        return this.env._t('This draft is deleted. This cannot be undone.');
    }

    /** The Delete draft button: asks, then deletes the email in the form. */
    askDeleteCurrent() {
        this.confirmDelete({
            title: this.env._t('Delete this email?'),
            body: this.deleteBody(this.state.emailState),
            confirm: () => this.onDeleteDraft(),
        });
    }

    /** Remove the draft and go back to the initial content of the form. */
    async onDeleteDraft() {
        this.dirty = false;
        await this.settleSave();
        const defaults = await orm(this.env, 'dwo.mail.composer', 'delete_email', [
            this.model,
            this.resId,
            this.state.emailId,
        ]);
        this.applyData(defaults);
        this.renderBody();
        this.state.newerEmail = false;
        this.chatter.dwoOnEmailChange(false);
        this.refreshList();
    }

    async onApplyDefaults() {
        const defaults = await orm(this.env, 'dwo.mail.composer', 'get_defaults', [
            this.model,
            this.resId,
            false,
            'reply',
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
        const emails = await orm(this.env, 'dwo.mail.composer', 'list_emails', [this.model, this.resId]);
        if (!this.destroyed) {
            this.state.emails = emails;
        }
    }

    /** Open an email of the list in the form, after saving the one being written. */
    async onOpenEmail(ev) {
        const id = Number(ev.currentTarget.dataset.id);
        if (id === this.state.emailId) {
            return;
        }
        await this.saveNow();
        const data = await orm(this.env, 'dwo.mail.composer', 'load_email', [id]);
        this.applyData(data);
        this.renderBody();
        this.state.newerEmail = false;
        this.chatter.dwoOnEmailChange(id);
        this.refreshReplyTo();
        this.refreshList();
    }

    /** Delete an email of the list (always after a question): the one in the form goes back to the defaults. */
    onDeleteListed(ev) {
        ev.stopPropagation();
        const id = Number(ev.currentTarget.dataset.id);
        const email = this.state.emails.find((e) => e.id === id);
        this.confirmDelete({
            title: this.env._t('Delete this email?'),
            body: this.deleteBody(email.state),
            confirm: async () => {
                if (email.id === this.state.emailId) {
                    return this.onDeleteDraft();
                }
                await orm(this.env, 'dwo.mail.composer', 'delete_email', [this.model, this.resId, email.id]);
                this.refreshList();
            },
        });
    }

    formatListDate(serialized) {
        return formatListDate(serialized);
    }

    // --- the message on the whole screen ------------------------------------

    toggleExpanded() {
        this.state.expanded = !this.state.expanded;
    }

    onKeydown(ev) {
        // a dialog opened from the editor (a link, an image) has its own Esc; the hidden dialogs the editor keeps in the page do not count
        const openDialog = [...document.querySelectorAll('.modal')].some((modal) => modal.offsetParent !== null);
        if (ev.key === 'Escape' && this.state.expanded && !openDialog) {
            this.state.expanded = false;
        }
    }

    async onNewEmail() {
        await this.saveNow();
        const defaults = await orm(this.env, 'dwo.mail.composer', 'get_defaults', [
            this.model,
            this.resId,
            false,
            'reply',
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
        this.state.menu = '';
        const { approver_ids, allow_self_approval, user_id } = this.state.policy;
        this.openDialog('approval', {
            // empty list: everybody can approve
            allowedIds: approver_ids,
            excludedId: allow_self_approval ? false : user_id,
            onConfirm: async ({ approverIds, comment }) => {
                this.state.sending = true;
                try {
                    await this.settleSave();
                    this.syncBody();
                    this.bodyHtml = await this.getInlinedBody();
                    const result = await orm(this.env, 'dwo.mail.composer', 'request_approval', [
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
                    const loaded = await orm(this.env, 'dwo.mail.composer', 'load_email', [result.id]);
                    this.state.approvers = loaded.approvers;
                    this.state.requestComment = loaded.request_comment;
                    this.state.decisionComment = '';
                    this.state.editedAfterRequest = false;
                    this.notify(this.env._t('The approval was requested'), 'success');
                } finally {
                    this.state.sending = false;
                }
            },
        });
    }

    get stateLabel() {
        return {
            draft: this.env._t('Draft'),
            pending: this.env._t('Waiting for approval'),
            rejected: this.env._t('Rejected'),
            sent: this.env._t('Approved and sent'),
        }[this.state.emailState];
    }

    get approverNames() {
        return this.state.approvers.map((u) => u.name).join(', ');
    }

    /** An address typed but not yet turned into a badge is committed first, so the draft keeps it. */
    async commitTypedAddresses() {
        const typing = [...document.querySelectorAll('.o-dwo-emailComposer .o-dwo-addressText')].filter(
            (input) => input.value.trim()
        );
        if (typing.length) {
            // blur() sends nothing when the window has no focus (a headless browser): the event is sent too
            typing.forEach((input) => {
                input.blur();
                input.dispatchEvent(new FocusEvent('blur'));
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
            this.chatter.dwoOnEmailClose();
        }
    }
}

Object.assign(DwoEmailComposer, {
    props: { chatterLocalId: String },
    template: 'dwo_mail_compose.EmailComposer',
    components: {
        ComponentAdapter,
        DwoAddressInput,
        DwoApprovalDialog,
        DwoConfirmDialog,
        DwoSaveTemplateDialog,
        DwoTemplateConflictDialog,
        DwoTemplateDropdown,
    },
});

registerMessagingComponent(DwoEmailComposer);
