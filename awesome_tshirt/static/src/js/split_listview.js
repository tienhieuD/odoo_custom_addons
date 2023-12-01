odoo.define("awesome.SplitListView", function (require) {
    "use strict";

    const ListController = require('web.ListController');
    const ListRenderer = require('web.ListRenderer');
    const ListModel = require('web.ListModel');
    const ListView = require('web.ListView');

    const SplitListController = ListController.extend({});
    const SplitListRenderer = ListRenderer.extend({
        /**
         * @override 
         */
        _onRowClicked: function (ev) {
            if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click') && !this.no_open) {
                const id = $(ev.currentTarget).data('id');
                if (id) {
                    this.trigger_up('open_record_split', { id: id, target: ev.target });
                }
            }
        },
    });
    const SplitListModel = ListModel.extend({});
    const SplitListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Model: SplitListModel,
            Controller: SplitListController,
            Renderer: SplitListRenderer,
        }),
    });

    return SplitListView;
});