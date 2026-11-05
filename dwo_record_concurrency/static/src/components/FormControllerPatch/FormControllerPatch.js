/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { formatDate, formatDateTime } from "@web/core/l10n/dates";
import { sprintf } from "@web/core/utils/strings";
import { patch } from "@web/core/utils/patch";
import { useBus, useService } from "@web/core/utils/hooks";
import { FormController } from "@web/views/form/form_controller";
import { ConcurrencyDialog } from "../ConcurrencyDialog/ConcurrencyDialog";
import { DWO_TAB_ID, RECORD_PRESENCE_CHANNEL_KEY } from "../../utils/tab_id";

const { onWillDestroy, useEffect } = owl;

const MODEL = "dwo.model.concurrency";
// watched fields per model, shared by every form of the page
const watchedFieldsByModel = new Map();

/**
 * Soft concurrency control. Nothing here can refuse a save: when the fields the user is saving were changed on
 * the server after the form was loaded, a dialog lets the user choose Force Save / Discard / Cancel.
 *
 * Every way of saving goes through `Record.save` (see RecordPatch), which calls `dwoBeforeSave` below.
 * The bus only gives early information.
 */
patch(FormController.prototype, "dwo_record_concurrency.FormController", {
    setup() {
        this._super(...arguments);
        this._dwoNotification = useService("notification");
        this._dwoDialog = useService("dialog");
        this._dwoOrm = useService("orm");
        this._dwoBus = useService("bus_service");
        this._dwoChannel = null;
        this._dwoToken = 0;
        this._dwoSnapshot = null; // normalized values of the watched fields, taken at load
        this._dwoWatched = [];
        this._dwoStale = null; // { fields: Set, userName } told by the bus
        useBus(this._dwoBus, "notification", (ev) => this._dwoOnNotification(ev.detail));
        this.model.dwoBeforeSave = (record) => this._dwoBeforeSave(record);
        this.model.dwoAfterSave = (record) => {
            this._dwoStale = null;
            this._dwoRefreshSnapshot(record.resModel, record.resId);
        };
        useEffect(
            () => {
                const { resModel, resId } = this.model.root;
                this._dwoStale = null;
                this._dwoSetChannel(resId ? `${RECORD_PRESENCE_CHANNEL_KEY}:${resModel}:${resId}` : null);
                this._dwoRefreshSnapshot(resModel, resId);
            },
            () => [this.model.root.resModel, this.model.root.resId]
        );
        onWillDestroy(() => this._dwoSetChannel(null));
    },

    _dwoSetChannel(channel) {
        if (this._dwoChannel === channel) {
            return;
        }
        if (this._dwoChannel) {
            this._dwoBus.deleteChannel(this._dwoChannel);
        }
        this._dwoChannel = channel;
        if (channel) {
            this._dwoBus.addChannel(channel);
        }
    },

    async _dwoRefreshSnapshot(resModel, resId) {
        const token = ++this._dwoToken;
        this._dwoSnapshot = null;
        if (!resId) {
            return;
        }
        try {
            if (!watchedFieldsByModel.has(resModel)) {
                watchedFieldsByModel.set(resModel, this._dwoOrm.call(MODEL, "get_watched_fields", [resModel]));
            }
            const watched = await watchedFieldsByModel.get(resModel);
            if (token !== this._dwoToken || !watched.length) {
                return;
            }
            const snapshot = await this._dwoOrm.call(MODEL, "dwo_snapshot", [resModel, resId]);
            if (token === this._dwoToken) {
                this._dwoWatched = watched;
                this._dwoSnapshot = snapshot;
            }
        } catch (_e) {
            watchedFieldsByModel.delete(resModel); // soft: without a snapshot we simply do not check
        }
    },

    _dwoChangedFields(record) {
        return Object.keys(this.model.__bm__.localData[record.__bm_handle__]._changes || {});
    },

    // ------------------------------------------------------------------ bus (early information only)
    async _dwoOnNotification(notifications) {
        const root = this.model.root;
        for (const { type, payload } of notifications) {
            if (
                type !== "dwo_record_presence" ||
                payload.model !== root.resModel ||
                payload.res_id !== root.resId ||
                payload.current_tab_id === DWO_TAB_ID
            ) {
                continue;
            }
            const fields = new Set([...(this._dwoStale?.fields || []), ...payload.fields]);
            this._dwoStale = { fields, userName: payload.user_name };
            await root.askChanges(); // commit what the user is typing: until then the record does not know the edit yet
            const edited = this._dwoChangedFields(root);
            if (payload.fields.some((name) => edited.includes(name))) {
                this._dwoNotification.add(
                    sprintf(_t("%(user)s changed fields you are editing. You will be asked before saving."), {
                        user: payload.user_name,
                    }),
                    { type: "warning" }
                );
            }
        }
    },

    // ------------------------------------------------------------------ the check (true = go on with the save)
    async _dwoBeforeSave(record) {
        if (!this._dwoSnapshot) {
            return true;
        }
        const dirty = this._dwoChangedFields(record).filter((name) => this._dwoWatched.includes(name));
        if (!dirty.length) {
            return true;
        }
        let conflicts;
        try {
            conflicts = await this._dwoOrm.call(MODEL, "dwo_check_conflict", [
                record.resModel,
                record.resId,
                this._dwoSnapshot,
                dirty,
            ]);
        } catch (_e) {
            return true; // soft: if the check itself fails, never get in the way of the save
        }
        if (!conflicts.length) {
            return true;
        }
        if (document.visibilityState === "hidden") {
            return false; // automatic save of a hidden tab: keep the changes, ask nothing, overwrite nothing
        }
        for (const conflict of conflicts) {
            conflict.mine = this._dwoDisplayValue(record, conflict);
        }
        const choice = await new Promise((resolve) => {
            this._dwoDialog.add(
                ConcurrencyDialog,
                { conflicts, onChoice: resolve },
                { onClose: () => resolve("cancel") }
            );
        });
        if (choice === "continue") {
            return true;
        }
        if (choice === "discard") {
            // drop the edits, then show the latest data of the server instead of the values the form was opened with
            setTimeout(async () => {
                await this.discard();
                await this.model.root.load();
                this.model.notify();
                this._dwoStale = null;
                this._dwoRefreshSnapshot(record.resModel, record.resId);
            });
        }
        return false;
    },

    _dwoDisplayValue(record, { name, type }) {
        const value = record.data[name];
        switch (type) {
            case "many2one":
                return Array.isArray(value) ? value[1] : value ? value.display_name : "";
            case "one2many":
            case "many2many":
                return sprintf(_t("%(count)s records"), { count: value?.count ?? value?.length ?? 0 });
            case "date":
                return value ? formatDate(value) : "";
            case "datetime":
                return value ? formatDateTime(value) : "";
            case "boolean":
                return value ? _t("Yes") : _t("No");
            case "binary":
                return _t("Binary content");
            case "selection": {
                const selection = record.fields[name].selection || [];
                const found = selection.find(([key]) => key === value);
                return found ? found[1] : value || "";
            }
            default:
                return value === false || value === undefined || value === null ? "" : String(value);
        }
    },

    /**
     * Closing the tab: the unload cannot wait for a server answer, so it relies on what the bus already told us.
     * Never overwrite silently when we know the record changed under the user.
     */
    async beforeUnload(ev) {
        if (this.model.root.isDirty && this._dwoStale) {
            ev.preventDefault();
            ev.returnValue = "";
            return;
        }
        return this._super(...arguments);
    },
});
