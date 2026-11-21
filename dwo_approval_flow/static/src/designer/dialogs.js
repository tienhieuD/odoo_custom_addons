import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { browser } from "@web/core/browser/browser";
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { RecordSelector } from "@web/core/record_selectors/record_selector";
import { useService } from "@web/core/utils/hooks";

export const EXPR_PART = /^(record|user)(\.[a-z_][a-z0-9_]*)+$/;

/** Same rule as the server: `record.a.b or user.c`. Returns an error text or "". */
export function checkExpression(text) {
    if (!(text || "").trim()) {
        return _t("Type an expression.");
    }
    for (const part of text.trim().split(/\s+or\s+/)) {
        if (!EXPR_PART.test(part.trim())) {
            return _t(
                '"%s" is not allowed. Use record.field.field or user.field.field joined with "or". No calls, no brackets.',
                part.trim()
            );
        }
    }
    return "";
}

export const APPROVER_TYPES = [
    ["users", _t("A specific user")],
    ["group", _t("A group")],
    ["dept", _t("Same department as the document")],
    ["field", _t("User named on the document")],
    ["expr", _t("An expression (record / user)")],
];

export const ACTION_TYPES = [
    ["notify", _t("Notify in chatter")],
    ["email", _t("Send an email")],
    ["update", _t("Update a field")],
    ["server", _t("Run a server action")],
];

/** Fields of the document model, loaded once. */
export function useModelFields(getModel) {
    const orm = useService("orm");
    const state = useState({ fields: [] });
    onWillStart(async () => {
        const fields = await orm.call(getModel(), "fields_get", [], {
            attributes: ["string", "type", "relation", "readonly"],
        });
        state.fields = Object.entries(fields)
            .map(([name, info]) => ({ name, ...info }))
            .sort((a, b) => a.string.localeCompare(b.string));
    });
    return state;
}

/** The approvers of an arrow, with how many approvals are needed. */
export class WhoDialog extends Component {
    static template = "dwo_approval_flow.WhoDialog";
    static components = { Dialog, MultiRecordSelector, RecordSelector };
    static props = {
        model: String,
        approvers: Array,
        mode: String,
        n: Number,
        confirm: Function,
        close: Function,
    };

    setup() {
        this.types = APPROVER_TYPES;
        this.nameService = useService("name");
        this.fieldsState = useModelFields(() => this.props.model);
        this.state = useState({
            rows: this.props.approvers.length
                ? this.props.approvers.map((a) => ({ ...a, user_ids: [...(a.user_ids || [])] }))
                : [{ type: "users", user_ids: [], group_id: false, value: "" }],
            mode: this.props.mode,
            n: this.props.n || 2,
            error: "",
        });
    }

    get userFields() {
        return this.fieldsState.fields.filter((f) => f.relation === "res.users");
    }

    setType(row, type) {
        row.type = type;
        row.value = type === "field" ? (this.userFields[0] || {}).name || "" : "";
        row.user_ids = [];
        row.group_id = false;
    }

    setValue(row, value) {
        row.value = value;
    }

    setIds(row, ids) {
        row.user_ids = ids;
    }

    setGroup(row, id) {
        row.group_id = id;
    }

    setMode(mode) {
        this.state.mode = mode;
    }

    setN(value) {
        this.state.n = parseInt(value, 10) || 2;
    }

    addRow() {
        this.state.rows.push({ type: "users", user_ids: [], group_id: false, value: "" });
    }

    removeRow(index) {
        this.state.rows.splice(index, 1);
        if (this.state.mode === "all" && this.state.rows.length < 2) {
            this.state.mode = "any";
        }
    }

    async label(row) {
        if (row.type === "users") {
            const names = await this.nameService.loadDisplayNames("res.users", row.user_ids);
            return Object.values(names).join(", ");
        }
        if (row.type === "group") {
            const names = await this.nameService.loadDisplayNames("res.groups", [row.group_id]);
            return Object.values(names).join("");
        }
        if (row.type === "dept") {
            return _t("Same department as the document");
        }
        return row.value;
    }

    async onSave() {
        for (const row of this.state.rows) {
            const bad =
                (row.type === "users" && !row.user_ids.length && _t("Pick at least one user.")) ||
                (row.type === "group" && !row.group_id && _t("Pick a group.")) ||
                (row.type === "field" && !row.value && _t("Pick a field.")) ||
                (row.type === "expr" && checkExpression(row.value));
            if (bad) {
                this.state.error = bad;
                return;
            }
        }
        for (const row of this.state.rows) {
            row.label = await this.label(row);
        }
        const mode = this.state.rows.length < 2 && this.state.mode === "all" ? "any" : this.state.mode;
        await this.props.confirm({ approvers: this.state.rows, mode, n: this.state.n });
        this.props.close();
    }
}

/** A rule on the document: an Odoo domain that may use `user`. */
export class RuleDialog extends Component {
    static template = "dwo_approval_flow.RuleDialog";
    static components = { Dialog };
    static props = { model: String, domain: String, confirm: Function, close: Function };

    setup() {
        this.dialog = useService("dialog");
        this.state = useState({ domain: this.props.domain || "[]", error: "" });
    }

    openEditor() {
        this.dialog.add(DomainSelectorDialog, {
            resModel: this.props.model,
            domain: this.state.domain,
            isDebugMode: Boolean(this.env.debug),
            onConfirm: (domain) => {
                this.state.domain = domain;
            },
        });
    }

    async onSave() {
        const text = this.state.domain.trim();
        if (!text.startsWith("[")) {
            this.state.error = _t("A domain is a list, such as [(\"amount_total\", \">\", 50000)].");
            return;
        }
        await this.props.confirm(text);
        this.props.close();
    }
}

/** What happens to the document when the button is pressed (the main step). */
export class StepDialog extends Component {
    static template = "dwo_approval_flow.StepDialog";
    static components = { Dialog, RecordSelector };
    static props = { model: String, step: Object, confirm: Function, close: Function };

    setup() {
        this.state = useState({ ...this.props.step });
    }

    get serverActionDomain() {
        return [["model_id.model", "=", this.props.model]];
    }

    setField(name, value) {
        this.state[name] = value;
    }

    async onSave() {
        if (this.state.mode === "call_method" && !this.state.method.trim() && !this.state.server_action_id) {
            this.state.error = _t("Type a method name or pick a server action.");
            return;
        }
        const { error, ...step } = this.state;
        await this.props.confirm(step);
        this.props.close();
    }
}

/** An extra action run after the state changed. */
export class ActionDialog extends Component {
    static template = "dwo_approval_flow.ActionDialog";
    static components = { Dialog, MultiRecordSelector, RecordSelector };
    static props = {
        model: String,
        action: [Object, { value: null }],
        confirm: Function,
        close: Function,
    };

    setup() {
        this.types = ACTION_TYPES;
        this.nameService = useService("name");
        this.fieldsState = useModelFields(() => this.props.model);
        this.state = useState({
            type: "notify",
            user_ids: [],
            expr: "",
            message: "",
            field: "",
            value: "",
            server_action_id: false,
            template_id: false,
            error: "",
            ...(this.props.action || {}),
        });
    }

    get serverActionDomain() {
        return [["model_id.model", "=", this.props.model]];
    }

    setField(name, value) {
        this.state[name] = value;
    }

    get templateDomain() {
        return [["model_id.model", "=", this.props.model]];
    }

    get writableFields() {
        return this.fieldsState.fields.filter((f) => !f.readonly && !["one2many", "many2many"].includes(f.type));
    }

    async label() {
        const s = this.state;
        if (s.type === "update") {
            return `${s.field} = ${s.value}`;
        }
        if (s.type === "server") {
            const names = await this.nameService.loadDisplayNames("ir.actions.server", [s.server_action_id]);
            return Object.values(names).join("");
        }
        const names = s.user_ids.length
            ? Object.values(await this.nameService.loadDisplayNames("res.users", s.user_ids)).join(", ")
            : "";
        return [names, s.expr].filter(Boolean).join(", ") || _t("the requester");
    }

    async onSave() {
        const s = this.state;
        if (s.type === "update" && !s.field) {
            s.error = _t("Pick a field.");
            return;
        }
        if (s.type === "server" && !s.server_action_id) {
            s.error = _t("Pick a server action.");
            return;
        }
        if (s.expr && checkExpression(s.expr)) {
            s.error = checkExpression(s.expr);
            return;
        }
        const { error, ...action } = s;
        action.label = await this.label();
        await this.props.confirm(action);
        this.props.close();
    }
}

/** Copy the flow as JSON, or paste one to replace it. */
export class JsonDialog extends Component {
    static template = "dwo_approval_flow.JsonDialog";
    static components = { Dialog };
    static props = { mode: String, text: { type: String, optional: true }, load: Function, close: Function };

    setup() {
        this.state = useState({ text: this.props.text || "", errors: [], copied: false });
    }

    async copy() {
        try {
            await browser.navigator.clipboard.writeText(this.state.text);
            this.state.copied = true;
        } catch {
            this.state.copied = false;
        }
    }

    async onLoad() {
        const errors = await this.props.load(this.state.text);
        if (errors && errors.length) {
            this.state.errors = errors;
            return;
        }
        this.props.close();
    }
}

/** Describe a flow in words; the AI suggests one; the person applies it to the diagram. */
export class AiDialog extends Component {
    static template = "dwo_approval_flow.AiDialog";
    static components = { Dialog };
    static props = { editing: Boolean, ask: Function, apply: Function, close: Function };

    setup() {
        this.state = useState({ request: "", busy: false, errors: [], result: null });
    }

    async onAsk() {
        if (!this.state.request.trim()) {
            this.state.errors = [_t("Describe the flow you want first.")];
            return;
        }
        this.state.busy = true;
        this.state.errors = [];
        try {
            const result = await this.props.ask(this.state.request);
            if (result.errors) {
                this.state.errors = result.errors;
            } else {
                this.state.result = result;
            }
        } finally {
            this.state.busy = false;
        }
    }

    onBack() {
        this.state.result = null;
    }

    onApply() {
        this.props.apply(this.state.result.graph);
        this.props.close();
    }
}
