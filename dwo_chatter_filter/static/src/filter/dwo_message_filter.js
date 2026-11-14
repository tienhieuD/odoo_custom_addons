/* @odoo-module */

import { Component, onWillUnmount, useEffect, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";

const ALL_COLOR = "#212529";

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
    return 1.05 / (L + 0.05) >= (L + 0.05) / 0.05 ? "#ffffff" : "#000000";
}

/**
 * The chips at the top of the chatter: All, then the chips the administrator made (see the model
 * dwo.chatter.filter), each with its number of messages. One at a time; a click shows only the messages of
 * that chip. Closing the record forgets the choice. The administrators have a link to edit the chips.
 */
export class DwoMessageFilter extends Component {
    static template = "dwo_chatter_filter.MessageFilter";
    static props = { thread: Object };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.threadService = useService("mail.thread");
        this.isAdmin = Boolean(session.is_admin);
        this.state = useState({ data: null, text: "" });
        this.searchTimer = null;
        this.timer = null;
        this.lastNewestId = undefined;
        onWillUnmount(() => {
            this.unmounted = true;
            clearTimeout(this.timer);
            clearTimeout(this.searchTimer);
        });
        // a new record, or leaving this one: back to all the messages
        useEffect(
            (thread) => {
                this.loadChips();
                this.state.text = thread.dwoSearch || "";
                return () => {
                    clearTimeout(this.timer);
                    clearTimeout(this.searchTimer);
                    this.threadService.dwoReset(thread);
                };
            },
            () => [this.props.thread]
        );
        // a message arrived (bus) or was posted: the numbers follow, and the list if a chip is chosen
        useEffect(
            () => {
                clearTimeout(this.timer);
                this.timer = setTimeout(() => this.onNewMessage(), 400);
            },
            () => [this.props.thread.newestPersistentMessage?.id]
        );
    }

    get items() {
        const data = this.state.data || { all: 0, chips: [] };
        return [{ id: false, label: _t("All"), color: ALL_COLOR, count: data.all }].concat(
            data.chips.map((chip) => ({
                id: chip.id,
                label: chip.name,
                color: chip.color,
                count: chip.count,
            }))
        );
    }

    isActive(item) {
        return (this.props.thread.dwoFilter || false) === item.id;
    }

    isDisabled(item) {
        return Boolean(item.id) && !this.isActive(item) && !item.count;
    }

    chipStyle(item) {
        return `--dwo-chip: ${item.color}; --dwo-chip-text: ${textColorOn(item.color)}`;
    }

    async loadChips() {
        const thread = this.props.thread;
        if (!thread.id || this.unmounted) {
            return;
        }
        try {
            const data = await this.orm.call("mail.message", "dwo_filter_chips", [
                thread.model,
                thread.id,
                thread.dwoSearch || null,
            ]);
            if (this.unmounted) {
                return;
            }
            this.state.data = data;
            // the chip that is chosen was archived or deleted meanwhile: back to all the messages
            if (thread.dwoFilter && !data.chips.some((chip) => chip.id === thread.dwoFilter)) {
                this.threadService.dwoSetFilter(thread, false);
            }
        } catch {
            // the chips are a convenience: without them the row stays hidden
        }
    }

    async onNewMessage() {
        const thread = this.props.thread;
        if (this.unmounted) {
            return;
        }
        const newestId = thread.newestPersistentMessage?.id;
        const changed = newestId !== this.lastNewestId;
        this.lastNewestId = newestId;
        await this.loadChips();
        // the server decides which messages a chip shows: ask it again when a new message came
        if (changed && (thread.dwoFilter || thread.dwoSearch) && !this.unmounted) {
            await this.threadService.dwoReload(thread);
            this.lastNewestId = thread.newestPersistentMessage?.id;
        }
    }

    async select(item) {
        await this.threadService.dwoSetFilter(this.props.thread, item.id);
        this.lastNewestId = this.props.thread.newestPersistentMessage?.id;
    }

    /** Typing: search 300 ms after the last key. */
    onSearchInput(ev) {
        this.state.text = ev.target.value;
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => this.applySearch(), 300);
    }

    onSearchKeydown(ev) {
        if (ev.key === "Escape" && this.state.text) {
            ev.stopPropagation();
            this.clearSearch();
        }
    }

    clearSearch() {
        this.state.text = "";
        clearTimeout(this.searchTimer);
        return this.applySearch();
    }

    async applySearch() {
        const thread = this.props.thread;
        if (this.unmounted) {
            return;
        }
        await this.threadService.dwoSetSearch(thread, this.state.text);
        this.lastNewestId = thread.newestPersistentMessage?.id;
        await this.loadChips();
    }

    edit() {
        this.action.doAction("dwo_chatter_filter.action_dwo_chatter_filter");
    }
}
