/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { deserializeDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { formatDateTimeShort } from "./utils";

/** Who sees a page and who may change it. Everything is decided by the server (record rules): this dialog only lists
 * and asks. Recipients always see their own data in the widgets, never the owner's. */
export class ShareDialog extends Component {
    static template = "dwo_dashboard.ShareDialog";
    static components = { Dialog };
    static props = { pageId: Number, pageName: String, hasSql: { type: Boolean, optional: true }, close: Function };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ shares: [], query: "", found: null, level: "view", error: "", log: null });
        this.timer = null;
        onWillStart(async () => {
            this.state.shares = await this.call("get_shares");
        });
    }

    call(method, ...args) {
        return this.orm.call("dwo.dashboard.page", method, [[this.props.pageId], ...args]);
    }

    onQuery(ev) {
        this.state.query = ev.target.value;
        clearTimeout(this.timer);
        this.timer = setTimeout(async () => {
            const q = this.state.query.trim();
            this.state.found = q
                ? await this.orm.call("dwo.dashboard.page", "search_recipients", [q])
                : null;
        }, 200);
    }

    async add(kind, id) {
        try {
            this.state.shares = await this.call(
                "share_with", kind === "user" ? [id] : [], kind === "group" ? [id] : [], this.state.level
            );
            this.state.query = "";
            this.state.found = null;
            this.state.error = "";
        } catch (error) {
            this.state.error = (error.data && error.data.message) || _t("Could not share the page.");
        }
    }

    async setLevel(share, ev) {
        this.state.shares = await this.call(
            "share_with", share.kind === "user" ? [share.user_id] : [], share.kind === "group" ? [share.group_id] : [], ev.target.value
        );
    }

    async revoke(share) {
        this.state.shares = await this.call("revoke_share", share.id);
    }

    async toggleLog() {
        if (this.state.log) {
            this.state.log = null;
            return;
        }
        const rows = await this.orm.call("dwo.dashboard.page", "share_log", [this.props.pageId]);
        const words = { grant: _t("Shared with"), change: _t("Level changed for"), revoke: _t("Revoked from") };
        this.state.log = rows.map((r) => ({
            id: r.id,
            when: formatDateTimeShort(deserializeDateTime(r.create_date)),
            text: `${words[r.action] || r.action} ${r.target}`,
            level: r.action === "revoke" ? "" : r.level === "edit" ? _t("Edit") : _t("View"),
        }));
    }
}
