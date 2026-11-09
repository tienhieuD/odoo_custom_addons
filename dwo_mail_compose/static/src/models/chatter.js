/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'Chatter',
    fields: {
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
    },
    recordMethods: {
        /**
         * The other forms of the chatter close the email form.
         *
         * @override
         */
        onClickSendMessage(ev) {
            this.update({ dwoEmailOpen: false });
            return this._super(ev);
        },
        /**
         * @override
         */
        onClickLogNote(ev) {
            this.update({ dwoEmailOpen: false });
            return this._super(ev);
        },
        /** The Send email button: opens the form on the saved draft, or on the defaults. */
        dwoToggleEmail() {
            if (this.dwoEmailOpen) {
                this.update({ dwoEmailOpen: false });
                return;
            }
            this.update({
                composerView: clear(),
                dwoEmailOpen: true,
                dwoMode: false,
                dwoRefMessageId: false,
                dwoKey: this.dwoKey + 1,
            });
        },
        /** Reply or Forward on a message: a new email, the others are left as they are. */
        dwoOpenEmail({ mode, refMessageId }) {
            this.update({
                composerView: clear(),
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
            if (this.thread && this.thread.cache) {
                // the email is on the record now: the new messages are loaded (Odoo 16: no thread.refresh())
                this.thread.cache.loadNewMessages();
            }
        },
        async dwoRefreshDraft() {
            const thread = this.thread;
            if (!thread || !thread.id) {
                return;
            }
            const hasDraft = await this.messaging.rpc({
                model: 'dwo.mail.composer',
                method: 'has_draft',
                args: [thread.model, thread.id],
            });
            if (this.exists()) {
                this.update({ dwoHasDraft: Boolean(hasDraft) });
            }
        },
        /** Another record in the same screen: the choice made on the previous one is forgotten. */
        _dwoOnThreadChanged() {
            this.update({ dwoRememberedEmailId: false, dwoEmailOpen: false });
            this.dwoRefreshDraft();
        },
    },
    onChanges: [
        {
            dependencies: ['thread'],
            methodName: '_dwoOnThreadChanged',
        },
    ],
});
