odoo.define('dwo_mail_compose/static/src/models/chatter.js', function (require) {
'use strict';

const { registerFieldPatchModel, registerInstancePatchModel } = require('mail/static/src/model/model_core.js');
const { attr } = require('mail/static/src/model/model_field.js');

const NAME = 'dwo_mail_compose/static/src/models/chatter.js';

registerFieldPatchModel('mail.chatter', NAME, {
    /** The email form takes the room of the chatter while it is open. */
    dwoEmailOpen: attr({ default: false }),
    /** reply, reply_sender, forward, or false for a new email. */
    dwoMode: attr({ default: false }),
    dwoRefMessageId: attr({ default: false }),
    /** Changes each time the form must be made again. */
    dwoKey: attr({ default: 0 }),
    /** The user has a draft on this record: a dot on the button. */
    dwoHasDraft: attr({ default: false }),
    /**
     * The email the user opened last on this screen. It lives as long as this chatter does: leaving the
     * screen or reloading the page forgets it.
     */
    dwoRememberedEmailId: attr({ default: false }),
    /**
     * The record this chatter shows. A change of record (the same screen, the pager of a form) forgets the choices
     * made on the previous one and asks again whether the user has a draft there.
     */
    dwoThreadKey: attr({
        compute: '_computeDwoThreadKey',
        dependencies: ['threadId', 'threadModel'],
    }),
});

registerInstancePatchModel('mail.chatter', NAME, {
    /**
     * @override
     */
    _created() {
        this._super(...arguments);
        // used as a handler by the template of the topbar
        this.dwoToggleEmail = this.dwoToggleEmail.bind(this);
    },

    /**
     * The other forms of the chatter close the email form.
     *
     * @override
     */
    showSendMessage() {
        this.update({ dwoEmailOpen: false });
        return this._super(...arguments);
    },

    /**
     * @override
     */
    showLogNote() {
        this.update({ dwoEmailOpen: false });
        return this._super(...arguments);
    },

    /** The Send email button: opens the form on the saved draft, or on the defaults. */
    dwoToggleEmail() {
        if (this.dwoEmailOpen) {
            this.update({ dwoEmailOpen: false });
            return;
        }
        this.update({
            isComposerVisible: false,
            dwoEmailOpen: true,
            dwoMode: false,
            dwoRefMessageId: false,
            dwoKey: this.dwoKey + 1,
        });
    },

    /** Reply or Forward on a message: a new email, the others are left as they are. */
    dwoOpenEmail({ mode, refMessageId }) {
        this.update({
            isComposerVisible: false,
            dwoEmailOpen: true,
            dwoMode: mode,
            dwoRefMessageId: refMessageId,
            dwoKey: this.dwoKey + 1,
        });
    },

    dwoOnEmailChange(emailId) {
        this.update({ dwoRememberedEmailId: emailId });
    },

    dwoOnEmailClose() {
        this.update({ dwoEmailOpen: false });
        this.dwoRefreshDraft();
    },

    dwoOnEmailSent() {
        this.update({ dwoEmailOpen: false, dwoHasDraft: false });
        if (this.thread) {
            // the email is on the record now: the new messages are loaded
            this.thread.refresh();
        }
    },

    async dwoRefreshDraft() {
        const thread = this.thread;
        if (!thread || !thread.id) {
            return;
        }
        let hasDraft;
        try {
            hasDraft = await this.env.services.rpc({
                model: 'dwo.mail.composer',
                method: 'has_draft',
                args: [thread.model, thread.id],
            });
        } catch (_error) {
            // the page is leaving, or the server is not reached: the dot stays as it was
            return;
        }
        if (this.exists()) {
            this.update({ dwoHasDraft: Boolean(hasDraft) });
        }
    },

    /**
     * @private
     * @returns {string}
     */
    _computeDwoThreadKey() {
        const key = this.threadId && this.threadModel ? `${this.threadModel}:${this.threadId}` : '';
        if (key !== this._dwoLastKey) {
            this._dwoLastKey = key;
            // not inside the compute: a compute does not write
            setTimeout(() => {
                if (this.exists()) {
                    this.update({ dwoRememberedEmailId: false, dwoEmailOpen: false });
                    this.dwoRefreshDraft();
                }
            });
        }
        return key;
    },
});

});
