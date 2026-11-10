odoo.define('dwo_mail_compose/static/src/approval_handler.js', function (require) {
'use strict';

const { registerInstancePatchModel } = require('mail/static/src/model/model_core.js');
const { notify } = require('dwo_mail_compose/static/src/composer/dwo_utils.js');

const NAME = 'dwo_mail_compose/static/src/approval_handler.js';

/**
 * Screen notification when somebody asks for the approval of an email, or decides on yours.
 * The server sends "dwo_mail_approval" on the bus channel of each person concerned; the
 * notification has a button that opens the page of the email. The handler of the notifications of
 * the messaging is extended.
 */
registerInstancePatchModel('mail.messaging_notification_handler', NAME, {
    /**
     * @override
     */
    async _handleNotifications(notifications) {
        // Odoo 14: a notification is [[db, model, id], message]; ours goes to the channel of the partner
        const partner = this.env.messaging && this.env.messaging.currentPartner;
        for (const notification of notifications) {
            const [channel, message] = notification;
            if (
                Array.isArray(channel) && channel[1] === 'res.partner' && partner && channel[2] === partner.id &&
                message && message.type === 'dwo_mail_approval'
            ) {
                this._dwoNotify(message.payload);
            }
        }
        return this._super(...arguments);
    },

    /**
     * @private
     * @param {Object} payload
     */
    _dwoNotify(payload) {
        const buttons = [];
        if (payload.email_id && payload.kind !== 'closed') {
            buttons.push({
                name: this.env._t('Open the email'),
                primary: true,
                onClick: () =>
                    this.env.bus.trigger('do-action', {
                        action: {
                            type: 'ir.actions.act_window',
                            res_model: 'dwo.mail.email',
                            res_id: payload.email_id,
                            views: [[false, 'form']],
                            target: 'current',
                        },
                    }),
            });
        }
        const message = payload.comment ? `${payload.message}\n"${payload.comment}"` : payload.message;
        notify(this.env, message, {
            title: payload.title,
            type: payload.kind === 'rejected' ? 'warning' : 'info',
            sticky: true,
            buttons,
        });
    },
});

});
