odoo.define('dwo_mail_compose/static/src/composer/dwo_editor_host.js', function (require) {
'use strict';

const Widget = require('web.Widget');
const Wysiwyg = require('web_editor.wysiwyg.root');

/**
 * The HTML editor of Odoo 14 (web_editor) is a legacy widget built on summernote: it is attached to a textarea.
 * This widget makes the textarea, starts the editor and gives it to the form once it is started. The form
 * puts it in the page with a ComponentAdapter.
 */
const DwoEditorHost = Widget.extend({
    /**
     * @param {Widget} parent
     * @param {Object} options the options of the editor (options.value is the content)
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
        const $textarea = $('<textarea/>').val(this._options.value || '<p><br></p>').appendTo(this.$el);
        this.wysiwyg = new Wysiwyg(this, this._options);
        await this.wysiwyg.attachTo($textarea);
        await this._onStart(this.wysiwyg);
    },
});

return { DwoEditorHost };

});
