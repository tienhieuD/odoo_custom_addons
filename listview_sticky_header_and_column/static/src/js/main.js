/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import {
    onWillDestroy,
    onMounted,
} from "@odoo/owl";


patch(ListRenderer.prototype, "my_list_view_patch", {
    // Define the patched method here
    setup() {
        this._super(...arguments);

        onWillDestroy(() => {
            this.lshcRemoveOldStyle();
        });

        onMounted(() => {
            this.lshcRemoveOldStyle();
            const columnIndex = this.lshcGetColumnIndex();
            if (columnIndex) {
                this.lshcFreezeColumnListView(columnIndex);
            }
        });
    },

    /**
     * Custom config for this module
     * @param {'key' | 'viewKey'} name name of config
     * @returns {any}
     */
    lshcConfig(name) {
        return {
            'key': 'listview_sticky_header_and_column',
            'viewKey': `listview_sticky_header_and_column__viewId_${this.env.config.viewId}`,
        }[name];
    },

    /**
     * Sleep mixin
     * @param {number} secs milliseconds to sleep
     * @returns {Promise}
     */
    lshcSleep(secs) {
        return new Promise(r => setTimeout(r, secs));
    },
    
    /**
     * remove <style /> freeze if exist
     */
    lshcRemoveOldStyle() {
        const id = this.lshcConfig('key');
        const style = document.getElementById(id);
        if (style) {
            style.remove();
        }
    },

    /**
     * On click pin
     * @param {Event} e click event
     */
    async _onPinThisColumnClick(e) {
        e.stopPropagation();
        e.preventDefault();

        const columnIndex = $(e.target).closest('th').index();
        const savedColumnIndex = this.lshcGetColumnIndex();

        if (savedColumnIndex === columnIndex) {
            this.lshcSaveColumnIndex(-1);
            this.lshcRemoveOldStyle();
        } else {
            this.lshcSaveColumnIndex(columnIndex);
            await this.lshcFreezeColumnListView(columnIndex);
        }
    },

    /**
     * @param {number} columnIndex 
     */
    lshcSaveColumnIndex(columnIndex) {
        const key = this.lshcConfig('viewKey');
        localStorage.setItem(key, columnIndex);
    },

    /**
     * @returns {number}
     */
    lshcGetColumnIndex() {
        const key = this.lshcConfig('viewKey');
        const result = localStorage.getItem(key);
        return Number(result);
    },

    /**
     * do freeze list view column of list view on dom
     * @param {number} columnIndex index of the column to freeze
     */
    async lshcFreezeColumnListView(columnIndex) {
        const el = this.__owl__.bdom.el;

        this.lshcRemoveOldStyle();
        await this.lshcSleep(300);

        const headerTableRow = el.querySelector('table thead tr');
        const headerTableColumns = Array.from(headerTableRow.querySelectorAll('th'));
        const offsetLefts = headerTableColumns.map(th => th.offsetLeft).slice(0, columnIndex + 1);

        const styles = [`
            .o_content .table-responsive table thead tr th {
                background-color: #eee;
            }
        `];
        for (let index in offsetLefts) {
            const offsetLeft = offsetLefts[index];
            const cssNthChildIndex = Number(index) + 1;
            styles.push(`
                .o_content .table-responsive table thead tr th:nth-child(${cssNthChildIndex}),
                .o_content .table-responsive table tfoot tr td:nth-child(${cssNthChildIndex}),
                .o_content .table-responsive table tbody tr.o_data_row td:nth-child(${cssNthChildIndex}) {
                    position: sticky;
                    left: ${offsetLeft}px;
                    z-index: 1;
                    border-right: 1px solid #dee2e6;
                    box-shadow: -1px 0 0 #dee2e6 inset;
                }
                .o_content .table-responsive table thead tr th:nth-child(${cssNthChildIndex}) {
                    top: 0;
                    z-index: 10;
                }
                .o_content .table-responsive table tbody tr:nth-of-type(odd).o_data_row td:nth-child(${cssNthChildIndex}) {
                    background-color: #f9f9f9;
                }
                .o_content .table-responsive table tbody tr:nth-of-type(even).o_data_row td:nth-child(${cssNthChildIndex}) {
                    background-color: #fff;
                }
            `)
        }

        const id = this.lshcConfig('key');
        const newStyleNode = $(`
            <style id="${id}">
                ${styles.join(' ')}
            </style>`);

        $(document.head).append(newStyleNode);
    }
});
