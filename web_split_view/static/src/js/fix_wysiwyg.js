/** @odoo-module **/


import Wysiwyg from 'web_editor.wysiwyg'

Wysiwyg.include({
    start: async function () {
        if (!this.toolbar) {
            this.toolbar = {
                $el: [document.createElement('div')],
            }
        }
        try {
            return await this._super(...arguments);
        } catch (error) {
            // The record shown in the split pane can be replaced (or sent to the full form view) while an html
            // field is still starting: the editor is then already destroyed, its failure is of no interest.
            if (this.isDestroyed && this.isDestroyed()) {
                return;
            }
            throw error;
        }
    }
});
