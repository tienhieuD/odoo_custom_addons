/** @odoo-module **/


import Wysiwyg from 'web_editor.wysiwyg'

Wysiwyg.include({
    start: async function () {
        if (!this.toolbar) {
            this.toolbar = {
                $el: [document.createElement('div')],
            }
        }
        return this._super(...arguments);
    }
});
