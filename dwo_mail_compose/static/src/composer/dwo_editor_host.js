/** @odoo-module **/

import Widget from 'web.Widget';
import { createWysiwyg } from 'web_editor.loader';

/**
 * The HTML editor of Odoo 15 (web_editor) is a legacy widget: this widget creates it and gives it to the form
 * once it is started. The form puts it in the page with a ComponentAdapter.
 */
export const DwoEditorHost = Widget.extend({
    /**
     * @param {Widget} parent
     * @param {Object} options the options of the editor
     * @param {function} onStart called with the editor once it is started
     */
    init(parent, options, onStart) {
        this._super(parent);
        this._options = options;
        this._onStart = onStart;
    },

    /**
     * @override
     */
    async start() {
        await this._super(...arguments);
        this.wysiwyg = await createWysiwyg(this, this._options);
        await this.wysiwyg.appendTo(this.$el);
        await this._onStart(this.wysiwyg);
    },
});
