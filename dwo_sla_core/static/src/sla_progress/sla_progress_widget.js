/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { formatDateTime } from "@web/core/l10n/dates";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

import { Component } from "@odoo/owl";

const { DateTime } = luxon;

/**
 * Rich visual timeline/progress card for `sla.task`.
 *
 * Replaces the plain `business_percent_used` progressbar with a status
 * chip, a capped-and-striped progress bar (so a heavily overdue task shows
 * "+187%" instead of an unreadable "27807%"/unusably wide bar) and a
 * three-point milestone row (Start / Deadline / End). Pure presentation:
 * every number it shows already exists on the record, nothing is
 * recomputed or guessed.
 */
export class SlaProgressWidget extends Component {
    static template = "dwo_sla_core.SlaProgressWidget";
    static props = { ...standardWidgetProps };

    get data() {
        return this.props.record.data;
    }

    get statusMeta() {
        const d = this.data;
        const STATUS = {
            cancelled: { label: _t("Cancelled"), icon: "fa-ban", color: "secondary" },
            paused: { label: _t("Paused"), icon: "fa-pause-circle", color: "warning" },
            achieved: { label: _t("Achieved on time"), icon: "fa-check-circle", color: "success" },
            breached_done: { label: _t("Completed late"), icon: "fa-exclamation-circle", color: "danger" },
            breaching: { label: _t("Breaching now"), icon: "fa-bolt", color: "danger" },
            due_soon: { label: _t("Due soon"), icon: "fa-hourglass-half", color: "warning" },
            on_track: { label: _t("On track"), icon: "fa-play-circle", color: "info" },
        };
        let key = "on_track";
        if (d.stage === "cancelled") {
            key = "cancelled";
        } else if (d.stage === "paused") {
            key = "paused";
        } else if (d.stage === "achieved") {
            key = "achieved";
        } else if (d.stage === "breached") {
            key = d.end_time ? "breached_done" : "breaching";
        } else if (d.has_breached) {
            key = "breaching";
        } else if (d.is_due_soon) {
            key = "due_soon";
        }
        return { key, ...STATUS[key] };
    }

    get percent() {
        return Math.max(this.data.business_percent_used || 0, 0);
    }
    get barPercent() {
        return Math.min(this.percent, 100);
    }
    get overPercent() {
        return Math.max(this.percent - 100, 0);
    }
    get isOver() {
        return this.overPercent > 0;
    }
    /** Past ~3x the target, "+2900%" stops being readable -- switch to a
     * "7.0x over target" multiplier instead. Same underlying number, shown
     * in a form a human can actually parse at a glance. */
    get overflowAsMultiplier() {
        return this.percent > 300;
    }
    get showPercentOverflow() {
        return this.isOver && !this.overflowAsMultiplier;
    }
    get overflowMultiplier() {
        // Derived from the same live `business_percent_used` the headline
        // number uses (not business_duration/target_duration): while a
        // task is still running, business_duration is only refreshed on
        // pause/resume/complete, so it can lag well behind the live
        // percent and give a misleading ratio.
        return `${(this.percent / 100).toFixed(1)}×`;
    }
    /** Headline number: capped at 100 once we switch to the multiplier
     * badge, so the big colored figure never reads "7000%". */
    get headlinePercent() {
        return this.overflowAsMultiplier ? 100 : this.percent;
    }

    get calendarLabel() {
        const scheduleId = this.data.schedule_id;
        return scheduleId ? scheduleId[1] : _t("24/7 (no calendar)");
    }

    get hasPause() {
        return (this.data.business_pause_duration || 0) > 0;
    }

    /** One decimal, trims a trailing ".0". */
    _fmtHours(value) {
        const n = Math.round((value || 0) * 10) / 10;
        return `${n % 1 === 0 ? n.toFixed(0) : n.toFixed(1)}h`;
    }

    /** `business_duration` is only persisted on pause/resume/complete, so
     * while a task is still running it can read stale (e.g. "0h worked" on
     * a task that is well past its deadline). Derive a live estimate from
     * the same percent the rest of the card already shows instead, so the
     * numbers never visibly contradict each other. */
    get businessUsedHours() {
        if (this.data.stage === "in_progress") {
            return (this.percent / 100) * (this.data.target_duration || 0);
        }
        return this.data.business_duration || 0;
    }
    get businessUsedLabel() {
        return `${this._fmtHours(this.businessUsedHours)} / ${this._fmtHours(this.data.target_duration)}`;
    }
    get pauseLabel() {
        return this._fmtHours(this.data.business_pause_duration);
    }

    _milestone(fieldValue) {
        if (!fieldValue) {
            return null;
        }
        const dt = fieldValue instanceof DateTime ? fieldValue : DateTime.fromISO(fieldValue);
        return {
            absolute: formatDateTime(dt, { format: "dd MMM yyyy HH:mm" }),
            relative: dt.toRelative(),
        };
    }
    get startMilestone() {
        return this._milestone(this.data.start_time);
    }
    get deadlineMilestone() {
        return this._milestone(this.data.planned_end_time || this.data.original_breach_time);
    }
    get endMilestone() {
        return this._milestone(this.data.end_time);
    }
}

export const slaProgressWidget = {
    component: SlaProgressWidget,
    fieldDependencies: [
        { name: "stage", type: "selection" },
        { name: "has_breached", type: "boolean" },
        { name: "is_due_soon", type: "boolean" },
        { name: "business_percent_used", type: "integer" },
        { name: "business_duration", type: "float" },
        { name: "target_duration", type: "float" },
        { name: "business_pause_duration", type: "float" },
        { name: "start_time", type: "datetime" },
        { name: "planned_end_time", type: "datetime" },
        { name: "original_breach_time", type: "datetime" },
        { name: "end_time", type: "datetime" },
        { name: "schedule_id", type: "many2one" },
    ],
};

registry.category("view_widgets").add("sla_progress", slaProgressWidget);
