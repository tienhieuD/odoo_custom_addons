import { Component, onWillStart, onWillUnmount, useRef, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { CallbackRecorder, useSetupAction } from "@web/search/action_hook";
import { Layout } from "@web/search/layout";
import { standardViewProps } from "@web/views/standard_view_props";
import { SplitPane } from "./split_pane";

const MIN_WIDTH = 15; // % of the available width, for each side

export class SplitController extends Component {
    static template = "web_split_view.SplitView";
    static components = { Layout, SplitPane };
    static props = {
        ...standardViewProps,
        archInfo: Object,
        buttonTemplate: String,
    };

    setup() {
        this.orm = useService("orm");
        this.viewService = useService("view");
        this.action = useService("action");
        this.rootRef = useRef("root");
        this.splitRef = useRef("split");

        this.state = useState({
            // id of the record shown on the right; `false` + `mode: "new"` = new record
            activeId: false,
            mode: "empty", // "empty" | "record" | "new"
            formKey: 0,
            listKey: 0,
            leftWidth: this.restoreWidth(),
        });

        // everything the embedded form registers for "before leaving" (save / discard dirty record)
        this.formBeforeLeave = new CallbackRecorder();

        // Each embedded view exports its own state (search facets, pager, group by, scroll...) into its own
        // recorders, so they do not mix. The state is handed back to the views when the split view is shown
        // again (breadcrumb, back from the full form view...) or when the list is reloaded.
        this.panes = {
            list: { globalState: new CallbackRecorder(), localState: new CallbackRecorder() },
            form: { globalState: new CallbackRecorder(), localState: new CallbackRecorder() },
        };
        this.restored = {
            list: { globalState: this.props.globalState?.split?.list, state: this.props.state?.split?.list },
            form: { state: this.props.state?.split?.form },
        };
        useSetupAction({
            beforeLeave: () => this.canLeaveForm(),
            getGlobalState: () => ({
                split: { list: this.collect(this.panes.list.globalState), form: this.collect(this.panes.form.globalState) },
            }),
            getLocalState: () => ({
                split: { list: this.collect(this.panes.list.localState), form: this.collect(this.panes.form.localState) },
            }),
        });

        // `onFormClosed` is called by the embedded form (discarded new record, deleted record...)
        this.closePane = () => this.onFormClosed();

        onWillStart(async () => {
            const { listRef, formRef, listArch, formArch } = this.props.archInfo;
            [this.listViewProps, this.formViewBaseProps] = await Promise.all([
                this.buildSubViewProps("list", listRef, listArch),
                this.buildSubViewProps("form", formRef, formArch),
            ]);
            await this.restoreActiveRecord();
        });

        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
        onWillUnmount(() => this.stopResize());
    }

    /** state exported by an embedded view (same merge as the action service does for a view) */
    collect(recorder) {
        const exports = recorder.callbacks.map((callback) => callback());
        return Object.assign({}, ...exports);
    }

    /** Remount the list, keeping its search, pager, group by... (a plain remount would reset them). */
    reloadList() {
        this.restored.list = {
            globalState: this.collect(this.panes.list.globalState),
            state: this.collect(this.panes.list.localState),
        };
        this.state.listKey++;
    }

    // ------------------------------------------------------------------ sub views
    async buildSubViewProps(type, ref, arch) {
        const props = { resModel: this.props.resModel, type };
        if (arch) {
            // inline arch: we only need the fields of the model, the arch is ours
            const { fields, relatedModels } = await this.loadModelFields(arch);
            return { ...props, arch, fields, relatedModels };
        }
        let viewId = ref ? await this.orm.call("base", "get_id_by_xmlid", [ref]) : false;
        if (!viewId) {
            // automatic mode: use the list / form view the action itself declares (default view if none)
            viewId = this.actionViewId(type);
        }
        return { ...props, viewId: viewId || undefined };
    }

    /** id of the view of the given type declared by the action ([id|false, type] pairs), or false. */
    actionViewId(type) {
        const entry = (this.env.config.views || []).find((view) => view[1] === type);
        return entry ? entry[0] : false;
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
        const relatedModels = { [resModel]: { fields } };
        await Promise.all(
            [...comodels].map(async (model) => {
                relatedModels[model] = { fields: await this.getFields(model) };
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
            // no inline editing in the split list, whatever the arch says: a click opens the record on the right
            editable: false,
            context: this.props.context,
            domain: this.props.domain,
            display: { searchPanel: false },
            loadIrFilters: true,
            searchViewId: this.actionViewId("search") || undefined,
            allowOpenAction: false,
            noBreadcrumbs: true,
            showButtons: false,
            selectRecord: (resId) => this.onSelectRecord(resId),
            globalState: this.restored.list.globalState,
            state: this.restored.list.state,
            // the View component reads these from its props (not from the env): the list reports its state here
            __getGlobalState__: this.panes.list.globalState,
            __getLocalState__: this.panes.list.localState,
        };
    }

    get formState() {
        // only the first mount gets the state exported before leaving the split view
        return this.restored.form.state;
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
            state: this.formState,
            __getGlobalState__: this.panes.form.globalState,
            __getLocalState__: this.panes.form.localState,
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
        this.saveActiveRecord(resId);
        this.restored.form.state = undefined;
    }

    /** Open the record shown on the right in the full form view (the normal form of the action). */
    async onExpand() {
        const resId = this.state.activeId;
        if (!resId) {
            return;
        }
        // the action service asks the embedded form to save / discard its pending changes first
        const hasForm = (this.env.config.views || []).some((view) => view[1] === "form");
        if (hasForm) {
            await this.action.switchView("form", { resId, resIds: [resId] });
        } else {
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: this.props.resModel,
                res_id: resId,
                views: [[this.actionViewId("form") || false, "form"]],
                target: "current",
            });
        }
    }

    async onCreate() {
        if (!(await this.canLeaveForm())) {
            return;
        }
        this.state.activeId = false;
        this.state.mode = "new";
        this.state.formKey++;
        this.saveActiveRecord(false);
        this.restored.form.state = undefined;
    }

    onFormSaved(record) {
        // a new record becomes the active one; the list is reloaded to show the change
        if (this.state.mode === "new" && record.resId) {
            this.state.activeId = record.resId;
            this.state.mode = "record";
            this.saveActiveRecord(record.resId);
        }
        this.reloadList();
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
        this.reloadList();
        this.saveActiveRecord(false);
    }

    // ------------------------------------------------------------------ resizer
    /** one key per action (and model / explicit view): each split view remembers its own state */
    get actionKey() {
        const config = this.env.config;
        return [config.actionId || 0, this.props.resModel, config.viewId || ""].join("_");
    }

    /** width of the panes: kept in the browser, for good */
    get storageKey() {
        return `web_split_view_width_${this.actionKey}`;
    }

    /** record shown on the right: kept for the tab session (survives a page reload) */
    get recordKey() {
        return `web_split_view_record_${this.actionKey}`;
    }

    saveActiveRecord(resId) {
        try {
            if (resId) {
                browser.sessionStorage.setItem(this.recordKey, String(resId));
            } else {
                browser.sessionStorage.removeItem(this.recordKey);
            }
        } catch {
            // sessionStorage unavailable
        }
    }

    /** Reopen the record that was displayed before the page was reloaded (if it still matches the action). */
    async restoreActiveRecord() {
        let resId = 0;
        try {
            resId = parseInt(browser.sessionStorage.getItem(this.recordKey), 10) || 0;
        } catch {
            // sessionStorage unavailable
        }
        if (!resId) {
            return;
        }
        const domain = [["id", "=", resId], ...(this.props.domain || [])];
        const count = await this.orm.searchCount(this.props.resModel, domain);
        if (count) {
            this.state.activeId = resId;
            this.state.mode = "record";
        } else {
            this.saveActiveRecord(false);
        }
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
