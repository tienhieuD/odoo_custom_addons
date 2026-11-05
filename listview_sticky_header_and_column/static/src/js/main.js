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
let lshcUidCounter = 0;

patch(ListRenderer.prototype, "listview_sticky_header_and_column.ListRenderer", {
    // Define the patched method here
    setup() {
        this._super(...arguments);
        // Unique per renderer instance: several lists can live in one form view
        this.lshcUid = ++lshcUidCounter;

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
        // Lazy: 'key' is also needed on destroy, when the DOM (and so the field suffix) is gone
        if (name === 'key') {
            return MODULE_KEY;
        }
        return `${MODULE_KEY}__viewId_${this.env.config.viewId}${this.lshcGetFieldSuffix()}`;
    },

    /**
     * For a list embedded in a form (x2many field) return `__field_<name>` so that each list
     * remembers its own pinned column. Empty for a main list view (keeps the old key).
     * Must be called after mount (needs the DOM).
     * @returns {string}
     */
    lshcGetFieldSuffix() {
        const name = this.lshcGetRootElement()?.closest('.o_field_widget[name]')?.getAttribute('name');
        return name ? `__field_${name}` : '';
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
        return this.rootRef?.el || this.__owl__.bdom?.el || null;
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
        this.lshcResizeObserver?.disconnect();
        this.lshcResizeObserver = null;
        const styleName = this.lshcConfig('key');
        const styles = document.head.querySelectorAll(`style[name="${styleName}"][data-owner="${this.lshcUid}"]`);
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

        // Scope every rule to THIS list only
        el.dataset.lshcId = this.lshcUid;
        // List embedded in a form (x2many): it must keep its own scrollbar (overflow auto of
        // .table-responsive) because the form does not scroll horizontally for it.
        const isEmbedded = !!el.closest('.o_field_widget[name]');
        const scope = `.o_content .table-responsive[data-lshc-id="${this.lshcUid}"]`;

        // Add preliminary styles
        const preStyles = `
            ${isEmbedded ? '' : `${scope} {
                overflow: visible;
            }`}
            ${scope} thead,
            ${scope} thead th {
                position: sticky !important;
                top: 0;
                background-color: var(--ListRenderer-thead-bg-color);
                z-index: 2;
            }
            ${scope} .o_data_row {
                position: relative;
            }
        `;
        const preStyleNode = document.createElement('style');
        preStyleNode.setAttribute('name', styleName);
        preStyleNode.setAttribute('data-owner', this.lshcUid);
        preStyleNode.textContent = preStyles;
        document.head.appendChild(preStyleNode);

        // Wait for DOM update
        await this.lshcSleep(SLEEP_DELAY);

        // Calculate offsets and create freeze styles
        const headerTableRow = el.querySelector('table thead tr');
        const pinnedColumns = Array.from(headerTableRow.querySelectorAll('th')).slice(0, columnIndex + 1);

        // `left` = sum of the widths of the previous pinned columns. Do not use `offsetLeft`:
        // once a column is sticky it reflects the scroll-shifted position, not the natural one.
        const buildStyles = () => {
            let acc = 0;
            return pinnedColumns.map(th => {
                const offsetLeft = acc;
                acc += th.getBoundingClientRect().width;
                return offsetLeft;
            });
        };
        const buildCss = () => buildStyles().map((offsetLeft, index) => {
            const cssNthChildIndex = index + 1;
            return `
                ${scope} table thead tr th:nth-child(${cssNthChildIndex}),
                ${scope} table tfoot tr td:nth-child(${cssNthChildIndex}),
                ${scope} table tbody tr.o_data_row td:nth-child(${cssNthChildIndex}) {
                    position: sticky;
                    left: ${offsetLeft}px;
                    z-index: 1;
                    /* theme row colors (stripe/hover/focus); border only on the last pinned column */
                    box-shadow: ${index === pinnedColumns.length - 1 ? '-1px 0 0 #dee2e6 inset,' : ''}
                        inset 0 0 0 9999px var(--table-bg-state, var(--table-bg-type, var(--table-accent-bg)));
                }
                ${scope} table thead tr th:nth-child(${cssNthChildIndex}) {
                    top: 0;
                    z-index: 10;
                }
            `;
        }).join('');

        const newStyleNode = document.createElement('style');
        newStyleNode.setAttribute('name', styleName);
        newStyleNode.setAttribute('data-owner', this.lshcUid);
        newStyleNode.textContent = buildCss();
        document.head.appendChild(newStyleNode);

        // Recompute `left` whenever a pinned column is resized (e.g. drag & drop)
        this.lshcResizeObserver = new ResizeObserver(() => {
            newStyleNode.textContent = buildCss();
        });
        pinnedColumns.forEach(th => this.lshcResizeObserver.observe(th));
    }
});
