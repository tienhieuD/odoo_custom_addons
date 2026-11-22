/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import { Dialog } from "@web/core/dialog/dialog";
import { browser } from "@web/core/browser/browser";
import { RecordPicker } from "./record_picker";
import { useService } from "@web/core/utils/hooks";

export const EXPR_PART = /^(record|user)(\.[a-z_][a-z0-9_]*)+$/;

/** Same rule as the server: `record.a.b or user.c`. Returns an error text or "". */
export function checkExpression(text) {
    if (!(text || "").trim()) {
        return _t("Type an expression.");
    }
    for (const part of text.trim().split(/\s+or\s+/)) {
        if (!EXPR_PART.test(part.trim())) {
            return sprintf(_t('"%s" is not allowed. Use record.field.field or user.field.field joined with "or". No calls, no brackets.'), part.trim());
        }
    }
    return "";
}

export const APPROVER_TYPES = [
    ["users", _t("A specific user")],
    ["group", _t("A group")],
    ["field", _t("User named on the document")],
    ["expr", _t("An expression (record / user)")],
];

const NO_CHANNELS = { bus: false, activity: false, email: false };
/** The rows of the table of notifications: key, name, what it does. */
const CHANNELS = [
    ["bus", _t("System notification"), _t("A pop-up in Odoo")],
    ["activity", _t("Activity"), _t("A \"To approve\" to-do")],
    ["email", _t("Email (inbox)"), _t("An email, or Discuss, as each person prefers")],
];

// Only shown for an arrow saved before this option was removed, so that it can still be opened.
const LEGACY_DEPT = ["dept", _t("Same department as the document")];

export const ACTION_TYPES = [
    ["notify", _t("Notify in chatter")],
    ["email", _t("Send an email")],
    ["update", _t("Update a field")],
    ["server", _t("Run a server action")],
];

/** ``{id: name}`` of some records (Odoo 16 has no name service). */
async function displayNames(orm, model, ids) {
    const wanted = ids.filter(Boolean);
    if (!wanted.length) {
        return {};
    }
    return Object.fromEntries(await orm.call(model, "name_get", [wanted]));
}

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
    static components = { Dialog, RecordPicker };
    static props = {
        model: String,
        approvers: Array,
        mode: String,
        n: Number,
        followers: Object,
        confirm: Function,
        close: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.fieldsState = useModelFields(() => this.props.model);
        this.state = useState({
            rows: this.props.approvers.length
                ? this.props.approvers.map((a) => ({
                      ...a,
                      user_ids: [...(a.user_ids || [])],
                      notify: { ...NO_CHANNELS, ...a.notify },
                  }))
                : [this.newRow()],
            mode: this.props.mode,
            n: this.props.n || 2,
            followers: { ...NO_CHANNELS, ...this.props.followers },
            error: "",
        });
        this.channels = CHANNELS;
    }

    newRow() {
        return { type: "users", user_ids: [], group_id: false, value: "", notify: { ...NO_CHANNELS } };
    }

    /** Header of the column of an approver line in the table of notifications. */
    columnLabel(row) {
        const type = (this.types.find((t) => t[0] === row.type) || [])[1] || "";
        return row.label || row.value || type;
    }

    async refreshLabel(row) {
        row.label = await this.label(row);
    }

    setNotify(target, channel, checked) {
        target[channel] = checked;
    }

    get userFields() {
        return this.fieldsState.fields.filter((f) => f.relation === "res.users");
    }

    setType(row, type) {
        row.type = type;
        row.value = type === "field" ? (this.userFields[0] || {}).name || "" : "";
        row.user_ids = [];
        row.group_id = false;
        row.label = "";
    }

    setValue(row, value) {
        row.value = value;
        this.refreshLabel(row);
    }

    setIds(row, ids) {
        row.user_ids = ids;
        this.refreshLabel(row);
    }

    setGroup(row, id) {
        row.group_id = id;
        this.refreshLabel(row);
    }

    setMode(mode) {
        this.state.mode = mode;
    }

    setN(value) {
        this.state.n = parseInt(value, 10) || 2;
    }

    addRow() {
        this.state.rows.push(this.newRow());
    }

    get types() {
        return this.state.rows.some((row) => row.type === "dept") ? [...APPROVER_TYPES, LEGACY_DEPT] : APPROVER_TYPES;
    }

    removeRow(index) {
        this.state.rows.splice(index, 1);
        if (this.state.mode === "all" && this.state.rows.length < 2) {
            this.state.mode = "any";
        }
    }

    async label(row) {
        if (row.type === "users") {
            const names = await displayNames(this.orm, "res.users", row.user_ids);
            return Object.values(names).join(", ");
        }
        if (row.type === "group") {
            const names = await displayNames(this.orm, "res.groups", [row.group_id]);
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
        await this.props.confirm({ approvers: this.state.rows, mode, n: this.state.n, followers: { ...this.state.followers } });
        this.props.close();
    }
}

/** What happens to the document when the button is pressed (the main step). */
export class StepDialog extends Component {
    static template = "dwo_approval_flow.StepDialog";
    static components = { Dialog, RecordPicker };
    static props = { model: String, step: Object, confirm: Function, close: Function };

    setup() {
        this.orm = useService("orm");
        const step = this.props.step;
        // three choices on screen, two modes in the data: a server action is a "call" without a method
        const kind = step.mode !== "call_method" ? "state" : step.server_action_id && !step.method ? "server" : "method";
        this.state = useState({ ...step, kind, error: "", methods: [], listOpen: false });
        onWillStart(async () => {
            try {
                this.state.methods = await this.orm.call("dwo.approval.flow", "model_methods", [this.props.model]);
            } catch {
                this.state.methods = []; // no list: the name can still be typed
            }
        });
    }

    get serverActionDomain() {
        return [["model_id.model", "=", this.props.model]];
    }

    get matches() {
        const text = (this.state.method || "").trim().toLowerCase();
        return this.state.methods.filter((m) => !text || m.name.toLowerCase().includes(text)).slice(0, 8);
    }

    get picked() {
        return this.state.methods.find((m) => m.name === (this.state.method || "").trim());
    }

    /** First line of a docstring. */
    shortDoc(doc) {
        const line = (doc || "").split("\n").find((l) => l.trim()) || "";
        return line.trim();
    }

    onMethodInput(ev) {
        this.state.method = ev.target.value;
        this.state.listOpen = true;
    }

    pickMethod(name) {
        this.state.method = name;
        this.state.listOpen = false;
    }

    closeListLater() {
        setTimeout(() => (this.state.listOpen = false), 150);
    }

    setField(name, value) {
        this.state[name] = value;
    }

    async onSave() {
        const { kind, error, methods, listOpen, ...step } = this.state;
        step.method = (step.method || "").trim();
        if (kind === "method" && !step.method) {
            this.state.error = _t("Type the name of a method.");
            return;
        }
        if (kind === "method" && methods.length && !methods.some((m) => m.name === step.method)) {
            this.state.error = _t("This is not a public method of the model.");
            return;
        }
        if (kind === "server" && !step.server_action_id) {
            this.state.error = _t("Pick a server action.");
            return;
        }
        if (kind === "state") {
            Object.assign(step, { mode: "set_state", method: "", server_action_id: false });
        } else if (kind === "server") {
            Object.assign(step, { mode: "call_method", method: "" });
        } else {
            Object.assign(step, { mode: "call_method", server_action_id: false });
        }
        await this.props.confirm(step);
        this.props.close();
    }
}

/** An extra action run after the state changed. */
export class ActionDialog extends Component {
    static template = "dwo_approval_flow.ActionDialog";
    static components = { Dialog, RecordPicker };
    static props = {
        model: String,
        action: [Object, { value: null }],
        confirm: Function,
        close: Function,
    };

    setup() {
        this.types = ACTION_TYPES;
        this.orm = useService("orm");
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
            const names = await displayNames(this.orm, "ir.actions.server", [s.server_action_id]);
            return Object.values(names).join("");
        }
        const names = s.user_ids.length
            ? Object.values(await displayNames(this.orm, "res.users", s.user_ids)).join(", ")
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
