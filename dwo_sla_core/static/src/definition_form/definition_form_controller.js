/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";

// Fields whose change applies immediately to tasks that are already running
// (they are not snapshotted on the task). Refs: plan-improvement-sla-01-review 6.14
const RUNNING_TASK_FIELDS = [
    "start_domain",
    "cancel_domain",
    "pause_domain",
    "resume_domain",
    "stop_domain",
    "reset_domain",
    "cancel_mode",
    "resume_mode",
];

/**
 * Ask for confirmation before saving a change to the conditions of an SLA
 * definition that has running tasks. Saving is not blocked: the user can
 * confirm, or cancel and keep editing (the record is not discarded).
 */
export class SlaDefinitionFormController extends FormController {
    async onWillSaveRecord(record, changes) {
        const runningCount = record.data.running_task_count;
        if (!runningCount || !RUNNING_TASK_FIELDS.some((name) => name in changes)) {
            return true;
        }
        return new Promise((resolve) => {
            this.dialogService.add(ConfirmationDialog, {
                title: _t("Change conditions?"),
                body: _t(
                    "%(count)s task(s) are running or paused under this SLA. The new conditions apply to them at their next evaluation, so some may be stopped, cancelled or paused.",
                    { count: runningCount }
                ),
                confirmLabel: _t("Save"),
                cancelLabel: _t("Keep editing"),
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });
    }
}

export const slaDefinitionFormView = {
    ...formView,
    Controller: SlaDefinitionFormController,
};

registry.category("views").add("sla_definition_form", slaDefinitionFormView);
