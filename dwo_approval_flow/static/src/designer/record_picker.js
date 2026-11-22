/** @odoo-module **/
import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Pick one record, or several, of a model: a small search box with a list under it.
 * (Odoo 16 has no RecordSelector.) Props: resModel, resId | resIds + multi, domain, update(id | ids).
 */
export class RecordPicker extends Component {
    static template = "dwo_approval_flow.RecordPicker";
    static props = {
        resModel: String,
        resId: { type: [Number, Boolean], optional: true },
        resIds: { type: Array, optional: true },
        multi: { type: Boolean, optional: true },
        domain: { type: Array, optional: true },
        update: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ text: "", options: [], open: false, names: {} });
        onWillStart(() => this.loadNames(this.props));
        onWillUpdateProps((next) => this.loadNames(next));
    }

    idsOf(props) {
        return props.multi ? props.resIds || [] : props.resId ? [props.resId] : [];
    }

    get selected() {
        return this.idsOf(this.props).map((id) => ({ id, name: this.state.names[id] || "…" }));
    }

    async loadNames(props) {
        const missing = this.idsOf(props).filter((id) => !(id in this.state.names));
        if (!missing.length) {
            return;
        }
        const rows = await this.orm.call(props.resModel, "name_get", [missing]);
        for (const [id, name] of rows) {
            this.state.names[id] = name;
        }
    }

    async search(ev) {
        this.state.text = ev.target.value;
        this.state.open = true;
        const rows = await this.orm.call(this.props.resModel, "name_search", [], {
            name: this.state.text,
            args: this.props.domain || [],
            limit: 8,
        });
        const taken = this.idsOf(this.props);
        this.state.options = rows.filter(([id]) => !taken.includes(id));
    }

    pick(id, name) {
        this.state.names[id] = name;
        if (this.props.multi) {
            this.props.update([...this.idsOf(this.props), id]);
        } else {
            this.props.update(id);
        }
        this.state.text = "";
        this.state.open = false;
    }

    remove(id) {
        if (this.props.multi) {
            this.props.update(this.idsOf(this.props).filter((x) => x !== id));
        } else {
            this.props.update(false);
        }
    }

    closeLater() {
        setTimeout(() => (this.state.open = false), 150);
    }
}
