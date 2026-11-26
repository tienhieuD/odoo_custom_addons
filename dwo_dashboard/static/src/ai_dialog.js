/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { DwoSelect } from "./select";

const EXAMPLES = [
    _t("Add a KPI with the number of orders this month, compared with last month"),
    _t("Add a bar chart of revenue by salesperson below the table"),
    _t("Replace the doughnut by a pie chart and show the percentages"),
];

/** Asks for a change in words. The answer is a proposal: nothing is saved, and "Load into the page" only puts it in the
 * editor, where Save and Discard decide (so does the revision check of the page). */
export class AiDialog extends Component {
    static template = "dwo_dashboard.AiDialog";
    static components = { Dialog, DwoSelect };
    static props = { pageId: Number, spec: Object, datasets: Array, onApply: Function, close: Function };

    setup() {
        this.orm = useService("orm");
        this.examples = EXAMPLES;
        this.state = useState({
            status: null, request: "", extra: "", options: [], busy: false, error: "", errors: [], proposal: null,
        });
        onWillStart(async () => {
            const [status, options] = await Promise.all([
                this.orm.call("dwo.dashboard.ai", "get_status", []),
                this.orm.call("dwo.dashboard.explore", "list_datasets", []),
            ]);
            this.state.status = status;
            this.state.options = options;
        });
    }

    setExtra(ev) {
        this.state.extra = ev.target.value;
    }

    get extraOptions() {
        return this.state.options.map((o) => ({ value: o.ref, label: o.label }));
    }

    get chosen() {
        return [...new Set([...this.props.datasets, ...(this.state.extra ? [this.state.extra] : [])])];
    }

    label(ref) {
        const found = this.state.options.find((o) => o.ref === ref);
        return found ? found.label : ref;
    }

    titleOf(id) {
        const all = [...(this.props.spec.widgets || []), ...((this.state.proposal && this.state.proposal.spec.widgets) || [])];
        const w = all.find((x) => x.id === id);
        return (w && (w.title || w.type)) || id;
    }

    async generate() {
        const s = this.state;
        s.busy = true;
        s.error = "";
        s.errors = [];
        s.proposal = null;
        try {
            const answer = await this.orm.call("dwo.dashboard.ai", "propose", [
                this.props.pageId, s.request, this.chosen, this.props.spec,
            ]);
            if (answer.ok) {
                s.proposal = answer;
            } else {
                s.error = answer.message;
                s.errors = answer.errors || [];
            }
        } catch (error) {
            s.error = (error.data && error.data.message) || _t("The assistant could not be reached.");
        } finally {
            s.busy = false;
        }
    }

    apply() {
        this.props.onApply(this.state.proposal.spec);
        this.props.close();
    }
}
