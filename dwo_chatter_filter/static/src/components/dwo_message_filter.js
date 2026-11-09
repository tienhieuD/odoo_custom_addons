/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { _lt } from '@web/core/l10n/translation';
import { useService } from '@web/core/utils/hooks';

const { Component, onMounted, onPatched, onWillUnmount, useState } = owl;

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
 * The record of the component is the chatter.
 */
export class DwoMessageFilter extends Component {

    setup() {
        super.setup();
        this.orm = useService('orm');
        this.state = useState({ counts: null });
        this.timer = null;
        this.watched = null;
        onMounted(() => this._loadCounts());
        // a message arrived (bus) or was posted: the numbers follow
        onPatched(() => {
            const key = this.thread && this.thread.id + ':' + (this.thread.lastMessage ? this.thread.lastMessage.id : 0);
            if (key !== this.watched) {
                this.watched = key;
                clearTimeout(this.timer);
                this.timer = setTimeout(() => this._loadCounts(), 400);
            }
        });
        onWillUnmount(() => {
            this.unmounted = true;
            clearTimeout(this.timer);
            // leaving this record: back to all the messages
            if (this.thread && this.thread.exists()) {
                this.thread.dwoReset();
            }
        });
    }

    /** @returns {Thread|undefined} */
    get thread() {
        return this.props.record.thread;
    }

    get items() {
        const counts = this.state.counts || {};
        return [{ id: false, label: this.env._t('All'), color: 'dark', count: counts.all || 0 }].concat(
            KINDS.map((kind) => ({ ...kind, label: kind.label.toString(), count: counts[kind.id] || 0 }))
        );
    }

    isActive(item) {
        return ((this.thread && this.thread.dwoFilter) || false) === item.id;
    }

    async _loadCounts() {
        const thread = this.thread;
        if (!thread || !thread.id || this.unmounted) {
            return;
        }
        try {
            const counts = await this.orm.call('mail.message', 'dwo_filter_counts', [thread.model, thread.id]);
            if (!this.unmounted) {
                this.state.counts = counts;
            }
        } catch (_e) {
            // the badges are a convenience: without numbers they stay hidden
        }
    }

    select(item) {
        if (this.thread) {
            this.thread.dwoSetFilter(item.id);
        }
    }
}

Object.assign(DwoMessageFilter, {
    props: { record: Object },
    template: 'dwo_chatter_filter.MessageFilter',
});

registerMessagingComponent(DwoMessageFilter);
