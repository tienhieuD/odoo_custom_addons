odoo.define('dwo_mail_compose.dialogs', function (require) {
'use strict';

var core = require('web.core');
var Dialog = require('web.Dialog');
var session = require('web.session');

var QWeb = core.qweb;
var _t = core._t;

/**
 * Asks who should approve the email (one or several people, the first decision counts, the author can be
 * one of them) and an optional comment for them.
 *
 * @param {Widget} parent
 * @param {Object} options
 * @param {number[]} [options.allowedIds] the people who can be chosen (empty: every internal user)
 * @param {number|boolean} [options.excludedId] the one who cannot (the author)
 * @param {Function} options.onConfirm called with {approverIds, comment}, may return a promise
 */
function openApprovalDialog(parent, options) {
    var approvers = [];
    var timer = null;
    var requestId = 0;
    var saving = false;
    var dialog = new Dialog(parent, {
        title: _t('Request approval'),
        size: 'medium',
        $content: $(QWeb.render('dwo_mail_compose.ApprovalDialog', {canChooseYourself: !options.excludedId})),
        buttons: [
            {text: _t('Ask for approval'), classes: 'btn-primary o-dwo-approvalConfirm', close: false, click: function () {
                if (!approvers.length || saving) {
                    return;
                }
                saving = true;
                refresh();
                Promise.resolve(options.onConfirm({
                    approverIds: _.pluck(approvers, 'id'),
                    comment: dialog.$('#dwo_approval_comment').val().trim(),
                })).then(function () {
                    dialog.close();
                }, function () {
                    saving = false;
                    refresh();
                });
            }},
            {text: _t('Cancel'), close: true},
        ],
    });
    var $chips, $input, $results, $confirm;

    function refresh() {
        $chips.html(QWeb.render('dwo_mail_compose.ApproverChips', {approvers: approvers}));
        $confirm.prop('disabled', !approvers.length || saving);
    }

    function search() {
        var id = ++requestId;
        var chosen = _.pluck(approvers, 'id');
        if (options.excludedId) {
            chosen.push(options.excludedId);
        }
        var domain = [['share', '=', false], ['id', 'not in', chosen]];
        if (options.allowedIds && options.allowedIds.length) {
            domain.push(['id', 'in', options.allowedIds]);
        }
        Promise.resolve(session.rpc('/web/dataset/call_kw/res.users/name_search', {
            model: 'res.users',
            method: 'name_search',
            args: [],
            kwargs: {name: $input.val().trim(), args: domain, limit: 8, context: session.user_context},
        })).then(function (result) {
            if (id !== requestId) {
                return;
            }
            $results.empty();
            _.each(result, function (item) {
                $('<a href="#" class="o-dwo-approverItem dropdown-item"/>')
                    .attr('data-id', item[0]).text(item[1]).appendTo($results);
            });
            $results.toggleClass('show', result.length > 0);
        });
    }

    dialog.opened().then(function () {
        $chips = dialog.$('.o-dwo-approverChips');
        $input = dialog.$('#dwo_approver_input');
        $results = dialog.$('.o-dwo-approverResults');
        $confirm = dialog.$footer.find('.o-dwo-approvalConfirm');
        refresh();
        $input.on('input focus click', function () {
            clearTimeout(timer);
            timer = setTimeout(search, 150);
        });
        $input.on('blur', function () {
            setTimeout(function () { $results.removeClass('show'); }, 150);
        });
        dialog.$el.on('mousedown', '.o-dwo-approverItem', function (ev) {
            ev.preventDefault();
            var id = $(ev.currentTarget).data('id');
            if (!_.findWhere(approvers, {id: id})) {
                approvers.push({id: id, name: $(ev.currentTarget).text()});
            }
            $input.val('');
            $results.removeClass('show').empty();
            refresh();
        });
        dialog.$el.on('click', '.o-dwo-approverRemove', function (ev) {
            var id = $(ev.currentTarget).data('id');
            approvers = _.reject(approvers, function (user) { return user.id === id; });
            refresh();
        });
    });
    dialog.open();
    return dialog;
}

/**
 * "Save as Template": asks for a name.
 *
 * @param {Widget} parent
 * @param {Function} onSave called with the name, may return a promise
 */
function openSaveTemplateDialog(parent, onSave) {
    var saving = false;
    var dialog = new Dialog(parent, {
        title: _t('Save as Template'),
        size: 'medium',
        $content: $(QWeb.render('dwo_mail_compose.SaveTemplateDialog')),
        buttons: [
            {text: _t('Save'), classes: 'btn-primary o-dwo-saveTemplateConfirm', close: false, click: save},
            {text: _t('Cancel'), close: true},
        ],
    });
    function save() {
        var name = dialog.$('#dwo_template_name').val().trim();
        if (!name || saving) {
            return;
        }
        saving = true;
        Promise.resolve(onSave(name)).then(function () {
            dialog.close();
        }, function () {
            saving = false;
        });
    }
    dialog.opened().then(function () {
        dialog.$('#dwo_template_name').on('keydown', function (ev) {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                save();
            }
        }).focus();
    });
    dialog.open();
    return dialog;
}

/**
 * The template is about to replace text the user wrote: overwrite, add after, or cancel.
 *
 * @param {Widget} parent
 * @param {Object} options
 * @param {Function} options.onOverwrite
 * @param {Function} options.onAppend
 */
function openTemplateConflictDialog(parent, options) {
    var dialog = new Dialog(parent, {
        title: _t('Replace what you are writing?'),
        size: 'medium',
        $content: $(QWeb.render('dwo_mail_compose.TemplateConflictDialog')),
        buttons: [
            {text: _t('Overwrite'), classes: 'btn-primary o-dwo-templateOverwrite', close: true, click: options.onOverwrite},
            {text: _t('Add after my text'), classes: 'btn-secondary o-dwo-templateAppend', close: true, click: options.onAppend},
            {text: _t('Cancel'), close: true},
        ],
    });
    dialog.open();
    return dialog;
}

/**
 * Every deletion asks first.
 *
 * @param {Widget} parent
 * @param {Object} options title, body, confirmLabel, confirm
 */
function confirmDelete(parent, options) {
    var dialog = new Dialog(parent, {
        title: options.title,
        size: 'medium',
        $content: $('<div/>').text(options.body),
        buttons: [
            {text: options.confirmLabel || _t('Delete'), classes: 'btn-primary o-dwo-confirmDelete', close: true, click: options.confirm},
            {text: _t('Cancel'), close: true},
        ],
    });
    dialog.open();
    return dialog;
}

return {
    openApprovalDialog: openApprovalDialog,
    openSaveTemplateDialog: openSaveTemplateDialog,
    openTemplateConflictDialog: openTemplateConflictDialog,
    confirmDelete: confirmDelete,
};

});
