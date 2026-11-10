odoo.define('dwo_mail_compose/static/src/composer/dwo_dialogs.js', function (require) {
'use strict';

const { orm } = require('dwo_mail_compose/static/src/composer/dwo_utils.js');

const { Component } = owl;
const { useRef, useState } = owl.hooks;

// Odoo 15 has no Owl dialog service: each dialog is a small component with the markup of a Bootstrap modal,
// shown by the form while its name is in state.dialog (the form passes what the dialog needs and `close`).

/** A question before something is deleted or removed. */
class DwoConfirmDialog extends Component {
    async confirm() {
        this.props.close();
        await this.props.onConfirm();
    }
}
Object.assign(DwoConfirmDialog, { template: 'dwo_mail_compose.ConfirmDialog' });

/**
 * Asked when a template is chosen while the subject or the message already holds the
 * user's own text: replace it, keep it and add the template after it, or give up.
 */
class DwoTemplateConflictDialog extends Component {
    overwrite() {
        this.props.close();
        this.props.onOverwrite();
    }

    append() {
        this.props.close();
        this.props.onAppend();
    }
}
Object.assign(DwoTemplateConflictDialog, { template: 'dwo_mail_compose.TemplateConflictDialog' });

/** Asks the name of the template made from the email being written. */
class DwoSaveTemplateDialog extends Component {
    setup() {
        super.setup();
        this.inputRef = useRef('name');
        this.state = useState({ name: '', saving: false });
    }

    mounted() {
        if (this.inputRef.el) {
            this.inputRef.el.focus();
        }
    }

    onInput(ev) {
        this.state.name = ev.target.value;
    }

    get canSave() {
        return Boolean(this.state.name.trim()) && !this.state.saving;
    }

    async save() {
        if (!this.canSave) {
            return;
        }
        this.state.saving = true;
        try {
            await this.props.onSave(this.state.name.trim());
            this.props.close();
        } finally {
            this.state.saving = false;
        }
    }

    onKeydown(ev) {
        if (ev.key === 'Enter') {
            ev.preventDefault();
            this.save();
        }
    }
}
Object.assign(DwoSaveTemplateDialog, { template: 'dwo_mail_compose.SaveTemplateDialog' });

/**
 * Asks who should approve the email (one or several people, the first decision counts,
 * the author can be one of them) and an optional comment for them.
 */
class DwoApprovalDialog extends Component {
    setup() {
        super.setup();
        // the people chosen, what is typed to look for another one, the matches
        this.state = useState({ approvers: [], comment: '', saving: false, text: '', matches: [] });
        this.timer = null;
        this.requestId = 0;
    }

    willUnmount() {
        clearTimeout(this.timer);
    }

    get canChooseYourself() {
        return !this.props.excludedId;
    }

    get canConfirm() {
        return this.state.approvers.length > 0 && !this.state.saving;
    }

    /** Internal users only, not already chosen, within the list of the company when it has one. */
    approverDomain() {
        const excluded = this.state.approvers.map((u) => u.id);
        if (this.props.excludedId) {
            excluded.push(this.props.excludedId);
        }
        const domain = [['share', '=', false], ['id', 'not in', excluded]];
        if (this.props.allowedIds && this.props.allowedIds.length) {
            domain.push(['id', 'in', this.props.allowedIds]);
        }
        return domain;
    }

    onInput(ev) {
        this.state.text = ev.target.value;
        clearTimeout(this.timer);
        this.timer = setTimeout(() => this.search(), 200);
    }

    onFocus() {
        this.search();
    }

    async search() {
        const requestId = ++this.requestId;
        const found = await orm(this.env, 'res.users', 'name_search', [], {
            name: this.state.text.trim(),
            args: this.approverDomain(),
            limit: 8,
        });
        if (requestId === this.requestId) {
            this.state.matches = found.map(([id, name]) => ({ id, name }));
        }
    }

    onMousedownMatch(ev) {
        ev.preventDefault();
        const id = Number(ev.currentTarget.dataset.id);
        const match = this.state.matches.find((m) => m.id === id);
        if (match && !this.state.approvers.some((u) => u.id === id)) {
            this.state.approvers.push({ id: match.id, name: match.name });
        }
        // the field is emptied for the next person
        this.state.text = '';
        this.state.matches = [];
    }

    onBlur() {
        setTimeout(() => {
            this.state.matches = [];
        }, 150);
    }

    onClickRemove(ev) {
        const id = Number(ev.currentTarget.dataset.id);
        this.state.approvers = this.state.approvers.filter((u) => u.id !== id);
    }

    onInputComment(ev) {
        this.state.comment = ev.target.value;
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
}
Object.assign(DwoApprovalDialog, { template: 'dwo_mail_compose.ApprovalDialog' });

return { DwoConfirmDialog, DwoTemplateConflictDialog, DwoSaveTemplateDialog, DwoApprovalDialog };

});
