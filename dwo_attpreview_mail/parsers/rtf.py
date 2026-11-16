# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The body of an Outlook message that has only an RTF body: decompress it ([MS-OXRTFCP]) and keep the text.
Formatting is dropped on purpose: a reader needs the words, and no RTF feature can run anything here."""
import codecs
import re
import struct

COMPRESSED, UNCOMPRESSED = 0x75465A4C, 0x414C454D
DICTIONARY = (
    b"{\\rtf1\\ansi\\mac\\deff0\\deftab720{\\fonttbl;}{\\f0\\fnil \\froman \\fswiss \\fmodern \\fscript "
    b"\\fdecor MS Sans SerifSymbolArialTimes New RomanCourier{\\colortbl\\red0\\green0\\blue0\r\n\\par "
    b"\\pard\\plain\\f0\\fs20\\b\\i\\u\\tab\\tx"
)
MAX_RTF = 20 * 1024 * 1024


def decompress_rtf(data):
    if len(data) < 16:
        raise ValueError("RTF header missing")
    _size, raw_size, magic, _crc = struct.unpack_from("<IIII", data)
    if raw_size > MAX_RTF:
        raise ValueError("RTF body too large")
    if magic == UNCOMPRESSED:
        return bytes(data[16:16 + raw_size])
    if magic != COMPRESSED:
        raise ValueError("unknown RTF compression")
    window = bytearray(4096)
    window[:len(DICTIONARY)] = DICTIONARY
    write = len(DICTIONARY)
    out = bytearray()
    src, pos, end = data, 16, len(data)
    while pos < end and len(out) < raw_size:
        flags = src[pos]
        pos += 1
        for bit in range(8):
            if pos >= end or len(out) >= raw_size:
                break
            if flags & (1 << bit):
                if pos + 1 >= end:
                    return bytes(out)
                ref = (src[pos] << 8) | src[pos + 1]
                pos += 2
                offset, length = ref >> 4, (ref & 0xF) + 2
                if offset == write:  # end marker
                    return bytes(out)
                for k in range(length):
                    char = window[(offset + k) % 4096]
                    out.append(char)
                    window[write] = char
                    write = (write + 1) % 4096
            else:
                char = src[pos]
                pos += 1
                out.append(char)
                window[write] = char
                write = (write + 1) % 4096
    return bytes(out[:raw_size])


TOKEN = re.compile(r"\\([a-z]{1,32})(-?\d{1,10})?[ ]?|\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)", re.I | re.S)
DESTINATIONS = {
    "aftncn", "aftnsep", "aftnsepc", "annotation", "atnauthor", "atndate", "atnicn", "atnid", "atnparent", "atnref",
    "atntime", "atrfend", "atrfstart", "author", "background", "bkmkend", "bkmkstart", "blipuid", "buptim",
    "category", "colorschememapping", "colortbl", "comment", "company", "creatim", "datafield", "datastore",
    "defchp", "defpap", "do", "doccomm", "docvar", "dptxbxtext", "ebcend", "ebcstart", "factoidname", "falt",
    "fchars", "ffdeftext", "ffentrymcr", "ffexitmcr", "ffformat", "ffhelptext", "ffl", "ffname", "ffstattext",
    "field", "file", "filetbl", "fldinst", "fldtype", "fname", "fontemb", "fontfile", "fonttbl", "footer",
    "footerf", "footerl", "footerr", "footnote", "formfield", "ftncn", "ftnsep", "ftnsepc", "g", "generator",
    "gridtbl", "header", "headerf", "headerl", "headerr", "hl", "hlfr", "hlinkbase", "hlloc", "hlsrc", "hsv",
    "htmltag", "info", "keycode", "keywords", "latentstyles", "lchars", "levelnumbers", "leveltext", "lfolevel",
    "linkval", "list", "listlevel", "listname", "listoverride", "listoverridetable", "listpicture", "liststylename",
    "listtable", "listtext", "lsdlockedexcept", "macc", "maccPr", "mailmerge", "maln", "malnScr", "manager",
    "margPr", "mbar", "mbarPr", "mbaseJc", "mbegChr", "mborderBox", "mborderBoxPr", "mbox", "mboxPr", "mchr",
    "mcount", "mctrlPr", "md", "mdeg", "mdegHide", "mden", "mdiff", "mdPr", "me", "mendChr", "meqArr", "meqArrPr",
    "mf", "mfName", "mfPr", "mfunc", "mfuncPr", "mgroupChr", "mgroupChrPr", "mgrow", "mhideBot", "mhideLeft",
    "mhideRight", "mhideTop", "mhtmltag", "mlim", "mlimloc", "mlimlow", "mlimlowPr", "mlimupp", "mlimuppPr", "mm",
    "mmaddfieldname", "mmath", "mmathPict", "mmathPr", "mmaxdist", "mmc", "mmcJc", "mmconnectstr",
    "mmconnectstrdata", "mmcPr", "mmcs", "mmdatasource", "mmheadersource", "mmmailsubject", "mmodso",
    "mmodsofilter", "mmodsofldmpdata", "mmodsomappedname", "mmodsoname", "mmodsorecipdata", "mmodsosort",
    "mmodsosrc", "mmodsotable", "mmodsoudl", "mmodsoudldata", "mmodsouniquetag", "mmPr", "mmquery", "mmr",
    "mnary", "mnaryPr", "mnoBreak", "mnum", "mobjDist", "moMath", "moMathPara", "moMathParaPr", "mopEmu",
    "mphant", "mphantPr", "mplcHide", "mpos", "mr", "mrad", "mradPr", "mrPr", "msepChr", "mshow", "mshp",
    "msPre", "msPrePr", "msSub", "msSubPr", "msSubSup", "msSubSupPr", "msSup", "msSupPr", "mstrikeBLTR",
    "mstrikeH", "mstrikeTLBR", "mstrikeV", "msub", "msubHide", "msup", "msupHide", "mtransp", "mtype", "mvertJc",
    "mvfmf", "mvfml", "mvtof", "mvtol", "mzeroAsc", "mzeroDesc", "mzeroWid", "nesttableprops", "nextfile",
    "nonesttables", "objalias", "objclass", "objdata", "object", "objname", "objsect", "objtime", "oldcprops",
    "oldpprops", "oldsprops", "oldtprops", "oleclsid", "operator", "panose", "password", "passwordhash", "pgp",
    "pgptbl", "picprop", "pict", "pn", "pnseclvl", "pntext", "pntxta", "pntxtb", "printim", "private",
    "propname", "protend", "protstart", "protusertbl", "pxe", "result", "revtbl", "revtim", "rsidtbl", "rxe",
    "shp", "shpgrp", "shpinst", "shppict", "shprslt", "shptxt", "sn", "sp", "staticval", "stylesheet", "subject",
    "sv", "svb", "tc", "template", "themedata", "title", "txe", "ud", "upr", "userprops", "wgrffmtfilter",
    "windowcaption", "writereservation", "writereservhash", "xe", "xform", "xmlattrname", "xmlattrvalue",
    "xmlclose", "xmlname", "xmlnstbl", "xmlopen",
}
DESTINATIONS = {d.lower() for d in DESTINATIONS}
SPECIAL = {"par": "\n", "sect": "\n\n", "page": "\n\n", "line": "\n", "tab": "\t", "emdash": "\u2014",
           "endash": "\u2013", "emspace": "\u2003", "enspace": "\u2002", "qmspace": "\u2005", "bullet": "\u2022",
           "lquote": "\u2018", "rquote": "\u2019", "ldblquote": "\u201c", "rdblquote": "\u201d", "row": "\n",
           "cell": " ", "nestcell": " "}


def rtf_to_text(rtf, codec="cp1252"):
    """Plain text of an RTF document (bytes). Unknown destinations are skipped; \\uN characters are kept."""
    text = rtf.decode("latin-1")
    declared = re.search(r"\\ansicpg(\d+)", text[:4000])
    if declared:
        try:
            codec = codecs.lookup("cp%s" % declared.group(1)).name
        except LookupError:
            pass
    stack, ignorable, uc_skip, skip, out = [], False, 1, 0, []
    pending = bytearray()

    def flush():
        if pending:
            out.append(bytes(pending).decode(codec, "replace"))
            pending.clear()

    for match in TOKEN.finditer(text):
        word, arg, hexa, char, brace, plain = match.groups()
        if brace:
            skip = 0
            flush()
            if brace == "{":
                stack.append((uc_skip, ignorable))
            elif stack:
                uc_skip, ignorable = stack.pop()
        elif char:
            skip = 0
            if char == "~":
                if not ignorable:
                    out.append("\u00a0")
            elif char in "{}\\":
                if not ignorable:
                    flush()
                    out.append(char)
            elif char == "*":
                ignorable = True
            elif char == "\n" or char == "\r":
                if not ignorable:
                    flush()
                    out.append("\n")
        elif word:
            skip = 0
            word = word.lower()
            if word in DESTINATIONS:
                ignorable = True
            elif ignorable:
                continue
            elif word in SPECIAL:
                flush()
                out.append(SPECIAL[word])
            elif word == "uc":
                uc_skip = int(arg or 1)
            elif word == "u":
                flush()
                value = int(arg or 0)
                out.append(chr(value + 0x10000 if value < 0 else value))
                skip = uc_skip
        elif hexa:
            if skip > 0:
                skip -= 1
            elif not ignorable:
                pending.append(int(hexa, 16))
        elif plain:
            if skip > 0:
                skip -= 1
            elif not ignorable:
                flush()
                out.append(plain)
    flush()
    # \\uN gives UTF-16 units: join the surrogate pairs (emoji...), replace a lone one
    result = "".join(out).replace("\x00", "").encode("utf-16-le", "surrogatepass").decode("utf-16-le", "replace")
    return re.sub(r"\n{3,}", "\n\n", result).strip()
