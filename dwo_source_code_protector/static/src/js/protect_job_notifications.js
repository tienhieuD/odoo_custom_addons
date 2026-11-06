/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Lắng nghe kênh bus "dwo_protect_job" (server gửi khi một job trong
 * dwo.protect.job kết thúc, xem models/dwo_protect_job.py::_notify_user), hiện toast
 * thành công/thất bại kèm nút mở lại màn hình Settings > Source Code Protector — hiện được
 * NGAY CẢ KHI người dùng đang ở màn hình khác (không phải đợi quay lại mới biết).
 */
const dwoProtectJobNotificationService = {
    dependencies: ["bus_service", "notification", "action"],
    start(env, { bus_service, notification, action }) {
        bus_service.subscribe("dwo_protect_job", (payload) => {
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
        });
        // Khong can bus_service.addChannel: server gui qua _sendone(partner, ...), va moi
        // client dang dang nhap da TU DONG duoc subscribe vao dung kenh cua partner minh
        // (xem _build_bus_channel_list trong bus/models/ir_websocket.py cua Odoo). Chi can
        // subscribe() theo ĐÚNG notification_type ("dwo_protect_job") la nhan duoc.
    },
};

registry.category("services").add("dwo_protect_job_notifications", dwoProtectJobNotificationService);
