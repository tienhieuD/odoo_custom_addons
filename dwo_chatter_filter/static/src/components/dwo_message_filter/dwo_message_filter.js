/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { _lt } from '@web/core/l10n/translation';

const { Component } = owl;
const { useState } = owl.hooks;

// Each kind has its own colour (a Bootstrap contextual colour, and purple, defined in the stylesheet): outlined when off, filled when chosen.
const KINDS = [
    { id: 'discussion', label: _lt('Discussions'), color: 'primary' },
    { id: 'email', label: _lt('Emails'), color: 'info' },
    { id: 'activity', label: _lt('Activities'), color: 'purple' },
    { id: 'note', label: _lt('Notes'), color: 'warning' },
    { id: 'tracking', label: _lt('Tracking'), color: 'success' },
    { id: 'other', label: _lt('Other'), color: 'danger' },
];

/**
 * The badges at the top of the chatter: All, Discussions, Emails, Activities, Notes, Tracking, Other, each with its
 * number of messages. One at a time; a click shows only that kind. Closing the record forgets the choice.
 */
export class DwoMessageFilter extends Component {

    /**
     * @override
     */
    setup() {
        super.setup();
        this.state = useState({ counts: null });
        this.timer = null;
        this.watched = null;
    }

    mounted() {
        this._loadCounts();
    }

    /** A message arrived (bus) or was posted: the numbers follow. */
    patched() {
        const thread = this.thread;
        const key = thread && thread.id + ':' + (thread.lastMessage ? thread.lastMessage.id : 0);
        if (key !== this.watched) {
            this.watched = key;
            clearTimeout(this.timer);
            this.timer = setTimeout(() => this._loadCounts(), 400);
        }
    }

    willUnmount() {
        this.unmounted = true;
        clearTimeout(this.timer);
        // leaving this record: back to all the messages
        const thread = this.thread;
        if (thread && thread.exists()) {
            thread.dwoReset();
        }
    }

    /** @returns {mail.chatter} */
    get chatter() {
        return this.messaging && this.messaging.models['mail.chatter'].get(this.props.chatterLocalId);
    }

    /** @returns {mail.thread|undefined} */
    get thread() {
        return this.chatter && this.chatter.thread;
    }

    get items() {
        const counts = this.state.counts || {};
        return [{ id: false, label: this.env._t('All'), color: 'dark', count: counts.all || 0 }].concat(
            KINDS.map((kind) => ({ ...kind, label: kind.label.toString(), count: counts[kind.id] || 0 }))
        );
    }

    isActive(item) {
        const thread = this.thread;
        return ((thread && thread.dwoFilter) || false) === item.id;
    }

    async _loadCounts() {
        const thread = this.thread;
        if (!thread || !thread.id || this.unmounted) {
            return;
        }
        try {
            const counts = await this.env.services.rpc({
                model: 'mail.message',
                method: 'dwo_filter_counts',
                args: [thread.model, thread.id],
            });
            if (!this.unmounted) {
                this.state.counts = counts;
            }
        } catch (_e) {
            // the badges are a convenience: without numbers they stay hidden
        }
    }

    /**
     * @param {MouseEvent} ev
     */
    onClickBadge(ev) {
        const kind = ev.currentTarget.dataset.kind;
        const thread = this.thread;
        if (thread) {
            thread.dwoSetFilter(kind === 'all' ? false : kind);
        }
    }
}

Object.assign(DwoMessageFilter, {
    props: { chatterLocalId: String },
    template: 'dwo_chatter_filter.MessageFilter',
});

registerMessagingComponent(DwoMessageFilter);
