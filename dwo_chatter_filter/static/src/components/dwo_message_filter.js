/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { _lt } from '@web/core/l10n/translation';
import { session } from '@web/session';
import { useService } from '@web/core/utils/hooks';

const { Component, onMounted, onPatched, onWillUnmount, useState } = owl;

const ALL_COLOR = '#212529';

/** Relative luminance (WCAG) of a colour given as #rrggbb. */
function luminance(hex) {
    const [r, g, b] = [1, 3, 5].map((i) => {
        const c = parseInt(hex.slice(i, i + 2), 16) / 255;
        return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** The text of a chip that is filled with that colour: white or black, whichever reads better. */
export function textColorOn(hex) {
    const L = luminance(hex);
    return 1.05 / (L + 0.05) >= (L + 0.05) / 0.05 ? '#ffffff' : '#000000';
}

/**
 * The chips at the top of the chatter: All, then the chips the administrator made (see the model
 * dwo.chatter.filter), each with its number of messages. One at a time; a click shows only the messages of
 * that chip. Closing the record forgets the choice. The administrators have a link to edit the chips.
 * The record of the component is the chatter.
 */
export class DwoMessageFilter extends Component {

    setup() {
        super.setup();
        this.orm = useService('orm');
        this.action = useService('action');
        this.isAdmin = Boolean(session.is_admin);
        this.state = useState({ data: null, text: '' });
        this.searchTimer = null;
        this.timer = null;
        this.watched = null;
        onMounted(() => this._loadChips());
        // a message arrived (bus) or was posted: the numbers follow, and the list if a chip is chosen
        onPatched(() => {
            const key = this.thread && this.thread.id + ':' + (this.thread.lastMessage ? this.thread.lastMessage.id : 0);
            const threadId = this.thread && this.thread.id;
            if (threadId !== this.watchedThreadId) {
                // another record in the same chatter: its own text
                this.watchedThreadId = threadId;
                this.state.text = (this.thread && this.thread.dwoSearch) || '';
            }
            if (key !== this.watched) {
                const first = this.watched === null;
                this.watched = key;
                if (!first) {
                    clearTimeout(this.timer);
                    this.timer = setTimeout(() => this._onNewMessage(), 400);
                }
            }
        });
        onWillUnmount(() => {
            this.unmounted = true;
            clearTimeout(this.timer);
            clearTimeout(this.searchTimer);
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
        const data = this.state.data || { all: 0, chips: [] };
        return [{ id: false, label: this.env._t('All'), color: ALL_COLOR, count: data.all }].concat(
            data.chips.map((chip) => ({ id: chip.id, label: chip.name, color: chip.color, count: chip.count }))
        );
    }

    isActive(item) {
        return ((this.thread && this.thread.dwoFilter) || false) === item.id;
    }

    isDisabled(item) {
        return Boolean(item.id) && !this.isActive(item) && !item.count;
    }

    chipStyle(item) {
        return `--dwo-chip: ${item.color}; --dwo-chip-text: ${textColorOn(item.color)}`;
    }

    async _loadChips() {
        const thread = this.thread;
        if (!thread || !thread.id || this.unmounted) {
            return;
        }
        try {
            const data = await this.orm.call('mail.message', 'dwo_filter_chips', [thread.model, thread.id, thread.dwoSearch || null]);
            if (this.unmounted) {
                return;
            }
            this.state.data = data;
            // the chip that is chosen was archived or deleted meanwhile: back to all the messages
            if (thread.dwoFilter && !data.chips.some((chip) => chip.id === thread.dwoFilter)) {
                thread.dwoSetFilter(false);
            }
        } catch (_e) {
            // the chips are a convenience: without them the row stays hidden
        }
    }

    async _onNewMessage() {
        if (this.unmounted) {
            return;
        }
        await this._loadChips();
        // the server decides which messages a chip shows: ask it again when a new message came
        if (this.thread && this.thread.exists() && (this.thread.dwoFilter || this.thread.dwoSearch) && !this.unmounted) {
            this.thread.dwoReload();
        }
    }

    select(item) {
        if (this.thread) {
            this.thread.dwoSetFilter(item.id);
        }
    }

    /** Typing: search 300 ms after the last key. */
    onSearchInput(ev) {
        this.state.text = ev.target.value;
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => this.applySearch(), 300);
    }

    onSearchKeydown(ev) {
        if (ev.key === 'Escape' && this.state.text) {
            ev.stopPropagation();
            this.clearSearch();
        }
    }

    clearSearch() {
        this.state.text = '';
        clearTimeout(this.searchTimer);
        return this.applySearch();
    }

    async applySearch() {
        const thread = this.thread;
        if (this.unmounted || !thread || !thread.exists()) {
            return;
        }
        thread.dwoSetSearch(this.state.text);
        await this._loadChips();
    }

    edit() {
        this.action.doAction('dwo_chatter_filter.action_dwo_chatter_filter');
    }
}

Object.assign(DwoMessageFilter, {
    props: { record: Object },
    template: 'dwo_chatter_filter.MessageFilter',
});

registerMessagingComponent(DwoMessageFilter);
