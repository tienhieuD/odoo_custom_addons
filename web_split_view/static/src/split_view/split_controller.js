/** @odoo-module **/

import { Component, onWillStart, onWillUnmount, useRef, useState, useSubEnv } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { CallbackRecorder, useSetupAction } from "@web/webclient/actions/action_hook";
import { Layout } from "@web/search/layout";
import { standardViewProps } from "@web/views/standard_view_props";
import { View } from "@web/views/view";

const MIN_WIDTH = 15; // % of the available width, for each side

export class SplitController extends Component {
    static template = "web_split_view.SplitView";
    static components = { Layout, View };
    static props = {
        ...standardViewProps,
        archInfo: Object,
        buttonTemplate: String,
    };

    setup() {
        this.orm = useService("orm");
        this.viewService = useService("view");
        this.rootRef = useRef("root");
        this.splitRef = useRef("split");

        this.state = useState({
            // id of the record shown on the right; `false` + `mode: "new"` = new record
            activeId: false,
            mode: "empty", // "empty" | "record" | "new"
            formKey: 0,
            listKey: 0,
            loading: false,
            leftWidth: this.restoreWidth(),
        });

        // everything the embedded form registers for "before leaving" (save / discard dirty record)
        this.formBeforeLeave = new CallbackRecorder();
        useSetupAction({ beforeLeave: () => this.canLeaveForm() });

        useSubEnv({
            splitState: this.state,
            // the embedded views must not hijack the breadcrumbs / display name of the action
            config: {
                ...this.env.config,
                noBreadcrumbs: true,
                setDisplayName: () => {},
                historyBack: () => this.onFormClosed(),
            },
        });

        onWillStart(async () => {
            const { listRef, formRef, listArch, formArch } = this.props.archInfo;
            [this.listViewProps, this.formViewBaseProps] = await Promise.all([
                this.buildSubViewProps("list", listRef, listArch),
                this.buildSubViewProps("form", formRef, formArch),
            ]);
        });

        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
        onWillUnmount(() => this.stopResize());
    }

    // ------------------------------------------------------------------ sub views
    async buildSubViewProps(type, ref, arch) {
        const props = { resModel: this.props.resModel, type };
        if (arch) {
            // inline arch: we only need the fields of the model, the arch is ours
            const { fields, relatedModels } = await this.loadModelFields(arch);
            return { ...props, arch, fields, relatedModels };
        }
        const viewId = ref ? await this.orm.call("base", "get_id_by_xmlid", [ref]) : false;
        return { ...props, viewId: viewId || undefined };
    }

    /** `fields_get` result, with the `name` key the view parsers expect on each field. */
    async getFields(model) {
        const fields = await this.orm.call(model, "fields_get", [], {});
        for (const [name, field] of Object.entries(fields)) {
            field.name = name;
        }
        return fields;
    }

    /**
     * Fields (and comodels' fields) needed by an inline arch. The default view of the model
     * cannot be used: it only returns the fields it displays itself.
     */
    async loadModelFields(arch) {
        const resModel = this.props.resModel;
        const fields = await this.getFields(resModel);
        const names = new Set(
            [...new DOMParser().parseFromString(arch, "text/xml").getElementsByTagName("field")].map(
                (el) => el.getAttribute("name")
            )
        );
        const comodels = new Set(
            [...names].map((name) => fields[name]?.relation).filter((rel) => rel && rel !== resModel)
        );
        const relatedModels = { [resModel]: fields };
        await Promise.all(
            [...comodels].map(async (model) => {
                relatedModels[model] = await this.getFields(model);
            })
        );
        return { fields, relatedModels };
    }

    get layoutDisplay() {
        // only keep breadcrumbs + buttons in the main control panel: search/filter/pager live in the list
        return { ...this.props.display, controlPanel: { layoutActions: false } };
    }

    get listProps() {
        return {
            ...this.listViewProps,
            context: this.props.context,
            domain: this.props.domain,
            display: { searchPanel: false },
            loadIrFilters: true,
            searchViewId: false,
            allowOpenAction: false,
            noBreadcrumbs: true,
            showButtons: false,
            selectRecord: (resId) => this.onSelectRecord(resId),
        };
    }

    get formProps() {
        return {
            ...this.formViewBaseProps,
            context: this.props.context,
            resId: this.state.mode === "new" ? false : this.state.activeId,
            display: { controlPanel: { layoutActions: false } },
            noBreadcrumbs: true,
            onSave: (record) => this.onFormSaved(record),
            onDiscard: (record) => this.onFormDiscarded(record),
            __beforeLeave__: this.formBeforeLeave,
        };
    }

    // ------------------------------------------------------------------ record selection
    /** Ask the embedded form to save/discard its pending changes; `false` = stay on the current record. */
    async canLeaveForm() {
        const results = await Promise.all(this.formBeforeLeave.callbacks.map((cb) => cb()));
        return !results.includes(false);
    }

    async onSelectRecord(resId) {
        if (!(await this.canLeaveForm())) {
            return;
        }
        this.state.activeId = resId;
        this.state.mode = "record";
        this.state.formKey++;
    }

    async onCreate() {
        if (!(await this.canLeaveForm())) {
            return;
        }
        this.state.activeId = false;
        this.state.mode = "new";
        this.state.formKey++;
    }

    async onReload() {
        this.state.loading = true;
        this.state.listKey++; // remounts the list: reloads its data
        if (this.state.mode === "record") {
            this.state.formKey++;
        }
        browser.setTimeout(() => (this.state.loading = false), 300);
    }

    onFormSaved(record) {
        // a new record becomes the active one; the list is reloaded to show the change
        if (this.state.mode === "new" && record.resId) {
            this.state.activeId = record.resId;
            this.state.mode = "record";
        }
        this.state.listKey++;
    }

    onFormDiscarded(record) {
        if (this.state.mode === "new") {
            this.onFormClosed();
        }
    }

    /** form closed itself (new record discarded, record deleted...) */
    onFormClosed() {
        this.state.activeId = false;
        this.state.mode = "empty";
        this.state.listKey++;
    }

    // ------------------------------------------------------------------ resizer
    get storageKey() {
        return `web_split_view_${this.env.config.viewId || "default"}`;
    }

    restoreWidth() {
        try {
            const value = parseFloat(browser.localStorage.getItem(this.storageKey));
            if (value >= MIN_WIDTH && value <= 100 - MIN_WIDTH) {
                return value;
            }
        } catch {
            // localStorage unavailable
        }
        return 50;
    }

    startResize(ev) {
        ev.preventDefault();
        this.resizing = true;
        document.addEventListener("mousemove", this.onMouseMove);
        document.addEventListener("mouseup", this.onMouseUp);
        this.splitRef.el?.classList.add("split_resizing");
    }

    onMouseMove(ev) {
        const rect = this.splitRef.el.getBoundingClientRect();
        const percent = ((ev.clientX - rect.left) / rect.width) * 100;
        this.state.leftWidth = Math.min(100 - MIN_WIDTH, Math.max(MIN_WIDTH, percent));
    }

    onMouseUp() {
        this.stopResize();
        try {
            browser.localStorage.setItem(this.storageKey, String(this.state.leftWidth));
        } catch {
            // localStorage unavailable
        }
    }

    stopResize() {
        if (!this.resizing) {
            return;
        }
        this.resizing = false;
        document.removeEventListener("mousemove", this.onMouseMove);
        document.removeEventListener("mouseup", this.onMouseUp);
        this.splitRef.el?.classList.remove("split_resizing");
    }

    get placeholder() {
        return _t("Select an item from the list to display details.");
    }
}
