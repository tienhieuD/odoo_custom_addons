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
            this.$el.on('click', '.o_split_expand', this._onExpand.bind(this));
            await this._restoreActiveRecord();
            return res;
        },
        /**
         * @override
         */
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            if (this.formInDOM()) {
                this.formController.reload();
            }
        },
        /**
         * Odoo 13: the control panel sends its `search` event to the controller: the list on the left is the
         * one that shows the records, so the query is forwarded to it.
         * @override
         */
        _onSearch: function (ev) {
            ev.stopPropagation();
            this.lastSearchQuery = ev.data;
            return this.listController && this.listController.reload(_.extend({ offset: 0, groupsOffset: 0 }, ev.data));
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

        /**
         * One key per action (and model / explicit view): each split view remembers its own state.
         */
        actionKey() {
            const info = this.actionInfo || {};
            return [(info.action && info.action.id) || 0, this.modelName, info.viewId || ''].join('_');
        },

        saveSize(left, right) {
            localStorage.setItem(`web_split_view_width_${this.actionKey()}`, JSON.stringify([left, right]));
        },

        restoreSize() {
            const item = localStorage.getItem(`web_split_view_width_${this.actionKey()}`);
            if (!item) {
                return [50, 50];
            }
            return JSON.parse(item);
        },

        /**
         * Record shown on the right: kept for the tab session (survives a page reload).
         */
        saveActiveRecord(resId) {
            const key = `web_split_view_record_${this.actionKey()}`;
            try {
                if (resId) {
                    sessionStorage.setItem(key, String(resId));
                } else {
                    sessionStorage.removeItem(key);
                }
            } catch (e) {
                // sessionStorage unavailable
            }
        },

        /**
         * Reopen the record that was displayed before the page was reloaded (if it still exists).
         */
        _restoreActiveRecord: async function () {
            let resId = 0;
            try {
                resId = parseInt(sessionStorage.getItem(`web_split_view_record_${this.actionKey()}`), 10) || 0;
            } catch (e) {
                // sessionStorage unavailable
            }
            if (!resId) {
                return;
            }
            const count = await rpc.query({ model: this.modelName, method: 'search_count', args: [[['id', '=', resId]]] });
            if (!count) {
                this.saveActiveRecord(false);
                return;
            }
            await this._showRecord(resId);
        },

        /**
         * Display a record in the form on the right and highlight its row in the list.
         */
        _showRecord: async function (resId) {
            if (!this.formInDOM()) {
                this.renderFormView();
            }
            this.activeId = resId;
            this._highlightActiveRow();
            await this.formController.update({ currentId: resId, mode: 'readonly' });
            this.formController.do_show();
            this.saveActiveRecord(resId);
            this.$('.o_split_expand').removeClass('d-none');
        },

        _highlightActiveRow: function () {
            const rows = Array.from(this.listController.renderer.el.querySelectorAll('tr.o_data_row'));
            rows.forEach(node => node.classList.toggle('split_active_row', !!this.activeId && node.dataset.id && this.listController.model.get(node.dataset.id, { raw: true }).res_id === this.activeId));
        },

        /**
         * The embedded form is the one that may have unsaved changes: ask it (save / discard dialog) before the
         * action manager leaves the split view.
         * @override
         */
        canBeRemoved: function () {
            if (this.formInDOM() && this.formController) {
                return this.formController.canBeRemoved();
            }
            return Promise.resolve();
        },

        /**
         * Open the record shown on the right in the normal full form view of the action.
         */
        _onExpand: async function (ev) {
            ev.preventDefault();
            if (!this.activeId) {
                return;
            }
            const actionViews = (this.actionInfo && this.actionInfo.action && this.actionInfo.action.views) || [];
            if (actionViews.some(view => view[1] === 'form')) {
                this.trigger_up('switch_view', { view_type: 'form', res_id: this.activeId, mode: 'readonly' });
            } else {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: this.modelName,
                    res_id: this.activeId,
                    views: [[false, 'form']],
                    target: 'current',
                });
            }
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
            this.activeId = null;
            this._highlightActiveRow();
            this.saveActiveRecord(false);
            this.$('.o_split_expand').addClass('d-none');
        },

        _onOpenRecordSplit: async function (ev) {
            ev.stopPropagation();
            this.showLoading();
            const record = this.listController.model.get(ev.data.id, { raw: true });
            await this._showRecord(record.res_id);
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

        _onFormSavedRecord: async function (ev) {
            const form = ev.data && ev.data.form;
            const record = form && form.model.get(form.handle, { raw: true });
            if (record && record.res_id) {
                this.activeId = record.res_id;
                this.saveActiveRecord(record.res_id);
                this.$('.o_split_expand').removeClass('d-none');
            } else {
                this.activeId = null;
                this.saveActiveRecord(false);
                this.$('.o_split_expand').addClass('d-none');
            }
            await this.listController.reload();
            this._highlightActiveRow();
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
            controller.actionInfo = { action: this.params.action || {}, viewId: this.viewInfo.view_id };

            if (controller.ListView && controller.FormView) {
                return controller;
            }

            const modelName = controller.modelName;
            const context = controller.initialState.context;

            const xml = new DOMParser().parseFromString(this.viewInfo.arch, "text/xml");

            const treeRef = xml.documentElement.getAttribute('tree_view_ref');
            const formRef = xml.documentElement.getAttribute('form_view_ref');
            const treeXml = xml.documentElement.getElementsByTagName('tree')[0];
            const formXml = xml.documentElement.getElementsByTagName('form')[0];
            
            // automatic mode: no ref and no inline view -> use the list / form view the action itself declares
            const actionViews = (this.params.action && this.params.action.views) || [];
            const actionViewId = (types) => {
                const entry = actionViews.find(view => types.includes(view[1]));
                return entry ? entry[0] : false;
            };
            const [treeId, formId] = await Promise.all([
                treeRef ? this.xmlid(treeRef) : actionViewId(['list', 'tree']),
                formRef ? this.xmlid(formRef) : actionViewId(['form']),
            ]);
            const views = [[treeId, 'list'], [formId, 'form']];
            const viewInfo = await controller.loadViews(modelName, context, views);

            const viewInfoList = treeXml ? {...this.viewInfo, arch: treeXml.outerHTML} : {...viewInfo.list};
            const viewInfoForm = formXml ? {...this.viewInfo, arch: formXml.outerHTML} : {...viewInfo.form};

            this.ListView = new ListView(viewInfoList, { ...this.params, withControlPanel: false, withSearchBar: false, withSearchPanel: false, });
            this.FormView = new FormView(viewInfoForm, { ...this.params, withControlPanel: true, withSearchBar: false, withSearchPanel: false, });

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