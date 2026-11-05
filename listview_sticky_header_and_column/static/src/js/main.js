odoo.define('listview_sticky_header_and_column.ListRenderer', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');
    var localStorage = require('web.local_storage');

    var MODULE_KEY = 'listview_sticky_header_and_column';
    var PIN_CLASS = 'js_pin_this_column';
    var uidCounter = 0;

    /** First non-transparent background colour found going up from `el` (white if none). */
    function opaqueBackground(el) {
        while (el && el.nodeType === 1) {
            var c = window.getComputedStyle(el).backgroundColor;
            if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) {
                return c;
            }
            el = el.parentElement;
        }
        return '#fff';
    }

    ListRenderer.include({
        init: function () {
            this._super.apply(this, arguments);
            // Unique per renderer: several lists can live in one form view
            this.lshcUid = ++uidCounter;
        },

        destroy: function () {
            this._lshcRemoveOldStyle();
            this._super.apply(this, arguments);
        },

        _renderView: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function (result) {
                // the table is rebuilt on every render: remove the stale style and freeze again
                self._lshcRemoveOldStyle();
                setTimeout(function () {
                    if (self.isDestroyed && self.isDestroyed()) {
                        return;
                    }
                    var columnIndex = self._lshcGetColumnIndex();
                    if (columnIndex) {
                        self._lshcFreezeColumnListView(columnIndex);
                    }
                }, 300);
                return result;
            });
        },

        _renderHeaderCell: function (node) {
            var self = this;
            var $cell = this._super.apply(this, arguments);
            $('<span>', {class: 'display-on-hover ' + PIN_CLASS})
                .html('<i class="fa fa-thumb-tack"></i>')
                .on('click', function (e) {
                    e.stopPropagation();
                    e.preventDefault();
                    self._lshcOnPinClick($(e.currentTarget).closest('th'));
                })
                .appendTo($cell);
            return $cell;
        },

        // ------------------------------------------------------------------ helpers
        _lshcGetWrapper: function () {
            return this.$el.hasClass('table-responsive') ? this.$el : this.$('.table-responsive').first();
        },

        /** localStorage key: one per model, and per x2many field when the list lives inside a form */
        _lshcGetKey: function () {
            var parent = this.getParent();
            var field = (parent && parent.attrs && parent.name) ? '__field_' + parent.name : '';
            return MODULE_KEY + '__model_' + (this.state && this.state.model) + field;
        },

        _lshcGetColumnIndex: function () {
            return Number(localStorage.getItem(this._lshcGetKey()));
        },

        _lshcSaveColumnIndex: function (index) {
            localStorage.setItem(this._lshcGetKey(), index);
        },

        _lshcRemoveOldStyle: function () {
            if (this.lshcResizeObserver) {
                this.lshcResizeObserver.disconnect();
                this.lshcResizeObserver = null;
            }
            $('style[name="' + MODULE_KEY + '"][data-owner="' + this.lshcUid + '"]').remove();
        },

        _lshcOnPinClick: function ($th) {
            var columnIndex = $th.index();
            if (this._lshcGetColumnIndex() === columnIndex) {
                this._lshcSaveColumnIndex(-1);
                this._lshcRemoveOldStyle();
            } else {
                this._lshcSaveColumnIndex(columnIndex);
                this._lshcFreezeColumnListView(columnIndex);
            }
        },

        /** Freeze the columns 0..columnIndex of this list (sticky header + sticky left columns). */
        _lshcFreezeColumnListView: function (columnIndex) {
            var self = this;
            var $wrapper = this._lshcGetWrapper();
            if (!$wrapper.length) {
                return;
            }
            this._lshcRemoveOldStyle();

            // Scope every rule to THIS list only
            $wrapper.attr('data-lshc-id', this.lshcUid);
            var isEmbedded = !!this.$el.closest('.o_field_widget, .o_field_x2many').length;
            var scope = '.o_content .table-responsive[data-lshc-id="' + this.lshcUid + '"]';

            var headBg = opaqueBackground($wrapper.find('thead th')[0]);
            var baseBg = opaqueBackground($wrapper[0]);
            var $rows = $wrapper.find('tbody tr.o_data_row');
            var oddBg = $rows.length ? window.getComputedStyle($rows[0]).backgroundColor : 'transparent';
            var evenBg = $rows.length > 1 ? window.getComputedStyle($rows[1]).backgroundColor : 'transparent';
            var tint = function (color) {
                return 'background-color: ' + baseBg + '; background-image: linear-gradient(' + color + ', ' + color + ');';
            };

            var preStyles = (isEmbedded ? '' : scope + ' { overflow: visible; }') + '\n' +
                scope + ' thead, ' + scope + ' thead th { position: sticky !important; top: 0; background-color: ' + headBg + '; z-index: 2; }\n' +
                scope + ' .o_data_row { position: relative; }';
            this._lshcAppendStyle(preStyles);

            var $headRow = $wrapper.find('table thead tr').first();
            var pinnedColumns = Array.prototype.slice.call($headRow.find('th'), 0, columnIndex + 1);
            if (!pinnedColumns.length) {
                return;
            }

            // `left` = sum of the widths of the previous pinned columns (never `offsetLeft`: it is scroll-shifted
            // once the column is sticky)
            var buildCss = function () {
                var acc = 0;
                return pinnedColumns.map(function (th, index) {
                    var left = acc;
                    acc += th.getBoundingClientRect().width;
                    var n = index + 1;
                    var last = index === pinnedColumns.length - 1;
                    var cells = scope + ' table thead tr th:nth-child(' + n + '), ' +
                        scope + ' table tfoot tr td:nth-child(' + n + '), ' +
                        scope + ' table tbody tr.o_data_row td:nth-child(' + n + ')';
                    return cells + ' { position: sticky; left: ' + left + 'px; z-index: 1;' +
                            (last ? ' box-shadow: -1px 0 0 #dee2e6 inset;' : '') + ' }\n' +
                        scope + ' table thead tr th:nth-child(' + n + ') { top: 0; z-index: 10; }\n' +
                        scope + ' table tbody tr.o_data_row:nth-of-type(odd) td:nth-child(' + n + ') { ' + tint(oddBg) + ' }\n' +
                        scope + ' table tbody tr.o_data_row:nth-of-type(even) td:nth-child(' + n + ') { ' + tint(evenBg) + ' }\n' +
                        scope + ' table tfoot tr td:nth-child(' + n + ') { background-color: ' + baseBg + '; }\n' +
                        scope + ' table tbody tr.o_data_row:hover td:nth-child(' + n + ') { background-image: linear-gradient(rgba(0, 0, 0, .075), rgba(0, 0, 0, .075)); }';
                }).join('\n');
            };
            var styleNode = this._lshcAppendStyle(buildCss());

            // Recompute `left` whenever a pinned column is resized
            if (window.ResizeObserver) {
                this.lshcResizeObserver = new window.ResizeObserver(function () {
                    styleNode.textContent = buildCss();
                });
                pinnedColumns.forEach(function (th) {
                    self.lshcResizeObserver.observe(th);
                });
            }
        },

        _lshcAppendStyle: function (css) {
            var node = document.createElement('style');
            node.setAttribute('name', MODULE_KEY);
            node.setAttribute('data-owner', this.lshcUid);
            node.textContent = css;
            document.head.appendChild(node);
            return node;
        },
    });

});
