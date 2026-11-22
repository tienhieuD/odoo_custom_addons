/** @odoo-module **/
import { Component, onWillUpdateProps, useRef, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useRecordObserver } from "@web/model/relational_model/utils";
import { ColorList } from "@web/core/colorlist/colorlist";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { DomainSelector } from "@web/core/domain_selector/domain_selector";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { ActionDialog, AiDialog, JsonDialog, StepDialog, WhoDialog } from "./dialogs";
import { COLORS } from "./palette";
import { NH, NW, collides, computeLayout, freeSpot } from "./layout";

// The AI button works end to end (dialog, prompt, checks) but the model call is still a mock: switch to true when the real one is in.
const AI_READY = false;

let counter = 0;
const cid = () => `c${++counter}`;

function parse(text) {
    let graph;
    try {
        graph = JSON.parse(text || "{}");
    } catch {
        graph = {};
    }
    graph.schema = graph.schema || "dwo_approval_flow/1";
    graph.states = graph.states || [];
    graph.transitions = graph.transitions || [];
    graph.states.forEach((s) => (s.cid = cid()));
    graph.transitions.forEach((t) => {
        t.cid = cid();
        t.rules = t.rules || [];
        t.actions = t.actions || [];
        t.main_step = t.main_step || { mode: "set_state" };
    });
    return graph;
}

/** Field widget: the state diagram of an approval flow (boxes are states, arrows are buttons). */
export class FlowDesigner extends Component {
    static template = "dwo_approval_flow.Designer";
    static components = { ColorList, DomainSelector };
    static props = {
        ...standardFieldProps,
        modelField: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.svgRef = useRef("svg");
        this.colorIds = COLORS.map((_c, index) => index);
        this.state = useState({
            graph: parse(this.props.record.data[this.props.name]),
            selected: null, // { kind: "state"|"transition", cid }
            showChecks: false,
            connecting: null,
        });
        this.lastSeen = this.props.record.data[this.props.name];
        this.fieldKey = this.fieldKeyOf(this.props.record);
        // the state field was picked or changed on this very record: load its values into the diagram
        useRecordObserver((record) => {
            const key = this.fieldKeyOf(record);
            const [oldRes, oldRest] = [this.fieldKey.split("|")[0], this.fieldKey.slice(this.fieldKey.indexOf("|"))];
            this.fieldKey = key;
            if (key.split("|")[0] === oldRes && key.slice(key.indexOf("|")) !== oldRest && record.data.state_mode === "field") {
                this.loadFieldStates(record);
            }
        });
        onWillUpdateProps((next) => {
            const text = next.record.data[next.name];
            if (text !== this.lastSeen) {
                this.lastSeen = text;
                this.state.graph = parse(text);
                this.state.selected = null;
            }
        });
    }

    fieldKeyOf(record) {
        const d = record.data;
        const model = d.model_id ? d.model_id.id : 0;
        const field = d.state_field_id ? d.state_field_id.id : 0;
        return `${record.resId || 0}|${d.state_mode}|${model}|${field}`;
    }

    async loadFieldStates(record) {
        const d = record.data;
        if (!d.model_id || !d.state_field_id) {
            return;
        }
        let values;
        try {
            values = await this.orm.call("dwo.approval.flow", "field_states", [d.model_id.id, d.state_field_id.id]);
        } catch (error) {
            this.notification.add(error.data?.message || _t("Cannot read the values of this field."), { type: "danger" });
            return;
        }
        const old = new Map(this.graph.states.map((s) => [s.key, s]));
        const used = new Set(this.graph.transitions.flatMap((t) => [t.from, t.to]));
        const states = values.map((v, i) => {
            const known = old.get(v.key);
            if (known) {
                return Object.assign(known, { name: v.name, missing: false });
            }
            return {
                cid: cid(), id: false, key: v.key, name: v.name, color: 0, visible: true, missing: false,
                x: 10 + (i % 4) * 230, y: 20 + Math.floor(i / 4) * 110,
            };
        });
        const keys = new Set(values.map((v) => v.key));
        for (const s of this.graph.states) {
            if (!keys.has(s.key) && used.has(s.key)) {
                s.missing = true; // arrows still point to it: keep it, flagged
                states.push(s);
            }
        }
        this.state.graph.states = states;
        this.state.selected = null;
        this.commit();
    }

    // ------------------------------------------------------------------
    // data
    // ------------------------------------------------------------------
    get data() {
        return this.props.record.data;
    }

    get modelName() {
        return this.data[this.props.modelField || "model_name"] || "";
    }

    get isFieldMode() {
        return this.data.state_mode === "field";
    }

    get readonly() {
        return this.props.readonly;
    }

    get graph() {
        return this.state.graph;
    }

    get selectedState() {
        const sel = this.state.selected;
        return sel && sel.kind === "state" ? this.graph.states.find((s) => s.cid === sel.cid) : null;
    }

    get selectedTransition() {
        const sel = this.state.selected;
        return sel && sel.kind === "transition" ? this.graph.transitions.find((t) => t.cid === sel.cid) : null;
    }

    stateByKey(key) {
        return this.graph.states.find((s) => s.key === key);
    }

    commit() {
        const text = JSON.stringify(this.graph, (key, value) => (key === "cid" ? undefined : value));
        this.lastSeen = text;
        this.props.record.update({ [this.props.name]: text });
    }

    // ------------------------------------------------------------------
    // drawing
    // ------------------------------------------------------------------
    get canvasSize() {
        const xs = this.graph.states.map((s) => s.x + NW + 60);
        const ys = this.graph.states.map((s) => s.y + NH + 60);
        return { width: Math.max(760, ...xs), height: Math.max(420, ...ys) };
    }

    stroke(color) {
        return COLORS[color] || "";
    }

    nodeStyle(state) {
        const c = this.stroke(state.color);
        return c ? `stroke: ${c}; stroke-width: 2; fill: ${c}; fill-opacity: 0.16` : "";
    }

    edgeStyle(t) {
        const c = this.stroke(t.color);
        return c ? `stroke: ${c}` : "";
    }

    labelStyle(t) {
        const c = this.stroke(t.color);
        return c ? `stroke: ${c}; stroke-width: 1.8` : "";
    }

    get layout() {
        return computeLayout(this.graph.states, this.graph.transitions);
    }

    pointer(ev) {
        const rect = this.svgRef.el.getBoundingClientRect();
        return { x: ev.clientX - rect.left, y: ev.clientY - rect.top };
    }

    // ------------------------------------------------------------------
    // selecting, dragging, connecting
    // ------------------------------------------------------------------
    clearSelection() {
        this.state.selected = null;
    }

    selectTransition(ev, t) {
        ev.stopPropagation();
        this.state.selected = { kind: "transition", cid: t.cid };
    }

    startDrag(ev, s) {
        ev.stopPropagation();
        this.state.selected = { kind: "state", cid: s.cid };
        if (this.readonly) {
            return;
        }
        const start = this.pointer(ev);
        const ox = start.x - s.x;
        const oy = start.y - s.y;
        let moved = false;
        const move = (e) => {
            const p = this.pointer(e);
            const x = Math.max(4, Math.round(p.x - ox));
            const y = Math.max(4, Math.round(p.y - oy));
            // boxes never overlap: slide along one axis when the other is blocked
            const states = this.graph.states;
            if (!collides(states, s, x, y)) {
                s.x = x;
                s.y = y;
            } else if (!collides(states, s, x, s.y)) {
                s.x = x;
            } else if (!collides(states, s, s.x, y)) {
                s.y = y;
            }
            moved = true;
        };
        const up = () => {
            browser.removeEventListener("pointermove", move);
            browser.removeEventListener("pointerup", up);
            if (moved) {
                this.commit();
            }
        };
        browser.addEventListener("pointermove", move);
        browser.addEventListener("pointerup", up);
    }

    startConnect(ev, s) {
        ev.stopPropagation();
        ev.preventDefault();
        if (this.readonly) {
            return;
        }
        this.state.connecting = { x1: s.x + NW, y1: s.y + NH / 2, x2: s.x + NW, y2: s.y + NH / 2, target: null };
        const move = (e) => {
            const p = this.pointer(e);
            const el = document.elementFromPoint(e.clientX, e.clientY)?.closest("[data-skey]");
            const target = el && el.dataset.skey !== s.key ? el.dataset.skey : null;
            Object.assign(this.state.connecting, { x2: p.x, y2: p.y, target });
        };
        const up = () => {
            browser.removeEventListener("pointermove", move);
            browser.removeEventListener("pointerup", up);
            const target = this.state.connecting.target;
            this.state.connecting = null;
            if (target) {
                this.addTransition(s.key, target);
            }
        };
        browser.addEventListener("pointermove", move);
        browser.addEventListener("pointerup", up);
    }

    // ------------------------------------------------------------------
    // editing the graph
    // ------------------------------------------------------------------
    addState() {
        const index = this.graph.states.length;
        let n = index + 1;
        while (this.stateByKey(`state_${n}`)) {
            n++;
        }
        const s = {
            cid: cid(), id: false, key: `state_${n}`, name: _t("New state"), color: 0, visible: true, missing: false,
            ...freeSpot(this.graph.states),
        };
        this.graph.states.push(s);
        this.state.selected = { kind: "state", cid: s.cid };
        this.commit();
    }

    addTransition(from, to) {
        const existing = this.graph.transitions.find((t) => t.from === from && t.to === to);
        if (existing) {
            this.state.selected = { kind: "transition", cid: existing.cid };
            return;
        }
        const t = {
            cid: cid(), id: false, name: _t("New action"), from, to, color: 0, ask_reason: false, list_action: false, notify: { followers: {}, creator: false },
            who: null, rules: [], main_step: { mode: "set_state", method: "", server_action_id: false, verify: true, run_as: "user", guard: "direct" },
            actions: [],
        };
        this.graph.transitions.push(t);
        this.state.selected = { kind: "transition", cid: t.cid };
        this.commit();
    }

    addWayBack(t) {
        if (!t.from) {
            return;
        }
        this.addTransition(t.to, t.from);
        const back = this.graph.transitions[this.graph.transitions.length - 1];
        back.name = _t("Send back");
        this.commit();
    }

    deleteState(s) {
        this.graph.states = this.graph.states.filter((x) => x !== s);
        this.graph.transitions = this.graph.transitions.filter((t) => t.from !== s.key && t.to !== s.key);
        this.state.selected = null;
        this.commit();
    }

    deleteTransition(t) {
        this.graph.transitions = this.graph.transitions.filter((x) => x !== t);
        this.state.selected = null;
        this.commit();
    }

    setStateKey(s, key) {
        const old = s.key;
        s.key = key;
        this.graph.transitions.forEach((t) => {
            t.from = t.from === old ? key : t.from;
            t.to = t.to === old ? key : t.to;
        });
        this.commit();
    }

    setVisible(state, value) {
        state.visible = value;
        this.commit();
    }

    setColor(item, color) {
        item.color = color;
        this.commit();
    }

    // ------------------------------------------------------------------
    // texts shown in the panel
    // ------------------------------------------------------------------
    approverText(t) {
        return (t.who ? t.who.approvers : []).map((a) => a.label || this.approverLabel(a)).join(_t(" or "));
    }

    approverLabel(a) {
        return a.type === "dept" ? _t("Same department as the document") : a.value || "…";
    }

    approvalsText(t) {
        const w = t.who;
        if (w.approvals.mode === "all") {
            return _t("Everyone listed approves");
        }
        if (w.approvals.mode === "n") {
            return _t("At least %s approve", w.approvals.n);
        }
        return w.approvers.length > 1 ? _t("1 approval") : _t("Anyone from this list");
    }

    stepText(t) {
        const step = t.main_step;
        const to = (this.stateByKey(t.to) || {}).name;
        if (step.mode === "call_method") {
            return step.method
                ? _t("Call the method %(method)s (the state must become %(to)s)", { method: step.method, to })
                : _t("Run a server action (the state must become %s)", to);
        }
        return _t("Change state to %s", to);
    }

    actionText(a) {
        const kinds = { notify: _t("Notify"), email: _t("Email"), update: _t("Update"), server: _t("Server action") };
        return `${kinds[a.type]}: ${a.label || ""}${a.message ? ` — ${a.message}` : ""}`;
    }

    checkLines(t) {
        const lines = [_t("The document is in “%s”", t.from || _t("any state"))];
        if (t.who) {
            lines.push(_t("The user is: %s", this.approverText(t)));
        }
        t.rules.forEach((rule) => lines.push(_t("The document matches %s", rule)));
        return lines;
    }

    get problems() {
        const out = [];
        const first = this.graph.states[0];
        this.graph.states.forEach((s) => {
            const incoming = this.graph.transitions.some((t) => t.to === s.key);
            if (s !== first && !incoming && !s.missing) {
                out.push({ cid: s.cid, text: _t("“%s” cannot be reached: no arrow points to it.", s.name) });
            }
            if (s.missing) {
                out.push({ cid: s.cid, text: _t("“%s” no longer exists on the model's field.", s.name) });
            }
        });
        return out;
    }

    // ------------------------------------------------------------------
    // dialogs
    // ------------------------------------------------------------------
    editWho(t) {
        this.dialog.add(WhoDialog, {
            model: this.modelName,
            approvers: t.who ? t.who.approvers : [],
            mode: t.who ? t.who.approvals.mode : "any",
            n: t.who ? t.who.approvals.n : 2,
            followers: (t.notify && t.notify.followers) || {},
            confirm: ({ approvers, mode, n, followers }) => {
                t.who = { approvers, approvals: { mode, n } };
                t.notify = Object.assign({}, t.notify, { followers });
                this.commit();
            },
        });
    }

    notifyText(t) {
        const names = { bus: _t("system"), activity: _t("activity"), email: _t("email") };
        const list = (flags) => Object.keys(names).filter((c) => flags && flags[c]).map((c) => names[c]).join(", ");
        const parts = [];
        const approvers = new Set();
        ((t.who && t.who.approvers) || []).forEach((a) => Object.keys(names).forEach((c) => a.notify && a.notify[c] && approvers.add(c)));
        if (approvers.size) {
            parts.push(_t("approvers: %s", list(Object.fromEntries([...approvers].map((c) => [c, true])))));
        }
        const followers = list(t.notify && t.notify.followers);
        if (followers) {
            parts.push(_t("followers: %s", followers));
        }
        return parts.length ? _t("Told on arrival: %s", parts.join("; ")) : "";
    }

    removeWho(t) {
        t.who = null;
        t.notify = Object.assign({}, t.notify, { followers: { bus: false, activity: false, email: false } });
        this.commit();
    }

    editRule(t, index) {
        // the Odoo domain editor, straight away: no domain text to type
        this.dialog.add(DomainSelectorDialog, {
            resModel: this.modelName,
            domain: index >= 0 ? t.rules[index] : "[]",
            isDebugMode: Boolean(this.env.debug),
            onConfirm: (domain) => {
                if (index >= 0) {
                    t.rules[index] = domain;
                } else {
                    t.rules.push(domain);
                }
                this.commit();
            },
        });
    }

    removeRule(t, index) {
        t.rules.splice(index, 1);
        this.commit();
    }

    addCondition(t) {
        this.editRule(t, -1);
    }

    editStep(t) {
        const step = t.main_step;
        this.dialog.add(StepDialog, {
            model: this.modelName,
            step: {
                mode: step.mode, method: step.method || "", server_action_id: step.server_action_id || false,
                verify: step.verify !== false, run_as: step.run_as || "user", guard: step.guard || "direct",
            },
            confirm: (value) => {
                t.main_step = value;
                this.commit();
            },
        });
    }

    editAction(t, index) {
        this.dialog.add(ActionDialog, {
            model: this.modelName,
            action: index >= 0 ? { ...t.actions[index] } : null,
            confirm: (action) => {
                if (index >= 0) {
                    t.actions[index] = action;
                } else {
                    t.actions.push(action);
                }
                this.commit();
            },
        });
    }

    removeAction(t, index) {
        t.actions.splice(index, 1);
        this.commit();
    }

    onNameInput(item, ev) {
        item.name = ev.target.value;
    }

    onNameChange() {
        this.commit();
    }

    onStateNameChange(s) {
        // a new box still has its automatic value (state_2): derive a readable one from the name
        if (!s.id && /^state_\d+$/.test(s.key)) {
            const base = (s.name || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                .replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
            let key = base || s.key;
            for (let n = 2; this.graph.states.some((x) => x !== s && x.key === key); n++) {
                key = `${base}_${n}`;
            }
            if (key !== s.key) {
                this.setStateKey(s, key);
                return;
            }
        }
        this.commit();
    }

    toggleNotify(t, key, ev) {
        t.notify = Object.assign({}, t.notify, { [key]: ev.target.checked });
        this.commit();
    }

    toggleListAction(t, ev) {
        t.list_action = ev.target.checked;
        this.commit();
    }

    toggleReason(t, ev) {
        t.ask_reason = ev.target.checked;
        this.commit();
    }

    // ------------------------------------------------------------------
    // JSON
    // ------------------------------------------------------------------
    async copyJson() {
        const text = JSON.stringify(this.graph, (key, value) => (key === "cid" ? undefined : value));
        const shared = await this.orm.call("dwo.approval.flow", "graph_to_share", [text]);
        try {
            await browser.navigator.clipboard.writeText(shared);
            this.notification.add(_t("Flow copied as JSON."), { type: "success" });
        } catch {
            this.dialog.add(JsonDialog, { mode: "copy", text: shared, load: () => [], close: () => {} });
        }
    }

    get hasDiagram() {
        return this.graph.states.length > 0 && this.graph.transitions.length > 0;
    }

    get aiTitle() {
        if (!AI_READY) {
            return _t("Build a flow with AI: coming soon");
        }
        return this.hasDiagram ? _t("Edit this flow with AI") : _t("Build a flow with AI");
    }

    aiFlow() {
        if (!AI_READY) {
            this.notification.add(_t("The AI flow builder is coming soon."), { type: "info" });
            return;
        }
        const record = this.props.record;
        this.dialog.add(AiDialog, {
            editing: this.hasDiagram,
            ask: (request) => this.orm.call("dwo.approval.flow", "ai_suggest", [
                record.data.model_id.id,
                record.data.state_mode,
                record.data.state_field_id ? record.data.state_field_id.id : false,
                request,
                this.hasDiagram ? JSON.stringify(this.graph, (key, value) => (key === "cid" ? undefined : value)) : null,
                record.resId || false,
            ]),
            apply: (graph) => {
                this.state.graph = parse(graph);
                this.state.selected = null;
                this.commit();
            },
        });
    }

    loadJson() {
        const record = this.props.record;
        this.dialog.add(JsonDialog, {
            mode: "load",
            load: async (text) => {
                const result = await this.orm.call("dwo.approval.flow", "share_to_graph", [
                    record.data.model_id.id,
                    record.data.state_mode,
                    record.data.state_field_id ? record.data.state_field_id.id : false,
                    text,
                    record.resId || false,
                ]);
                if (result.errors) {
                    return result.errors;
                }
                this.state.graph = parse(result.graph);
                this.state.selected = null;
                this.commit();
                return [];
            },
        });
    }
}

registry.category("fields").add("dwo_flow_designer", {
    component: FlowDesigner,
    displayName: _t("Approval flow designer"),
    supportedTypes: ["text"],
    extractProps: ({ options }) => ({ modelField: options.model_field }),
});
