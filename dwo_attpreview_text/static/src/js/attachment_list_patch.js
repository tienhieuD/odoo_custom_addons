/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { AttachmentList } from "@mail/core/common/attachment_list";
import { patch } from "@web/core/utils/patch";

// Odoo shows text files (text/plain, html, json, css, js) itself, as bare text in a frame. With this engine they open
// in the Attachment Preview dialog instead (syntax colours, tree, find...). The core opens the other files.
// Odoo 18: there is no `onClickAttachment` as in 19 (the template calls `this.fileViewer.open(...)` straight away), so
// the file viewer of the component, already wrapped by the core, is wrapped once more for text files.
patch(AttachmentList.prototype, {
    setup() {
        super.setup();
        const fileViewer = this.fileViewer;
        this.fileViewer = {
            ...fileViewer,
            open: (attachment, files) => {
                if (attachment.isText && !attachment.uploading && Number.isInteger(attachment.id) && this.dwoAttPreview) {
                    const ids = (this.props.attachments || [])
                        .filter((a) => !a.uploading && Number.isInteger(a.id))
                        .map((a) => a.id);
                    this.dwoAttPreview.open(attachment.id, { ids });
                    return;
                }
                return fileViewer.open(attachment, files);
            },
        };
    },
});
