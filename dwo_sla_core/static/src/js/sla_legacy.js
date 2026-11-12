/*
 * SLA & Escalation, web client of Odoo 12 to 15 (legacy widgets, jQuery).
 *   1. field widget `float_time_unit`   (HH:MM and the unit "h")
 *   2. view widget  `sla_progress`      (card of the SLA task form)
 *   3. view         `sla_definition_form` (asks to confirm a change of conditions on a definition with running tasks)
 *   4. SLA status chip next to the pager of the form of a model that has an SLA
 * Presentation only: the server decides the state and the numbers.
 */
odoo.define('dwo_sla_core.float_time_unit', function (require) {
"use strict";

var core = require('web.core');
var fieldRegistry = require('web.field_registry');
var FieldFloatTime = require('web.basic_fields').FieldFloatTime;
var _t = core._t;

var FieldFloatTimeUnit = FieldFloatTime.extend({
    /**
     * Read-only: "04:30 h". (In edition the input keeps the plain HH:MM: the legacy input field has no room for
     * a label, the unit is in the field label of the form.)
     */
    _renderReadonly: function () {
        this._super.apply(this, arguments);
        this.$el.append($('<span class="text-muted ml-1"/>').text(this.nodeOptions.unit || _t("h")));
    },
});

fieldRegistry.add('float_time_unit', FieldFloatTimeUnit);

return FieldFloatTimeUnit;
});

odoo.define('dwo_sla_core.sla_progress', function (require) {
"use strict";

var core = require('web.core');
var fieldUtils = require('web.field_utils');
var Widget = require('web.Widget');
var widgetRegistry = require('web.widget_registry');
var _t = core._t;

function fmtHours(value) {
    var n = Math.round((value || 0) * 10) / 10;
    return (n % 1 === 0 ? n.toFixed(0) : n.toFixed(1)) + 'h';
}

var SlaProgress = Widget.extend({
    className: 'o_sla_progress_widget',

    init: function (parent, record) {
        this._super.apply(this, arguments);
        this.d = record.data;
    },
    start: function () {
        this._render();
        return this._super.apply(this, arguments);
    },
    updateState: function (state) {
        this.d = state.data;
        this._render();
    },

    _status: function () {
        var d = this.d;
        var STATUS = {
            cancelled: {label: _t("Cancelled"), icon: "fa-ban", color: "secondary"},
            paused: {label: _t("Paused"), icon: "fa-pause-circle", color: "warning"},
            achieved: {label: _t("Achieved on time"), icon: "fa-check-circle", color: "success"},
            breached_done: {label: _t("Completed late"), icon: "fa-exclamation-circle", color: "danger"},
            breaching: {label: _t("Breaching now"), icon: "fa-bolt", color: "danger"},
            due_soon: {label: _t("Due soon"), icon: "fa-hourglass-half", color: "warning"},
            on_track: {label: _t("On track"), icon: "fa-play-circle", color: "info"}
        };
        var key = "on_track";
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
        return _.extend({key: key}, STATUS[key]);
    },

    _milestone: function (value) {
        if (!value) {
            return null;
        }
        return {
            absolute: fieldUtils.format.datetime(value, {type: 'datetime'}, {timezone: true}),
            relative: value.fromNow()
        };
    },

    _milestoneHtml: function (icon, label, milestone, emptyText) {
        var $m = $('<div class="o_sla_progress_milestone"/>');
        $m.append($('<i class="fa text-muted mr-1"/>').addClass(icon));
        $m.append($('<span class="o_sla_progress_milestone_label"/>').text(label));
        if (milestone) {
            $m.append($('<div class="o_sla_progress_milestone_value"/>').text(milestone.absolute));
            $m.append($('<div class="o_sla_progress_milestone_relative text-muted"/>').text(milestone.relative));
        } else {
            $m.append($('<div class="o_sla_progress_milestone_value text-muted"/>').text(emptyText));
        }
        return $m;
    },

    _render: function () {
        var d = this.d;
        var st = this._status();
        var percent = Math.max(d.business_percent_used || 0, 0);
        var over = Math.max(percent - 100, 0);
        var asMultiplier = percent > 300;
        var headline = asMultiplier ? 100 : percent;
        var used = d.stage === "in_progress" ? (percent / 100) * (d.target_duration || 0) : (d.business_duration || 0);
        var schedule = d.schedule_id && d.schedule_id.data ? d.schedule_id.data.display_name : false;

        var $card = $('<div class="o_sla_progress_card"/>').addClass('o_sla_progress_card_' + st.key);
        var $head = $('<div class="o_sla_progress_head"/>').appendTo($card);
        $('<span class="o_sla_progress_badge badge badge-pill"/>').addClass('badge-' + st.color)
            .append($('<i class="fa mr-1"/>').addClass(st.icon)).append(document.createTextNode(st.label)).appendTo($head);
        var $pct = $('<span class="o_sla_progress_percent"/>').addClass('text-' + st.color)
            .text(headline + '%').appendTo($head);
        if (over > 0 && !asMultiplier) {
            $('<small class="o_sla_progress_over"/>').attr('title', _t("Over the target time"))
                .text(' (+' + over + '%)').appendTo($pct);
        }
        if (asMultiplier) {
            $('<small class="o_sla_progress_over"/>').attr('title', _t("Business time used, as a multiple of the target"))
                .text(' (' + (percent / 100).toFixed(1) + '× ' + _t("over target") + ')').appendTo($pct);
        }

        var $track = $('<div class="o_sla_progress_track"/>').appendTo($card);
        $('<div class="o_sla_progress_target_line"/>').attr('title', _t("100% of target")).appendTo($track);
        $('<div class="o_sla_progress_fill"/>').addClass('bg-' + st.color)
            .css('width', Math.min(percent, 100) + '%').appendTo($track);
        if (over > 0) {
            $('<div class="o_sla_progress_overflow bg-danger"/>').attr('title', _t("Running over target")).appendTo($track);
        }

        var $miles = $('<div class="o_sla_progress_milestones"/>').appendTo($card);
        $miles.append(this._milestoneHtml('fa-flag-checkered', _t("Start"), this._milestone(d.start_time), '—'));
        $miles.append(this._milestoneHtml('fa-bullseye', _t("Deadline"),
            this._milestone(d.planned_end_time || d.original_breach_time), '—'));
        $miles.append(this._milestoneHtml('fa-check-square-o', _t("End"), this._milestone(d.end_time), _t("In progress")));

        var $foot = $('<div class="o_sla_progress_foot text-muted"/>').appendTo($card);
        $('<span class="o_sla_progress_foot_item"/>').append($('<i class="fa fa-clock-o mr-1"/>'))
            .append(document.createTextNode(fmtHours(used) + ' / ' + fmtHours(d.target_duration) + ' ' + _t("worked"))).appendTo($foot);
        if ((d.business_pause_duration || 0) > 0) {
            $('<span class="o_sla_progress_foot_item"/>').append($('<i class="fa fa-pause mr-1"/>'))
                .append(document.createTextNode(fmtHours(d.business_pause_duration) + ' ' + _t("paused"))).appendTo($foot);
        }
        $('<span class="o_sla_progress_foot_item"/>').append($('<i class="fa fa-calendar-o mr-1"/>'))
            .append(document.createTextNode(schedule || _t("24/7 (no calendar)"))).appendTo($foot);

        this.$el.empty().append($card);
    }
});

widgetRegistry.add('sla_progress', SlaProgress);

return SlaProgress;
});

odoo.define('dwo_sla_core.definition_form', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var FormController = require('web.FormController');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');
var _t = core._t;

// Fields whose change applies immediately to tasks that are already running
var RUNNING_TASK_FIELDS = ["start_domain", "cancel_domain", "pause_domain", "resume_domain", "stop_domain",
    "reset_domain", "cancel_mode", "resume_mode"];

var SlaDefinitionFormController = FormController.extend({
    /**
     * Asks for a confirmation before saving a change of the conditions of a definition that has running tasks.
     * Saving is not blocked: the user can confirm, or keep editing (the record is not discarded).
     */
    saveRecord: function () {
        var self = this;
        var args = arguments;
        var superSave = this._super.bind(this);
        var local = this.model.localData[this.handle] || {};
        var changes = local._changes || {};
        var running = this.model.get(this.handle).data.running_task_count;
        if (!running || !RUNNING_TASK_FIELDS.some(function (name) { return name in changes; })) {
            return superSave.apply(this, args);
        }
        // Odoo 12: `saveRecord` returns a jQuery Deferred (`.always` is called on it), not a native Promise
        var def = $.Deferred();
        (function (resolve) {
            var confirmed = false;
            new Dialog(self, {
                title: _t("Change conditions?"),
                size: 'medium',
                $content: $('<div/>').text(_.str.sprintf(_t(
                    "%(count)s task(s) are running or paused under this SLA. The new conditions apply to them at their next evaluation, so some may be stopped, cancelled or paused."),
                    {count: running})),
                buttons: [
                    {text: _t("Save"), classes: 'btn-primary', close: true, click: function () { confirmed = true; }},
                    {text: _t("Keep editing"), close: true},
                ],
                // the dialog is closed after the click handlers (or by the user): decide here
            }).on('closed', null, function () {
                $.when(confirmed ? superSave.apply(self, args) : []).then(resolve, function () { def.reject(); });
            }).open();
        })(function () { def.resolve.apply(def, arguments); });
        return def.promise();
    },
});

var SlaDefinitionFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {Controller: SlaDefinitionFormController}),
});

viewRegistry.add('sla_definition_form', SlaDefinitionFormView);

return SlaDefinitionFormView;
});

odoo.define('dwo_sla_core.form_chip', function (require) {
"use strict";

var core = require('web.core');
var FormController = require('web.FormController');
var session = require('web.session');
var _t = core._t;

var STATE_META = {
    running: {icon: "fa-play-circle", cls: "o_sla_status_running"},
    due_soon: {icon: "fa-hourglass-half", cls: "o_sla_status_due_soon"},
    paused: {icon: "fa-pause-circle", cls: "o_sla_status_paused"},
    breached: {icon: "fa-bolt", cls: "o_sla_status_breached"},
    met: {icon: "fa-check-circle", cls: "o_sla_status_met"},
    missed: {icon: "fa-exclamation-circle", cls: "o_sla_status_missed"}
};

/** "2h 15m" / "3d 4h" / "12m" for a positive duration in minutes. */
function formatLate(minutes) {
    var days = Math.floor(minutes / 1440);
    var hours = Math.floor((minutes % 1440) / 60);
    var mins = Math.floor(minutes % 60);
    if (days) {
        return days + "d " + hours + "h";
    }
    return hours ? hours + "h " + mins + "m" : mins + "m";
}

/** "16:30", "tomorrow 09:00" or "Mar 5 09:00" (browser timezone). */
function formatDue(dt, now) {
    var time = dt.format("HH:mm");
    if (dt.isSame(now, "day")) {
        return time;
    }
    if (dt.isSame(now.clone().add(1, "days"), "day")) {
        return _t("tomorrow") + " " + time;
    }
    return dt.format("MMM D") + " " + time;
}

function detail(summary) {
    var planned = summary.planned_end_time ? moment.utc(summary.planned_end_time).local() : null;
    var now = moment();
    switch (summary.state) {
        case "running":
            return summary.percent + "%";
        case "paused":
            return _t("Paused") + " " + summary.percent + "%";
        case "due_soon":
            return planned ? _t("Due") + " " + formatDue(planned, now) : _t("Due soon");
        case "breached":
            if (summary.count > 1) {
                return summary.late_count + " " + _t("late");
            }
            if (!planned) {
                return _t("Late");
            }
            return _t("Late") + " " + formatLate(Math.max(Math.floor(now.diff(planned, "minutes")), 0));
        case "met":
            return _t("Met");
        default:
            return summary.late_count + " " + _t("missed");
    }
}

FormController.include({
    destroy: function () {
        this._dwoRemoveChip();
        this._super.apply(this, arguments);
    },

    _update: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function (result) {
            self._dwoLoadChip();
            return result;
        });
    },

    _dwoRemoveChip: function () {
        if (this._dwoChip) {
            this._dwoChip.remove();
            this._dwoChip = null;
        }
    },

    /** Not awaited by `_update`: a secondary RPC must never delay the form. */
    _dwoLoadChip: function () {
        var self = this;
        var models = session.dwo_sla_models || [];
        var state = this.handle && this.model.get(this.handle);
        var resId = state && state.res_id;
        if (!resId || models.indexOf(this.modelName) < 0 || $(this.el).closest('.modal').length) {
            this._dwoRemoveChip();
            return;
        }
        var token = this._dwoToken = (this._dwoToken || 0) + 1;
        this._rpc({
            model: 'sla.task', method: 'get_record_sla_summary', args: [this.modelName, resId],
        }).then(function (summary) {
            if (token === self._dwoToken) {
                self._dwoShowChip(summary);
            }
        }, function (error, event) {
            if (event && event.preventDefault) { event.preventDefault(); }  // e.g. no access: no chip
            self._dwoRemoveChip();
        });
    },

    _dwoShowChip: function (summary) {
        var self = this;
        this._dwoRemoveChip();
        if (!summary || !summary.state) {
            return;
        }
        var meta = STATE_META[summary.state];
        var showCount = summary.count > 1 && ["met", "missed"].indexOf(summary.state) < 0;
        var label = "SLA" + (showCount ? " " + summary.count : "") + " · " + detail(summary);
        var lines = (summary.lines || []).map(function (line) {
            var tail = ["running", "paused"].indexOf(line.state) >= 0 ? " " + line.percent + "%" : "";
            return line.name + ": " + line.state.replace("_", " ") + tail;
        });
        var $chip = $('<button type="button" class="o_sla_status_chip btn btn-sm ml-2"/>').addClass(meta.cls)
            .attr('title', lines.join("\n"));
        $chip.append($('<i class="fa mr-1"/>').addClass(meta.icon));
        $chip.append($('<span class="o_sla_status_label"/>').text(label));
        if (["running", "due_soon", "paused", "breached"].indexOf(summary.state) >= 0) {
            var width = summary.state === "breached" ? 100 : summary.percent;
            $chip.append($('<span class="o_sla_status_bar"/>').append(
                $('<span class="o_sla_status_bar_fill"/>').css('width', width + '%')));
        }
        $chip.on('click', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            self.do_action({
                type: 'ir.actions.act_window',
                name: _t("SLA Tasks"),
                res_model: 'sla.task',
                views: [[false, 'list'], [false, 'form']],
                domain: [['res_model', '=', self.modelName], ['res_id', '=', self.model.get(self.handle).res_id]],
                context: {},
            });
        });
        var $pager = $('.o_control_panel .o_cp_pager').first();
        if ($pager.length) {
            $chip.insertBefore($pager);
        } else {
            $chip.appendTo($('.o_control_panel .o_cp_right, .o_control_panel').first());
        }
        this._dwoChip = $chip;
    },
});

});
