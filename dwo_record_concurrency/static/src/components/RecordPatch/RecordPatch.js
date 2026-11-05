/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Record } from "@web/views/basic_relational_model";
import { DWO_TAB_ID } from "../../utils/tab_id";

/**
 * Every save of the form root goes through the form controller first (conflict check) and carries the id of this
 * tab, so the server can tell the other tabs (and users) who wrote.
 */
patch(Record.prototype, "dwo_record_concurrency.Record", {
    async save() {
        const superSave = this._super.bind(this); // _super is only available before the first await
        const isRoot = this.model.root === this;
        if (isRoot && this.model.dwoBeforeSave && this.resId) {
            await this.askChanges(); // commit what the user is typing
            if (!(await this.model.dwoBeforeSave(this))) {
                return false;
            }
        }
        const dataPoint = this.model.__bm__.localData[this.__bm_handle__];
        dataPoint.context = { ...dataPoint.context, current_tab_id: DWO_TAB_ID };
        const saved = await superSave(...arguments);
        if (saved && isRoot && this.model.dwoAfterSave) {
            this.model.dwoAfterSave(this);
        }
        return saved;
    },
});
