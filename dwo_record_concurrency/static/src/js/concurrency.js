odoo.define('dwo_record_concurrency.tab', function () {
"use strict";

return {
    // one identifier per browser tab / page load: lets a tab ignore the notification of its own save
    TAB_ID: Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10),
    CHANNEL_PREFIX: 'dwo_record_presence',
};

});

odoo.define('dwo_record_concurrency.FormController', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var FormController = require('web.FormController');
var fieldUtils = require('web.field_utils');
var tab = require('dwo_record_concurrency.tab');

var _t = core._t;
var MODEL = 'dwo.model.concurrency';
// watched fields per model, shared by every form of the page
var watchedFieldsByModel = {};

/**
 * Soft concurrency control. Nothing here can refuse a save: when the fields the user is saving were changed on the
 * server after the form was loaded, a dialog lets the user choose Force Save / Discard / Cancel.
 *
 * Every way of saving goes through `saveRecord`, which is therefore the single place where the check is made.
 * The bus only gives early information.
 */
FormController.include({
    init: function () {
        this._super.apply(this, arguments);
        this._dwoChannel = null;
        this._dwoToken = 0;
        this._dwoSnapshot = null;   // normalized values of the watched fields, taken at load
        this._dwoWatched = [];
        this._dwoStale = null;      // {fields: [...], userName} told by the bus
        this._dwoKey = null;        // model:id of the record the snapshot belongs to
    },

    start: function () {
        var self = this;
        this.call('bus_service', 'onNotification', this, this._dwoOnNotification);
        this._dwoUnload = function (ev) {
            // closing the tab: the unload cannot wait for a server answer, so it relies on what the bus told us
            if (self._dwoStale && self.handle && self.model.isDirty(self.handle)) {
                ev.preventDefault();
                ev.returnValue = '';
            }
        };
        window.addEventListener('beforeunload', this._dwoUnload);
        return this._super.apply(this, arguments);
    },

    destroy: function () {
        window.removeEventListener('beforeunload', this._dwoUnload);
        this._dwoSetChannel(null);
        this._super.apply(this, arguments);
    },

    /**
     * Called after every (re)load: follow the record that is displayed.
     * @override
     */
    update: function () {
        var self = this;
        var result = this._super.apply(this, arguments);
        var done = function () {
            self._dwoOnUpdate();
        };
        if (result && result.then) {
            result.then(done);
        }
        return result;
    },

    // ------------------------------------------------------------------ record followed
    _dwoState: function () {
        return this.handle ? this.model.get(this.handle, {raw: true}) : null;
    },

    _dwoOnUpdate: function () {
        var state = this._dwoState();
        if (!state) {
            return;
        }
        var key = state.res_id ? state.model + ':' + state.res_id : null;
        if (key === this._dwoKey) {
            return;
        }
        this._dwoKey = key;
        this._dwoStale = null;
        this._dwoSetChannel(key ? tab.CHANNEL_PREFIX + ':' + key : null);
        this._dwoRefreshSnapshot();
    },

    _dwoSetChannel: function (channel) {
        if (this._dwoChannel === channel) {
            return;
        }
        if (this._dwoChannel) {
            this.call('bus_service', 'deleteChannel', this._dwoChannel);
        }
        this._dwoChannel = channel;
        if (channel) {
            this.call('bus_service', 'addChannel', channel);
            this.call('bus_service', 'startPolling');
        }
    },

    _dwoRefreshSnapshot: function () {
        var self = this;
        var token = ++this._dwoToken;
        var state = this._dwoState();
        this._dwoSnapshot = null;
        if (!state || !state.res_id) {
            return;
        }
        if (!watchedFieldsByModel[state.model]) {
            watchedFieldsByModel[state.model] = this._rpc({
                model: MODEL, method: 'get_watched_fields', args: [state.model],
            });
        }
        this._dwoPending = Promise.resolve(watchedFieldsByModel[state.model]).then(function (watched) {
            if (token !== self._dwoToken || !watched.length) {
                return;
            }
            return Promise.resolve(self._rpc({
                model: MODEL, method: 'dwo_snapshot', args: [state.model, state.res_id],
            })).then(function (snapshot) {
                if (token === self._dwoToken) {
                    self._dwoWatched = watched;
                    self._dwoSnapshot = snapshot;
                }
            });
        }).catch(function () {
            delete watchedFieldsByModel[state.model];   // soft: without a snapshot we simply do not check
        });
    },

    _dwoChangedFields: function (handle) {
        var record = this.model.localData[handle];
        return record ? _.keys(record._changes || {}) : [];
    },

    // ------------------------------------------------------------------ bus (early information only)
    _dwoOnNotification: function (notifications) {
        var self = this;
        var state = this._dwoState();
        if (!state) {
            return;
        }
        _.each(notifications, function (notification) {
            // 15: {type, payload}; 12 .. 14: [channel, {type, payload}]
            var message = _.isArray(notification) ? notification[1] : notification;
            if (!message || message.type !== 'dwo_record_presence') {
                return;
            }
            var payload = message.payload;
            if (payload.model !== state.model || payload.res_id !== state.res_id ||
                    payload.current_tab_id === tab.TAB_ID) {
                return;
            }
            var fields = _.union((self._dwoStale && self._dwoStale.fields) || [], payload.fields);
            self._dwoStale = {fields: fields, userName: payload.user_name};
            // commit what the user is typing: until then the record does not know the edit yet
            Promise.resolve(self.renderer.commitChanges(self.handle)).then(function () {
                if (_.intersection(payload.fields, self._dwoChangedFields(self.handle)).length) {
                    // Odoo 12 has no displayNotification
                    self.do_warn(_t("Concurrency warning"), _.str.sprintf(
                        _t("%s changed fields you are editing. You will be asked before saving."),
                        payload.user_name));
                }
            });
        });
    },

    // ------------------------------------------------------------------ the check
    /**
     * @override
     */
    saveRecord: function (recordID) {
        var self = this;
        var superSave = this._super.bind(this);     // _super is only available synchronously
        var args = arguments;
        var handle = recordID || this.handle;
        if (handle !== this.handle) {
            return superSave.apply(this, args);
        }
        // a snapshot still being fetched is waited for (it only takes a round trip)
        var deferred = $.Deferred();
        Promise.resolve(this._dwoPending).then(function () {
            return self._dwoSave(superSave, args, handle);
        }).then(function (result) {
            deferred.resolve(result);
        }, function (error) {
            deferred.reject(error);
        });
        return deferred.promise();
    },

    _dwoSave: function (superSave, args, handle) {
        var self = this;
        // the context of the record carries the id of this tab, so the server can tell who wrote
        var record = this.model.localData[handle];
        record.context = _.extend({}, record.context, {current_tab_id: tab.TAB_ID});
        if (!this._dwoSnapshot) {
            return superSave.apply(this, args);
        }
        return Promise.resolve(this.renderer.commitChanges(handle)).then(function () {
            return self._dwoCheck(handle);
        }).then(function (proceed) {
            if (!proceed) {
                return Promise.reject('dwo_record_concurrency: save cancelled by the user');
            }
            return superSave.apply(self, args);
        }).then(function (result) {
            self._dwoStale = null;
            self._dwoRefreshSnapshot();
            return result;
        });
    },

    /**
     * @returns {Promise<boolean>} true to go on with the save
     */
    _dwoCheck: function (handle) {
        var self = this;
        var dirty = _.intersection(this._dwoChangedFields(handle), this._dwoWatched);
        if (!dirty.length) {
            return Promise.resolve(true);
        }
        var state = this._dwoState();
        return Promise.resolve(this._rpc({
            model: MODEL, method: 'dwo_check_conflict',
            args: [state.model, state.res_id, this._dwoSnapshot, dirty],
        })).then(function (conflicts) {
            if (!conflicts.length) {
                return true;
            }
            if (document.visibilityState === 'hidden') {
                return false;   // automatic save of a hidden tab: keep the changes, ask nothing, overwrite nothing
            }
            return self._dwoAsk(conflicts, handle);
        }, function (error, event) {
            if (event && event.preventDefault) {
                event.preventDefault();
            }
            return true;        // soft: if the check itself fails, never get in the way of the save
        });
    },

    _dwoDisplayValue: function (handle, conflict) {
        var state = this.model.get(handle);
        try {
            return String(fieldUtils.format[conflict.type](state.data[conflict.name], state.fields[conflict.name], {
                data: state.data, forceString: true,
            }) || '');
        } catch (e) {
            return '';
        }
    },

    _dwoAsk: function (conflicts, handle) {
        var self = this;
        var $content = $('<div/>');
        $content.append($('<p/>').text(_t("Another user changed fields you are editing. What do you want to do?")));
        var $table = $('<table class="table table-sm table-bordered mt-2"/>').appendTo($content);
        $table.append($('<thead/>').append($('<tr/>')
            .append($('<th/>').text('#'))
            .append($('<th/>').text(_t("Field")))
            .append($('<th/>').text(_t("Your Updates")))
            .append($('<th/>').text(_t("Latest Data")))));
        var $body = $('<tbody/>').appendTo($table);
        _.each(conflicts, function (conflict, index) {
            $body.append($('<tr/>')
                .append($('<td/>').text(index + 1))
                .append($('<td/>').text(conflict.label))
                .append($('<td/>').append($('<span class="badge badge-secondary"/>').text(self._dwoDisplayValue(handle, conflict))))
                .append($('<td/>').append($('<span class="badge badge-secondary"/>').text(conflict.server))));
        });
        var writer = (_.find(conflicts, function (conflict) { return conflict.write_uid_name; }) || {}).write_uid_name;
        if (writer) {
            $content.append($('<p class="font-italic"/>').text(_.str.sprintf(_t("Last updated by %s."), writer)));
        }
        return new Promise(function (resolve) {
            var choice = function (value) {
                return function () {
                    resolve(value === 'continue');
                    if (value === 'discard') {
                        // drop the edits, then show the latest data of the server instead of the values the form
                        // was opened with
                        setTimeout(function () {
                            self.model.discardChanges(handle);
                            self.update({mode: 'readonly'}, {reload: true});
                            self._dwoStale = null;
                        });
                    }
                };
            };
            new Dialog(self, {
                title: _t("Saving Record with Concurrency Warning!"),
                size: 'large',
                $content: $content,
                buttons: [
                    {text: _t("Force Save"), classes: 'btn-primary', close: true, click: choice('continue')},
                    {text: _t("Discard My Updates"), close: true, click: choice('discard')},
                    {text: _t("Cancel"), close: true, click: choice('cancel')},
                ],
                onForceClose: choice('cancel'),
            }).open();
        });
    },
});

});
