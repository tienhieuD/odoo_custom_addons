/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { deserializeDateTime } from "@web/core/l10n/dates";
import { session } from "@web/session";
import { FormController } from "@web/views/form/form_controller";

import { Component, onMounted, onWillUpdateProps, useState } from "@odoo/owl";

const { DateTime } = luxon;

// Presentation only: the server decides `state` and caps `percent` at 100.
const STATE_META = {
    running: { icon: "fa-play-circle", cls: "o_sla_status_running" },
    due_soon: { icon: "fa-hourglass-half", cls: "o_sla_status_due_soon" },
    paused: { icon: "fa-pause-circle", cls: "o_sla_status_paused" },
    breached: { icon: "fa-bolt", cls: "o_sla_status_breached" },
    met: { icon: "fa-check-circle", cls: "o_sla_status_met" },
    missed: { icon: "fa-exclamation-circle", cls: "o_sla_status_missed" },
};

/** "2h 15m" / "3d 4h" / "12m" for a positive duration in minutes. */
function formatLate(minutes) {
    const days = Math.floor(minutes / 1440);
    const hours = Math.floor((minutes % 1440) / 60);
    const mins = Math.floor(minutes % 60);
    if (days) {
        return `${days}d ${hours}h`;
    }
    return hours ? `${hours}h ${mins}m` : `${mins}m`;
}

/** "16:30", "tomorrow 09:00" or "Mar 5 09:00" (browser timezone). */
function formatDue(dt, now) {
    const time = dt.toFormat("HH:mm");
    if (dt.hasSame(now, "day")) {
        return time;
    }
    if (dt.hasSame(now.plus({ days: 1 }), "day")) {
        const tomorrow = _t("tomorrow");
        return `${tomorrow} ${time}`;
    }
    return `${dt.toLocaleString({ month: "short", day: "numeric" })} ${time}`;
}

/**
 * Small SLA status chip shown next to the pager of a form whose model is
 * measured by an SLA. Click opens the SLA tasks of the record.
 */
export class SlaStatusChip extends Component {
    static template = "dwo_sla_core.SlaStatusChip";
    static props = { resModel: String, resId: Number, reloadKey: { type: Number, optional: true } };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ summary: null });
        // Not awaited in willStart/willUpdateProps: a secondary RPC must never delay the form.
        onMounted(() => this.load(this.props));
        onWillUpdateProps((next) => {
            if (next.resId !== this.props.resId || next.reloadKey !== this.props.reloadKey) {
                this.load(next);
            }
        });
    }

    async load({ resModel, resId }) {
        let summary = null;
        try {
            summary = await this.orm.call("sla.task", "get_record_sla_summary", [resModel, resId]);
        } catch {
            summary = null; // e.g. no access: the chip simply stays hidden
        }
        if (resId === this.props.resId) {
            this.state.summary = summary;
        }
    }

    get summary() {
        return this.state.summary?.state ? this.state.summary : null;
    }

    get meta() {
        return STATE_META[this.summary.state];
    }

    get hasBar() {
        return ["running", "due_soon", "paused", "breached"].includes(this.summary.state);
    }

    get barWidth() {
        return this.summary.state === "breached" ? 100 : this.summary.percent;
    }

    /** Text after "SLA", e.g. "42%", "Due 16:30", "Late 2h 15m", "1 late". */
    get detail() {
        const { state, count, late_count, percent, planned_end_time } = this.summary;
        const planned = planned_end_time ? deserializeDateTime(planned_end_time) : null;
        const now = DateTime.now();
        // _t() calls are kept out of template literals so the translation export finds them.
        const paused = _t("Paused");
        const due = _t("Due");
        const late = _t("Late");
        const lateCount = _t("late");
        const missed = _t("missed");
        switch (state) {
            case "running":
                return `${percent}%`;
            case "paused":
                return `${paused} ${percent}%`;
            case "due_soon":
                return planned ? `${due} ${formatDue(planned, now)}` : _t("Due soon");
            case "breached": {
                if (count > 1) {
                    return `${late_count} ${lateCount}`;
                }
                if (!planned) {
                    return late;
                }
                const minutes = Math.max(Math.floor(now.diff(planned, "minutes").minutes), 0);
                return `${late} ${formatLate(minutes)}`;
            }
            case "met":
                return _t("Met");
            default:
                return `${late_count} ${missed}`;
        }
    }

    get label() {
        const count = this.summary.count;
        const showCount = count > 1 && !["met", "missed"].includes(this.summary.state);
        return `SLA${showCount ? " " + count : ""} · ${this.detail}`;
    }

    get tooltipInfo() {
        const lines = (this.summary.lines || []).map((line) => {
            const tail = ["running", "paused"].includes(line.state) ? ` ${line.percent}%` : "";
            return `${line.name}: ${line.state.replace("_", " ")}${tail}`;
        });
        return JSON.stringify({ lines });
    }

    openTasks() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("SLA Tasks"),
            res_model: "sla.task",
            views: [[false, "list"], [false, "form"]],
            domain: [["res_model", "=", this.props.resModel], ["res_id", "=", this.props.resId]],
            context: {},
        });
    }
}

// The chip is injected by a template inheritance of web.FormView, with a dynamic
// t-component fed by getters on the prototype: it is NOT added to `static components`
// (subclasses copy that object when the module loads and would not see it).
patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.slaChipState = useState({ key: 0 });
    },
    get SlaStatusChip() {
        return SlaStatusChip;
    },
    get slaChipVisible() {
        return Boolean(
            session.dwo_sla_models?.includes(this.props.resModel) && this.model.root.resId
        );
    },
    async onRecordSaved(record, changes) {
        await super.onRecordSaved(...arguments);
        this.slaChipState.key++;
    },
});
