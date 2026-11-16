/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
// File type -> icon kind. The icons are the original SVG set of this module (static/img/dwo_attpreview_<kind>.svg).
const BY_EXT = {
    pdf: ["pdf"],
    word: ["doc", "docx", "docm", "dot", "dotx", "odt", "rtf"],
    sheet: ["xls", "xlsx", "xlsm", "xlsb", "xltx", "ods", "csv", "tsv"],
    slide: ["ppt", "pptx", "pptm", "pps", "ppsx", "odp"],
    image: ["png", "jpg", "jpeg", "gif", "webp", "avif", "bmp", "svg", "tif", "tiff", "ico", "heic"],
    video: ["mp4", "webm", "mov", "mkv", "avi", "m4v", "ogv"],
    audio: ["mp3", "wav", "ogg", "oga", "m4a", "flac", "aac", "opus"],
    archive: ["zip", "rar", "7z", "tar", "gz", "tgz", "bz2", "xz", "jar"],
    markdown: ["md", "markdown"],
    code: ["json", "xml", "html", "htm", "js", "mjs", "ts", "py", "css", "scss", "yml", "yaml", "sql", "sh", "java", "c", "cpp", "h", "php", "rb", "go", "rs"],
    text: ["txt", "log", "ini", "cfg", "conf", "rst"],
    mail: ["eml", "msg", "oft", "mbox", "emlx", "ics", "vcf"],
    cad: ["dxf", "dwg", "dwf", "stl"],
};
const EXT_TO_KIND = {};
for (const [kind, exts] of Object.entries(BY_EXT)) {
    for (const ext of exts) {
        EXT_TO_KIND[ext] = kind;
    }
}

export const DWO_ATTPREVIEW_KINDS = [...Object.keys(BY_EXT), "default"];

/** Icon kind of a file from its name (first) and its mimetype (fallback). */
export function dwoAttPreviewKind(name, mimetype) {
    const dot = (name || "").lastIndexOf(".");
    const ext = dot >= 0 ? name.slice(dot + 1).toLowerCase() : "";
    if (EXT_TO_KIND[ext]) {
        return EXT_TO_KIND[ext];
    }
    const mime = mimetype || "";
    if (mime === "application/pdf") return "pdf";
    if (mime.startsWith("image/")) return "image";
    if (mime.startsWith("video/")) return "video";
    if (mime.startsWith("audio/")) return "audio";
    if (mime.startsWith("text/")) return "text";
    if (mime === "message/rfc822") return "mail";
    return "default";
}

export function dwoAttPreviewIconUrl(name, mimetype) {
    return `/dwo_attpreview_core/static/img/dwo_attpreview_${dwoAttPreviewKind(name, mimetype)}.svg`;
}
