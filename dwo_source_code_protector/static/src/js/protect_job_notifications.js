/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";

/**
 * Lắng nghe kênh bus "dwo_protect_job-<uid>" (server gửi khi một job trong dwo.protect.job
 * kết thúc, xem models/dwo_protect_job.py::_notify_user), hiện toast thành công/thất bại kèm
 * nút mở lại màn hình job — hiện được NGAY CẢ KHI người dùng đang ở màn hình khác.
 *
 * Odoo 16's bus_service has NO subscribe()/auto-subscribe-to-own-partner-channel (that only
 * exists from 17 onward) -- it exposes addChannel()/addEventListener() instead, and the
 * server must target an explicit channel string the client opts into itself. Matches
 * _dwo_protect_job_channel() server-side exactly.
 */
const dwoProtectJobNotificationService = {
    dependencies: ["bus_service", "notification", "action"],
    start(env, { bus_service, notification, action }) {
        const channel = "dwo_protect_job-" + session.uid;
        bus_service.addEventListener("notification", ({ detail: notifications }) => {
            for (const { type, payload } of notifications) {
                if (type !== "dwo_protect_job") {
                    continue;
                }
                const { job_id, name, success, error_message } = payload;
                notification.add(
                    success
                        ? _t("%s was protected successfully.", name)
                        : _t("%(name)s failed: %(error)s", { name, error: error_message || "" }),
                    {
                        type: success ? "success" : "danger",
                        sticky: true,
                        title: success ? _t("Source Code Protector") : _t("Source Code Protector — Error"),
                        buttons: [
                            {
                                name: _t("View"),
                                onClick: () =>
                                    action.doAction({
                                        type: "ir.actions.act_window",
                                        res_model: "dwo.protect.job",
                                        res_id: job_id,
                                        views: [[false, "form"]],
                                        target: "current",
                                    }),
                            },
                        ],
                    }
                );
            }
        });
        bus_service.addChannel(channel);
    },
};

registry.category("services").add("dwo_protect_job_notifications", dwoProtectJobNotificationService);
