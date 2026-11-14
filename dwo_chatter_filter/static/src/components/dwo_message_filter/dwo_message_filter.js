/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
import session from 'web.session';

const { Component } = owl;
const { useState } = owl.hooks;

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
 */
export class DwoMessageFilter extends Component {

    /**
     * @override
     */
    setup() {
        super.setup();
        this.isAdmin = Boolean(session.is_admin);
        this.state = useState({ data: null, text: '' });
        this.searchTimer = null;
        this.timer = null;
        this.watched = null;
    }

    mounted() {
        // Odoo 15 can mount the same component again (back from the list of chips): it is alive again
        this.unmounted = false;
        this.chatterLocalId = this.props.chatterLocalId;
        this._loadChips();
        // Odoo 15 keeps this component when the record is shown again (back from the list of chips): the chips are read again
        this.env.bus.on('ACTION_MANAGER:UI-UPDATED', this, this._onUiUpdated);
    }

    _onUiUpdated() {
        if (!this.unmounted) {
            this._loadChips();
        }
    }

    /** A message arrived (bus) or was posted: the numbers follow, and the list if a chip is chosen. */
    patched() {
        // the record was shown again (back from the list of chips, say): the chatter is a new one, the chips are read again
        if (this.props.chatterLocalId !== this.chatterLocalId) {
            this.chatterLocalId = this.props.chatterLocalId;
            this.state.text = (this.thread && this.thread.dwoSearch) || '';
            this._loadChips();
        }
        const thread = this.thread;
        if (thread && thread.id && !this.state.data && !this.loading) {
            // the thread was not there yet when the component was mounted
            this._loadChips();
        }
        const key = thread && thread.id + ':' + (thread.lastMessage ? thread.lastMessage.id : 0);
        if (key !== this.watched) {
            const first = this.watched === null;
            this.watched = key;
            if (!first) {
                clearTimeout(this.timer);
                this.timer = setTimeout(() => this._onNewMessage(), 400);
            }
        }
    }

    willUnmount() {
        this.unmounted = true;
        this.env.bus.off('ACTION_MANAGER:UI-UPDATED', this);
        clearTimeout(this.timer);
        clearTimeout(this.searchTimer);
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
        const data = this.state.data || { all: 0, chips: [] };
        return [{ id: false, label: this.env._t('All'), color: ALL_COLOR, count: data.all }].concat(
            data.chips.map((chip) => ({ id: chip.id, label: chip.name, color: chip.color, count: chip.count }))
        );
    }

    isActive(item) {
        const thread = this.thread;
        return ((thread && thread.dwoFilter) || false) === item.id;
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
        this.loading = true;
        try {
            const data = await this.env.services.rpc({
                model: 'mail.message',
                method: 'dwo_filter_chips',
                args: [thread.model, thread.id, thread.dwoSearch || null],
            });
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
        } finally {
            this.loading = false;
        }
    }

    async _onNewMessage() {
        if (this.unmounted) {
            return;
        }
        await this._loadChips();
        // the server decides which messages a chip shows: ask it again when a new message came
        const thread = this.thread;
        if (thread && thread.exists() && (thread.dwoFilter || thread.dwoSearch) && !this.unmounted) {
            thread.dwoReload();
        }
    }

    /**
     * @param {MouseEvent} ev
     */
    onClickChip(ev) {
        const chip = ev.currentTarget.dataset.chip;
        const thread = this.thread;
        if (thread) {
            thread.dwoSetFilter(chip === 'all' ? false : parseInt(chip, 10));
        }
    }

    /**
     * Typing: search 300 ms after the last key.
     *
     * @param {InputEvent} ev
     */
    onSearchInput(ev) {
        this.state.text = ev.target.value;
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => this._applySearch(), 300);
    }

    /**
     * @param {KeyboardEvent} ev
     */
    onSearchKeydown(ev) {
        if (ev.key === 'Escape' && this.state.text) {
            ev.stopPropagation();
            this.onClickClearSearch();
        }
    }

    onClickClearSearch() {
        this.state.text = '';
        clearTimeout(this.searchTimer);
        return this._applySearch();
    }

    async _applySearch() {
        const thread = this.thread;
        if (this.unmounted || !thread || !thread.exists()) {
            return;
        }
        thread.dwoSetSearch(this.state.text);
        await this._loadChips();
    }

    onClickEdit() {
        this.env.bus.trigger('do-action', { action: 'dwo_chatter_filter.action_dwo_chatter_filter' });
    }
}

Object.assign(DwoMessageFilter, {
    props: { chatterLocalId: String },
    template: 'dwo_chatter_filter.MessageFilter',
});

registerMessagingComponent(DwoMessageFilter);
