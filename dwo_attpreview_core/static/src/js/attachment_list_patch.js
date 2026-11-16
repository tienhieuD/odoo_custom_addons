/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { AttachmentList } from "@mail/core/common/attachment_list";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

// Files Odoo cannot show natively open the Attachment Preview dialog instead of doing nothing.
// Odoo 18: the cards and images of the list call `this.fileViewer.open(attachment, props.attachments)` straight from
// the template (there is no `onClickAttachment` as in 19), and that `open` ignores files that are not viewable.
// So the file viewer of the component is wrapped: non-viewable files go to the preview service.
patch(AttachmentList.prototype, {
    setup() {
        super.setup();
        this.dwoAttPreview = useService("dwo_attpreview");
        const fileViewer = this.fileViewer;
        this.fileViewer = {
            ...fileViewer,
            open: (attachment, files) => {
                if (!attachment.isViewable && !attachment.uploading && Number.isInteger(attachment.id)) {
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
