odoo.define('dwo_chatter_filter.filter', function (require) {
'use strict';

/**
 * Odoo 13: the chatter shows the messages of a record by their ids (the field message_ids) and loads the
 * text of the newest ones. A chip keeps the ids of its messages (the server finds them: dwo_filter_ids), so
 * "Load more" keeps working on the filtered list.
 */

const core = require('web.core');
const DocumentThread = require('mail.model.DocumentThread');
const ThreadField = require('mail.ThreadField');
const session = require('web.session');

const QWeb = core.qweb;
const _t = core._t;

const ALL_COLOR = '#212529';

/** Relative luminance (WCAG) of a colour given as #rrggbb. */
function luminance(hex) {
    const [r, g, b] = [1, 3, 5].map((i) => {
        const c = parseInt(hex.slice(i, i + 2), 16) / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** The text of a chip that is filled with that colour: white or black, whichever reads better. */
function textColorOn(hex) {
    const L = luminance(hex);
    return 1.05 / (L + 0.05) >= (L + 0.05) / 0.05 ? '#ffffff' : '#000000';
}

DocumentThread.include({
    /**
     * Show the messages of one chip (false: all of them).
     *
     * @param {number|false} chipID
     */
    dwoSetFilter: function (chipID) {
        this._dwoFilter = chipID || false;
        if (!this._dwoFilter) {
            this._dwoIDs = null;
        }
    },
    /**
     * Search a text in all the messages of the record (together with the chip chosen). The server finds
     * the ids, so it works on the messages that are not loaded too.
     *
     * @param {string} text
     */
    dwoSetSearch: function (text) {
        this._dwoSearch = (text || '').trim();
        if (!this.dwoIsFiltered()) {
            this._dwoIDs = null;
        }
    },
    /**
     * @returns {string}
     */
    dwoGetSearch: function () {
        return this._dwoSearch || '';
    },
    /**
     * @returns {boolean} whether a chip is chosen or a text is searched
     */
    dwoIsFiltered: function () {
        return Boolean(this._dwoFilter || this._dwoSearch);
    },
    /**
     * @returns {number|false}
     */
    dwoGetFilter: function () {
        return this._dwoFilter || false;
    },
    /**
     * @override
     */
    getMessageIDs: function () {
        return this.dwoIsFiltered() && this._dwoIDs ? this._dwoIDs : this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    getMessages: function () {
        const messages = this._super.apply(this, arguments);
        if (this.dwoIsFiltered() && this._dwoIDs) {
            return _.filter(messages, (message) => _.contains(this._dwoIDs, message.getID()));
        }
        // All: the filter may have loaded older messages of its chip. Only the messages without a hole (from the
        // newest one, no gap) are shown, so the history never has holes; "Load more" fills the gaps in order.
        const loaded = {};
        _.each(messages, (message) => { loaded[message.getID()] = true; });
        const known = {};
        _.each(this._messageIDs, (id) => { known[id] = true; });
        const visible = {};
        for (const id of _.sortBy(this._messageIDs, (id) => -id)) {
            if (!loaded[id]) {
                break;
            }
            visible[id] = true;
        }
        return _.filter(messages, (message) => visible[message.getID()] || !known[message.getID()]);
    },
    /**
     * While a chip is chosen, the ids of its messages come from the server.
     *
     * @override
     */
    _fetchMessageIDs: function () {
        const self = this;
        return this._super.apply(this, arguments).then(function () {
            if (!self.dwoIsFiltered() || !self.getDocumentID()) {
                self._dwoIDs = null;
                return;
            }
            return self._rpc({
                model: 'mail.message',
                method: 'dwo_filter_ids',
                args: [self.getDocumentModel(), self.getDocumentID(), self._dwoFilter, self._dwoSearch || null],
            }).then(function (ids) {
                // false: nothing to filter by (the chip is gone, archived or broken, and no text): every message is shown
                if (ids === false) {
                    self._dwoFilter = false;
                }
                self._dwoIDs = ids || null;
            });
        });
    },
    /**
     * With a chip chosen, the text of the messages is loaded for the ids of that chip.
     *
     * @override
     */
    _fetchMessages: function (options) {
        if (!this.dwoIsFiltered()) {
            return this._super.apply(this, arguments);
        }
        const self = this;
        return this._fetchMessageIDs().then(function () {
            if (!self.dwoIsFiltered()) {
                return self._super.apply(self, [options]);
            }
            const messageIDs = self._dwoIDs || [];
            const loadedIDs = _.map(self._messages, (message) => message.getID());
            const missing = _.difference(messageIDs, loadedIDs);
            options = options || {};
            const shouldFetch = _.difference(messageIDs.slice(0, self._FETCH_LIMIT), loadedIDs).length > 0;
            if (!(options.forceFetch || shouldFetch) || !missing.length) {
                return Promise.resolve();
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
            self._dwoData = null;
            self._$dwoFilter = $('<div class="o-dwo-messageFilter d-flex flex-wrap align-items-center px-3 py-2 d-print-none d-none"/>');
            // Under the planned activities and the files, above the messages. The chatter detaches and attaches
            // the element of this widget as a whole: the chips live in the same element as the thread.
            const $thread = self._threadWidget.$el;
            const $wrap = $('<div class="o-dwo-threadWrap"/>');
            $wrap.insertBefore($thread);
            $wrap.append(self._$dwoFilter, $thread);
            self.setElement($wrap);
            // setElement removes every '.widget_events' handler of the old element, the ones of the thread widget too
            self._threadWidget._delegateEvents();
            self._$dwoChips = $('<div class="o-dwo-chips d-flex flex-wrap align-items-center"/>');
            self._$dwoSearch = $('<div class="o-dwo-search position-relative d-inline-flex align-items-center ml-auto mb-1">' +
                '<input type="text" class="o-dwo-searchInput form-control form-control-sm"/>' +
                '<button type="button" class="o-dwo-searchClear btn btn-link btn-sm p-0 d-none" title="Clear">\u00d7</button>' +
                '</div>');
            self._$dwoSearch.find('input').attr('placeholder', _t('Search messages...'));
            self._$dwoFilter.append(self._$dwoChips, self._$dwoSearch);
            self._$dwoSearch.on('input', '.o-dwo-searchInput', self._dwoOnInputSearch.bind(self));
            self._$dwoSearch.on('keydown', '.o-dwo-searchInput', self._dwoOnKeydownSearch.bind(self));
            self._$dwoSearch.on('click', '.o-dwo-searchClear', self._dwoOnClickClearSearch.bind(self));
            self._$dwoFilter.on('click', '.o-dwo-filterBadge', self._dwoOnClickChip.bind(self));
            self._$dwoFilter.on('click', '.o-dwo-filterEdit', self._dwoOnClickEdit.bind(self));
        });
    },
    /**
     * Leaving this record: back to all the messages, the chips go.
     *
     * @override
     */
    destroy: function () {
        if (this._documentThread) {
            this._documentThread.dwoSetFilter(false);
            this._documentThread.dwoSetSearch('');
        }
        if (this._$dwoFilter) {
            this._$dwoFilter.remove();
        }
        clearTimeout(this._dwoTimer);
        clearTimeout(this._dwoSearchTimer);
        this._super.apply(this, arguments);
    },
    /**
     * The widget is kept when the record changes: the choice is forgotten, the chips are asked again.
     *
     * @override
     */
    _reset: function () {
        if (this._documentThread) {
            this._documentThread.dwoSetFilter(false);
            this._documentThread.dwoSetSearch('');
        }
        clearTimeout(this._dwoSearchTimer);
        if (this._$dwoSearch) {
            this._$dwoSearch.find('input').val('');
            this._$dwoSearch.find('.o-dwo-searchClear').addClass('d-none');
        }
        this._dwoData = null;
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
     * The chips and their numbers, asked again a moment after a change (a message arrived or was posted).
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
                method: 'dwo_filter_chips',
                args: [self.model, self.res_id, self._documentThread.dwoGetSearch()],
            }).then(function (data) {
                self._dwoData = data;
                // the chip that is chosen was archived or deleted meanwhile: back to all the messages
                const active = self._documentThread.dwoGetFilter();
                if (active && !_.some(data.chips, (chip) => chip.id === active)) {
                    self._documentThread.dwoSetFilter(false);
                    self._fetchAndRenderThread();
                }
                self._dwoRender();
            }).guardedCatch(function (ev) {
                // the chips are a convenience: without them the row stays hidden
                ev.preventDefault();
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
        if (!this._dwoData || !this.res_id) {
            this._$dwoFilter.addClass('d-none');
            this._$dwoChips.empty();
            return;
        }
        const active = (this._documentThread && this._documentThread.dwoGetFilter()) || false;
        const data = this._dwoData;
        const make = (id, label, color, count) => ({
            id: id,
            label: label,
            count: count,
            active: active === id,
            disabled: Boolean(id) && active !== id && !count,
            style: '--dwo-chip: ' + color + '; --dwo-chip-text: ' + textColorOn(color),
        });
        const items = [make(false, _t('All'), ALL_COLOR, data.all)].concat(
            _.map(data.chips, (chip) => make(chip.id, chip.name, chip.color, chip.count)));
        this._$dwoChips.html(QWeb.render('dwo_chatter_filter.MessageFilter', {
            items: items,
            isAdmin: Boolean(session.is_admin),
        }));
        this._$dwoFilter.removeClass('d-none');
    },
    /**
     * @private
     * @param {Event} ev
     */
    _dwoOnClickChip: function (ev) {
        ev.preventDefault();
        const chip = $(ev.currentTarget).data('chip');
        if (!this._documentThread) {
            return;
        }
        this._documentThread.dwoSetFilter(chip === 'all' ? false : parseInt(chip, 10));
        this._dwoRender();
        this._fetchAndRenderThread();
    },
    /**
     * The text is sent to the server 300 ms after the last key.
     *
     * @private
     */
    _dwoOnInputSearch: function () {
        this._$dwoSearch.find('.o-dwo-searchClear').toggleClass('d-none', !this._$dwoSearch.find('input').val());
        clearTimeout(this._dwoSearchTimer);
        this._dwoSearchTimer = setTimeout(this._dwoApplySearch.bind(this), 300);
    },
    /**
     * @private
     * @param {Event} ev
     */
    _dwoOnKeydownSearch: function (ev) {
        if (ev.which === $.ui.keyCode.ESCAPE) {
            ev.stopPropagation();
            this._dwoOnClickClearSearch(ev);
        }
    },
    /**
     * @private
     * @param {Event} ev
     */
    _dwoOnClickClearSearch: function (ev) {
        ev.preventDefault();
        this._$dwoSearch.find('input').val('');
        this._$dwoSearch.find('.o-dwo-searchClear').addClass('d-none');
        clearTimeout(this._dwoSearchTimer);
        this._dwoApplySearch();
    },
    /**
     * @private
     */
    _dwoApplySearch: function () {
        if (this.isDestroyed() || !this._documentThread) {
            return;
        }
        this._documentThread.dwoSetSearch(this._$dwoSearch.find('input').val());
        this._fetchAndRenderThread();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _dwoOnClickEdit: function (ev) {
        ev.preventDefault();
        this.do_action('dwo_chatter_filter.action_dwo_chatter_filter');
    },
});

});
