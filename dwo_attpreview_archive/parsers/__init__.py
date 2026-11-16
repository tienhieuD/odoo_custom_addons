# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Read archives (zip, tar and its compressed forms, gz/bz2/xz, rar, 7z) without extracting them to disk.

``list_archive`` returns the table of contents; ``extract_member`` returns the bytes of one file, by its position in
that table (the same position is used by the Core route /dwo_attpreview/part_info). Pure Python, no Odoo:
- zip, tar, gz, bz2, xz: standard library;
- rar: the shipped ``rarfile`` (listing always; a compressed member needs unrar/unar/7z/bsdtar on the server);
- 7z: ``py7zr`` when installed (optional, never required by the module).
Nothing is ever written to disk by this code; names such as ``../x`` or ``/etc/x`` are only shown.
"""
import bz2
import gzip
import io
import lzma
import tarfile
import zipfile
from datetime import datetime, timezone

MAX_ENTRIES = 100_000          # entries listed; the rest is reported as truncated
MAX_STREAM = 512 * 1024 * 1024  # bytes a compressed tar/gz may expand to while it is read
MAX_RATIO = 1000               # zip member: uncompressed / compressed

F_ENCRYPTED, F_SPECIAL = 1, 2  # flags of a file row (password protected; link or device: no data)

MAGIC = (
    (b"PK\x03\x04", "zip"), (b"PK\x05\x06", "zip"), (b"PK\x07\x08", "zip"),
    (b"Rar!\x1a\x07", "rar"), (b"7z\xbc\xaf\x27\x1c", "7z"),
    (b"\x1f\x8b", "gz"), (b"BZh", "bz2"), (b"\xfd7zXZ\x00", "xz"),
)
COMPRESSED_EXT = {"gz": (".gz", ".tgz"), "bz2": (".bz2", ".tbz2", ".tbz"), "xz": (".xz", ".txz")}


class ArchiveError(ValueError):
    """The archive cannot be read (damaged, unsupported, too large). ``hint`` says how to fix it when there is one."""

    def __init__(self, message, hint=""):
        super().__init__(message)
        self.hint = hint


class ToolMissing(ArchiveError):
    """Reading needs software that is not installed on the server (py7zr, unrar)."""


# --- helpers -------------------------------------------------------------------------------------------------------
class _Limited(io.RawIOBase):
    """A decompressing stream that stops with ArchiveError after ``limit`` bytes (gzip/bz2/xz bombs)."""

    def __init__(self, raw, limit):
        self.raw, self.left = raw, limit

    def readable(self):
        return True

    def readinto(self, buf):
        data = self.raw.read(min(len(buf), self.left + 1))
        if len(data) > self.left:
            raise ArchiveError("The archive expands to more than %d MB." % (MAX_STREAM // 1024 // 1024))
        self.left -= len(data)
        buf[:len(data)] = data
        return len(data)


def _decompressor(kind, content):
    opener = {"gz": gzip.GzipFile, "bz2": bz2.BZ2File, "xz": lzma.LZMAFile}[kind]
    if kind == "gz":
        return io.BufferedReader(_Limited(opener(fileobj=io.BytesIO(content)), MAX_STREAM), 1024 * 1024)
    return io.BufferedReader(_Limited(opener(io.BytesIO(content)), MAX_STREAM), 1024 * 1024)


def detect(content):
    for magic, kind in MAGIC:
        if content.startswith(magic):
            if kind in COMPRESSED_EXT:
                try:
                    head = _decompressor(kind, content).read(512)
                except (OSError, EOFError, lzma.LZMAError, ArchiveError) as e:
                    raise ArchiveError("The compressed file is damaged.") from e
                return "tar." + kind if head[257:262] == b"ustar" else kind
            return kind
    if content[257:262] == b"ustar":
        return "tar"
    raise ArchiveError("This file is not an archive this preview can read.")


def _zip_name(info):
    """A zip without the UTF-8 flag stores names in a local code page; Python reads them as cp437. Most such files
    today are UTF-8 anyway (and Vietnamese / Japanese names come out garbled as cp437)."""
    if info.flag_bits & 0x800:
        return info.filename
    try:
        return info.filename.encode("cp437").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return info.filename  # a real cp437 name (guessing other code pages would garble more names than it fixes)


def _epoch(value):
    try:
        if isinstance(value, datetime):
            return int((value if value.tzinfo else value.replace(tzinfo=timezone.utc)).timestamp())
        if isinstance(value, tuple):
            return int(datetime(*value[:6], tzinfo=timezone.utc).timestamp())
        return int(value or 0)
    except (ValueError, OverflowError, TypeError):
        return 0


def _clean_path(name):
    """Path shown in the tree: forward slashes, no empty or '.' parts. '..' stays visible (never resolved)."""
    parts = [p for p in name.replace("\\", "/").split("/") if p not in ("", ".")]
    return "/".join(parts)


def _single_name(filename, kind):
    lower = (filename or "file").lower()
    for ext in COMPRESSED_EXT.get(kind, ()):
        if lower.endswith(ext):
            return filename[:-len(ext)] or "file"
    return filename or "file"


# --- members per format: (path, is_dir, size, packed, mtime, flags, handle) ----------------------------------------
def _zip_members(content):
    try:
        zf = zipfile.ZipFile(io.BytesIO(content))
    except (zipfile.BadZipFile, ValueError, OSError) as e:
        raise ArchiveError("The zip file is damaged.") from e
    for info in zf.infolist():
        yield (_zip_name(info), info.is_dir(), info.file_size, info.compress_size, _epoch(info.date_time),
               F_ENCRYPTED if info.flag_bits & 0x1 else 0, (zf, info))


def _tar_members(content, kind):
    stream = _decompressor(kind.split(".")[1], content) if "." in kind else io.BytesIO(content)
    try:
        with tarfile.open(fileobj=stream, mode="r|") as tf:
            for member in tf:
                special = not (member.isfile() or member.isdir())
                yield (member.name, member.isdir(), 0 if special else member.size, 0, int(member.mtime or 0),
                       F_SPECIAL if special else 0, (tf, member))
    except (tarfile.TarError, OSError, EOFError, lzma.LZMAError) as e:
        raise ArchiveError("The tar archive is damaged.") from e


def _rar_members(content):
    from ..thirdparty import rarfile
    try:
        rf = rarfile.RarFile(io.BytesIO(content))
        infos = rf.infolist()
    except rarfile.NeedFirstVolume as e:
        raise ArchiveError("This is a part of a multi-volume RAR archive: open its first part.") from e
    except rarfile.PasswordRequired as e:
        raise ArchiveError("The file list of this RAR archive is protected by a password.") from e
    except (rarfile.Error, OSError, EOFError) as e:
        raise ArchiveError("The RAR file is damaged.") from e
    for info in infos:
        special = bool(getattr(info, "is_symlink", lambda: False)())
        yield (info.filename, info.is_dir(), info.file_size, info.compress_size, _epoch(info.mtime or info.date_time),
               (F_ENCRYPTED if info.needs_password() else 0) | (F_SPECIAL if special else 0), (rf, info))


def _py7zr():
    try:
        import py7zr  # optional: never required by the module
    except ImportError as e:
        raise ToolMissing("7z archives need the py7zr Python package on the server.",
                          hint="pip install py7zr (in the Python environment of Odoo), then restart Odoo.") from e
    return py7zr


def _7z_members(content):
    py7zr = _py7zr()
    try:
        archive = py7zr.SevenZipFile(io.BytesIO(content))
        entries = archive.list()
    except py7zr.exceptions.PasswordRequired as e:
        raise ArchiveError("The file list of this 7z archive is protected by a password.") from e
    except Exception as e:  # noqa: BLE001 - py7zr raises various errors on damaged files
        raise ArchiveError("The 7z file is damaged.") from e
    encrypted = archive.needs_password()
    for entry in entries:
        yield (entry.filename, entry.is_directory, entry.uncompressed or 0, entry.compressed or 0,
               _epoch(entry.creationtime),
               (F_ENCRYPTED if encrypted and not entry.is_directory else 0) | (F_SPECIAL if entry.is_symlink else 0),
               (archive, entry))


def _members(content, filename):
    kind = detect(content)
    if kind == "zip":
        return kind, _zip_members(content)
    if kind == "rar":
        return kind, _rar_members(content)
    if kind == "7z":
        return kind, _7z_members(content)
    if kind.startswith("tar"):
        return kind, _tar_members(content, kind)

    def single():  # one compressed file (report.csv.gz)
        size = 0
        stream = _decompressor(kind, content)
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
        yield (_single_name(filename, kind), False, size, len(content), 0, 0, (kind, None))
    return kind, single()


# --- API ------------------------------------------------------------------------------------------------------------
def list_archive(content, filename):
    """The table of contents::

        {"format", "dirs": ["", "a", "a/b"...], "files": [[dir_index, name, size, mtime, flags], ...],
         "size", "packed", "truncated", "encrypted"}

    ``files`` keeps the order of the archive: a file's position is its index for ``extract_member``. Folders that
    have no entry of their own (most zips) are made from the paths."""
    kind, members = _members(content, filename)
    dirs, dir_index, files = [""], {"": 0}, []
    total = encrypted = 0
    truncated = False

    def folder(path):
        if path in dir_index:
            return dir_index[path]
        parent, _, _name = path.rpartition("/")
        folder(parent)
        dir_index[path] = len(dirs)
        dirs.append(path)
        return dir_index[path]

    for path, is_dir, size, _packed, mtime, flags, _handle in members:
        if len(files) + len(dirs) > MAX_ENTRIES:
            truncated = True
            break
        path = _clean_path(path)
        if not path:
            continue
        if is_dir:
            folder(path)
            continue
        parent, _, name = path.rpartition("/")
        files.append([folder(parent), name, size, mtime, flags])
        total += size
        encrypted += bool(flags & F_ENCRYPTED)
    return {"format": kind, "dirs": dirs, "files": files, "size": total, "packed": len(content),
            "truncated": truncated, "encrypted": encrypted}


def extract_member(content, filename, index, limit):
    """``(name, bytes)`` of file number ``index`` of ``list_archive`` (``None`` if there is no such file). At most
    ``limit`` bytes are read (more: ArchiveError), whatever the size the archive claims."""
    kind, members = _members(content, filename)
    position = -1
    for path, is_dir, size, packed, _mtime, flags, handle in members:
        if is_dir or not _clean_path(path):
            continue
        position += 1
        if position != index:
            continue
        name = _clean_path(path).rpartition("/")[2]
        if flags & F_ENCRYPTED:
            raise ArchiveError("This file is protected by a password.")
        if flags & F_SPECIAL:
            raise ArchiveError("This entry is a link, not a file.")
        if size > limit:
            raise ArchiveError("This file is larger than the preview limit (%d MB)." % (limit // 1024 // 1024))
        return name, _read(kind, content, handle, size, packed, limit)
    return None


def _too_large(limit):
    return ArchiveError("This file is larger than the preview limit (%d MB)." % (limit // 1024 // 1024))


def _read(kind, content, handle, size, packed, limit):
    if kind == "zip":
        zf, info = handle
        if packed and size / max(packed, 1) > MAX_RATIO and size > 10 * 1024 * 1024:
            raise ArchiveError("This file looks like a zip bomb (compression ratio too high).")
        try:
            with zf.open(info) as fh:
                data = fh.read(limit + 1)
        except (zipfile.BadZipFile, RuntimeError, OSError, EOFError, NotImplementedError) as e:
            raise ArchiveError("This file could not be read from the zip (damaged or unsupported method).") from e
        if len(data) > limit:
            raise _too_large(limit)
        return data
    if kind.startswith("tar"):
        tf, member = handle
        try:
            data = tf.extractfile(member).read(limit + 1)
        except (tarfile.TarError, OSError, EOFError, AttributeError) as e:
            raise ArchiveError("This file could not be read from the tar archive.") from e
        if len(data) > limit:
            raise _too_large(limit)
        return data
    if kind == "rar":
        from ..thirdparty import rarfile
        rf, info = handle
        try:
            data = rf.read(info)
        except rarfile.RarCannotExec as e:
            raise ToolMissing("Opening files inside RAR archives needs the unrar tool on the server.",
                              hint="Install unrar (Debian/Ubuntu: apt install unrar), then try again.") from e
        except (rarfile.Error, OSError, EOFError) as e:
            raise ArchiveError("This file could not be read from the RAR archive. Installing unrar on the server "
                               "usually fixes it.", hint="Debian/Ubuntu: apt install unrar") from e
        if len(data) > limit:
            raise _too_large(limit)
        return data
    if kind == "7z":
        py7zr = _py7zr()
        _archive, entry = handle
        factory = py7zr.io.BytesIOFactory(limit=limit + 1)
        try:
            with py7zr.SevenZipFile(io.BytesIO(content)) as archive:
                archive.extract(targets=[entry.filename], factory=factory)
        except Exception as e:  # noqa: BLE001
            raise ArchiveError("This file could not be read from the 7z archive.") from e
        product = factory.products.get(entry.filename)
        data = product.read() if product is not None else b""
        if len(data) > limit:
            raise _too_large(limit)
        return data
    # one compressed file
    data = _decompressor(kind, content).read(limit + 1)
    if len(data) > limit:
        raise _too_large(limit)
    return data
