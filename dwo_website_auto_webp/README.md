# Website Auto WebP — Installation Guide

This module requires **Pillow with the WebP encoder** (built on `libwebp`) on the machine running Odoo.
If it is missing, the module will not crash, but it will not convert images (the log shows `KeyError: WEBP` or a "WebP not supported" warning) and original images are served instead.

Follow the section for your environment, then run the **Verify** step at the end.

> Always install Pillow with the **exact Python that Odoo runs** (venv or system). Installing into the wrong Python is the most common mistake.

---

## Linux (Ubuntu / Debian) — Production

1. Find the Python your Odoo service uses:
   ```bash
   systemctl cat odoo | grep ExecStart
   head -n 1 $(which odoo)   # e.g. "#!/usr/bin/python3"
   ```
2. Install libwebp and reinstall Pillow with that exact Python:
   ```bash
   sudo apt install -y libwebp-dev
   sudo /path/to/python3 -m pip install --upgrade pip
   sudo /path/to/python3 -m pip install --force-reinstall "Pillow>=10.0.1"
   sudo systemctl restart odoo
   ```
3. If pip refuses with `externally-managed-environment` (Debian/Ubuntu 12+, no venv), add `--break-system-packages` to the pip command.

Note: avoid `--no-binary Pillow` on Linux unless you really need to rebuild the native extension. It forces pip to compile from source, which is slow and can fail with `metadata for project name unknown` on older pip/setuptools. The prebuilt wheel already includes WebP.

## Docker

Add to the Odoo image's Dockerfile (or run inside the container and commit):
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libwebp-dev \
    && pip3 install --force-reinstall "Pillow>=10.0.1"
```
Then rebuild the image and restart the container.

## Windows

The official Pillow wheel for Windows already includes WebP:
```powershell
pip install --upgrade Pillow
```

## macOS (Intel)

```bash
brew install webp
/path/to/venv/bin/pip install --force-reinstall --no-cache-dir --no-binary Pillow Pillow
```

## macOS Apple Silicon (M1/M2/M3/M4) — local development

Homebrew on Apple Silicon lives in `/opt/homebrew/`. You must set the library paths explicitly, otherwise Pillow is built without WebP even though libwebp is installed:
```bash
brew install webp
LDFLAGS="-L/opt/homebrew/lib" CPPFLAGS="-I/opt/homebrew/include" \
  /path/to/venv/bin/pip install --force-reinstall --no-cache-dir --no-binary Pillow Pillow
```

---

## Verify

Run with the same Python/venv as Odoo:
```bash
python -c "from PIL import Image; import io; img=Image.new('RGB',(1,1)); out=io.BytesIO(); img.save(out,format='WEBP'); print('OK, bytes:', len(out.getvalue()))"
# Expected: OK, bytes: 44
```
If it prints `OK`, restart Odoo. If it raises `KeyError: 'WEBP'` / `encoder webp not available`, Pillow has no WebP support — repeat the install step above.

## Enable in Odoo

1. Install (or upgrade) the `dwo_website_auto_webp` module.
2. Go to **Settings → Auto WebP**, enable *Auto WebP Conversion* and adjust *WebP Quality* (default 85).
3. After changing quality, or to force re-conversion, click **Clear WebP Cache**.
