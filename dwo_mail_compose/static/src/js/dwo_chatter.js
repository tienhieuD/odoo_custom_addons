odoo.define('dwo_mail_compose.chatter', function (require) {
'use strict';

/**
 * Odoo 13 and 12: the chatter is a jQuery widget. The Send email button opens the form of the composer in
 * the chatter, in the place of the messages; the messages that are emails get a badge, their From / To / Cc
 * and the buttons Reply, Reply all and Forward.
 */

var AbstractService = require('web.AbstractService');
var Chatter = require('mail.Chatter');
var core = require('web.core');
var Message = require('mail.model.Message');
var session = require('web.session');
var ThreadWidget = require('mail.widget.Thread');
var EmailComposer = require('dwo_mail_compose.EmailComposer').EmailComposer;

var _t = core._t;

var EMAIL_KEYS = [
    'dwo_is_from_compose',
    'outgoing_email_to',
    'outgoing_email_cc',
    'dwo_incoming_email_to_all',
    'incoming_email_to',
    'incoming_email_cc',
];

//------------------------------------------------------------------------------
// The messages
//------------------------------------------------------------------------------

Message.include({
    /**
     * @override
     */
    _setInitialData: function (data) {
        this._super.apply(this, arguments);
        this._dwoData = _.pick(data, EMAIL_KEYS);
        this._dwoMessageType = data.message_type;
    },
    /**
     * An email received, or an official email sent with the Send email button.
     *
     * @returns {boolean}
     */
    dwoIsEmail: function () {
        return Boolean(this._dwoData && this._dwoData.dwo_is_from_compose) || this._dwoMessageType === 'email';
    },
    /**
     * From, To and Cc lines shown under the header of an email. Never the Bcc.
     *
     * @returns {Object[]} [{label, text}]
     */
    dwoMetaLines: function () {
        var data = this._dwoData || {};
        // An address is shown once, at the place of its first appearance, with its name if any line of the
        // email gave one (a header may repeat it with and without a name).
        var format = function (tuples) {
            var unique = {};
            var order = [];
            _.each(tuples || [], function (tuple) {
                var name = tuple[0];
                var email = tuple[1];
                var key = (email || '').toLowerCase();
                if (!unique[key]) {
                    unique[key] = [name, email];
                    order.push(key);
                } else if (name && !unique[key][0]) {
                    unique[key][0] = name;
                }
            });
            return _.map(order, function (key) {
                var pair = unique[key];
                return pair[0] ? pair[0] + ' <' + pair[1] + '>' : pair[1];
            }).join(', ');
        };
        var lines = [];
        if (this._emailFrom) {
            lines.push({label: _t('From'), text: this._emailFrom});
        }
        var isFromCompose = Boolean(data.dwo_is_from_compose);
        var allTo = data.dwo_incoming_email_to_all;
        var to = isFromCompose ? data.outgoing_email_to :
            format(allTo && allTo.length ? allTo : data.incoming_email_to);
        var cc = isFromCompose ? data.outgoing_email_cc : format(data.incoming_email_cc);
        if (to) {
            lines.push({label: _t('To'), text: to});
        }
        if (cc) {
            lines.push({label: _t('Cc'), text: cc});
        }
        return lines;
    },
});

ThreadWidget.include({
    events: _.extend({}, ThreadWidget.prototype.events, {
        'click .o-dwo-emailActions button': '_onDwoClickEmailAction',
    }),
    /**
     * Reply, Reply all or Forward on an email: the form of the chatter of its record opens.
     *
     * @private
     * @param {Event} ev
     */
    _onDwoClickEmailAction: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var $button = $(ev.currentTarget);
        this.trigger_up('dwo_open_email', {
            mode: $button.data('mode'),
            refMessageId: $button.data('message-id'),
        });
    },
});

//------------------------------------------------------------------------------
// The chatter
//------------------------------------------------------------------------------

Chatter.include({
    events: _.extend({}, Chatter.prototype.events, {
        'click .o_dwo_chatter_button_email': '_onDwoToggleEmail',
    }),
    custom_events: _.extend({}, Chatter.prototype.custom_events, {
        dwo_open_email: '_onDwoOpenEmail',
        dwo_email_close: '_onDwoEmailClose',
        dwo_email_sent: '_onDwoEmailSent',
        dwo_email_change: '_onDwoEmailChange',
    }),

    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function (result) {
            self._dwoRefreshDraft();
            return result;
        });
    },
    /**
     * Another record in the same screen: the choice made on the previous one is forgotten.
     *
     * @override
     */
    update: function (record) {
        if (this.record && record && this.record.res_id !== record.res_id) {
            this._dwoRememberedEmailId = false;
            this._dwoCloseEmail();
            var res = this._super.apply(this, arguments);
            this._dwoRefreshDraft();
            return res;
        }
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * The other forms of the chatter close the email form.
     *
     * @override
     */
    _openComposer: function () {
        this._dwoCloseEmail();
        return this._super.apply(this, arguments);
    },
    /**
     * @private
     */
    _dwoCloseEmail: function () {
        if (this._dwoComposer) {
            this._dwoComposer.destroy();
            this._dwoComposer = null;
        }
        this.$el.removeClass('o-dwo-emailOpen');
        this.$('.o_dwo_chatter_button_email').removeClass('o_active');
    },
    /**
     * Opens the form on the saved draft (no mode) or, for a Reply or a Forward, on a new email.
     *
     * @private
     * @param {Object} [options]
     * @param {string} [options.mode]
     * @param {number} [options.refMessageId]
     */
    _dwoOpenEmail: function (options) {
        var self = this;
        options = options || {};
        if (!this.record || !this.record.res_id) {
            return;
        }
        // the standard composer is closed (and kept empty)
        this._closeComposer(true);
        this._dwoCloseEmail();
        var composer = new EmailComposer(this, {
            model: this.record.model,
            resId: this.record.res_id,
            mode: options.mode || false,
            refMessageId: options.refMessageId || false,
            preferredEmailId: options.mode ? false : this._dwoRememberedEmailId,
        });
        this._dwoComposer = composer;
        // the messages are hidden at once: the form fills its place while it loads
        this.$el.addClass('o-dwo-emailOpen');
        composer.insertAfter(this.$('.o_chatter_topbar')).then(function () {
            if (self._dwoComposer !== composer) {
                return;
            }
            self.$el.addClass('o-dwo-emailOpen');
            self.$('.o_chatter_button_new_message, .o_chatter_button_log_note').removeClass('o_active');
            self.$('.o_dwo_chatter_button_email').addClass('o_active');
        });
    },
    /**
     * The dot on the button exists only while the user has a draft on this record.
     *
     * @private
     * @param {boolean} show
     */
    _dwoSetDot: function (show) {
        var $button = this.$('.o_dwo_chatter_button_email');
        $button.find('.o-dwo-draftDot').remove();
        if (show) {
            $('<span class="o-dwo-draftDot bg-primary ml-1" title="You have a draft"/>').appendTo($button);
        }
    },
    /**
     * Does the user have a draft on this record: a dot on the button.
     *
     * @private
     */
    _dwoRefreshDraft: function () {
        var self = this;
        if (!this.record || !this.record.res_id) {
            return;
        }
        var resId = this.record.res_id;
        Promise.resolve(session.rpc('/web/dataset/call_kw/dwo.mail.composer/has_draft', {
            model: 'dwo.mail.composer',
            method: 'has_draft',
            args: [this.record.model, resId],
            kwargs: {context: session.user_context},
        })).then(function (hasDraft) {
            if (!self.isDestroyed() && self.record.res_id === resId) {
                self._dwoSetDot(hasDraft);
            }
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * The Send email button.
     *
     * @private
     */
    _onDwoToggleEmail: function () {
        if (this._dwoComposer) {
            this._dwoCloseEmail();
            this._dwoRefreshDraft();
            return;
        }
        this._dwoOpenEmail();
    },
    /**
     * @private
     * @param {OdooEvent} ev
     */
    _onDwoOpenEmail: function (ev) {
        ev.stopPropagation();
        this._dwoOpenEmail(ev.data);
    },
    /**
     * @private
     * @param {OdooEvent} ev
     */
    _onDwoEmailClose: function (ev) {
        ev.stopPropagation();
        this._dwoCloseEmail();
        this._dwoRefreshDraft();
    },
    /**
     * @private
     * @param {OdooEvent} ev
     */
    _onDwoEmailChange: function (ev) {
        ev.stopPropagation();
        this._dwoRememberedEmailId = ev.data.emailId;
    },
    /**
     * @private
     * @param {OdooEvent} ev
     */
    _onDwoEmailSent: function (ev) {
        ev.stopPropagation();
        this._dwoCloseEmail();
        this._dwoSetDot(false);
        // the email is on the record now: the thread is loaded again
        this.trigger_up('reload', {keepChanges: true});
    },
});

//------------------------------------------------------------------------------
// Screen notification when somebody asks for the approval of an email, or decides on yours
//------------------------------------------------------------------------------

var DwoApprovalService = AbstractService.extend({
    dependencies: ['bus_service', 'notification'],
    /**
     * The server sends "dwo_mail_approval" on the bus channel of each person concerned; the notification
     * has a button that opens the page of the email.
     *
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this.call('bus_service', 'onNotification', this, this._onNotifications);
    },
    /**
     * @private
     * @param {Array} notifications [[channel, message], ...]
     */
    _onNotifications: function (notifications) {
        var self = this;
        _.each(notifications, function (notification) {
            var message = notification[1];
            if (!message || message.type !== 'dwo_mail_approval') {
                return;
            }
            var payload = message.payload;
            var buttons = [];
            if (payload.email_id && payload.kind !== 'closed') {
                buttons.push({
                    text: _t('Open the email'),
                    primary: true,
                    click: function () {
                        // the web client is reached through the registry at the time of the click (a service starts first)
                        odoo.__DEBUG__.services['web.web_client'].do_action({
                            type: 'ir.actions.act_window',
                            res_model: 'dwo.mail.email',
                            res_id: payload.email_id,
                            views: [[false, 'form']],
                            target: 'current',
                        });
                    },
                });
            }
            self.call('notification', 'notify', {
                title: payload.title,
                message: payload.comment ? payload.message + '\n"' + payload.comment + '"' : payload.message,
                type: payload.kind === 'rejected' ? 'warning' : 'info',
                sticky: true,
                buttons: buttons,
            });
        });
    },
});

core.serviceRegistry.add('dwo_mail_approval', DwoApprovalService);

});
