/** @odoo-module **/

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

const debugRegistry = registry.category("debug");

function splitSeparator({ action }) {
    if (!action.id || !action.res_model) {
        return null;
    }
    return {
        type: "separator",
        sequence: 225,
    };
}

function createViewSplit({ action, env }) {
    if (!action.id) {
        return null;
    }
    const description = env._t("⚡ Create View: Split");
    return {
        type: "item",
        description,
        callback: async () => {
            // editModelDebug(env, description, action.type, action.id);
            // const modelId = (
            //     await env.services.orm.search("ir.model", [["model", "=", action.res_model]], {
            //         limit: 1,
            //     })
            // )[0];
            env.services.action.doAction({
                res_model: "create.view.split.wizard",
                name: description,
                views: [[false, "form"]],
                // domain: [["model_id", "=", modelId]],
                type: "ir.actions.act_window",
                target: 'new',
                context: {
                    default_action_id: action.id,
                    default_res_model: action.res_model,
                },
            });
        },
        sequence: 228,
    };
}

function removeViewSplit({ action, env }) {
    return {
        type: "item",
        description: env._t("❌ Remove View: Split"),
        callback: async () => {
            await env.services.orm.call("create.view.split.wizard", 'remove_split_view_from_action_window', [], {
                action_window_id: action.id
            });
            browser.location.reload();
        },
        sequence: 229,
    };
}

debugRegistry
    .category("action")
    .add("splitSeparator", splitSeparator)
    .add("createViewSplit", createViewSplit)
    .add("removeViewSplit", removeViewSplit);
