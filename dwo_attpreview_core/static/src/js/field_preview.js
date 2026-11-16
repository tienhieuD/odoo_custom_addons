/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
// Preview buttons on the file fields of a form or a list: binary, many2many_binary, many2one to an attachment
// and every list or kanban of attachments (one2many / many2many / the Attachments menu). Each button opens the dialog of
// the "dwo_attpreview" service; what Odoo does on these fields (download, edit, clear, delete) is unchanged.
import { Component, useProps } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { BinaryField } from "@web/views/fields/binary/binary_field";
// Odoo 20: the files of many2many_binary are drawn by Many2XBinary (template web.Many2XBinary.attachment_preview)
import { Many2XBinary } from "@web/views/fields/many2x_binary/many2x_binary";
import { Many2One } from "@web/views/fields/many2one/many2one";
import { ListRenderer } from "@web/views/list/list_renderer";
import { KanbanRecord } from "@web/views/kanban/kanban_record";

const ATTACHMENT = "ir.attachment";

// --- binary --------------------------------------------------------------
patch(BinaryField.prototype, {
    setup() {
        super.setup(...arguments);
        this.dwoAttPreview = useService("dwo_attpreview");
    },
    /** A saved file only: a file just uploaded and not saved yet is not on the server. */
    get dwoCanPreview() {
        const { record, name } = this.props;
        // Odoo 20: a saved file reads as {size, checksum[, filename]}; a file just uploaded carries its "content"
        const value = record.data[name];
        return !!(record.resId && value && typeof value === "object" && !("content" in value));
    },
    onDwoPreview() {
        const { record, name, fileNameField } = this.props;
        if (record.resModel === ATTACHMENT && ["datas", "raw"].includes(name)) {
            // the record is the attachment: same preview as in the chatter
            return this.dwoAttPreview.open(record.resId);
        }
        return this.dwoAttPreview.openField({
            model: record.resModel,
            resId: record.resId,
            field: name,
            filenameField: fileNameField in record.fields ? fileNameField : undefined,
        });
    },
});

// --- many2many_binary ----------------------------------------------------
patch(Many2XBinary.prototype, {
    setup() {
        super.setup(...arguments);
        this.dwoAttPreview = useService("dwo_attpreview");
    },
    dwoCanPreviewFile(file) {
        // Odoo 20: Many2XBinary also draws many2one_binary; the eye stays on many2many_binary only, as in 19
        return !!this.props.multiUpload && Number.isInteger(file.id) && file.id > 0;
    },
    onDwoPreviewFile(file) {
        return this.dwoAttPreview.open(file.id);
    },
});

// --- many2one to ir.attachment ---------------------------------------------
patch(Many2One.prototype, {
    setup() {
        super.setup(...arguments);
        this.dwoAttPreview = useService("dwo_attpreview");
    },
    get dwoCanPreview() {
        return this.props.relation === ATTACHMENT && !!(this.props.value && this.props.value.id);
    },
    onDwoPreview() {
        return this.dwoAttPreview.open(this.props.value.id);
    },
});

// --- kanban of ir.attachment (the Attachments menu opens on it) -------------
patch(KanbanRecord.prototype, {
    setup() {
        super.setup(...arguments);
        this.dwoAttPreview = useService("dwo_attpreview");
    },
    get dwoCanPreview() {
        const record = this.props.record;
        return record.resModel === ATTACHMENT && !!record.resId && record.data.type !== "url";
    },
    onDwoPreview() {
        return this.dwoAttPreview.open(this.props.record.resId);
    },
});

// --- lists of ir.attachment ------------------------------------------------
/** The cell of the column added to every list of attachments. */
export class AttPreviewListButton extends Component {
    static template = "dwo_attpreview_core.ListButton";
    // Odoo 20 (Owl 3): no static props; record, readonly and any other prop of a view widget
    props = useProps();

    setup() {
        this.dwoAttPreview = useService("dwo_attpreview");
    }

    get canPreview() {
        return !!this.props.record.resId;
    }

    onClick() {
        return this.dwoAttPreview.open(this.props.record.resId);
    }
}

export const attPreviewListButton = {
    component: AttPreviewListButton,
    listViewWidth: 40,
};
registry.category("view_widgets").add("dwo_attpreview_button", attPreviewListButton);

const LIST_COLUMN = {
    type: "widget",
    id: "column_dwo_attpreview",
    name: "dwo_attpreview_button",
    widget: attPreviewListButton,
    options: {},
    attrs: {},
    props: {
        name: "dwo_attpreview_button",
        className: "",
        widgetInfo: { name: "dwo_attpreview_button", widget: attPreviewListButton, options: {}, attrs: {} },
    },
};

patch(ListRenderer.prototype, {
    processAllColumn(allColumns, list) {
        const columns = super.processAllColumn(...arguments);
        // a list (or a one2many / many2many field) of attachments gets a Preview button on each row, unless
        // its view already places the widget itself
        if (list && list.resModel === ATTACHMENT && !columns.some((c) => c.name === LIST_COLUMN.name)) {
            return [...columns, LIST_COLUMN];
        }
        return columns;
    },
});
