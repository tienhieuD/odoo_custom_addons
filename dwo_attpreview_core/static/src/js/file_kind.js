/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
// File type -> icon kind. The icons are the original SVG set of this module (static/img/dwo_attpreview_<kind>.svg).
const BY_EXT = {
    pdf: ["pdf"],
    word: ["doc", "docx", "docm", "dot", "dotx", "odt", "ott", "rtf"],
    sheet: ["xls", "xlsx", "xlsm", "xlsb", "xltx", "ods", "ots", "csv", "tsv"],
    slide: ["ppt", "pptx", "pptm", "pps", "ppsx", "odp", "otp"],
    image: ["png", "jpg", "jpeg", "gif", "webp", "avif", "bmp", "svg", "tif", "tiff", "ico", "heic", "heif", "psd", "ai", "eps", "raw", "cr2", "nef", "dng"],
    video: ["mp4", "webm", "mov", "mkv", "avi", "m4v", "ogv", "wmv", "flv", "3gp", "mpg", "mpeg"],
    audio: ["mp3", "wav", "ogg", "oga", "m4a", "flac", "aac", "opus", "wma", "aiff", "mid", "midi"],
    archive: ["zip", "rar", "7z", "tar", "gz", "tgz", "bz2", "tbz2", "tbz", "xz", "txz", "jar", "war", "apk", "cab", "iso", "dmg", "lz", "lzma", "zst"],
    markdown: ["md", "markdown"],
    code: ["json", "jsonc", "json5", "geojson", "ndjson", "xml", "xsd", "xsl", "html", "htm", "xhtml", "js", "mjs", "cjs", "jsx", "ts", "tsx", "vue", "py", "ipynb", "css", "scss", "sass", "less", "yml", "yaml", "toml", "sql", "sh", "bash", "zsh", "ps1", "bat", "java", "kt", "swift", "c", "cpp", "cc", "h", "hpp", "cs", "php", "rb", "go", "rs", "dart", "lua", "r", "pl", "scala", "groovy", "gradle", "dockerfile", "makefile"],
    text: ["txt", "log", "ini", "cfg", "conf", "rst", "env", "properties", "tex", "srt", "vtt", "po", "pot", "diff", "patch", "nfo", "out"],
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

/** Icons that are not a file type: folder (closed / open), password protected file, symbolic link. */
export function dwoAttPreviewSpecialIconUrl(kind) {
    return `/dwo_attpreview_core/static/img/dwo_attpreview_${kind}.svg`;
}

export function dwoAttPreviewIconUrl(name, mimetype) {
    return `/dwo_attpreview_core/static/img/dwo_attpreview_${dwoAttPreviewKind(name, mimetype)}.svg`;
}
