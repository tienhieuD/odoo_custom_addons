/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import {
    onWillDestroy,
    onMounted,
} from "@odoo/owl";


patch(ListRenderer.prototype, {
    // Define the patched method here
    setup() {
        super.setup(...arguments);

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
        const styleName = this.lshcConfig('key');
        const styles = document.head.querySelectorAll(`style[name="${styleName}"]`);
        styles.forEach(style => style.remove());
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
        const styleName = this.lshcConfig('key');

        // 1. remove old style if exist
        this.lshcRemoveOldStyle();

        // #region: 2. add pre style for header and table layout before calculate offsetLeft of columns
        const preStyles = [`
            /* 1. Container */
            .o_content .table-responsive {
                overflow: visible;
            }

            /* 2. Table */
            .o_content .table-responsive table {
                table-layout: auto !important;
            }

            /* 3. Header */
            .o_content .table-responsive thead,
            .o_content .table-responsive thead th {
                position: sticky !important;
                top: 0;
                background-color: #eee;
                z-index: 2;
            }

            /* 4. Row */
            .o_content .table-responsive .o_data_row {
                position: relative;
            }

            .o_content .table-responsive .o_data_row td {
                white-space: nowrap;
                padding: 0.3rem 0.75rem;
            }

            /* 5. States */
            .o_content .table-responsive .o_data_row:hover td {
                background-color: #eee !important;
            }

            .o_content .table-responsive .o_data_row:focus-within td {
                background-color: #ccc !important;
            }
        `];
        const preStyleNode = $(`
            <style name="${styleName}">
                ${preStyles.join(' ')}
            </style>`);
        $(document.head).append(preStyleNode);
        // #endregion
        
        // 3. sleep to wait for dom update and get correct offsetLeft of columns
        await this.lshcSleep(300);
        
        // #region: 4. calculate offsetLeft of columns
        const headerTableRow = el.querySelector('table thead tr');
        const headerTableColumns = Array.from(headerTableRow.querySelectorAll('th'));
        const offsetLefts = headerTableColumns.map(th => th.offsetLeft).slice(0, columnIndex + 1);

        const styles = [];
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
                    // border-right: 1px solid #dee2e6;
                    box-shadow: -1px 0 0 #dee2e6 inset;
                }
                .o_content .table-responsive table thead tr th:nth-child(${cssNthChildIndex}) {
                    top: 0;
                    z-index: 10;
                }
                .o_content .table-responsive table tbody tr:nth-of-type(even).o_data_row td:nth-child(${cssNthChildIndex}) {
                    background-color: #f9f9f9;
                }
                .o_content .table-responsive table tbody tr:nth-of-type(odd).o_data_row td:nth-child(${cssNthChildIndex}) {
                    background-color: #fff;
                }
            `)
        }

        const newStyleNode = $(`
            <style name="${styleName}">
                ${styles.join(' ')}
            </style>`);

        $(document.head).append(newStyleNode);
        // #endregion
    }
});
