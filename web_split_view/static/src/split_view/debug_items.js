import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

const debugRegistry = registry.category("debug");

function createViewSplit({ action, env }) {
    if (!action.id || !action.res_model) {
        return null;
    }
    const description = _t("Create View: Split");
    return {
        type: "item",
        description,
        callback: () => {
            env.services.action.doAction({
                res_model: "create.view.split.wizard",
                name: description,
                views: [[false, "form"]],
                type: "ir.actions.act_window",
                target: "new",
                context: {
                    default_action_id: action.id,
                    default_res_model: action.res_model,
                },
            });
        },
        sequence: 228,
        section: "ui",
    };
}

function removeViewSplit({ action, env }) {
    if (!action.id || !(action.view_mode || "").split(",").includes("split")) {
        return null;
    }
    return {
        type: "item",
        description: _t("Remove View: Split"),
        callback: async () => {
            await env.services.orm.call(
                "create.view.split.wizard",
                "remove_split_view_from_action_window",
                [],
                { action_window_id: action.id }
            );
            browser.location.reload();
        },
        sequence: 229,
        section: "ui",
    };
}

debugRegistry
    .category("action")
    .add("createViewSplit", createViewSplit)
    .add("removeViewSplit", removeViewSplit);
