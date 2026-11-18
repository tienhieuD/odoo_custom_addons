/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

// Approvers (online) see a toast for every session approval or PIN reset request, with Approve and Reject.
export const dwoApprovalToast = {
    dependencies: ["bus_service", "notification", "orm"],
    start(env, { bus_service, notification, orm }) {
        bus_service.subscribe("dwo_session/request", (payload) => {
            const decide = (method) => async () => {
                await orm.call("dwo.session.request", method, [[payload.id]]);
            };
            notification.add(payload.message, {
                type: "warning",
                sticky: true,
                title: payload.kind === "login" ? _t("Session approval") : _t("PIN reset request"),
                buttons: [
                    { name: _t("Approve"), primary: true, onClick: decide("action_approve") },
                    { name: _t("Reject"), onClick: decide("action_reject") },
                ],
            });
        });
    },
};

registry.category("services").add("dwo_approval_toast", dwoApprovalToast);
