odoo.define('dwo_chatter_filter/static/src/models/chatter/chatter.js', function (require) {
'use strict';

const { registerFieldPatchModel, registerInstancePatchModel } = require('mail/static/src/model/model_core.js');
const { attr } = require('mail/static/src/model/model_field.js');

const NAME = 'dwo_chatter_filter/static/src/models/chatter/chatter.js';

registerFieldPatchModel('mail.chatter', NAME, {
    /** The kind of message shown, false for all of them. */
    dwoFilter: attr({ default: false }),
});

registerInstancePatchModel('mail.chatter', NAME, {
    /**
     * Show one kind of message (false: all of them). Odoo 14 keeps one cache of messages for each domain
     * of the thread viewer: a domain with the leaf ("dwo_category", "=", kind) gives its own cache, loaded
     * from the server, where the server turns the leaf into the real domain (see message_fetch).
     *
     * @param {string|false} category
     */
    dwoSetFilter(category) {
        category = category || false;
        if (this.dwoFilter === category || !this.threadViewer) {
            return;
        }
        this.update({ dwoFilter: category });
        this.threadViewer.update({
            stringifiedDomain: category ? JSON.stringify([['dwo_category', '=', category]]) : '[]',
        });
    },

    /**
     * Back to all the messages, for the next time the record is opened.
     */
    dwoReset() {
        if (this.dwoFilter) {
            this.dwoSetFilter(false);
        }
    },
});

});
