odoo.define("awesome.splitView", function (require) {
    "use strict";

    const core = require('web.core');
    const viewRegistry = require('web.view_registry');
    const rpc = require('web.rpc');

    const BasicController = require('web.BasicController');
    const BasicModel = require('web.BasicModel');
    const BasicRenderer = require('web.BasicRenderer');
    const BasicView = require('web.BasicView');

    const ListView = require('awesome.SplitListView');
    const FormView = require('awesome.SplitFormView');

    const _lt = core._lt;
    const qweb = core.qweb;

    const SplitController = BasicController.extend({
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            open_record_split: '_onOpenRecordSplit',
            form_saved_record: '_onFormSavedRecord',
            form_discarded_record: '_onFormDiscardedRecord',
            get_active_id: '_onGetActiveId',
        }),

        init: function () {
            this._super(...arguments);
            this.activeId = null;
        },

        /**
         * @override
         */
        start: async function () {
            const res = await this._super(...arguments);
            this.listController = await this.ListView.getController(this);
            this.formController = await this.FormView.getController(this);
            this.renderListView();
            this.addResizeListener();
            return res;
        },
        /**
         * @override
         */
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            this.searchModel.on('search', this.listController, this.listController._onSearch);
            this.listController._onSearch(this.searchModel.get('query'));
            if (this.formInDOM()) {
                this.formController.reload();
            }
        },
        /**
         * @override
         */
        on_detach_callback: function () {
            this._super.apply(this, arguments);
            this.searchModel.off('search', this.listController);
        },
        /**
         * @override
         */
        _onPagerChanged: async function (ev) {
            return this._super(...arguments).then(() => this.listController._onPagerChanged(ev));
        },
        /**
         * @override
         */
        reload: function (params) {
            const isReloadFromSwitchView = params && ('controllerState' in params);
            const isReloadFromPageChange =
                Object.keys(params).includes('limit')
                && Object.keys(params).includes('offset')
                && Object.keys(params).length == 2;

            return this._super(...arguments).then(() => {
                if (isReloadFromSwitchView) {
                    // this.listController.reload();
                    // this.formController.reload();
                }
            });
        },
        /**
         * @override method from AbstractController
         * @param {jQuery} [$node]
         */
        renderButtons: function ($node) {
            if (!this.$buttons) {
                this.$buttons = $('<div/>');
                this.$buttons.append(qweb.render("awesome.SplitView.buttons", { widget: this }));
                this.$buttons.on('click', '.o_split_button_create', this._onCreate.bind(this));
                this.$buttons.on('click', '.o_split_button_reload', this._onReload.bind(this));
            }
            if (this.$buttons && $node) {
                this.$buttons.appendTo($node);
            }
        },

        listInDOM: function () {
            const container = this.el && this.el.querySelector('#list-view-container');
            return container && container.innerHTML.trim();
        },

        formInDOM: function () {
            const container = this.el && this.el.querySelector('#form-view-container');
            return container && container.innerHTML.trim();
        },

        saveSize(left, right) {
            const viewId = this.controlPanelProps.view.view_id;
            const key = `web_split_view_${viewId}`;
            localStorage.setItem(key, JSON.stringify([left, right]))
        },

        restoreSize() {
            const viewId = this.controlPanelProps.view.view_id;
            const key = `web_split_view_${viewId}`;
            const item = localStorage.getItem(key);
            if (!item) {
                return [50, 50];
            }
            return JSON.parse(item);
        },

        addResizeListener: function () {
            const self = this;
            const resizer = this.el.querySelector('.split_resizer');
            const leftSide = this.el.querySelector('.left-side');
            const rightSide = this.el.querySelector('.right-side');

            let [leftWidth, rightWidth] = this.restoreSize();
            leftSide.style.width = leftWidth + '%';
            rightSide.style.width = rightWidth + '%';

            function initDrag(e) {
                self.el.addEventListener('mousemove', doDrag);
                self.el.addEventListener('mouseup', stopDrag);
            }
            function doDrag(e) {
                leftWidth = Number(e.clientX / innerWidth * 100).toFixed(2);
                rightWidth = 100 - leftWidth;

                leftSide.style.width = leftWidth + '%';
                rightSide.style.width = rightWidth + '%';
            }
            function stopDrag(e) {
                self.el.removeEventListener('mousemove', doDrag);
                self.el.removeEventListener('mouseup', stopDrag);
                self.listController.reload();
                self.saveSize(leftWidth, rightWidth)
            }
            resizer.addEventListener('mousedown', initDrag, false);
        },

        _onCreate: function (ev) {
            if (!this.formInDOM()) {
                this.renderFormView();
            }
            this.formController.do_show();
            this.formController.update({ currentId: undefined });
        },

        _onReload: async function (ev) {
            ev.currentTarget.classList.add('disabled');
            ev.currentTarget.querySelector('i').classList.add('fa-spin');

            if (this.formInDOM()) {
                await this.formController.reload();
            }
            await this.listController.reload();
            
            ev.currentTarget.classList.remove('disabled');
            ev.currentTarget.querySelector('i').classList.remove('fa-spin');
        },

        _onOpenRecordSplit: async function (ev) {
            ev.stopPropagation();
            this.showLoading();

            if (!this.formInDOM()) {
                this.renderFormView();
            }

            const record = this.listController.model.get(ev.data.id, { raw: true });
            const params = {
                currentId: record.res_id,
                mode: 'readonly',
            };

            this.activeId = record.res_id;

            const allRowElements = Array.from(this.listController.renderer.el.querySelectorAll('tr'));
            allRowElements.forEach(node => node.classList.toggle('split_active_row', node.dataset.id === ev.data.id));

            await this.formController.update(params);
            this.formController.do_show();
            this.hideLoading();
        },

        showLoading() {
            this.$('.js_loading_split_form').addClass('active');
        },
        hideLoading() {
            this.$('.js_loading_split_form').removeClass('active');
        },

        _onGetActiveId: function (ev) {
            const { callback } = ev.data;
            callback(this.activeId);
        },

        _onFormSavedRecord: function () {
            this.listController.reload();
        },

        _onFormDiscardedRecord: function () {
            if (this.activeId) {
                return this.formController.update({
                    currentId: this.activeId,
                    mode: 'readonly',
                });
            }
            this.formController.do_hide();
        },

        renderListView: function () {
            this.listController.prependTo(this.el.querySelector('#list-view-container'));
        },

        renderFormView: function () {
            this.formController.prependTo(this.el.querySelector('#form-view-container'));
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
        withSearchPanel: false,  // todo: upgrade this
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
            this.viewInfo = viewInfo;
            this.params = params;
        },
        /**
         * @override
         */
        async getController() {
            const controller = await this._super(...arguments);

            if (controller.ListView && controller.FormView) {
                return controller;
            }

            const modelName = controller.modelName;
            const context = controller.initialState.context;
            const views = [];
            let archTree, archForm;

            const xml = new DOMParser().parseFromString(this.viewInfo.arch, "text/xml");

            const treeRef = xml.documentElement.getAttribute('tree_view_ref');
            const treeXml = xml.documentElement.getElementsByTagName('tree')[0];
            if (treeXml) {
                archTree = treeXml.outerHTML;
            } else if (treeRef) {
                const treeId = await this.xmlid(treeRef);
                views.push([treeId, 'list']);
            }

            const formRef = xml.documentElement.getAttribute('form_view_ref');
            const formXml = xml.documentElement.getElementsByTagName('form')[0];
            if (formXml) {
                archForm = formXml.outerHTML;
            } else if (formRef) {
                const formId = await this.xmlid(formRef);
                views.push([formId, 'form']);
            }

            if (views.length) {
                const { form, list } = await controller.loadViews(modelName, context, views);
                archTree = archTree || (list && list.arch);
                archForm = archForm || (form && form.arch);
            }

            this.ListView = new ListView({ ...this.viewInfo, arch: archTree, }, { ...this.params, withControlPanel: false, withSearchBar: false, withSearchPanel: false, });
            this.FormView = new FormView({ ...this.viewInfo, arch: archForm, }, { ...this.params, withControlPanel: true, withSearchBar: false, withSearchPanel: false, });

            controller.ListView = this.ListView;
            controller.FormView = this.FormView;
            return controller;
        },
        async xmlid(ref) {
            const id = await rpc.query({
                model: this.modelParams.modelName,
                method: 'get_id_by_xmlid',
                args: [ref],
            })
            return id;
        },
    });

    viewRegistry.add('split', SplitView);
});