odoo.define("awesome.splitView", function (require) {
    "use strict";

    const AbstractController = require('web.AbstractController');
    const BasicController = require('web.BasicController');
    const AbstractModel = require('web.AbstractModel');
    const BasicModel = require('web.BasicModel');
    const AbstractRenderer = require('web.AbstractRenderer');
    const BasicRenderer = require('web.BasicRenderer');
    const AbstractView = require('web.AbstractView');
    const BasicView = require('web.BasicView');
    const viewRegistry = require('web.view_registry');
    const core = require('web.core');
    const _t = core._t;
    const _lt = core._lt;
    const select_create_controllers_registry = require('web.select_create_controllers_registry');
    const ListView = require('awesome.SplitListView');
    const FormView = require('awesome.SplitFormView');

    const SplitController = BasicController.extend({
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            open_record_split: '_onOpenRecordSplit',
            form_saved_record: '_onFormSavedRecord',
        }),

        init: function () {
            this._super(...arguments);
            this.listInDOM = false;
            this.formInDOM = false;
        },

        /**
         * @override
         */
        start: async function () {
            const res = await this._super(...arguments);
            this.listController = await this.ListView.getController(this);
            this.formController = await this.FormView.getController(this);
            this.renderListView();
            return res;
        },
        /**
         * @override
         */
        _onSearch: function (searchQuery) {
            return this.listController._onSearch(searchQuery);
        },
        /**
         * @override
         */
        _onPagerChanged: async function (ev) {
            // TODO: rpc to `search_read` call twice, from this and from this.listController._onPagerChanged, fix later :)
            return this._super(...arguments).then(() => this.listController._onPagerChanged(ev));
        },

        // /**
        //  * @override
        //  * @returns {Promise}
        //  */
        // update: async function (params, options) {
        //     // const res = await this._super(...arguments);
        //     return this.listController.update(params, options);
        //     // return res;
        // },

        _onOpenRecordSplit: async function (ev) {
            ev.stopPropagation();

            if (!this.formInDOM) {
                this.renderFormView();
            }

            const record = this.listController.model.get(ev.data.id, { raw: true });
            const params = {
                currentId: record.res_id,
                mode: 'readonly',
            };
            await this.formController.update(params);
        },

        _onFormSavedRecord: function () {
            this.listController.reload();
        },

        renderListView: function () {
            this.listController.prependTo(this.el.querySelector('#list-view-container'));
            this.listInDOM = true;
        },

        renderFormView: function () {
            this.formController.prependTo(this.el.querySelector('#form-view-container'));
            this.formInDOM = true;
        },
    });
    const SplitRenderer = BasicRenderer.extend({
        template: 'awesome.SplitViewRenderer',
        /**
         * @override
         */
        async _renderView() {
            return this._super(...arguments);
        },
    });
    const SplitModel = BasicModel.extend({
        /**
         * @override
         */
        init: function (parent, params = {}) {
            return this._super(...arguments);
        },
    });
    const SplitView = BasicView.extend({
        display_name: _lt('Split'),
        icon: 'fa-columns',
        viewType: 'split',
        withSearchBar: true,
        withSearchPanel: true,
        withControlPanel: true,
        config: _.extend({}, BasicView.prototype.config, {
            Model: SplitModel,
            Controller: SplitController,
            Renderer: SplitRenderer,
        }),
        /**
         * @override
         */
        init(viewInfo, params) {
            this._super(...arguments);

            const archTree = viewInfo.arch.match(/<tree.*?>(.|\n)+?<\/tree>/ig)?.[0] || `<tree></tree>`;
            const archForm = viewInfo.arch.match(/<form.*?>(.|\n)+?<\/form>/ig)?.[0] || `<form></form>`;

            this.ListView = new ListView({ ...viewInfo, arch: archTree, }, { ...params, withControlPanel: false, });
            this.FormView = new FormView({ ...viewInfo, arch: archForm, }, {
                ...params,
                withControlPanel: true,
                withSearchBar: false,
                withSearchPanel: false,
            });
        },

        async getController() {
            const controller = await this._super(...arguments);
            controller.ListView = this.ListView;
            controller.FormView = this.FormView;
            return controller;
        }
    });

    viewRegistry.add('split', SplitView);
});