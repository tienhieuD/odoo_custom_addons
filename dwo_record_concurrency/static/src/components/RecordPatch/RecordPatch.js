/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Record } from "@web/model/relational_model/record";
import { DWO_TAB_ID } from "../../utils/tab_id";

patch(Record.prototype, {
    /**
     * Send the id of this tab with every save, so the server can tell the other tabs (and users) who wrote.
     */
    setup() {
        super.setup(...arguments);
        this._config.context = {
            ...this._config.context,
            current_tab_id: DWO_TAB_ID,
        };
    },
});
