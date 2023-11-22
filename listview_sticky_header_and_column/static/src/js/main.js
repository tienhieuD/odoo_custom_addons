/** @odoo-module **/
import ListRenderer from 'web.ListRenderer'

function _x_removeOldStyle () {
    const oldStyleNode = $("#listview_sticky_header_and_column");
    oldStyleNode.remove();
}

function _x_sleep (secs) {
    return new Promise(r => setTimeout(r, secs))
}

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
                            position: sticky !important;
                            left: ${offsetLeft}px !important;
                            z-index: 1 !important;
                            border-right: 1px solid #dee2e6 !important;
                        }
                        .o_content .o_list_view .table-responsive table thead tr th:nth-child(${cssNthChildIndex}) {
                            top: 0 !important;
                            z-index: 10 !important;
                        }
                        .o_content .o_list_view .table-responsive table tbody tr:nth-of-type(odd).o_data_row td:nth-child(${cssNthChildIndex}) {
                            background-color: #f9f9f9 !important;
                        }
                        .o_content .o_list_view .table-responsive table tbody tr:nth-of-type(even).o_data_row td:nth-child(${cssNthChildIndex}) {
                            background-color: #fff !important;
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
