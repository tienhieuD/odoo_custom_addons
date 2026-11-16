/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { Component, onWillStart, proxy, useProps } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { booleanField, BooleanField } from "@web/views/fields/boolean/boolean_field";

const ABSOLUTE_URL = /^\s*(?:[a-z][a-z0-9+.-]*:|\/\/)/i;
const DROP_TAGS = "script, iframe, frame, frameset, object, embed, applet, link, meta, base, form, noscript, template";

/**
 * Turns the description of an engine (HTML of ``static/catalog/<module>/index.html``) into the document shown in
 * the popup. Defense in depth: the iframe is sandboxed without scripts, the document carries a policy that allows
 * nothing but the pictures of the catalog folder, and the markup is cleaned (no script, no event handler, no remote
 * picture, no link away).
 */
export function dwoAttPreviewCatalogDoc(html, baseUrl, origin = window.location.origin) {
    const doc = new DOMParser().parseFromString(html || "", "text/html");
    doc.querySelectorAll(DROP_TAGS).forEach((el) => el.remove());
    doc.body.querySelectorAll("*").forEach((el) => {
        for (const attr of [...el.attributes]) {
            const name = attr.name.toLowerCase();
            if (name.startsWith("on") || name === "srcdoc" || name === "formaction") {
                el.removeAttribute(attr.name);
            } else if (["src", "srcset", "poster", "background", "data"].includes(name) && ABSOLUTE_URL.test(attr.value)) {
                if (!attr.value.trim().toLowerCase().startsWith("data:image/")) {
                    el.removeAttribute(attr.name);
                }
            } else if (name === "href") {
                el.removeAttribute(attr.name);
            }
        }
    });
    const policy =
        "default-src 'none'; img-src " + origin + baseUrl + " data:; style-src 'unsafe-inline'";
    const style =
        "body{margin:12px 16px;font:14px/1.5 system-ui,-apple-system,'Segoe UI',sans-serif;color:#212529;background:#fff}" +
        "img{max-width:100%;height:auto}h1,h2,h3,h4{line-height:1.25}";
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>" +
        `<meta http-equiv="Content-Security-Policy" content="${policy}">` +
        `<base href="${origin}${baseUrl}">` +
        `<style>${style}</style></head><body>${doc.body.innerHTML}</body></html>`
    );
}

export class EngineStoreDialog extends Component {
    static template = "dwo_attpreview_core.EngineStoreDialog";
    static components = { Dialog };
    // Odoo 20 (Owl 3): props through useProps (info, close), state is a proxy
    props = useProps();

    setup() {
        this.state = proxy({ srcdoc: "" });
        onWillStart(async () => {
            try {
                const response = await fetch(this.props.info.description_url, { credentials: "same-origin" });
                if (response.ok) {
                    this.state.srcdoc = dwoAttPreviewCatalogDoc(await response.text(), this.props.info.base_url);
                }
            } catch {
                // no description: the popup still shows the facts and the link
            }
        });
    }

    get extensions() {
        return this.props.info.extensions.map((e) => "." + e).join(", ");
    }
}

export class EngineBooleanField extends BooleanField {
    static template = "dwo_attpreview_core.EngineBooleanField";

    setup() {
        super.setup();
        this.dialogService = useService("dialog");
    }

    get module() {
        return this.props.name.replace(/^module_/, "");
    }

    get info() {
        const all = this.props.record.data.dwo_attpreview_engines || {};
        return all[this.module];
    }

    get extensions() {
        return (this.info?.extensions || []).map((e) => "." + e).join(" ");
    }

    get stateLabel() {
        return {
            installed: _t("Installed"),
            available: _t("Available"),
        }[this.info?.state] || _t("Not installed");
    }

    get stateClass() {
        return {
            installed: "text-bg-success",
            available: "text-bg-info",
        }[this.info?.state] || "text-bg-secondary";
    }

    onChange(newValue) {
        if (newValue && this.info && this.info.state === "missing") {
            // the module is not in the addons path: Odoo cannot install it. Show what it is and where to get it;
            // the tick does not stay.
            this.state.value = true;
            this.dialogService.add(
                EngineStoreDialog,
                { info: this.info },
                {
                    onClose: () => {
                        this.state.value = false;
                        this.props.record.update({ [this.props.name]: false });
                    },
                }
            );
            return;
        }
        super.onChange(newValue);
    }
}

export const engineBooleanField = {
    ...booleanField,
    component: EngineBooleanField,
    additionalClasses: [...(booleanField.additionalClasses || []), "o_field_boolean"],
};

registry.category("fields").add("dwo_attpreview_engine_boolean", engineBooleanField);
