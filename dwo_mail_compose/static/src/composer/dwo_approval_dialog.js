import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";

/**
 * Asks who should approve the email (one or several people, the first decision counts,
 * the author can be one of them) and an optional comment for them.
 */
export class DwoApprovalDialog extends Component {
    static template = "dwo_mail_compose.ApprovalDialog";
    static components = { Dialog, Many2XAutocomplete };
    static props = {
        // called with { approverIds, comment }
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ approvers: [], comment: "", saving: false, key: 0 });
    }

    get fieldActions() {
        return { create: false, createEdit: false, write: false };
    }

    approverDomain() {
        // internal users only, not already chosen
        return [["share", "=", false], ["id", "not in", this.state.approvers.map((u) => u.id)]];
    }

    async onPicked(records) {
        const picked = (records || []).filter((r) => r && r.id);
        // The dropdown gives the name, the "Search more..." popup gives only the id
        const unnamed = picked.filter((r) => !(r.display_name || r.name)).map((r) => r.id);
        const names = {};
        if (unnamed.length) {
            for (const user of await this.orm.read("res.users", unnamed, ["display_name"])) {
                names[user.id] = user.display_name;
            }
        }
        for (const record of picked) {
            if (!this.state.approvers.some((u) => u.id === record.id)) {
                this.state.approvers.push({
                    id: record.id,
                    name: record.display_name || record.name || names[record.id] || String(record.id),
                });
            }
        }
        // the field is emptied for the next person
        this.state.key++;
    }

    remove(user) {
        this.state.approvers = this.state.approvers.filter((u) => u.id !== user.id);
    }

    get canConfirm() {
        return this.state.approvers.length > 0 && !this.state.saving;
    }

    async confirm() {
        if (!this.canConfirm) {
            return;
        }
        this.state.saving = true;
        try {
            await this.props.onConfirm({
                approverIds: this.state.approvers.map((u) => u.id),
                comment: this.state.comment.trim(),
            });
            this.props.close();
        } finally {
            this.state.saving = false;
        }
    }

    get title() {
        return _t("Request approval");
    }
}
