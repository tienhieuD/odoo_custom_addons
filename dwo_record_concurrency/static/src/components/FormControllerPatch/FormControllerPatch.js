/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { useBus, useService } from "@web/core/utils/hooks";
import { patch } from '@web/core/utils/patch';
import { userService } from '@web/core/user_service';
import { markup, onMounted, onWillDestroy, onWillUnmount, remove, type, useEffect } from '@odoo/owl';
import { useDebounced } from '@web/core/utils/timing';
import { ConfirmationDialog } from '@web/core/confirmation_dialog/confirmation_dialog';
import { _t } from '@web/core/l10n/translation';
import { escape } from '@web/core/utils/strings';
import { formatDate, formatDateTime } from '@web/core/l10n/dates';

export const RECORD_PRESENCE_CHANNEL_KEY = 'dwo_record_presence';

patch(
    FormController.prototype,
    {
        setup() {
            super.setup();
            this.multiTabService = useService('multi_tab');
            this.busService = this.env.services.bus_service;

            this.currentTabId = this.multiTabService.currentTabId;
            this.channel = null;
            this.isStale = false;
            this.lastUpdateUserName = null;
            this.serverData = null;

            useBus(this.busService, 'notification', this.onPresenceMessage.bind(this));
        },

        /**
         * Dialog confirm save with options:
         *   1. Force save my updates (overwrite server data)
         *   2. Discard all my updates (discard, close the dialog)
         *   2. Cancel (do nothing, close the dialog)
         * @param {Object} options - option
         * @param {Boolean} options.withDiscard - show discard option
         */
        async showConcurrencyWarningDialog(options = {}) {
            const titleText = _t("Saving Record with Concurrency Warning!");
            const confirmText = _t("Force Save");
            const discardText = _t("Discard My Updates");
            const messageHtml = await this.buildConcurrencyWarningMessage();

            return new Promise((resolve) => {
                const dialogProps = {
                    title: titleText,
                    body: messageHtml,
                    bodyPrewrap: false,
                    confirmLabel: confirmText,
                    discardLabel: discardText,
                    confirm: () => resolve("continue"),
                    cancel: () => resolve("cancel"),
                };
                if (options.withDiscard) {
                    dialogProps.discard = () => resolve("discard_and_continue");
                }
                this.dialogService.add(ConfirmationDialog, dialogProps);
            });
        },

        async buildConcurrencyWarningMessage() {
            const messageText = _t(
                "The record has been updated by another user. " +
                "What do you want to do?"
            );
            const lastUpdateText = _t(
                "Last updated by <strong>%s</strong>.",
                this.lastUpdateUserName
            )
            const difference = await this.computeDataDifference();
            const tableHtml = await this.buildDifferenceTableHtml(difference);
            return markup(`
                <p>${messageText}</p>
                ${tableHtml}
                <p><i>${lastUpdateText}</i></p>
            `)
        },

        /**
         * @returns {Promise<{ [key: string]: { local: any, server: any} }>}
         */
        async computeDataDifference() {
            const localChanges = this.model.root._getChanges();
            const serverData = this.serverData;
            const diff = {};
            for (const key in localChanges) {
                if (key === 'id') {
                    continue;
                }
                diff[key] = {
                    local: localChanges[key],
                    server: serverData[key],
                };
            }
            return diff;
        },

        async buildDifferenceTableHtml(difference) {
            const noText = _t("#");
            const fieldText = _t("Field");
            const yourUpdatesText = _t("Your Updates");
            const serverDataText = _t("Latest Data");
            const previewText = _t("Preview Content");
            const cannotPreviewText = _t("Preview not Supported");
            
            // Store display names of many2many fields to avoid multiple orm call for the same field
            const storeDisplayNames = {};
            for (const field in difference) {
                storeDisplayNames[field] = this.props.fields[field].string;
                const fieldType = this.props.fields[field].type;
                if (fieldType === 'many2many' && Array.isArray(difference[field].server)) {
                    // make an orm call to get the display name of many2many records,
                    // because server only return the id of records
                    const record_ids = difference[field].server;
                    const domain = [['id', 'in', record_ids]];
                    const name = ''; // empty name to only search with domain
                    const result = await this.orm.call(this.props.fields[field].relation, "name_search", [], {
                        name: name,
                        operator: "ilike",
                        args: domain,
                        context: this.props.context,
                    });
                    storeDisplayNames[field] = result.map(record => record[1]);
                }
            }

            const getFieldString = (field) => this.props.fields[field].string;
            const getDisplayValue = (field, type) => {
                const fieldType = this.props.fields[field].type;

                if (fieldType === 'many2many') {
                    const displayNameList = type === 'server'
                        ? storeDisplayNames[field]
                        : this.model.root._changes[field].records.map(
                            record => record._textValues.display_name
                        );
                    const formatedDisplayNameList = displayNameList.map(
                        displayName => `<span class="badge text-bg-secondary">${
                            escape(displayName)
                        }</span>`
                    );
                    return formatedDisplayNameList.join(' ');

                } else if (fieldType === 'many2one') {
                    const displayName = type === 'server'
                        ? difference[field].server[1]
                        : this.model.root._changes[field][1];
                    return `<span class="badge text-bg-secondary">${escape(displayName)}</span>`;

                } else if (fieldType === 'datetime' || fieldType === 'date') {
                    const toLuxon = (value, fType) => {
                        const dateFormat = 'yyyy-MM-dd';
                        const datetimeFormat = 'yyyy-MM-dd HH:mm:ss';
                        const zone = { zone: "utc" };
                        if (fType === 'datetime') {
                            return luxon.DateTime.fromFormat(value, datetimeFormat, zone)
                        } else if (fType === 'date') {
                            return luxon.DateTime.fromFormat(value, dateFormat, zone)
                        }
                    }
                    const value = toLuxon(difference[field][type], fieldType);
                    const formatFunc = fieldType === 'datetime' ? formatDateTime : formatDate;
                    return formatFunc(value);

                } else if (fieldType === 'binary') {
                    if (type === 'server') {
                        const model = this.model.root.resModel;
                        const id = this.model.root.resId;
                        const unique = new Date().getTime();
                        return `
                        <a target="_blank"
                            class="badge text-bg-light"
                            href="/web/content/${model}/${id}/${field}?unique=${unique}">
                            ${previewText}
                            <i class="fa fa-external-link"></i>
                        </a>`;
                    } else {
                        return `<span class="badge text-bg-secondary">
                            ${cannotPreviewText}
                            <i class="fa fa-ban"></i>
                        </span>`;
                    }
                    
                } else if (fieldType === 'one2many') {
                    return `<span class="badge text-bg-secondary">
                        ${cannotPreviewText}
                        <i class="fa fa-ban"></i>
                    </span>`;
                    
                }
                return difference[field][type];
            }

            const tableHeaders = `
                <tr>
                    <th name="no">${noText}</th>
                    <th name="field">${fieldText}</th>
                    <th name="your_updates">${yourUpdatesText}</th>
                    <th name="server_data">${serverDataText}</th>
                </tr>
            `;
            const tableRows = Object.keys(difference).map((key, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td>${getFieldString(key)}</td>
                    <td>${getDisplayValue(key, 'local')}</td>
                    <td>${getDisplayValue(key, 'server')}</td>
                </tr>
            `).join('');

            const tableHtml = `
                <table class="table table-sm table-bordered table-hover position-relative mt-2">
                    <thead>
                        ${tableHeaders}
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            `
            return tableHtml;
        },

        async onPagerUpdate() {
            const dirty = await this.model.root.isDirty();
            if (this.isStale && dirty) {
                const choice = await this.showConcurrencyWarningDialog({
                    withDiscard: true
                });
                if (choice === "continue") {
                    this._savedFromPager = true;
                    const res = await super.onPagerUpdate(...arguments);
                    this._savedFromPager = false;
                    return res;
                }
                if (choice === "discard_and_continue") {
                    await this.model.root.discard();
                    return super.onPagerUpdate(...arguments);
                }
                // cancel → stay on page
            }

            return super.onPagerUpdate(...arguments);
        },

        /**
         * @override
         * If record is dirty and stale show dialog to confirm save
         * else make super call
         */
        async beforeLeave() {
            if (this.model.root.dirty && this.isStale) {
                const choice = await this.showConcurrencyWarningDialog({
                    withDiscard: true
                });
                if (choice === "continue") {
                    return super.beforeLeave(...arguments);
                }
                if (choice === "discard_and_continue") {
                    await this.model.root.discard();
                    return super.beforeLeave(...arguments);
                }
                // cancel → stay on page
                return false;
            }
            return super.beforeLeave(...arguments);
        },

        /**
         * @override
         * To prevent the conflict,
         * If record is stale, and dirty, 
         * show browser warning and prevent urgent save of base behavior
         */
        async beforeUnload(ev) {
            const dirty = await this.model.root.isDirty();
            if (this.isStale && dirty) {
                ev.preventDefault();
                ev.returnValue = "";
                return;
            }
            return super.beforeUnload(...arguments);
        },

        /**
         * @override
         * If record is stale, show Dialog to confirm save
         * Return `true` if the record should be saved, `false` to prevent save.
         * @returns {Promise<boolean>}
         */
        async onWillSaveRecord() {
            const res = super.onWillSaveRecord(...arguments);

            if (this._savedFromPager) {
                return res;
            }

            // If record is stale, show dialog
            if (this.isStale) {
                const choice = await this.showConcurrencyWarningDialog({
                    withDiscard: true
                });
                if (choice === "continue") {
                    return true;
                }
                if (choice === "discard_and_continue") {
                    this.discard();
                    return false;
                }
                // cancel → stay on page
                return false;
            }
            return res;
        },

        /**
         * @override
         * Reset `isStale` and `serverData`
         */
        async onRecordSaved() {
            const res = super.onRecordSaved(...arguments);
            this.isStale = false;
            this.serverData = null;
            return res;
        },

        /**
         * @override
         * Set `isStale` to `false` every time the record is loaded.
         */
        onWillLoadRoot(nextConfiguration) {
            super.onWillLoadRoot(...arguments);
            this.reloadChanel(nextConfiguration);
            this.isStale = false;
            this.serverData = null;
        },

        reloadChanel({ resModel, resId }) {
            const model = resModel || this.props.resModel;
            const id = resId || this.props.resId;
            const channelName = `${RECORD_PRESENCE_CHANNEL_KEY}:${model}:${id}`;
            if (this.channel === channelName) {
                return;
            }
            if (this.channel) {
                this.busService.deleteChannel(this.channel);
            }
            this.channel = channelName;
            this.busService.addChannel(channelName);
        },

        /**
         * @param {CustomEvent} event - The event containing the presence message.
         */
        onPresenceMessage(event) {
            const notifications = event.detail;
            for (const notification of notifications) {
                const { type, payload } = notification;
                if (type !== 'dwo_record_presence') {
                    continue;
                }
                const {
                    model,
                    res_id,
                    user_id,
                    user_name,
                    state,
                    current_tab_id,
                    data
                } = payload;

                // Check if should mark record is stale
                if (
                    model === this.model.root.resModel
                    && res_id === this.model.root.resId
                    && state === 'stale'
                    && !(
                        // Do not mark stale if the current tab is the one that made the save
                        user_id === this.user.userId
                        && current_tab_id === this.currentTabId
                    )
                ) {
                    this.isStale = true;
                    this.lastUpdateUserName = user_name;
                    this.serverData = {
                        ...this.serverData,
                        ...data
                    };
                    console.log(`Record ${model} ${res_id} is stale`);
                }
            }
        },
    }
)