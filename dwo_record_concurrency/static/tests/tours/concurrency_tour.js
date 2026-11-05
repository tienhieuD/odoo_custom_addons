odoo.define('dwo_record_concurrency.tour', function (require) {
"use strict";

var tour = require('web_tour.tour');

// synchronous on purpose: the legacy tours do not wait for a promise returned by a step
function writeOnServer(vals) {
    var call = function (method, args) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/web/dataset/call_kw/res.partner/' + method, false);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({jsonrpc: '2.0', method: 'call', params: {model: 'res.partner', method: method, args: args, kwargs: {}}}));
        return JSON.parse(xhr.responseText).result;
    };
    var partners = call('search_read', [[['name', 'in', ['DWO Conflict Partner', 'Edited by another user']]], ['id']]);
    call('write', [[partners[0].id], vals]);
}

var NAME = ".o_form_view input[name=name], .o_form_view textarea[name=name]";

function openAndEdit(value) {
    return [
        {trigger: ".o_form_button_edit", run: "click"},
        {trigger: NAME},
        // let the snapshot of the loaded record arrive before the other user writes
        {trigger: ".o_form_view", run: function () { return new Promise(function (resolve) { setTimeout(resolve, 1500); }); }},
        {trigger: NAME, run: "text " + value},
    ];
}

tour.register('dwo_concurrency_conflict', {test: true}, [].concat(openAndEdit("Mine"), [
    {content: "another user saves the same field", trigger: ".o_form_view", run: function () { return writeOnServer({name: "Edited by another user"}); }},
    {trigger: ".o_form_button_save", run: "click"},
    {content: "the conflict dialog shows both values", trigger: ".modal-title:contains('Concurrency Warning')"},
    {trigger: "table td:contains('Edited by another user')"},
    {trigger: "table td:contains('Mine')"},
    {trigger: "button:contains('Cancel')", run: "click"},
    {content: "cancel keeps the unsaved changes", trigger: ".o_form_button_save"},
    {trigger: ".o_form_button_save", run: "click"},
    {trigger: "button:contains('Force Save')", run: "click"},
    {content: "force save overwrites and the form is readonly again", trigger: ".o_form_view.o_form_readonly .o_field_widget[name=name]:contains('Mine')"},
]));

tour.register('dwo_concurrency_no_conflict', {test: true}, [].concat(openAndEdit("Mine"), [
    {content: "another user changes an unwatched field and the name is untouched", trigger: ".o_form_view", run: function () { return writeOnServer({website: "https://example.com"}); }},
    {trigger: ".o_form_button_save", run: "click"},
    {content: "no dialog: the save goes through", trigger: ".o_form_view.o_form_readonly .o_field_widget[name=name]:contains('Mine')"},
    {trigger: "body:not(:has(.modal))"},
]));

tour.register('dwo_concurrency_discard', {test: true}, [].concat(openAndEdit("Mine"), [
    {content: "another user saves the same field", trigger: ".o_form_view", run: function () { return writeOnServer({name: "Edited by another user"}); }},
    {trigger: ".o_form_button_save", run: "click"},
    {trigger: "button:contains('Discard My Updates')", run: "click"},
    {content: "my edits are dropped and the form shows the latest data of the server", trigger: ".o_form_view.o_form_readonly .o_field_widget[name=name]:contains('Edited by another user')"},
]));

});
