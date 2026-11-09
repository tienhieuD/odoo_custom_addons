import { Message } from "@mail/core/common/message_model";
import { Record } from "@mail/core/common/record";
import { patch } from "@web/core/utils/patch";

patch(Message.prototype, {
    setup() {
        super.setup();
        /** @type {boolean} */
        this.dwo_is_from_compose = Record.attr(false);
        /** @type {string} */
        this.outgoing_email_to = Record.attr("");
        /** @type {string} */
        this.outgoing_email_cc = Record.attr("");
        /** The To as received, aliases included (the core leaves them out of incoming_email_to). */
        this.dwo_incoming_email_to_all = Record.attr([]);
        /** Odoo 19 has these two in core; Odoo 18 gets them from this module (lists of [name, email]). */
        this.incoming_email_to = Record.attr([]);
        this.incoming_email_cc = Record.attr([]);
    },

    /** An email received, or an official email sent with the Send email button. */
    get isDwoEmail() {
        return Boolean(this.dwo_is_from_compose) || this.message_type === "email";
    },

    /** From, To and Cc lines shown under the header of an email. Never the Bcc. */
    get dwoMetaLines() {
        // An address is shown once, at the place of its first appearance, with its name if any
        // line of the email gave one (a header may repeat it with and without a name).
        const format = (tuples) => {
            const unique = new Map();
            for (const [name, email] of tuples || []) {
                const key = (email || "").toLowerCase();
                if (!unique.has(key)) {
                    unique.set(key, [name, email]);
                } else if (name && !unique.get(key)[0]) {
                    unique.get(key)[0] = name;
                }
            }
            return [...unique.values()]
                .map(([name, email]) => (name ? `${name} <${email}>` : email))
                .join(", ");
        };
        const lines = [];
        if (this.email_from) {
            lines.push({ label: "From", text: this.email_from });
        }
        const to = this.dwo_is_from_compose
            ? this.outgoing_email_to
            : format(
                  this.dwo_incoming_email_to_all?.length
                      ? this.dwo_incoming_email_to_all
                      : this.incoming_email_to
              );
        const cc = this.dwo_is_from_compose
            ? this.outgoing_email_cc
            : format(this.incoming_email_cc);
        if (to) {
            lines.push({ label: "To", text: to });
        }
        if (cc) {
            lines.push({ label: "Cc", text: cc });
        }
        return lines;
    },
});
