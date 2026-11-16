/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { AttachmentList } from "@mail/core/common/attachment_list";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

// Files Odoo cannot show natively open the Attachment Preview dialog instead of doing nothing.
// Odoo 20: Odoo's own viewer now also opens csv, markdown, xml and audio, which it did not in 19. As in 19, these
// open the Attachment Preview dialog; when no engine can preview one, Odoo's viewer opens it (no toast).
const ODOO20_NEW_VIEWABLE = ["text/csv", "text/markdown", "application/xml", "text/xml"];

function dwoOdoo19Viewable(attachment) {
    return attachment.isViewable && !attachment.isAudio && !ODOO20_NEW_VIEWABLE.includes(attachment.mimetype);
}

patch(AttachmentList.prototype, {
    setup() {
        super.setup();
        this.dwoAttPreview = useService("dwo_attpreview");
    },
    onClickAttachment(attachment) {
        // Odoo 20: the list gets attachmentGroups (not attachments) and a selection mode where a click selects
        if (!this.props.isSelecting && !dwoOdoo19Viewable(attachment) && !attachment.uploading && Number.isInteger(attachment.id)) {
            const ids = (this.props.attachmentGroups || []).map((group) => group.attachment)
                .filter((a) => !a.uploading && Number.isInteger(a.id))
                .map((a) => a.id);
            const onUnavailable = attachment.isViewable ? () => super.onClickAttachment(attachment) : undefined;
            this.dwoAttPreview.open(attachment.id, { ids, onUnavailable });
            return;
        }
        return super.onClickAttachment(attachment);
    },
});
