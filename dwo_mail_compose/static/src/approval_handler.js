/** @odoo-module **/

import { registerInstancePatchModel } from '@mail/model/model_core';
import { notify } from './composer/dwo_utils';

const NAME = 'dwo_mail_compose/static/src/approval_handler.js';

/**
 * Screen notification when somebody asks for the approval of an email, or decides on yours.
 * The server sends "dwo_mail_approval" on the bus channel of each person concerned; the
 * notification has a button that opens the page of the email. Odoo 15 has no service for it: the
 * handler of the notifications of the messaging is extended.
 */
registerInstancePatchModel('mail.messaging_notification_handler', NAME, {
    /**
     * @override
     */
    async _handleNotifications(notifications) {
        for (const notification of notifications) {
            if (typeof notification === 'object' && notification.type === 'dwo_mail_approval') {
                this._dwoNotify(notification.payload);
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
