odoo.define('dwo_mail_compose/static/src/composer/dwo_utils.js', function (require) {
'use strict';

const session = require('web.session');

/**
 * Call a method of a model (what the orm service of Odoo 16 does): Odoo 15 only has the rpc service.
 *
 * @param {Object} env
 * @param {string} model
 * @param {string} method
 * @param {Array} [args]
 * @param {Object} [kwargs]
 * @returns {Promise}
 */
function orm(env, model, method, args = [], kwargs = {}) {
    return env.services.rpc({
        model,
        method,
        args,
        kwargs: Object.assign({ context: session.user_context }, kwargs),
    });
}

/** Text of an HTML string, without loading anything (a parsed document is inert). */
function textOf(html) {
    const doc = new DOMParser().parseFromString(html || '', 'text/html');
    return (doc.body.textContent || '').replace(/\s+/g, ' ').trim();
}

/** Cut a body in what the user writes (above) and the quoted email (from the quote block on). */
function splitBody(html) {
    const doc = new DOMParser().parseFromString(html || '', 'text/html');
    const root = doc.body;
    const quote = root.querySelector('#divRplyFwdMsg');
    if (!quote) {
        return { above: root.innerHTML, quote: '' };
    }
    let top = quote;
    while (top.parentElement && top.parentElement !== root) {
        top = top.parentElement;
    }
    const nodes = [...root.childNodes];
    const index = nodes.indexOf(top);
    const serialize = (list) => {
        const holder = doc.createElement('div');
        list.forEach((node) => holder.appendChild(node.cloneNode(true)));
        return holder.innerHTML;
    };
    return { above: serialize(nodes.slice(0, index)), quote: serialize(nodes.slice(index)) };
}

/**
 * The body without the empty lines at its start: the lines a user finds to write in when an email
 * is started. What remains is the signature (and nothing else when there is none).
 */
function withoutLeadingBlankLines(html) {
    const doc = new DOMParser().parseFromString(html || '', 'text/html');
    const root = doc.body;
    const isBlank = (node) =>
        node.nodeType === Node.TEXT_NODE
            ? !node.textContent.trim()
            : ['P', 'DIV'].includes(node.tagName) &&
              !node.textContent.trim() &&
              ![...node.children].some((child) => child.tagName !== 'BR');
    while (root.firstChild && isBlank(root.firstChild)) {
        root.removeChild(root.firstChild);
    }
    return root.innerHTML;
}

/** "2026-11-09 08:15:00" (UTC, as the server sends it) as a short local date. */
function formatListDate(serialized) {
    if (!serialized) {
        return '';
    }
    const date = new Date(serialized.replace(' ', 'T') + 'Z');
    return date.toLocaleString([], { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

/**
 * A screen notification. Odoo 15 gives the Owl environment the legacy service: notify({ message, type, title,
 * sticky, buttons: [{ text, primary, click }] }) (Odoo 16 has add(message, options)).
 */
function notify(env, message, { title, type, sticky, buttons } = {}) {
    env.services.notification.notify({
        message,
        title,
        type,
        sticky,
        buttons: (buttons || []).map((button) => ({
            text: button.name,
            primary: button.primary,
            click: button.onClick,
        })),
    });
}

return { orm, textOf, splitBody, withoutLeadingBlankLines, formatListDate, notify };

});
