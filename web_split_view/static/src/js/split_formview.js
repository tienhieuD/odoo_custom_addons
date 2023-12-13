odoo.define("awesome.SplitFormView", function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const FormRenderer = require('web.FormRenderer');
    const BasicModel = require('web.BasicModel');
    const FormView = require('web.FormView');

    const SplitFormController = FormController.extend({
        /**
         * Remove the current ID to the state pushed in the url.
         * @override
         */
        getState: function () {
            const state = this._super.apply(this, arguments);
            const newState = { ...state };
            if ('id' in state) {
                delete newState.id;
            }
            return newState;
        },
        /**
         * Trigger `form_saved_record` to reload list view
         * @override
         */
        saveRecord: function () {
            return this._super(...arguments).then(() => {
                this.trigger_up('form_saved_record', { form: this });
            });
        },
        /**
         * @override
         */
        _onDiscard: function () {
            this._super(...arguments);
            this.trigger_up('form_discarded_record', { form: this });
        },
    });
    const SplitFormRenderer = FormRenderer.extend({});
    const SplitFormModel = BasicModel.extend({
        /**
         * Trigger `form_saved_record` to reload list view
         * @override
         */
        deleteRecords: function () {
            return this._super(...arguments).then(() => {
                this.trigger_up('form_saved_record', { form: this });
            });
        },
    });
    const SplitFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Model: SplitFormModel,
            Controller: SplitFormController,
            Renderer: SplitFormRenderer,
        }),
    });

    return SplitFormView;
});

