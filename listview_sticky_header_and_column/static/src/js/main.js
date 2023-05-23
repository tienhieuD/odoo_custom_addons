function _x_sleep(secs) {
    return new Promise(r => setTimeout(r, secs))
}

function _x_removeOldStyle() {
    const oldStyleNode = $("#listview_sticky_header_and_column");
    oldStyleNode.remove();
}

/**
 * 
 * @param {JQueryTheadElement} $thead header this table <thead/>
 * @param {number} currentColumnIndex index of column to frezze
 */
function _x_appendNewStyle($thead, currentColumnIndex) {
    const header_th_list = Array.from($thead.find('th'));
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


    const newStyleStr = `
        <style id="listview_sticky_header_and_column">
            ${styles.join(' ')}
        </style>`.replace(/\n/ig, '').replace(/\s\s/ig,'').trim()
    const newStyleNode = $(newStyleStr);
    _x_removeOldStyle();
    $(document.head).append(newStyleNode);
}

odoo.define('nev_widgets.ext_context_freeze_column', (require) => {
    require('web.ListRenderer').include({
        _renderHeader: function () {
            this.$thead = this._super.apply(this, arguments);
            _x_removeOldStyle();
            return this.$thead;
        },

        _renderHeaderCell: function (node) {
            var cell = this._super.apply(this, arguments);

            $('<span>', { class: 'display-on-hover js_pin_this_column' })
                .html('<i class="fa fa-thumb-tack"></i>')
                .on('click', async (e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    const currentColumnIndex = $(e.currentTarget).closest('th').index();

                    _x_removeOldStyle();
                    await _x_sleep(300);
                    _x_appendNewStyle(this.$thead, currentColumnIndex);
                })
                .appendTo(cell);
            return cell;
        },
    });
});