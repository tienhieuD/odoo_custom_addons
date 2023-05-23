function _x_removeOldStyle () {
    const oldStyleNode = $("#listview_sticky_header_and_column");
    oldStyleNode.remove();
}

function _x_sleep (secs) {
    return new Promise(r => setTimeout(r, secs))
}

odoo.define('nev_widgets.ext_context_freeze_column', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var ActionManager = require('web.ActionManager');
    var pyUtils = require('web.py_utils');
    var WebClient = require('web.WebClient');
    var ListRenderer = require('web.ListRenderer');
    var session = require('web.session');
    var core = require('web.core');
    let localStorage = require('web.local_storage');
    var qweb = core.qweb;

    // WebClient.include({
    //     custom_events: _.extend({}, WebClient.prototype.custom_events, {
    //         set_freeze: 'setFreeze',
    //     }),
    //     init: function () {
    //         this._super.apply(this, arguments);
    //         this.number_of_keep_columns = 0;
    //         this.arr_offset_lefts = [];
    //         core.bus.on("DOM_updated", this, this.setFreezePosition.bind(this));
    //     },
    //     on_hashchange: function () {
    //         var self = this;
    //         return this._super.apply(this, arguments).then(function () {
    //             self.number_of_keep_columns = self._getFreezePositionFromLocalStorage() || 0;
    //         });
    //     },
    //     setFreeze: function (event) {
    //         this.number_of_keep_columns = event.data.number_of_keep_columns;
    //         this.setFreezePosition();
    //         this._saveFreezePositionToLocalStorage();
    //     },
    //     setFreezePosition: function () {
    //         this._removeStyle();
    //         setTimeout(this._setFreezePosition.bind(this), 1000);
    //     },
    //     _setFreezePosition: function () {
    //         var $table = $('.table-responsive .o_list_view');
    //         if (!$table.length) {
    //             return
    //         }
    //         var wrapper_offset_left = $(".o_content").offset().left;
    //         var $table_footer = $table.find('tfoot');
    //         this.arr_offset_lefts.length = 0
    //         for (var i = 1; i <= this.number_of_keep_columns; i++) {
    //             var $td = $table_footer.find('td:nth-child(' + i + ')');
    //             if (!$td.length) {
    //                 continue
    //             }
    //             var offset = $td.offset().left - wrapper_offset_left;
    //             this.arr_offset_lefts.push(offset)
    //         }
    //         this._addStyle()
    //     },
    //     _addStyle: function () {
    //         $(document.head).append(
    //             qweb.render('listview_sticky_header_and_column.style', { arr_offset_lefts: this.arr_offset_lefts })
    //         );
    //     },
    //     _removeStyle: function () {
    //         $('.js_lvs_style').remove();
    //     },
    //     _prepareFreezePositionKey: function () {
    //         return String(this._current_state.action) + '_'
    //             + String(this._current_state.menu_id) + '_'
    //             + String(this._current_state.model) + '_'
    //             + String(this._current_state.view_type);
    //     },
    //     _saveFreezePositionToLocalStorage: function () {
    //         var key = this._prepareFreezePositionKey()
    //         var value = this.number_of_keep_columns;
    //         localStorage.setItem(key, value)
    //     },
    //     _getFreezePositionFromLocalStorage: function () {
    //         var key = this._prepareFreezePositionKey()
    //         return parseInt(localStorage.getItem(key));
    //     }

    // });


    ListRenderer.include({
        _renderHeader: function () {
            _x_removeOldStyle();
            return this._super.apply(this, arguments);
        },

        _renderHeaderCell: function (node) {
            var cell = this._super.apply(this, arguments);
            var grandpa = this.getParent().getParent();
            // if (_.isEmpty(grandpa && grandpa.actions)) {  // check is if a big listview, not listview in form, not listview in popup
            //     return cell;
            // }

            $('<span>', { class: 'display-on-hover js_pin_this_column' })
                .html('<i class="fa fa-thumb-tack"></i>')
                .on('click', async function (e) {
                    e.stopPropagation();
                    e.preventDefault();

                    _x_removeOldStyle();
                    await _x_sleep(300);

                    const currentColumnIndex = $(e.currentTarget).closest('th').index();
                    const header_tr = $(e.currentTarget).closest('tr');
                    const header_th_list = Array.from(header_tr.find('th'));
                    const offsetLefts = header_th_list.map(th => th.offsetLeft);
                    const firstOffsetLeft = Number(offsetLefts[0])

                    const styles = [`
                        .o_content .o_list_view .table-responsive table thead tr th {
                            background-color: #eee;
                        }
                    `];
                    for (let index in offsetLefts) {
                        if (index > currentColumnIndex) {
                            break;
                        }
                        const offsetLeft = offsetLefts[index] - firstOffsetLeft;
                        const cssNthChildIndex = Number(index) + 1;
                        styles.push(`
                            .o_content .o_list_view .table-responsive table thead tr th:nth-child(${cssNthChildIndex}),
                            .o_content .o_list_view .table-responsive table tfoot tr td:nth-child(${cssNthChildIndex}),
                            .o_content .o_list_view .table-responsive table tbody tr.o_data_row td:nth-child(${cssNthChildIndex}) {
                                position: sticky !important;
                                left: ${offsetLeft}px;
                                z-index: 1;
                                border-right: 1px solid #dee2e6;
                            }
                            .o_content .o_list_view .table-responsive table thead tr th:nth-child(${cssNthChildIndex}) {
                                top: 0;
                                z-index: 10;
                            }
                            .o_content .o_list_view .table-responsive table tbody tr:nth-of-type(odd).o_data_row td:nth-child(${cssNthChildIndex}) {
                                background-color: #f9f9f9;
                            }
                            .o_content .o_list_view .table-responsive table tbody tr:nth-of-type(even).o_data_row td:nth-child(${cssNthChildIndex}) {
                                background-color: #fff;
                            }
                        `)
                    }

                    const newStyleNode = $(`
                        <style id="listview_sticky_header_and_column">
                            ${styles.join(' ')}
                        </style>`);

                    $(document.head).append(newStyleNode);
                })
                .appendTo(cell);
            return cell;
        },
    });

});