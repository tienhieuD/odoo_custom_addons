/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { FormController } from "@web/views/form/form_controller";
import { useEffect } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.dwoExpiryOrm = useService("orm");
        this.dwoExpiryNotification = useService("notification");
        this.dwoExpiryAction = useService("action");
        this.dwoExpiryLastKey = null;

        useEffect(
            () => {
                const root = this.model?.root;
                if (!root || root.isNew || !root.resModel || !root.resId) {
                    return;
                }
                const key = `${root.resModel}:${root.resId}`;
                if (this.dwoExpiryLastKey === key) {
                    return;
                }
                this.dwoExpiryLastKey = key;
                this._showExpiryFormAlerts(root.resModel, root.resId);
            },
            () => [
                this.model?.root?.resModel ?? null,
                this.model?.root?.resId ?? null,
                this.model?.root?.isNew ?? null,
            ]
        );
    },

    async _dismissExpiryFor(minutes, label) {
        await this.dwoExpiryOrm.call("res.users", "action_set_expiry_dismiss", [minutes]);
        this.dwoExpiryNotification.add(label, { type: "info" });
    },

    _openExpiryRecords() {
        this.dwoExpiryAction.doAction({
            type: "ir.actions.act_window",
            name: _t("Expiry Records"),
            res_model: "dwo.expiry.record",
            view_mode: "tree,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["rule_user_id", "=", odoo.session_info?.uid || false]],
            target: "current",
        });
    },

    _buildAlertButtons() {
        return [
            {
                name: _t("View All"),
                onClick: () => this._openExpiryRecords(),
                primary: true,
            },
            {
                name: _t("Dismiss 5 min"),
                onClick: () => this._dismissExpiryFor(5, _t("Dismissed for 5 minutes.")),
            },
            {
                name: _t("Dismiss 1 hour"),
                onClick: () => this._dismissExpiryFor(60, _t("Dismissed for 1 hour.")),
            },
            {
                name: _t("Dismiss 1 day"),
                onClick: () => this._dismissExpiryFor(1440, _t("Dismissed for 1 day.")),
            },
            {
                name: _t("Dismiss 7 days"),
                onClick: () => this._dismissExpiryFor(10080, _t("Dismissed for 7 days.")),
            },
            {
                name: _t("Dismiss 30 days"),
                onClick: () => this._dismissExpiryFor(43200, _t("Dismissed for 30 days.")),
            },
        ];
    },

    async _showExpiryFormAlerts(modelName, resId) {
        let payload;
        try {
            payload = await this.dwoExpiryOrm.call("dwo.expiry.rule", "get_form_view_alerts", [modelName, resId]);
        } catch (e) {
            if (odoo.debug) {
                console.warn("[dwo_expiry] Form alerts RPC failed:", e);
            }
            return;
        }
        const alerts = payload && payload.alerts ? payload.alerts : [];
        if (!alerts.length) {
            return;
        }

        // Summarize all alerts into one notification
        const expiredCount = alerts.filter((a) => a.state === "expired").length;
        const upcomingCount = alerts.filter((a) => a.state === "upcoming").length;
        const totalCount = alerts.length + (payload.more_count || 0);
        const hasExpired = expiredCount > 0;

        let message;
        if (totalCount === 1) {
            message = alerts[0].message;
        } else {
            const parts = [];
            if (expiredCount) {
                parts.push(`${expiredCount} expired`);
            }
            if (upcomingCount) {
                parts.push(`${upcomingCount} upcoming`);
            }
            if (payload.more_count) {
                parts.push(`+${payload.more_count} more`);
            }
            message = _t("This record has %s expiry alert(s): %s.", totalCount, parts.join(", "));
        }

        this.dwoExpiryNotification.add(message, {
            title: _t("Expiry Alert"),
            type: hasExpired ? "danger" : "warning",
            sticky: hasExpired,
            buttons: this._buildAlertButtons(),
        });
    },
});
