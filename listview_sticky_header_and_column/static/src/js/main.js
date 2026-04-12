/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import {
    onWillDestroy,
    onMounted,
    onPatched,
} from "@odoo/owl";

// Constants
const MODULE_KEY = 'listview_sticky_header_and_column';
const TOOLTIP_DELAY_ATTR = 'data-tooltip-delay="1000"';
const PIN_BUTTON_CLASS = 'display-on-hover js_pin_this_column';
const PIN_ICON_HTML = '<i class="fa fa-thumb-tack"></i>';
const SLEEP_DELAY = 300;
const MOUNTED_SLEEP_DELAY = 100;

patch(ListRenderer.prototype, {
    // Define the patched method here
    setup() {
        super.setup(...arguments);

        onWillDestroy(() => {
            this.lshcRemoveOldStyle();
        });

        onMounted(async () => {
            this.lshcRemoveOldStyle();
            const columnIndex = this.lshcGetColumnIndex();
            if (columnIndex) {
                await this.lshcFreezeColumnListView(columnIndex);
            }
            await this.lshcSleep(MOUNTED_SLEEP_DELAY);
            this.lshcAddPinButtons();
        });

        onPatched(() => {
            this.lshcAddPinButtons();
        });
    },

    /**
     * Custom config for this module
     * @param {'key' | 'viewKey'} name name of config
     * @returns {any}
     */
    lshcConfig(name) {
        return {
            'key': MODULE_KEY,
            'viewKey': `${MODULE_KEY}__viewId_${this.env.config.viewId}`,
        }[name];
    },

    /**
     * Sleep utility
     * @param {number} ms milliseconds to sleep
     * @returns {Promise}
     */
    lshcSleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * Get the root element of the list view
     * @returns {HTMLElement|null}
     */
    lshcGetRootElement() {
        return this.rootRef?.el || this.__owl__.bdom.el;
    },

    /**
     * Add pin buttons to table headers
     */
    lshcAddPinButtons() {
        const el = this.lshcGetRootElement();
        if (!el) return;
        const thElements = el.querySelectorAll(`th[${TOOLTIP_DELAY_ATTR}]`);
        thElements.forEach(th => {
            if (!th.querySelector(`.${PIN_BUTTON_CLASS.split(' ')[1]}`)) {
                const span = document.createElement('span');
                span.className = PIN_BUTTON_CLASS;
                span.innerHTML = PIN_ICON_HTML;
                span.addEventListener('click', this._onPinThisColumnClick.bind(this));
                th.appendChild(span);
            }
        });
    },

    /**
     * Remove old styles
     */
    lshcRemoveOldStyle() {
        const styleName = this.lshcConfig('key');
        const styles = document.head.querySelectorAll(`style[name="${styleName}"]`);
        styles.forEach(style => style.remove());
    },

    /**
     * Handle pin button click
     * @param {Event} e click event
     */
    async _onPinThisColumnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        const th = e.target.closest('th');
        const columnIndex = Array.prototype.indexOf.call(th.parentNode.children, th);
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
     * Save column index to localStorage
     * @param {number} columnIndex
     */
    lshcSaveColumnIndex(columnIndex) {
        const key = this.lshcConfig('viewKey');
        localStorage.setItem(key, columnIndex);
    },

    /**
     * Get saved column index from localStorage
     * @returns {number}
     */
    lshcGetColumnIndex() {
        const key = this.lshcConfig('viewKey');
        const result = localStorage.getItem(key);
        return Number(result);
    },

    /**
     * Freeze columns in the list view
     * @param {number} columnIndex index of the column to freeze
     */
    async lshcFreezeColumnListView(columnIndex) {
        const el = this.lshcGetRootElement();
        const styleName = this.lshcConfig('key');

        // Remove old styles
        this.lshcRemoveOldStyle();

        // Add preliminary styles
        const preStyles = `
            .o_content .table-responsive {
                overflow: visible;
            }
            .o_content .table-responsive table {
                table-layout: auto !important;
            }
            .o_content .table-responsive thead,
            .o_content .table-responsive thead th {
                position: sticky !important;
                top: 0;
                background-color: #eee;
                z-index: 2;
            }
            .o_content .table-responsive .o_data_row {
                position: relative;
            }
            .o_content .table-responsive .o_data_row td {
                white-space: nowrap;
                padding: 0.3rem 0.75rem;
            }
            .o_content .table-responsive .o_data_row:hover td {
                background-color: #eee !important;
            }
            .o_content .table-responsive .o_data_row:focus-within td {
                background-color: #ccc !important;
            }
        `;
        const preStyleNode = document.createElement('style');
        preStyleNode.setAttribute('name', styleName);
        preStyleNode.textContent = preStyles;
        document.head.appendChild(preStyleNode);

        // Wait for DOM update
        await this.lshcSleep(SLEEP_DELAY);

        // Calculate offsets and create freeze styles
        const headerTableRow = el.querySelector('table thead tr');
        const headerTableColumns = Array.from(headerTableRow.querySelectorAll('th'));
        const offsetLefts = headerTableColumns.map(th => th.offsetLeft).slice(0, columnIndex + 1);

        const styles = offsetLefts.map((offsetLeft, index) => {
            const cssNthChildIndex = index + 1;
            return `
                .o_content .table-responsive table thead tr th:nth-child(${cssNthChildIndex}),
                .o_content .table-responsive table tfoot tr td:nth-child(${cssNthChildIndex}),
                .o_content .table-responsive table tbody tr.o_data_row td:nth-child(${cssNthChildIndex}) {
                    position: sticky;
                    left: ${offsetLeft}px;
                    z-index: 1;
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
            `;
        }).join('');

        const newStyleNode = document.createElement('style');
        newStyleNode.setAttribute('name', styleName);
        newStyleNode.textContent = styles;
        document.head.appendChild(newStyleNode);
    }
});
