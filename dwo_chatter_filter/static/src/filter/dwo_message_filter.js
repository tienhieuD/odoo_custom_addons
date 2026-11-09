/* @odoo-module */

import { Component, onWillUnmount, useEffect, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

// Each kind has its own colour (a Bootstrap contextual colour, and purple, defined in the stylesheet): outlined when off, filled when chosen.
const KINDS = [
    { id: "discussion", label: _t("Discussions"), color: "primary" },
    { id: "email", label: _t("Emails"), color: "info" },
    { id: "activity", label: _t("Activities"), color: "purple" },
    { id: "note", label: _t("Notes"), color: "warning" },
    { id: "tracking", label: _t("Tracking"), color: "success" },
    { id: "other", label: _t("Other"), color: "danger" },
];

/**
 * The badges at the top of the chatter: All, Discussions, Emails, Activities, Notes, Tracking, Other, each with its
 * number of messages. One at a time; a click shows only that kind. Closing the record forgets the choice.
 */
export class DwoMessageFilter extends Component {
    static template = "dwo_chatter_filter.MessageFilter";
    static props = { thread: Object };

    setup() {
        this.orm = useService("orm");
        this.threadService = useService("mail.thread");
        this.state = useState({ counts: null });
        this.timer = null;
        onWillUnmount(() => {
            this.unmounted = true;
            clearTimeout(this.timer);
        });
        // a new record, or leaving this one: back to all the messages
        useEffect(
            (thread) => {
                this.loadCounts();
                return () => {
                    clearTimeout(this.timer);
                    this.threadService.dwoReset(thread);
                };
            },
            () => [this.props.thread]
        );
        // a message arrived (bus) or was posted: the numbers follow
        useEffect(
            () => {
                clearTimeout(this.timer);
                this.timer = setTimeout(() => this.loadCounts(), 400);
            },
            () => [this.props.thread.newestPersistentMessage?.id]
        );
    }

    get items() {
        const counts = this.state.counts || {};
        return [{ id: false, label: _t("All"), color: "dark", count: counts.all ?? 0 }].concat(
            KINDS.map((kind) => ({ ...kind, count: counts[kind.id] ?? 0 }))
        );
    }

    isActive(item) {
        return (this.props.thread.dwoFilter || false) === item.id;
    }

    async loadCounts() {
        const thread = this.props.thread;
        if (!thread.id || this.unmounted) {
            return;
        }
        try {
            this.state.counts = await this.orm.call("mail.message", "dwo_filter_counts", [
                thread.model,
                thread.id,
            ]);
        } catch {
            // the badges are a convenience: without numbers they stay hidden
        }
    }

    select(item) {
        this.threadService.dwoSetFilter(this.props.thread, item.id);
    }
}
