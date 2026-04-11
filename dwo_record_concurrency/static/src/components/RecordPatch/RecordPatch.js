/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { Record } from '@web/model/relational_model/record';

patch(
    Record.prototype,
    {
        /**
         * @override to assign the custom context to the record.context
         */
        setup() {
            super.setup(...arguments);
            this.currentTabId = null;
            this._assignCustomContext();
        },

        /**
         * Update the custom context for the record with the current tab id.
         * this.context will be pass to Record._save method
         * use to check the concurrency of the tab is saving the record
         * Note: this.context is Proxy of this._config.context
         */
        _assignCustomContext() {
            const multiTabService = this.model.env.services.multi_tab;
            const currentTabId = multiTabService.currentTabId;
            
            this.currentTabId = currentTabId;
            this._config.context = {
                ...this._config.context,
                current_tab_id: currentTabId
            };
        },
    }
)
