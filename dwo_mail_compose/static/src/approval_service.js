/* @odoo-module */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Screen notification when somebody asks for the approval of an email, or decides on yours.
 * The server sends "dwo_mail_approval" on the bus channel of each person concerned; the
 * notification has a button that opens the page of the email.
 */
export const dwoApprovalService = {
    dependencies: ["bus_service", "notification", "action"],

    start(env, { bus_service, notification, action }) {
        // Odoo 16 has no bus_service.subscribe: every notification of the bus goes through one event
        bus_service.addEventListener("notification", ({ detail: notifications }) => {
          for (const { type, payload } of notifications) {
            if (type !== "dwo_mail_approval") {
                continue;
            }
            const buttons = [];
            if (payload.email_id && payload.kind !== "closed") {
                buttons.push({
                    name: _t("Open the email"),
                    primary: true,
                    onClick: () =>
                        action.doAction({
                            type: "ir.actions.act_window",
                            res_model: "dwo.mail.email",
                            res_id: payload.email_id,
                            views: [[false, "form"]],
                            target: "current",
                        }),
                });
            }
            const message = payload.comment ? `${payload.message}\n"${payload.comment}"` : payload.message;
            notification.add(message, {
                title: payload.title,
                type: payload.kind === "rejected" ? "warning" : "info",
                sticky: true,
                buttons,
            });
          }
        });
    },
};

registry.category("services").add("dwo_mail_approval", dwoApprovalService);
