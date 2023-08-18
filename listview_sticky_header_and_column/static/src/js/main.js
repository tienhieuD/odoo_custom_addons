/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import {
    onWillDestroy,
    onMounted,
} from "@odoo/owl";

function _x_removeOldStyle() {
    const oldStyleNode = $("#listview_sticky_header_and_column");
    oldStyleNode.remove();
}

function _x_sleep(secs) {
    return new Promise(r => setTimeout(r, secs))
}

patch(ListRenderer.prototype, "my_list_view_patch", {
    // Define the patched method here
    setup() {
        console.log("List view started!");
        this._super.apply(this, arguments);

        onWillDestroy(() => {
            _x_removeOldStyle();
        });

        onMounted(() => {
            _x_removeOldStyle();
        });
    },

    // Define a new method
    async _onPinThisColumnClick(e) {
        e.stopPropagation();
        e.preventDefault();

        _x_removeOldStyle();
        await _x_sleep(300);

        const currentColumnIndex = $(e.target).closest('th').index();
        const header_tr = $(e.target).closest('tr');
        const header_th_list = Array.from(header_tr.find('th'));
        const offsetLefts = header_th_list.map(th => th.offsetLeft);

        const styles = [`
            .o_content .table-responsive table thead tr th {
                background-color: #eee;
            }
        `];
        for (let index in offsetLefts) {
            if (index > currentColumnIndex) {
                break;
            }
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

        const newStyleNode = $(`
            <style id="listview_sticky_header_and_column">
                ${styles.join(' ')}
            </style>`);

        $(document.head).append(newStyleNode);
    },
});

/*
ListRenderer.include({
    _renderHeader: function () {
        _x_removeOldStyle();
        return this._super.apply(this, arguments);
    },

    _renderHeaderCell: function (node) {
        var cell = this._super.apply(this, arguments);

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

                const styles = [`
                    .o_content .o_list_view .table-responsive table thead tr th {
                        background-color: #eee;
                    }
                `];
                for (let index in offsetLefts) {
                    if (index > currentColumnIndex) {
                        break;
                    }
                    const offsetLeft = offsetLefts[index];
                    const cssNthChildIndex = Number(index) + 1;
                    styles.push(`
                        .o_content .o_list_view .table-responsive table thead tr th:nth-child(${cssNthChildIndex}),
                        .o_content .o_list_view .table-responsive table tfoot tr td:nth-child(${cssNthChildIndex}),
                        .o_content .o_list_view .table-responsive table tbody tr.o_data_row td:nth-child(${cssNthChildIndex}) {
                            position: sticky;
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
*/