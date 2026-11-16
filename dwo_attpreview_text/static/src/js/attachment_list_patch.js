/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { AttachmentList } from "@mail/core/common/attachment_list";
import { patch } from "@web/core/utils/patch";

// Odoo shows text files (text/plain, html, json, css, js) itself, as bare text in a frame. With this engine they open
// in the Attachment Preview dialog instead (syntax colours, tree, find...). The core opens the other files.
patch(AttachmentList.prototype, {
    onClickAttachment(attachment) {
        if (attachment.isText && !attachment.uploading && Number.isInteger(attachment.id) && this.dwoAttPreview) {
            const ids = (this.props.attachments || [])
                .filter((a) => !a.uploading && Number.isInteger(a.id))
                .map((a) => a.id);
            this.dwoAttPreview.open(attachment.id, { ids });
            return;
        }
        return super.onClickAttachment(attachment);
    },
});
