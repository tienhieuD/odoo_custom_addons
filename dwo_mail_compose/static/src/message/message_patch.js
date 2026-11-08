import { Message } from "@mail/core/common/message_model";
import { fields } from "@mail/core/common/record";
import { patch } from "@web/core/utils/patch";

patch(Message.prototype, {
    setup() {
        super.setup();
        /** @type {boolean} */
        this.dwo_is_official_email = fields.Attr(false);
        /** @type {string} */
        this.outgoing_email_to = fields.Attr("");
        /** @type {string} */
        this.outgoing_email_cc = fields.Attr("");
    },

    /** An email received, or an official email sent with the Send email button. */
    get isDwoEmail() {
        return Boolean(this.dwo_is_official_email) || this.message_type === "email";
    },

    /** From, To and Cc lines shown under the header of an email. Never the Bcc. */
    get dwoMetaLines() {
        const format = (tuples) =>
            (tuples || []).map(([name, email]) => (name ? `${name} <${email}>` : email)).join(", ");
        const lines = [];
        if (this.email_from) {
            lines.push({ label: "From", text: this.email_from });
        }
        const to = this.dwo_is_official_email
            ? this.outgoing_email_to
            : format(this.incoming_email_to);
        const cc = this.dwo_is_official_email
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
