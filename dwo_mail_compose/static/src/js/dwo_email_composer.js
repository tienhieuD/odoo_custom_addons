odoo.define('dwo_mail_compose.EmailComposer', function (require) {
'use strict';

/**
 * Inline form of the Send email button. All the rules (defaults, quote, subject, reply-all, sending) come
 * from the server model dwo.mail.composer; this widget displays, edits and autosaves the draft.
 *
 * Odoo 13 and 12: a jQuery widget. The body is the legacy HTML editor (summernote, web_editor), the
 * recipients are badges (dwo_mail_compose.AddressInput).
 */

var core = require('web.core');
var fieldUtils = require('web.field_utils');
var session = require('web.session');
var Widget = require('web.Widget');
var Wysiwyg = require('web_editor.wysiwyg.root');
var convertInline = require('web_editor.convertInline');
var AddressInput = require('dwo_mail_compose.AddressInput').AddressInput;
var dialogs = require('dwo_mail_compose.dialogs');

var QWeb = core.qweb;
var _t = core._t;

var SAVE_DELAY = 1500;
var TEMPLATE_LIMIT = 80;

/** Text of an HTML string, without loading anything (a parsed document is inert). */
function textOf(html) {
    var doc = new DOMParser().parseFromString(html || '', 'text/html');
    return (doc.body.textContent || '').replace(/\s+/g, ' ').trim();
}

/**
 * Cut a body in what the user writes (above) and the quoted email (from the quote block on).
 */
function splitBody(html) {
    var doc = new DOMParser().parseFromString(html || '', 'text/html');
    var root = doc.body;
    var quote = root.querySelector('#divRplyFwdMsg');
    if (!quote) {
        return {above: root.innerHTML, quote: ''};
    }
    var top = quote;
    while (top.parentElement && top.parentElement !== root) {
        top = top.parentElement;
    }
    var nodes = Array.prototype.slice.call(root.childNodes);
    var index = nodes.indexOf(top);
    var serialize = function (list) {
        var holder = doc.createElement('div');
        list.forEach(function (node) { holder.appendChild(node.cloneNode(true)); });
        return holder.innerHTML;
    };
    return {above: serialize(nodes.slice(0, index)), quote: serialize(nodes.slice(index))};
}

/**
 * The body without the empty lines at its start: the lines a user finds to write in when an email is
 * started. What remains is the signature (and nothing else when there is none).
 */
function withoutLeadingBlankLines(html) {
    var doc = new DOMParser().parseFromString(html || '', 'text/html');
    var root = doc.body;
    var isBlank = function (node) {
        if (node.nodeType === Node.TEXT_NODE) {
            return !node.textContent.trim();
        }
        return ['P', 'DIV'].indexOf(node.tagName) > -1 && !node.textContent.trim() &&
            !Array.prototype.some.call(node.children, function (child) { return child.tagName !== 'BR'; });
    };
    while (root.firstChild && isBlank(root.firstChild)) {
        root.removeChild(root.firstChild);
    }
    return root.innerHTML;
}

var EmailComposer = Widget.extend({
    template: 'dwo_mail_compose.EmailComposer',
    custom_events: {
        wysiwyg_change: '_onEditorChange',
    },
    events: {
        'click .o-dwo-closeBtn': '_onClose',
        'click .o-dwo-ccBtn': '_onShowCc',
        'click .o-dwo-bccBtn': '_onShowBcc',
        'change #dwo_from': '_onFromChange',
        'input #dwo_subject': '_onSubjectInput',
        'input #dwo_replyto': '_onReplyToInput',
        'change #dwo_replyto': '_onReplyToChange',
        'click .o-dwo-replyToReset': '_onReplyToReset',
        'click .o-dwo-replyToHide': '_onReplyToHide',
        'click .o-dwo-addReplyTo': '_onAddReplyTo',
        'click .o-dwo-expandBtn': '_onToggleExpanded',
        'click .o-dwo-collapseBtn': '_onToggleExpanded',
        'change .o-dwo-fileInput': '_onFilesSelected',
        'click .o-dwo-attachmentRemove': '_onClickAttachmentRemove',
        'click .o-dwo-templateItem': '_onTemplateItem',
        'click .o-dwo-saveTemplate': '_onSaveTemplate',
        'click .o-dwo-manageTemplates': '_onManageTemplates',
        'click .o-dwo-templateRemove': '_onTemplateRemove',
        'click .o-dwo-sendNow': '_onSend',
        'click .o-dwo-requestApproval': '_onRequestApproval',
        'click .o-dwo-deleteDraft': '_onAskDeleteCurrent',
        'click .o-dwo-applyDefaults': '_onApplyDefaults',
        'click .o-dwo-dismissBanner': '_onDismissBanner',
        'click .o-dwo-startNew': '_onNewEmail',
        'click .o-dwo-newEmail': '_onNewEmail',
        'click .o-dwo-emailRow': '_onOpenEmail',
        'click .o-dwo-rowDelete': '_onDeleteListed',
    },

    /**
     * @param {Widget} parent
     * @param {Object} options
     * @param {string} options.model
     * @param {number} options.resId
     * @param {string|boolean} [options.mode] reply, reply_sender, forward or false
     * @param {number|boolean} [options.refMessageId]
     * @param {number|boolean} [options.preferredEmailId] the email opened last on this screen
     */
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.model = options.model;
        this.resId = options.resId;
        this.mode = options.mode || false;
        this.refMessageId = options.refMessageId || false;
        this.preferredEmailId = options.preferredEmailId || false;
        this.st = {
            loading: true,
            expanded: false,
            from: '',
            to: [],
            cc: [],
            bcc: [],
            subject: '',
            templateId: 0,
            templateName: '',
            replyTo: '',
            replyToDefault: '',
            replyToCustom: false,
            replyToManaged: true,
            showReplyTo: false,
            attachments: [],
            fromOptions: [],
            mode: 'new',
            refMessageId: false,
            savedAt: '',
            hasDraft: false,
            emailId: false,
            emailState: 'draft',
            approvers: [],
            requestComment: '',
            decisionComment: '',
            decidedBy: '',
            editedAfterRequest: false,
            emails: [],
            policy: {
                require_approval: false, can_send_now: true, can_request_approval: false,
                allow_self_approval: true, approver_ids: [], user_id: 0,
            },
            newerEmail: false,
            sending: false,
            uploading: 0,
            templates: [],
        };
        this.bodyHtml = '';
        // what the editor holds right after it was loaded, i.e. the HTML tidied by the editor itself
        this.baselineHtml = null;
        // what the form held when it was loaded or last filled by a template
        this.snapshot = {subject: '', aboveText: ''};
        this.snapshotMode = 'capture';
        // what the current template added, so choosing another template can take it back
        this.templateAdded = {to: [], cc: [], bcc: [], attachments: []};
        this.wysiwyg = null;
        this.editorToken = 0;
        this.dirty = false;
        this.closing = false;
        this.locked = false;
        this.saveTimer = null;
        this.savePromise = null;
        this._onKeydownBound = this._onKeydown.bind(this);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        this.$title = this.$('.o-dwo-title');
        this.addresses = {};
        this._addressDefs = {};
        var defs = [this._super.apply(this, arguments), this._ensureAddress('to')];
        $(window).on('keydown', this._onKeydownBound);
        return Promise.all(defs).then(function () {
            self._renderTitle();
            return self._load();
        });
    },
    /**
     * Last save of the pending change; after this the widget must not touch the page.
     *
     * @override
     */
    destroy: function () {
        this.closing = true;
        clearTimeout(this.saveTimer);
        $(window).off('keydown', this._onKeydownBound);
        $('body').removeClass('o-dwo-composeExpanded');
        if (this.dirty && !this.locked && this.st.emailId !== undefined && !this.isDestroyed()) {
            this._syncBody();
            this._save(this.bodyHtml);
        }
        this.editorToken++;
        if (this.wysiwyg) {
            try {
                this.wysiwyg.destroy();
            } catch (e) {
                // the editor is going away with its host
            }
            this.wysiwyg = null;
        }
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Server
    //--------------------------------------------------------------------------

    /**
     * A call to the composer model. It goes through the session, not through the widget: the last save can
     * end after the form is gone.
     *
     * @private
     * @param {string} method
     * @param {Array} args
     * @returns {Promise}
     */
    _call: function (method, args) {
        return Promise.resolve(session.rpc('/web/dataset/call_kw/dwo.mail.composer/' + method, {
            model: 'dwo.mail.composer',
            method: method,
            args: args,
            kwargs: {context: session.user_context},
        }));
    },
    /**
     * @private
     * @param {string} model
     * @param {string} method
     * @param {Array} args
     * @param {Object} [kwargs]
     * @returns {Promise}
     */
    _callModel: function (model, method, args, kwargs) {
        return Promise.resolve(session.rpc('/web/dataset/call_kw/' + model + '/' + method, {
            model: model,
            method: method,
            args: args,
            kwargs: _.extend({context: session.user_context}, kwargs || {}),
        }));
    },
    /**
     * @private
     * @returns {Promise}
     */
    _load: async function () {
        var state = await this._call('get_state', [
            this.model, this.resId, this.mode ? false : this.preferredEmailId || false,
        ]);
        if (this.isDestroyed()) {
            return;
        }
        this.st.fromOptions = state.from_options;
        this.st.emails = state.emails;
        this.st.policy = state.policy;
        var data;
        if (this.mode) {
            data = await this._call('get_defaults', [this.model, this.resId, this.refMessageId || false, this.mode]);
        } else if (state.current) {
            data = state.current;
            this.st.newerEmail = state.newer_email;
        } else {
            data = state.defaults;
        }
        if (this.isDestroyed()) {
            return;
        }
        this._applyData(data);
        this.st.loading = false;
        this.$('.o-dwo-loading').addClass('d-none');
        this.$('.o-dwo-content').removeClass('d-none');
        this._renderFrom();
        this._renderAll();
        this._fetchTemplates();
        await this._renderBody();
        this._refreshReplyTo();
        if (this.mode) {
            // a Reply or Forward is a new email: it is stored now, not at the first edit
            this.dirty = true;
            this._saveNow();
        }
    },

    //--------------------------------------------------------------------------
    // State and rendering
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Object} data
     */
    _applyData: function (data) {
        var st = this.st;
        st.from = data.from || '';
        st.to = data.to || [];
        st.cc = data.cc || [];
        st.bcc = data.bcc || [];
        st.subject = data.subject || '';
        st.templateId = data.template_id || 0;
        st.templateName = data.template_name || '';
        st.replyTo = data.reply_to || '';
        st.replyToCustom = Boolean(data.reply_to_custom);
        st.replyToDefault = data.reply_to_custom ? '' : data.reply_to || '';
        st.replyToManaged = data.reply_to_managed === undefined ? true : data.reply_to_managed;
        st.showReplyTo = st.replyToCustom;
        this.snapshot.subject = data.subject || '';
        this.snapshotMode = 'capture';
        st.attachments = data.attachments || [];
        st.mode = data.mode || 'new';
        st.refMessageId = data.ref_message_id || false;
        st.emailId = data.id || false;
        st.emailState = data.state || 'draft';
        this.locked = false;
        st.approvers = data.approvers || [];
        st.requestComment = data.request_comment || '';
        st.decisionComment = data.decision_comment || '';
        st.decidedBy = data.decided_by || '';
        st.editedAfterRequest = Boolean(data.edited_after_request);
        st.hasDraft = Boolean(data.id);
        st.savedAt = data.id ? this._timeLabel(data.saved_at) : '';
        this.bodyHtml = data.body || '';
        this.templateAdded = {to: [], cc: [], bcc: [], attachments: []};
        if (!this.st.loading) {
            this._renderAll();
        }
    },
    /**
     * Everything the state shows, except the editor and the From options.
     *
     * @private
     */
    _renderAll: function () {
        var st = this.st;
        this._syncAddress('to');
        this._syncAddress('cc');
        this._syncAddress('bcc');
        this.$('.o-dwo-ccbcc').html(QWeb.render('dwo_mail_compose.CcBccButtons', {
            showCc: !this.addresses.cc, showBcc: !this.addresses.bcc,
        }));
        this.$('#dwo_subject').val(st.subject);
        this._renderTitle();
        this._renderNotes();
        this._renderReplyTo();
        this._renderAttachments();
        this._renderTemplateBadge();
        this._renderSend();
        this._renderList();
        this._renderFromSelection();
    },
    /**
     * Cc and Bcc exist in the page only when they have a value or after their button was used.
     *
     * @private
     * @param {string} field to, cc or bcc
     */
    _syncAddress: function (field) {
        var wanted = field === 'to' || this.st[field].length || this['_' + field + 'Shown'];
        var widget = this.addresses[field];
        if (wanted && !widget) {
            this._ensureAddress(field);
            return;
        }
        if (!wanted && widget) {
            widget.destroy();
            delete this.addresses[field];
            this.$('.o-dwo-' + field + 'Row').addClass('d-none');
            return;
        }
        if (widget) {
            widget.setValue(this.st[field]);
        }
    },
    /**
     * @private
     * @param {string} field to, cc or bcc
     * @returns {Promise}
     */
    _ensureAddress: function (field) {
        var self = this;
        if (this.addresses[field]) {
            return Promise.resolve();
        }
        var spec = {
            to: ['dwo_to', 'Type a name or an email, then press Enter or comma'],
            cc: ['dwo_cc', 'People to keep informed (visible to everyone)'],
            bcc: ['dwo_bcc', 'Hidden recipients (nobody else sees them)'],
        }[field];
        var widget = new AddressInput(this, {
            id: spec[0],
            value: this.st[field],
            placeholder: _t(spec[1]),
            onChange: function (value) { self._onFieldChange(field, value); },
        });
        this.addresses[field] = widget;
        this.$('.o-dwo-' + field + 'Row').removeClass('d-none');
        widget._started = widget.appendTo(this.$('[data-field="' + field + '"]'));
        return widget._started;
    },
    /**
     * @private
     */
    _renderTitle: function () {
        var st = this.st;
        var title = (st.subject || '').trim() || _t('Compose email');
        this.$title.text(title).attr('title', title);
        this.$('.o-dwo-expandedTitle').text((st.subject || '').trim() || _t('New email'));
        var $badge = this.$('.o-dwo-stateBadge');
        if (st.emailId) {
            $badge.removeClass('d-none badge-secondary badge-info badge-danger badge-success')
                .addClass({
                    draft: 'badge-secondary', pending: 'badge-info', rejected: 'badge-danger', sent: 'badge-success',
                }[st.emailState] || 'badge-secondary')
                .text(this._stateLabel());
        } else {
            $badge.addClass('d-none');
        }
    },
    /**
     * @private
     * @returns {string}
     */
    _stateLabel: function () {
        return {
            draft: _t('Draft'),
            pending: _t('Waiting for approval'),
            rejected: _t('Rejected'),
            sent: _t('Approved and sent'),
        }[this.st.emailState];
    },
    /**
     * @private
     */
    _renderNotes: function () {
        this.approverNames = _.pluck(this.st.approvers, 'name').join(', ');
        this.$('.o-dwo-notes').html(QWeb.render('dwo_mail_compose.Notes', {st: this.st, approverNames: this.approverNames}));
    },
    /**
     * The options of the From list (they come once, with the state).
     *
     * @private
     */
    _renderFrom: function () {
        this.$('#dwo_from').html(QWeb.render('dwo_mail_compose.FromOptions', {
            options: this.st.fromOptions, current: this.st.from,
        }));
        this._renderFromSelection();
    },
    /**
     * @private
     */
    _renderFromSelection: function () {
        var $from = this.$('#dwo_from');
        var known = _.findWhere(this.st.fromOptions, {email: this.st.from});
        $from.val(known ? this.st.from : (this.st.fromOptions[0] && this.st.fromOptions[0].email) || '');
    },
    /**
     * @private
     */
    _renderReplyTo: function (keepInput) {
        var st = this.st;
        // the row exists in the page only when it is shown
        var $slot = this.$('.o-dwo-replyToSlot');
        if (st.showReplyTo && !$slot.children().length) {
            $slot.html(QWeb.render('dwo_mail_compose.ReplyToRow'));
        } else if (!st.showReplyTo && $slot.children().length) {
            $slot.empty();
        }
        if (st.showReplyTo) {
            if (!keepInput) {
                this.$('#dwo_replyto').val(st.replyTo);
            }
            this.$('#dwo_replyto').toggleClass('text-muted', !st.replyToCustom);
            this.$('.o-dwo-replyToActions').html(QWeb.render('dwo_mail_compose.ReplyToActions', {st: st}));
        }
        this.$('.o-dwo-replyToDefault').text(st.replyToDefault || '...');
        this.$('.o-dwo-replyToCheck').toggleClass('d-none', !st.showReplyTo);
    },
    /**
     * @private
     */
    _renderAttachments: function () {
        this.$('.o-dwo-attachments').html(QWeb.render('dwo_mail_compose.Attachments', {attachments: this.st.attachments}));
        this.$('.o-dwo-attachIcon').attr('class', 'o-dwo-attachIcon fa ' +
            (this.st.uploading ? 'fa-circle-o-notch fa-spin' : 'fa-paperclip'));
    },
    /**
     * @private
     */
    _renderTemplateBadge: function () {
        var $slot = this.$('.o-dwo-templateBadgeSlot');
        if (this.st.templateId) {
            $slot.html(QWeb.render('dwo_mail_compose.TemplateBadge', {name: this.st.templateName}));
        } else {
            $slot.empty();
        }
    },
    /**
     * @private
     */
    _renderSend: function () {
        var st = this.st;
        var busy = st.sending || st.uploading || st.emailState === 'sent';
        this.$('.o-dwo-directNote').text(st.policy.can_send_now ?
            _t('This email is sent directly to the people in To, Cc and Bcc. The followers of the record are not notified.') :
            _t('An approver must approve this email before it is sent to the people in To, Cc and Bcc. The followers of the record are not notified.'));
        this.$('.o-dwo-sendArea').html(QWeb.render('dwo_mail_compose.SendArea', {st: st, busy: busy}));
        this._renderSaved();
    },
    /**
     * @private
     */
    _renderSaved: function () {
        var st = this.st;
        this.$('.o-dwo-savedAt').text(st.hasDraft ?
            (st.emailState === 'draft' ? _t('Draft saved') : _t('Saved')) + ' ' + st.savedAt : _t('No draft yet'));
    },
    /**
     * @private
     */
    _renderList: function () {
        var $slot = this.$('.o-dwo-emailListSlot');
        if (!this.st.loading && this.st.emails.length) {
            $slot.html(QWeb.render('dwo_mail_compose.EmailList', {st: this.st, formatDate: this._formatListDate}));
        } else {
            $slot.empty();
        }
    },
    /**
     * @private
     * @param {string} serialized
     * @returns {string}
     */
    _formatListDate: function (serialized) {
        return serialized ? fieldUtils.format.datetime(moment.utc(serialized)) : '';
    },
    /**
     * @private
     * @param {string} [datetimeString]
     * @returns {string}
     */
    _timeLabel: function (datetimeString) {
        var date = datetimeString ? new Date(datetimeString.replace(' ', 'T') + 'Z') : new Date();
        return date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
    },
    /**
     * @private
     */
    _fetchTemplates: async function () {
        var fields = ['display_name'];
        var templates = await this._callModel('mail.template', 'search_read', [
            [['model', '=', this.model], ['user_id', '=', session.uid]], fields], {limit: TEMPLATE_LIMIT});
        if (templates.length < TEMPLATE_LIMIT) {
            templates = templates.concat(await this._callModel('mail.template', 'search_read', [
                [['model', '=', this.model], ['user_id', '=', false]], fields],
                {limit: TEMPLATE_LIMIT - templates.length}));
        }
        if (this.isDestroyed()) {
            return;
        }
        this.st.templates = templates;
        this.$('.o-dwo-templateMenu').html(QWeb.render('dwo_mail_compose.TemplateMenu', {templates: templates}));
    },

    //--------------------------------------------------------------------------
    // Editor
    //--------------------------------------------------------------------------

    /**
     * The editor is created again for each content (a new template, a new email, an email chosen in the list).
     *
     * @private
     * @returns {Promise}
     */
    _renderBody: async function () {
        var self = this;
        var token = ++this.editorToken;
        if (this.wysiwyg) {
            try {
                this.wysiwyg.destroy();
            } catch (e) {
                // the editor is replaced anyway
            }
            this.wysiwyg = null;
        }
        var $host = this.$('.o-dwo-editorHost').empty();
        var $textarea = $('<textarea/>').val(this.bodyHtml).appendTo($host);
        var wysiwyg = new Wysiwyg(this, {
            recordInfo: {context: session.user_context, res_model: this.model, res_id: this.resId},
            noAttachment: false,
            tabsize: 0,
            height: 180,
            generateOptions: function (options) {
                options.noVideos = true;
                options.prettifyHtml = false;
                return options;
            },
        });
        await wysiwyg.attachTo($textarea);
        if (token !== this.editorToken || this.isDestroyed()) {
            wysiwyg.destroy();
            return;
        }
        this.wysiwyg = wysiwyg;
        this.$editable = wysiwyg.$editor || wysiwyg.getEditable();
        this.$editable.addClass('o-dwo-editor');
        // the few things the form needs: the editor starts after the form is shown, what it holds now is the baseline
        this._captureSnapshot();
        self.trigger('editor_ready');
    },
    /**
     * @private
     * @returns {string}
     */
    _editorContent: function () {
        return this.wysiwyg && this.$editable && this.$editable.closest('body').length ?
            this.wysiwyg.getValue() : this.bodyHtml;
    },
    /**
     * @private
     */
    _onEditorChange: function (ev) {
        if (ev) {
            ev.stopPropagation();
        }
        // the editor reports a last change while it is being closed: it must not replace the draft
        if (this.closing || this.isDestroyed() || !this.wysiwyg) {
            return;
        }
        this.bodyHtml = this.wysiwyg.getValue();
        this._scheduleSave();
    },
    /**
     * Read the content straight from the editor. Its change event comes one step late, so a text typed just
     * before Close or Send would otherwise be missing from the draft.
     *
     * @private
     */
    _syncBody: function () {
        if (this.isDestroyed() || !this.wysiwyg || !this.$editable || !this.$editable.closest('body').length) {
            return;
        }
        var html = this.wysiwyg.getValue();
        if (html !== this.bodyHtml) {
            this.bodyHtml = html;
            // The editor tidies the HTML it is given: only a difference with what the editor held when it
            // loaded is an edit, otherwise opening the form and closing it would store a draft nobody wrote.
            if (this.baselineHtml === null || html !== this.baselineHtml) {
                this.dirty = true;
            }
        }
    },
    /**
     * The content with its CSS turned into inline styles, as mail clients ignore stylesheets. It is what is
     * stored on every save, so a send from the browser and a send made later by the server use the same HTML.
     *
     * @private
     * @returns {string}
     */
    _getInlinedBody: function () {
        if (!this.wysiwyg || !this.$editable || !this.$editable.closest('body').length) {
            return this.bodyHtml;
        }
        var html = this.wysiwyg.getValue({'style-inline': true});
        var $el = $('<div/>').css({position: 'absolute', left: '-9999px', top: 0}).html(html);
        $el.appendTo(this.$('.o-dwo-editorBox'));
        try {
            convertInline.attachmentThumbnailToLinkImg($el);
            convertInline.fontToImg($el);
            convertInline.classToStyle($el);
            html = $el.html();
        } catch (e) {
            // an email without inline styles is better than no email
            html = this.wysiwyg.getValue();
        }
        $el.remove();
        return html;
    },

    //--------------------------------------------------------------------------
    // Autosave
    //--------------------------------------------------------------------------

    /**
     * @private
     * @returns {Object}
     */
    _payload: function (body) {
        var st = this.st;
        return {
            from: st.from,
            to: st.to,
            cc: st.cc,
            bcc: st.bcc,
            subject: st.subject,
            reply_to: st.replyTo,
            reply_to_custom: st.replyToCustom,
            body: body === undefined ? this.bodyHtml : body,
            template_id: st.templateId || false,
            attachment_ids: _.pluck(st.attachments, 'id'),
            mode: st.mode,
            ref_message_id: st.refMessageId,
            email_id: st.emailId,
        };
    },
    /**
     * @private
     */
    _scheduleSave: function () {
        var self = this;
        if (this.isDestroyed() || this.locked) {
            return;
        }
        this.dirty = true;
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(function () { self._saveNow(); }, SAVE_DELAY);
    },
    /**
     * Saves are chained: a save never starts before the previous one is stored.
     *
     * @private
     * @returns {Promise}
     */
    _saveNow: function () {
        var self = this;
        clearTimeout(this.saveTimer);
        var previous = this.savePromise || Promise.resolve();
        this.savePromise = previous.catch(function () {}).then(function () { return self._doSave(); });
        return this.savePromise;
    },
    /**
     * @private
     */
    _doSave: async function () {
        this._syncBody();
        if (this.st.sending || !this.dirty) {
            return;
        }
        this.dirty = false;
        var body = this._getInlinedBody();
        await this._save(body);
    },
    /**
     * Store the email. Each save carries the id the first one got: saves are chained, so there is never a
     * second record.
     *
     * @private
     * @param {string} body
     */
    _save: async function (body) {
        var st = this.st;
        var saved = await this._call('save_email', [this.model, this.resId, st.emailId, this._payload(body)]);
        if (this.isDestroyed()) {
            return;
        }
        var stateChanged = saved.state !== st.emailState;
        if (saved.id !== st.emailId) {
            this.trigger_up('dwo_email_change', {emailId: saved.id});
        }
        st.emailId = saved.id;
        st.emailState = saved.state;
        st.hasDraft = true;
        st.savedAt = this._timeLabel();
        this._renderTitle();
        this._renderSend();
        if (saved.state === 'sent') {
            // an approver approved it while it was open: it left, the server did not write the edit
            this.locked = true;
            this.dirty = false;
            clearTimeout(this.saveTimer);
            this.do_warn(_t('This email was approved and sent. Your last changes were not saved.'));
        }
        if (stateChanged) {
            // approved, rejected or reassigned meanwhile: show who decided and what they wrote
            await this._refreshMeta();
        }
        this._refreshList();
    },
    /**
     * The approval data of the stored email, without touching what the user is writing.
     *
     * @private
     */
    _refreshMeta: async function () {
        var data = await this._call('load_email', [this.st.emailId]);
        if (this.isDestroyed()) {
            return;
        }
        var st = this.st;
        st.emailState = data.state;
        st.approvers = data.approvers;
        st.requestComment = data.request_comment;
        st.decisionComment = data.decision_comment;
        st.decidedBy = data.decided_by;
        st.editedAfterRequest = data.edited_after_request;
        this._renderTitle();
        this._renderNotes();
        this._renderSend();
    },
    /**
     * A save already on the wire could land after the draft is deleted: wait for it.
     *
     * @private
     */
    _settleSave: async function () {
        clearTimeout(this.saveTimer);
        try {
            await this.savePromise;
        } catch (e) {
            // a failed autosave does not matter here
        }
    },

    //--------------------------------------------------------------------------
    // Editing
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onFieldChange: function (field, value) {
        this.st[field] = value;
        if (field === 'cc' && !value.length) {
            // the row stays visible once it was opened
        }
        this._scheduleSave();
    },
    /**
     * @private
     */
    _onShowCc: function () {
        this._ccShown = true;
        this._renderAll();
        this._focusAddress('cc');
    },
    /**
     * @private
     */
    _onShowBcc: function () {
        this._bccShown = true;
        this._renderAll();
        this._focusAddress('bcc');
    },
    /**
     * @private
     * @param {string} field
     */
    _focusAddress: function (field) {
        var widget = this.addresses[field];
        if (widget && widget._started) {
            widget._started.then(function () { widget.$input.focus(); });
        }
    },
    /**
     * @private
     */
    _onSubjectInput: function (ev) {
        this.st.subject = ev.currentTarget.value;
        this._renderTitle();
        this._scheduleSave();
    },
    /**
     * @private
     */
    _onFromChange: function (ev) {
        this._pickFrom(ev.currentTarget.value);
    },
    /**
     * @private
     * @param {string} email
     */
    _pickFrom: function (email) {
        this.st.from = email;
        this._renderFromSelection();
        this._scheduleSave();
        if (!this.st.replyToCustom) {
            this._refreshReplyTo();
        }
    },

    //--------------------------------------------------------------------------
    // Advanced: Reply-To
    //--------------------------------------------------------------------------

    /**
     * The default comes from the model of the record (the sales team address in CRM).
     *
     * @private
     */
    _refreshReplyTo: async function () {
        if (this.isDestroyed()) {
            return;
        }
        var st = this.st;
        var result = await this._call('get_reply_to', [
            this.model, this.resId, st.from || false, st.replyToCustom ? st.replyTo : false,
        ]);
        if (this.isDestroyed()) {
            return;
        }
        st.replyToDefault = result.default.email;
        st.replyToManaged = result.managed;
        if (!st.replyToCustom) {
            st.replyTo = result.default.email;
        }
        this._renderReplyTo();
    },
    /**
     * @private
     */
    _onAddReplyTo: function (ev) {
        ev.preventDefault();
        this.st.showReplyTo = true;
        this._renderReplyTo();
    },
    /**
     * The row only goes away while it holds the default: a custom value stays visible.
     *
     * @private
     */
    _onReplyToHide: function () {
        if (!this.st.replyToCustom) {
            this.st.showReplyTo = false;
            this._renderReplyTo();
        }
    },
    /**
     * @private
     */
    _onReplyToInput: function (ev) {
        var st = this.st;
        st.replyTo = ev.currentTarget.value;
        st.replyToCustom = st.replyTo.trim().toLowerCase() !== st.replyToDefault;
        this._renderReplyTo(true);
        this._scheduleSave();
    },
    /**
     * @private
     */
    _onReplyToChange: function () {
        this._refreshReplyTo();
    },
    /**
     * @private
     */
    _onReplyToReset: function () {
        this.st.replyToCustom = false;
        this._refreshReplyTo();
        this._scheduleSave();
    },

    //--------------------------------------------------------------------------
    // Templates
    //--------------------------------------------------------------------------

    /**
     * What the user wrote, compared to what the form held when it was filled.
     *
     * @private
     * @returns {boolean}
     */
    _isContentDirty: function () {
        var subjectDirty = (this.st.subject || '').trim() !== (this.snapshot.subject || '').trim();
        var bodyDirty = textOf(splitBody(this._editorContent()).above) !== this.snapshot.aboveText;
        return subjectDirty || bodyDirty;
    },
    /**
     * @private
     */
    _captureSnapshot: function () {
        if (this.st.loading) {
            return;
        }
        this.baselineHtml = this.wysiwyg ? this._editorContent() : null;
        if (this.snapshotMode === 'keep') {
            // the template text was added after the user's: still the user's content
            this.snapshotMode = 'capture';
            return;
        }
        this.snapshot.aboveText = textOf(splitBody(this._editorContent()).above);
    },
    /**
     * @private
     */
    _onTemplateItem: function (ev) {
        ev.preventDefault();
        var id = $(ev.currentTarget).data('id');
        var record = _.findWhere(this.st.templates, {id: id});
        this._onTemplatePicked(record);
    },
    /**
     * A template chosen in the menu.
     *
     * @private
     */
    _onTemplatePicked: function (record) {
        var self = this;
        if (!record || record.id === this.st.templateId) {
            return;
        }
        if (!this._isContentDirty()) {
            // nothing written yet: the template goes into the empty lines, the signature stays
            return this._applyTemplate(record, 'fill');
        }
        dialogs.openTemplateConflictDialog(this, {
            onOverwrite: function () { self._applyTemplate(record, 'overwrite'); },
            onAppend: function () { self._applyTemplate(record, 'append'); },
        });
    },
    /**
     * Take back what the current template added; the text of the user stays.
     *
     * @private
     */
    _onTemplateRemove: function () {
        this.st.templateId = 0;
        this.st.templateName = '';
        this._removeTemplateAdditions();
        this._renderAll();
        this._scheduleSave();
    },
    /**
     * Apply a template: subject, body (above the quote), From, recipients and attachments, all computed on
     * this record by the server. Recipients of the template are added to the ones already there (a reply-all
     * keeps its people), and choosing another template first takes back what the previous one added.
     * "append" keeps the user's subject and message and puts the template text after it. "fill" is for a
     * form nothing was written in: the text takes the place of the empty lines and the signature stays under
     * it. "overwrite" replaces everything above the quote.
     *
     * @private
     */
    _applyTemplate: async function (record, mode) {
        var st = this.st;
        this._removeTemplateAdditions();
        var result = await this._call('apply_template', [record.id, this.model, this.resId]);
        if (this.isDestroyed()) {
            return;
        }
        st.templateId = record.id;
        st.templateName = record.display_name || record.name || '';
        if (result.subject && (mode !== 'append' || !st.subject.trim())) {
            st.subject = result.subject;
        }
        if (mode !== 'append') {
            this.snapshot.subject = st.subject;
        }
        if (result.from) {
            this._pickFrom(result.from);
        }
        this._mergeRecipients(result);
        st.attachments = st.attachments.concat(result.attachments);
        this.templateAdded.attachments = _.pluck(result.attachments, 'id');
        var rebuild = false;
        if (result.body) {
            var parts = splitBody(this._editorContent());
            var newAbove = result.body;
            if (mode === 'append') {
                newAbove = parts.above + result.body;
            } else if (mode === 'fill') {
                // into the empty lines: what follows them (the signature) is kept
                newAbove = result.body + withoutLeadingBlankLines(parts.above);
            }
            this.bodyHtml = newAbove + (parts.quote ? '<br/>' + parts.quote : '');
            this.snapshotMode = mode === 'append' ? 'keep' : 'capture';
            rebuild = true;
        }
        this._renderAll();
        if (rebuild) {
            await this._renderBody();
        }
        _.each(result.warnings, function (warning) { this.do_warn(warning); }, this);
        this._scheduleSave();
    },
    /**
     * @private
     */
    _mergeRecipients: function (result) {
        var st = this.st;
        _.each(['to', 'cc', 'bcc'], function (field) {
            // no limit between the fields; an address is not added twice in the same one
            var used = {};
            _.each(st[field], function (a) { used[a.email] = true; });
            var added = [];
            _.each(result[field], function (address) {
                if (!used[address.email]) {
                    used[address.email] = true;
                    added.push({email: address.email, name: address.name});
                }
            });
            st[field] = st[field].concat(added);
            this.templateAdded[field] = _.pluck(added, 'email');
        }, this);
        if (result.cc.length) {
            this._ccShown = true;
        }
        if (result.bcc.length) {
            this._bccShown = true;
        }
    },
    /**
     * @private
     */
    _removeTemplateAdditions: function () {
        var st = this.st;
        var added = this.templateAdded;
        _.each(['to', 'cc', 'bcc'], function (field) {
            st[field] = _.reject(st[field], function (a) { return _.contains(added[field], a.email); });
        });
        st.attachments = _.reject(st.attachments, function (a) { return _.contains(added.attachments, a.id); });
        this.templateAdded = {to: [], cc: [], bcc: [], attachments: []};
    },
    /**
     * Save the email being written as a template of this kind of record.
     *
     * @private
     */
    _onSaveTemplate: function (ev) {
        var self = this;
        ev.preventDefault();
        dialogs.openSaveTemplateDialog(this, async function (name) {
            self._syncBody();
            var template = await self._call('save_as_template', [self.model, self.resId, name, {
                subject: self.st.subject,
                body: self.bodyHtml,
                attachment_ids: _.pluck(self.st.attachments, 'id'),
            }]);
            self.do_notify(_t('Template saved: %s').replace('%s', template.name));
            self._fetchTemplates();
        });
    },
    /**
     * @private
     */
    _onManageTemplates: function (ev) {
        ev.preventDefault();
        this.do_action('mail.action_email_template_tree_all', {
            additional_context: {
                search_default_my_templates: 1,
                search_default_model: this.model,
                default_model: this.model,
                default_user_id: session.uid,
            },
        });
    },

    //--------------------------------------------------------------------------
    // Attachments
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {File} file
     * @returns {Promise<string>} the content in base64
     */
    _readFile: function (file) {
        return new Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.onload = function () {
                resolve(String(reader.result).split(',')[1] || '');
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },
    /**
     * @private
     */
    _onFilesSelected: async function (ev) {
        var input = ev.currentTarget;
        var files = Array.prototype.slice.call(input.files);
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            this.st.uploading++;
            this._renderAttachments();
            this._renderSend();
            try {
                var datas = await this._readFile(file);
                // a pending file, like the ones of the composer of the core: it belongs to nobody until sent
                var id = await this._callModel('ir.attachment', 'create', [{
                    name: file.name, datas: datas, type: 'binary',
                    res_model: 'mail.compose.message', res_id: 0,
                }]);
                if (this.isDestroyed()) {
                    return;
                }
                this.st.attachments.push({id: id, name: file.name, size: file.size});
                this._scheduleSave();
            } finally {
                this.st.uploading--;
                if (!this.isDestroyed()) {
                    this._renderAttachments();
                    this._renderSend();
                }
            }
        }
        input.value = '';
    },
    /**
     * @private
     */
    _onClickAttachmentRemove: function (ev) {
        var self = this;
        var id = $(ev.currentTarget).data('id');
        var attachment = _.findWhere(this.st.attachments, {id: id});
        if (!attachment) {
            return;
        }
        dialogs.confirmDelete(this, {
            title: _t('Remove the file?'),
            body: _t('%s will no longer be attached to this email.').replace('%s', attachment.name),
            confirmLabel: _t('Remove'),
            confirm: function () {
                self.st.attachments = _.reject(self.st.attachments, function (a) { return a.id === id; });
                self._renderAttachments();
                self._scheduleSave();
            },
        });
    },

    //--------------------------------------------------------------------------
    // Actions
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onSend: async function (ev) {
        if (ev) {
            ev.preventDefault();
        }
        var st = this.st;
        if (st.sending || st.uploading || st.emailState === 'sent') {
            return;
        }
        st.sending = true;
        this._renderSend();
        try {
            await this._commitTypedAddresses();
            await this._settleSave();
            this._syncBody();
            this.bodyHtml = this._getInlinedBody();
            var result = await this._call('send', [this.model, this.resId, this._payload()]);
            this.dirty = false;
            this.do_notify(_t('Email sent'));
            this.trigger_up('dwo_email_sent', {messageId: result.message_id});
        } finally {
            if (!this.isDestroyed()) {
                st.sending = false;
                this._renderSend();
            }
        }
    },
    /**
     * @private
     * @param {string} state
     * @returns {string}
     */
    _deleteBody: function (state) {
        if (state === 'pending') {
            return _t('The approval request is closed and the people who were asked are told. The email is deleted.');
        }
        if (state === 'rejected') {
            return _t('The email and what the approver wrote about it are deleted.');
        }
        return _t('This draft is deleted. This cannot be undone.');
    },
    /**
     * The Delete draft button: asks, then deletes the email in the form.
     *
     * @private
     */
    _onAskDeleteCurrent: function () {
        var self = this;
        dialogs.confirmDelete(this, {
            title: _t('Delete this email?'),
            body: this._deleteBody(this.st.emailState),
            confirm: function () { self._deleteDraft(); },
        });
    },
    /**
     * Remove the draft and go back to the initial content of the form.
     *
     * @private
     */
    _deleteDraft: async function () {
        this.dirty = false;
        await this._settleSave();
        var defaults = await this._call('delete_email', [this.model, this.resId, this.st.emailId]);
        if (this.isDestroyed()) {
            return;
        }
        this._applyData(defaults);
        this.st.newerEmail = false;
        this._renderAll();
        await this._renderBody();
        this.trigger_up('dwo_email_change', {emailId: false});
        this._refreshList();
    },
    /**
     * @private
     */
    _onApplyDefaults: async function () {
        var defaults = await this._call('get_defaults', [this.model, this.resId, false, 'reply']);
        if (this.isDestroyed()) {
            return;
        }
        // same stored email, new content
        var emailId = this.st.emailId;
        var emailState = this.st.emailState;
        this._applyData(defaults);
        this.st.emailId = emailId;
        this.st.emailState = emailState;
        this.st.hasDraft = Boolean(emailId);
        this.st.newerEmail = false;
        this._renderAll();
        await this._renderBody();
        this._scheduleSave();
    },
    /**
     * @private
     */
    _onDismissBanner: function () {
        this.st.newerEmail = false;
        this._renderNotes();
    },

    //--------------------------------------------------------------------------
    // The stored emails of the user on this record
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _refreshList: async function () {
        if (this.isDestroyed()) {
            return;
        }
        var emails = await this._call('list_emails', [this.model, this.resId]);
        if (this.isDestroyed()) {
            return;
        }
        this.st.emails = emails;
        this._renderList();
    },
    /**
     * Open an email of the list in the form, after saving the one being written.
     *
     * @private
     */
    _onOpenEmail: async function (ev) {
        if ($(ev.target).closest('.o-dwo-rowDelete').length) {
            return;
        }
        var id = $(ev.currentTarget).data('id');
        if (id === this.st.emailId) {
            return;
        }
        await this._saveNow();
        var data = await this._call('load_email', [id]);
        if (this.isDestroyed()) {
            return;
        }
        this._applyData(data);
        this.st.newerEmail = false;
        this._renderAll();
        await this._renderBody();
        this.trigger_up('dwo_email_change', {emailId: id});
        this._refreshReplyTo();
        this._refreshList();
    },
    /**
     * Delete an email of the list (always after a question): the one in the form goes back to the defaults.
     *
     * @private
     */
    _onDeleteListed: function (ev) {
        var self = this;
        ev.stopPropagation();
        var id = $(ev.currentTarget).data('id');
        var email = _.findWhere(this.st.emails, {id: id});
        dialogs.confirmDelete(this, {
            title: _t('Delete this email?'),
            body: this._deleteBody(email && email.state),
            confirm: async function () {
                if (id === self.st.emailId) {
                    return self._deleteDraft();
                }
                await self._call('delete_email', [self.model, self.resId, id]);
                self._refreshList();
            },
        });
    },
    /**
     * @private
     */
    _onNewEmail: async function () {
        await this._saveNow();
        var defaults = await this._call('get_defaults', [this.model, this.resId, false, 'reply']);
        if (this.isDestroyed()) {
            return;
        }
        this._applyData(defaults);
        this.st.newerEmail = false;
        this._renderAll();
        await this._renderBody();
        // the new email is created in the database right away: it is in the list, remembered, and shows up
        // when the form is opened again, even if nothing was typed yet
        this.dirty = true;
        await this._saveNow();
        this._refreshReplyTo();
    },

    //--------------------------------------------------------------------------
    // The message on the whole screen
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onToggleExpanded: function () {
        this.st.expanded = !this.st.expanded;
        this.$('.o-dwo-editorBox').toggleClass('o-dwo-expanded bg-white', this.st.expanded);
        this.$('.o-dwo-expandedBar').toggleClass('d-none', !this.st.expanded).toggleClass('d-flex', this.st.expanded);
        this.$('.o-dwo-expandBtn').toggleClass('d-none', this.st.expanded);
        $('body').toggleClass('o-dwo-composeExpanded', this.st.expanded);
        this._renderTitle();
    },
    /**
     * Esc brings the expanded body back, wherever the focus is.
     *
     * @private
     */
    _onKeydown: function (ev) {
        // a dialog opened from the editor (a link, an image) has its own Esc
        if (ev.key === 'Escape' && this.st.expanded && !$('.modal:visible').length) {
            this._onToggleExpanded();
        }
    },

    //--------------------------------------------------------------------------
    // Approval
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onRequestApproval: function (ev) {
        var self = this;
        if (ev) {
            ev.preventDefault();
        }
        var st = this.st;
        if (st.sending || st.uploading || st.emailState === 'sent') {
            return;
        }
        var policy = st.policy;
        dialogs.openApprovalDialog(this, {
            // empty list: everybody can approve
            allowedIds: policy.approver_ids,
            excludedId: policy.allow_self_approval ? false : policy.user_id,
            onConfirm: async function (result) {
                st.sending = true;
                self._renderSend();
                try {
                    await self._commitTypedAddresses();
                    await self._settleSave();
                    self._syncBody();
                    self.bodyHtml = self._getInlinedBody();
                    var sent = await self._call('request_approval', [
                        self.model, self.resId, st.emailId, self._payload(),
                        result.approverIds, result.comment || null,
                    ]);
                    self.dirty = false;
                    st.emailId = sent.id;
                    st.emailState = sent.state;
                    st.hasDraft = true;
                    st.emails = sent.emails;
                    var loaded = await self._call('load_email', [sent.id]);
                    st.approvers = loaded.approvers;
                    st.requestComment = loaded.request_comment;
                    st.decisionComment = '';
                    st.editedAfterRequest = false;
                    self._renderTitle();
                    self._renderNotes();
                    self._renderList();
                    self.do_notify(_t('The approval was requested'));
                } finally {
                    st.sending = false;
                    self._renderSend();
                }
            },
        });
    },
    /**
     * An address typed but not yet turned into a badge is committed first, so the draft keeps it.
     *
     * @private
     */
    _commitTypedAddresses: async function () {
        var pending = false;
        _.each(this.addresses, function (widget) {
            if (widget.hasPendingText()) {
                pending = true;
                widget.commitPending();
            }
        });
        if (pending) {
            // the badge is made a moment after the blur
            await new Promise(function (resolve) { setTimeout(resolve, 200); });
        }
    },
    /**
     * @private
     */
    _onClose: async function () {
        // wait for the draft to be stored, so the Send email button can show it; the form closes even when
        // the save fails
        try {
            await this._commitTypedAddresses();
            await this._saveNow();
        } finally {
            this.closing = true;
            this.trigger_up('dwo_email_close');
        }
    },
});

return {
    EmailComposer: EmailComposer,
    splitBody: splitBody,
    withoutLeadingBlankLines: withoutLeadingBlankLines,
};

});
