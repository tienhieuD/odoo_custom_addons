odoo.define('dwo_chatter_filter.filter', function (require) {
'use strict';

/**
 * Odoo 12: the chatter shows the messages of a record by their ids (the field message_ids) and loads the
 * text of the newest ones. The badges keep the ids of one kind (the server finds them: dwo_filter_ids), so
 * "Load more" keeps working on the filtered list.
 */

const core = require('web.core');
const DocumentThread = require('mail.model.DocumentThread');
const ThreadField = require('mail.ThreadField');
const session = require('web.session');

const QWeb = core.qweb;
const _t = core._t;

// Each kind has its own colour (a Bootstrap contextual colour, and purple, defined in the stylesheet): outlined when off, filled when chosen.
const KINDS = [
    { id: 'discussion', label: _t('Discussions'), color: 'primary' },
    { id: 'email', label: _t('Emails'), color: 'info' },
    { id: 'activity', label: _t('Activities'), color: 'purple' },
    { id: 'note', label: _t('Notes'), color: 'warning' },
    { id: 'tracking', label: _t('Tracking'), color: 'success' },
    { id: 'other', label: _t('Other'), color: 'danger' },
];

DocumentThread.include({
    /**
     * Show one kind of message (false: all of them).
     *
     * @param {string|false} category
     */
    dwoSetFilter: function (category) {
        this._dwoFilter = category || false;
        if (!this._dwoFilter) {
            this._dwoIDs = null;
        }
    },
    /**
     * @returns {string|false}
     */
    dwoGetFilter: function () {
        return this._dwoFilter || false;
    },
    /**
     * @override
     */
    getMessageIDs: function () {
        return this._dwoFilter && this._dwoIDs ? this._dwoIDs : this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    getMessages: function () {
        const messages = this._super.apply(this, arguments);
        if (!this._dwoFilter || !this._dwoIDs) {
            return messages;
        }
        return _.filter(messages, (message) => _.contains(this._dwoIDs, message.getID()));
    },
    /**
     * While a kind is chosen, the ids of that kind come from the server.
     *
     * @override
     */
    _fetchMessageIDs: function () {
        const self = this;
        return this._super.apply(this, arguments).then(function () {
            if (!self._dwoFilter || !self.getDocumentID()) {
                self._dwoIDs = null;
                return;
            }
            return self._rpc({
                model: 'mail.message',
                method: 'dwo_filter_ids',
                args: [self.getDocumentModel(), self.getDocumentID(), self._dwoFilter],
            }).then(function (ids) {
                self._dwoIDs = ids;
            });
        });
    },
    /**
     * With a kind chosen, the text of the messages is loaded for the ids of that kind.
     *
     * @override
     */
    _fetchMessages: function (options) {
        if (!this._dwoFilter) {
            return this._super.apply(this, arguments);
        }
        const self = this;
        return this._fetchMessageIDs().then(function () {
            const messageIDs = self._dwoIDs || [];
            const loadedIDs = _.map(self._messages, (message) => message.getID());
            const missing = _.difference(messageIDs, loadedIDs);
            options = options || {};
            const shouldFetch = _.difference(messageIDs.slice(0, self._FETCH_LIMIT), loadedIDs).length > 0;
            if (!(options.forceFetch || shouldFetch) || !missing.length) {
                return $.when();
            }
            return self._rpc({
                model: 'mail.message',
                method: 'message_format',
                args: [missing.slice(0, self._FETCH_LIMIT)],
                context: session.user_context,
            }).then(function (messagesData) {
                _.each(messagesData, function (messageData) {
                    self.call('mail_service', 'addMessage', messageData, { silent: true });
                });
            });
        });
    },
});

ThreadField.include({
    /**
     * @override
     */
    start: function () {
        const self = this;
        return this._super.apply(this, arguments).then(function () {
            self._dwoCounts = null;
            self._$dwoFilter = $('<div class="o-dwo-messageFilter d-flex flex-wrap align-items-center px-3 py-2 d-print-none d-none"/>');
            // Under the planned activities and the files, above the messages. The chatter detaches and attaches
            // the element of this widget as a whole: the badges live in the same element as the thread.
            const $thread = self._threadWidget.$el;
            const $wrap = $('<div class="o-dwo-threadWrap"/>');
            $wrap.insertBefore($thread);
            $wrap.append(self._$dwoFilter, $thread);
            self.setElement($wrap);
            self._$dwoFilter.on('click', '.o-dwo-filterBadge', self._dwoOnClickBadge.bind(self));
        });
    },
    /**
     * Leaving this record: back to all the messages, the badges go.
     *
     * @override
     */
    destroy: function () {
        if (this._documentThread) {
            this._documentThread.dwoSetFilter(false);
        }
        if (this._$dwoFilter) {
            this._$dwoFilter.remove();
        }
        clearTimeout(this._dwoTimer);
        this._super.apply(this, arguments);
    },
    /**
     * The widget is kept when the record changes: the choice is forgotten, the numbers are asked again.
     *
     * @override
     */
    _reset: function () {
        if (this._documentThread) {
            this._documentThread.dwoSetFilter(false);
        }
        this._dwoCounts = null;
        this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    _fetchAndRenderThread: function () {
        const self = this;
        return this._super.apply(this, arguments).then(function (result) {
            self._dwoRefresh();
            return result;
        });
    },
    /**
     * Numbers of the badges, asked again a moment after a change (a message arrived or was posted).
     *
     * @private
     */
    _dwoRefresh: function () {
        const self = this;
        clearTimeout(this._dwoTimer);
        this._dwoTimer = setTimeout(function () {
            if (self.isDestroyed() || !self.res_id || !self._documentThread) {
                self._dwoRender();
                return;
            }
            self._rpc({
                model: 'mail.message',
                method: 'dwo_filter_counts',
                args: [self.model, self.res_id],
            }).then(function (counts) {
                self._dwoCounts = counts;
                self._dwoRender();
            }).fail(function () {
                // the badges are a convenience: without numbers they stay hidden
            });
        }, 300);
    },
    /**
     * @private
     */
    _dwoRender: function () {
        if (!this._$dwoFilter) {
            return;
        }
        if (!this._dwoCounts || !this.res_id) {
            this._$dwoFilter.addClass('d-none').empty();
            return;
        }
        const active = (this._documentThread && this._documentThread.dwoGetFilter()) || false;
        const counts = this._dwoCounts;
        const items = [{ id: false, label: _t('All'), color: 'dark', count: counts.all || 0, active: active === false }]
            .concat(KINDS.map((kind) => ({
                id: kind.id, label: kind.label, color: kind.color, count: counts[kind.id] || 0, active: active === kind.id,
            })));
        this._$dwoFilter.html(QWeb.render('dwo_chatter_filter.MessageFilter', { items: items })).removeClass('d-none');
    },
    /**
     * @private
     * @param {Event} ev
     */
    _dwoOnClickBadge: function (ev) {
        ev.preventDefault();
        const kind = $(ev.currentTarget).data('kind');
        if (!this._documentThread) {
            return;
        }
        this._documentThread.dwoSetFilter(kind === 'all' ? false : kind);
        this._dwoRender();
        this._fetchAndRenderThread();
    },
});

});
