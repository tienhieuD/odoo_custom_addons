/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';

registerPatch({
    name: 'Message',
    modelMethods: {
        /**
         * @override
         */
        convertData(data) {
            const res = this._super(data);
            for (const key of [
                'dwo_is_from_compose',
                'outgoing_email_to',
                'outgoing_email_cc',
                'dwo_incoming_email_to_all',
                'incoming_email_to',
                'incoming_email_cc',
            ]) {
                if (key in data) {
                    res[key] = data[key];
                }
            }
            return res;
        },
    },
    recordMethods: {
        /**
         * Reply, Reply all or Forward on this email: the form of the chatter of its record opens.
         *
         * @param {string} mode reply_sender, reply or forward
         */
        dwoOpenEmail(mode) {
            const thread = this.originThread;
            const chatter = thread && this.messaging.models['Chatter'].all().find(
                (candidate) => candidate.thread === thread
            );
            if (chatter) {
                chatter.dwoOpenEmail({ mode, refMessageId: this.id });
            }
        },
    },
    fields: {
        /** Sent with the Send email button of the composer. */
        dwo_is_from_compose: attr({ default: false }),
        outgoing_email_to: attr({ default: '' }),
        outgoing_email_cc: attr({ default: '' }),
        /** The To as received, aliases included (the core leaves them out of incoming_email_to). */
        dwo_incoming_email_to_all: attr({ default: [] }),
        /** Lists of [name, email]. */
        incoming_email_to: attr({ default: [] }),
        incoming_email_cc: attr({ default: [] }),
        /** An email received, or an official email sent with the Send email button. */
        isDwoEmail: attr({
            compute() {
                return Boolean(this.dwo_is_from_compose) || this.message_type === 'email';
            },
        }),
        /** From, To and Cc lines shown under the header of an email. Never the Bcc. */
        dwoMetaLines: attr({
            compute() {
                // An address is shown once, at the place of its first appearance, with its name if any
                // line of the email gave one (a header may repeat it with and without a name).
                const format = (tuples) => {
                    const unique = new Map();
                    for (const [name, email] of tuples || []) {
                        const key = (email || '').toLowerCase();
                        if (!unique.has(key)) {
                            unique.set(key, [name, email]);
                        } else if (name && !unique.get(key)[0]) {
                            unique.get(key)[0] = name;
                        }
                    }
                    return [...unique.values()]
                        .map(([name, email]) => (name ? `${name} <${email}>` : email))
                        .join(', ');
                };
                const lines = [];
                if (this.email_from) {
                    lines.push({ label: 'From', text: this.email_from });
                }
                const to = this.dwo_is_from_compose
                    ? this.outgoing_email_to
                    : format(
                          this.dwo_incoming_email_to_all && this.dwo_incoming_email_to_all.length
                              ? this.dwo_incoming_email_to_all
                              : this.incoming_email_to
                      );
                const cc = this.dwo_is_from_compose ? this.outgoing_email_cc : format(this.incoming_email_cc);
                if (to) {
                    lines.push({ label: 'To', text: to });
                }
                if (cc) {
                    lines.push({ label: 'Cc', text: cc });
                }
                return lines;
            },
        }),
    },
});
