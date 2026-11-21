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
// Every data header: field columns (`data-name`, `data-tooltip-delay`) and, defensively, any labelled header (`tabindex`)
// such as the `<column>` groups of Odoo 20 (no `data-name` there). Excluded by class below: record selector (checkbox),
// handle, button columns, open-form and optional-columns cells.
const PIN_TARGET_SELECTOR = 'thead tr th[data-name], thead tr th[tabindex]';
const PIN_EXCLUDED_CLASSES = [
    'o_list_record_selector', 'o_list_controller', 'o_list_actions_header',
    'o_list_open_form_view', 'o_list_button', 'o_handle_cell',
];
const PIN_BUTTON_CLASS = 'display-on-hover js_pin_this_column';
const PIN_ICON_HTML = '<i class="fa fa-thumb-tack"></i>';
const SLEEP_DELAY = 300;
const MOUNTED_SLEEP_DELAY = 100;
let lshcUidCounter = 0;

patch(ListRenderer.prototype, {
    // Define the patched method here
    setup() {
        super.setup(...arguments);
        // Unique per renderer instance: several lists can live in one form view
        this.lshcUid = ++lshcUidCounter;

        onWillDestroy(() => {
            this.lshcRemoveOldStyle();
        });

        onMounted(async () => {
            this.lshcRemoveOldStyle();
            const columnIndex = this.lshcGetColumnIndex();
            if (columnIndex !== null) {
                await this.lshcFreezeColumnListView(columnIndex);
            }
            await this.lshcSleep(MOUNTED_SLEEP_DELAY);
            this.lshcAddPinButtons();
            this.lshcListenResize();
            this.lshcApplyWidths();
        });

        onPatched(() => {
            this.lshcAddPinButtons();
            // Odoo re-applies its own widths on every patch: put the remembered ones back
            this.lshcApplyWidths();
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
        const thElements = el.querySelectorAll(PIN_TARGET_SELECTOR);
        thElements.forEach(th => {
            if (PIN_EXCLUDED_CLASSES.some(cls => th.classList.contains(cls))) return;
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

        if (savedColumnIndex !== null && savedColumnIndex === columnIndex) {
            // Unpin: forget the column (null = nothing pinned), never store a sentinel like -1
            this.lshcClearColumnIndex();
            this.lshcRemoveOldStyle();
            // Sticky is off: forget the remembered widths and go back to the Odoo widths
            this.lshcClearWidths();
            this.lshcResetOdooWidths();
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
     * Forget the pinned column (removes the localStorage key)
     */
    lshcClearColumnIndex() {
        localStorage.removeItem(this.lshcConfig('viewKey'));
    },

    /**
     * Get saved column index from localStorage
     * @returns {number|null} null when no column is pinned (0 is a valid index: first column)
     */
    lshcGetColumnIndex() {
        const key = this.lshcConfig('viewKey');
        const result = localStorage.getItem(key);
        if (result === null || result === '') {
            return null;
        }
        const index = Number(result);
        if (!Number.isInteger(index) || index < 0) {
            // legacy "-1" left by older versions after an unpin, or garbage: nothing pinned
            localStorage.removeItem(key);
            return null;
        }
        return index;
    },

    /**
     * Key of a header in the remembered widths: the field name, else its position
     * @param {HTMLElement} th
     * @returns {string|null} null for the technical columns (checkbox, buttons, ...)
     */
    lshcWidthKey(th) {
        if (PIN_EXCLUDED_CLASSES.some(cls => th.classList.contains(cls))) {
            return null;
        }
        return th.dataset.name || `#${Array.prototype.indexOf.call(th.parentNode.children, th)}`;
    },

    lshcWidthsStorageKey() {
        return `${this.lshcConfig('viewKey')}__widths`;
    },

    /**
     * @returns {Object} remembered widths {key: px}; empty when none
     */
    lshcGetWidths() {
        try {
            const widths = JSON.parse(localStorage.getItem(this.lshcWidthsStorageKey()) || '{}');
            return widths && typeof widths === 'object' ? widths : {};
        } catch {
            return {};
        }
    },

    lshcClearWidths() {
        localStorage.removeItem(this.lshcWidthsStorageKey());
    },

    /**
     * Remember the widths of the columns, only while a column is pinned
     */
    lshcSaveWidths() {
        const el = this.lshcGetRootElement();
        if (!el || this.lshcGetColumnIndex() === null) return;
        const widths = {};
        el.querySelectorAll('thead tr th').forEach(th => {
            const key = this.lshcWidthKey(th);
            if (key) widths[key] = Math.round(th.getBoundingClientRect().width);
        });
        localStorage.setItem(this.lshcWidthsStorageKey(), JSON.stringify(widths));
    },

    /**
     * Save the widths when the user lets go of a column resize handle
     */
    lshcListenResize() {
        const el = this.lshcGetRootElement();
        if (!el || el.dataset.lshcResize) return;
        el.dataset.lshcResize = '1';
        el.addEventListener('pointerdown', (ev) => {
            if (!ev.target.closest?.('.o_resize')) return;
            const onUp = () => {
                window.removeEventListener('pointerup', onUp);
                // after Odoo's own pointerup handler has stored the final widths
                setTimeout(() => this.lshcSaveWidths(), 0);
            };
            window.addEventListener('pointerup', onUp);
        }, true); // capture: Odoo's own handle handler may stop the event
    },

    /**
     * Give the headers back to Odoo: forget the widths a user dragged (or that we applied)
     */
    lshcResetOdooWidths() {
        if (typeof this.columnWidths?.resetWidths === 'function') {
            // Odoo 19, 20
            this.columnWidths.resetWidths();
            return;
        }
        const table = this.lshcGetRootElement()?.querySelector('table');
        if (!table) return;
        table.style.width = '';
        table.querySelectorAll('thead tr th').forEach(th => {
            th.style.width = '';
            th.style.maxWidth = '';
        });
        if (typeof this.freezeColumnWidths === 'function') {
            // Odoo 17: widths are computed again from the content
            this.keepColumnWidths = false;
            this.columnWidths = null;
            this.freezeColumnWidths();
        } else {
            // Odoo 18: the list recomputes its widths when the window is resized
            window.dispatchEvent(new Event('resize'));
        }
    },

    /**
     * Put the remembered widths on the headers (only while a column is pinned)
     */
    lshcApplyWidths() {
        const el = this.lshcGetRootElement();
        const table = el?.querySelector('table');
        if (!table || this.lshcGetColumnIndex() === null) return;
        const widths = this.lshcGetWidths();
        if (!Object.keys(widths).length || this.columnWidths?.resizing || this.resizing) return;
        const headers = Array.from(table.querySelectorAll('thead tr th'));
        let applied = false;
        headers.forEach(th => {
            const width = widths[this.lshcWidthKey(th)];
            if (Number.isFinite(width) && width > 0) {
                th.style.width = `${width}px`;
                applied = true;
            }
        });
        if (applied) {
            table.style.tableLayout = 'fixed';
            table.style.width = `${Math.floor(headers.reduce((sum, th) => sum + th.getBoundingClientRect().width, 0))}px`;
        }
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
        // `.o_content` for list views / x2many in forms, `.modal-body` for lists in dialogs
        const scope = `:is(.o_content, .modal-body) .table-responsive[data-lshc-id="${this.lshcUid}"]`;

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
                /* A dropdown opened from a field in this row (e.g. a Many2one autocomplete) is
                   rendered as an absolutely-positioned child of this very cell, with its own
                   very high z-index (see web's autocomplete.scss) -- but sibling sticky <td>s
                   of the rows below still paint over it: browsers give position:sticky table
                   cells their own compositing layer, and layers with equal z-index can end up
                   ordered by paint/DOM order rather than by the dropdown's own (much higher)
                   z-index, since the dropdown's stacking context is nested one level deeper.
                   Raising the EDITED row's pinned cell above every other row's (same selector,
                   declared later so it wins the tie) lifts the dropdown along with it, without
                   having to detect "is a dropdown currently open" at all. */
                ${scope} table tbody tr.o_selected_row td:nth-child(${cssNthChildIndex}) {
                    z-index: 20;
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
