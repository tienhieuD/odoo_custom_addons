odoo.define('dwo_mail_compose.AddressInput', function (require) {
'use strict';

/**
 * Email field made of badges. Typing suggests users, partners and the addresses already used; any valid
 * address can be typed. An address is shown once per field; the same address may be in To, Cc and Bcc.
 * Odoo 13 and 12: a jQuery widget (the form is not made of Owl components).
 */

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');

var QWeb = core.qweb;

var EMAIL_RE = /^[^\s@<>,;]+@[^\s@<>,;]+\.[^\s@<>,;]+$/;

/**
 * Parse "Name <a@b.com>", "a@b.com" or a list separated by , ; or new lines.
 * @returns {{email: string, name: string, valid: boolean}[]}
 */
function parseAddresses(text) {
    var result = [];
    _.each((text || '').split(/[,;\n]+/), function (raw) {
        var part = raw.trim();
        if (!part) {
            return;
        }
        var match = part.match(/^(.*?)\s*<([^>]+)>$/);
        var email = (match ? match[2] : part).trim().toLowerCase();
        var name = match ? match[1].replace(/^["']|["']$/g, '').trim() : '';
        result.push({email: email, name: name, valid: EMAIL_RE.test(email)});
    });
    return result;
}

var AddressInput = Widget.extend({
    template: 'dwo_mail_compose.AddressInput',
    events: {
        'input .o-dwo-addressText': '_onInput',
        'keydown .o-dwo-addressText': '_onKeydown',
        'focus .o-dwo-addressText': '_onFocus',
        'click .o-dwo-addressText': '_onFocus',
        'blur .o-dwo-addressText': '_onBlur',
        'paste .o-dwo-addressText': '_onPaste',
        'click .o-dwo-chipRemove': '_onClickRemove',
        'mousedown .o-dwo-suggestion': '_onPickSuggestion',
        'click .o-dwo-addressInput': '_onClickBox',
    },

    /**
     * @param {Widget} parent
     * @param {Object} options
     * @param {string} options.id id of the text input
     * @param {Object[]} [options.value] [{email, name, isNew}]
     * @param {string} [options.placeholder]
     * @param {Function} options.onChange called with the new list
     */
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.inputId = options.id;
        this.value = options.value || [];
        this.placeholder = options.placeholder || '';
        this.onChange = options.onChange;
        this.suggestions = [];
        this.active = -1;
        this.requestId = 0;
        this.timer = null;
    },
    /**
     * @override
     */
    start: function () {
        this.$input = this.$('.o-dwo-addressText');
        this._renderChips();
        return this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    destroy: function () {
        clearTimeout(this.timer);
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Replace the list without telling the parent.
     *
     * @param {Object[]} value
     */
    setValue: function (value) {
        this.value = value || [];
        this._renderChips();
    },
    /**
     * An address typed but not yet turned into a badge becomes one.
     */
    commitPending: function () {
        this._commitText({silent: true});
    },
    /**
     * @returns {boolean} true if text is waiting to be turned into a badge
     */
    hasPendingText: function () {
        return !!this.$input.val().trim();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _renderChips: function () {
        this.$('.o-dwo-chips').html(QWeb.render('dwo_mail_compose.AddressChips', {chips: this.value}));
        this.$input.attr('placeholder', this.value.length ? '' : this.placeholder);
    },
    /**
     * @private
     * @param {Object[]} items
     */
    _add: function (items) {
        var used = _.object(_.map(this.value, function (a) { return [a.email, true]; }));
        var fresh = [];
        _.each(items, function (item) {
            if (!used[item.email]) {
                used[item.email] = true;
                fresh.push(item);
            }
        });
        if (fresh.length) {
            this._change(this.value.concat(fresh));
        }
    },
    /**
     * @private
     * @param {Object[]} value
     */
    _change: function (value) {
        this.value = value;
        this._renderChips();
        this.onChange(value);
    },
    /**
     * @private
     * @param {Object} [options]
     * @param {boolean} [options.silent] no error message when the text is not an address
     */
    _commitText: function (options) {
        var silent = options && options.silent;
        var parsed = parseAddresses(this.$input.val());
        if (!parsed.length) {
            return;
        }
        var valid = _.filter(parsed, function (a) { return a.valid; });
        var invalid = _.reject(parsed, function (a) { return a.valid; });
        this._cancelPendingSuggestions();
        this._hideSuggestions();
        this._add(_.map(valid, function (a) { return {email: a.email, name: a.name, isNew: true}; }));
        if (invalid.length) {
            // keep what could not be read so the user can fix it
            this.$input.val(_.pluck(invalid, 'email').join(', '));
            this.$('.o-dwo-invalidMsg').toggleClass('d-none', !!silent);
            this.$('.o-dwo-addressInput').toggleClass('o-dwo-invalid', !silent);
        } else {
            this.$input.val('');
            this.$('.o-dwo-invalidMsg').addClass('d-none');
            this.$('.o-dwo-addressInput').removeClass('o-dwo-invalid');
        }
        this._renderChips();
    },
    /**
     * @private
     */
    _cancelPendingSuggestions: function () {
        clearTimeout(this.timer);
        this.requestId++;
    },
    /**
     * @private
     */
    _fetchSuggestions: function () {
        var self = this;
        var requestId = ++this.requestId;
        Promise.resolve(session.rpc('/web/dataset/call_kw/dwo.mail.composer/suggest', {
            model: 'dwo.mail.composer',
            method: 'suggest',
            args: [],
            kwargs: {
                query: this.$input.val().trim(),
                exclude: _.pluck(this.value, 'email'),
                context: session.user_context,
            },
        })).then(function (suggestions) {
            if (requestId === self.requestId && !self.isDestroyed()) {
                self.suggestions = suggestions;
                self.active = -1;
                self._renderSuggestions();
            }
        }).catch(function () {
            // a request cut by a page that closes: no suggestions
        });
    },
    /**
     * @private
     */
    _renderSuggestions: function () {
        if (!this.suggestions.length) {
            this._hideSuggestions();
            return;
        }
        // the list exists in the page only while it is open
        if (!this.$('.o-dwo-suggestions').length) {
            $('<div class="o-dwo-suggestions dropdown-menu show w-100" style="top:100%;left:0;max-height:240px;overflow:auto;"/>')
                .appendTo(this.$('.o-dwo-addressInput'));
        }
        this.$('.o-dwo-suggestions').html(QWeb.render('dwo_mail_compose.Suggestions', {
            suggestions: this.suggestions, active: this.active,
        }));
    },
    /**
     * @private
     */
    _hideSuggestions: function () {
        this.suggestions = [];
        this.active = -1;
        this.$('.o-dwo-suggestions').remove();
    },
    /**
     * @private
     * @param {Object} suggestion
     */
    _pick: function (suggestion) {
        this._cancelPendingSuggestions();
        this._add([{email: suggestion.email, name: suggestion.name}]);
        this.$input.val('');
        this._hideSuggestions();
        // the focus comes back to the field without asking for suggestions again
        this._skipFocusFetch = true;
        this.$input.focus();
        this._skipFocusFetch = false;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickBox: function (ev) {
        if (ev.target === ev.currentTarget || $(ev.target).hasClass('o-dwo-chips')) {
            this.$input.focus();
        }
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickRemove: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var email = $(ev.currentTarget).data('email');
        this._change(_.reject(this.value, function (a) { return a.email === email; }));
    },
    /**
     * @private
     */
    _onFocus: function () {
        if (this._skipFocusFetch) {
            return;
        }
        this._fetchSuggestions();
    },
    /**
     * @private
     */
    _onBlur: function () {
        var self = this;
        // let a click on a suggestion happen first
        setTimeout(function () {
            if (self.isDestroyed()) {
                return;
            }
            self._commitText({silent: true});
            self._hideSuggestions();
        }, 120);
    },
    /**
     * @private
     */
    _onInput: function () {
        var self = this;
        this.$('.o-dwo-invalidMsg').addClass('d-none');
        this.$('.o-dwo-addressInput').removeClass('o-dwo-invalid');
        if (/[,;]\s*$/.test(this.$input.val())) {
            this._commitText();
            return;
        }
        clearTimeout(this.timer);
        this.timer = setTimeout(function () {
            self._fetchSuggestions();
        }, 150);
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onKeydown: function (ev) {
        var count = this.suggestions.length;
        var text = this.$input.val();
        if (ev.key === 'ArrowDown' && count) {
            ev.preventDefault();
            this.active = Math.min(this.active + 1, count - 1);
            this._renderSuggestions();
        } else if (ev.key === 'ArrowUp' && count) {
            ev.preventDefault();
            this.active = Math.max(this.active - 1, 0);
            this._renderSuggestions();
        } else if (ev.key === 'Enter' || (ev.key === 'Tab' && text.trim())) {
            if (this.active > -1 && this.suggestions[this.active]) {
                ev.preventDefault();
                this._pick(this.suggestions[this.active]);
            } else if (text.trim()) {
                ev.preventDefault();
                this._commitText();
            }
        } else if (ev.key === 'Escape') {
            this._hideSuggestions();
        } else if (ev.key === 'Backspace' && !text && this.value.length) {
            this._change(this.value.slice(0, -1));
        }
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onPaste: function (ev) {
        var clipboard = ev.originalEvent && ev.originalEvent.clipboardData;
        var text = (clipboard && clipboard.getData('text')) || '';
        if (/[,;\n]/.test(text)) {
            ev.preventDefault();
            this.$input.val(this.$input.val() + text);
            this._commitText();
        }
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onPickSuggestion: function (ev) {
        ev.preventDefault();
        var index = $(ev.currentTarget).data('index');
        if (this.suggestions[index]) {
            this._pick(this.suggestions[index]);
        }
    },
});

return {
    AddressInput: AddressInput,
    parseAddresses: parseAddresses,
};

});
