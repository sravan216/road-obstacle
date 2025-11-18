Large files excluded from this repository
======================================

To keep the Git repository small and fast, several large files and folders were intentionally excluded via `.gitignore` and not pushed to the remote. This document lists those artifacts, why they are excluded, and how to obtain or restore them locally.

Excluded items (examples found in the working copy)
--------------------------------------------------
- `.venv/` — local Python virtual environment and site-packages (many large binaries). Recreate locally with `python -m venv .venv` and `pip install -r requirements.txt`.
- `assets/` (video/data) — example: `assets/night video.mp4` (~73 MB). Large video files are not included.
- `output/` — generated outputs (annotated videos, images) should not be pushed.
- Large binary site-packages discovered earlier (examples):
  - `.venv/Lib/site-packages/torch/lib/torch_cpu.dll` (~250 MB)
  - `.venv/Lib/site-packages/_polars_runtime_32/_polars_runtime_32.pyd` (~139 MB)
  - `.venv/Lib/site-packages/cv2/cv2.pyd` (~68 MB)

Model weights
-------------
- `yolov8n.pt` (Ultralytics YOLO weights) — if you want the project to run exactly as in development you can either:
  1. Download weights from Ultralytics or their releases and place them at `road obstacle night/road obstacle night/yolov8n.pt`, or
  2. Let Ultralytics download the model automatically at runtime (the `ultralytics` package may fetch weights when they are referenced). If you prefer, upload the weights to a cloud storage (Google Drive, AWS S3, GitHub release) and add instructions below.

How to restore the environment and assets locally
-------------------------------------------------
1. Create a virtual environment and install dependencies (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r "road obstacle night\road obstacle night\requirements.txt"
```

2. Add any large assets or model weights you need manually. Example:

Place `yolov8n.pt` at:
```
road obstacle night\road obstacle night\yolov8n.pt
```

3. Run the project from the repository root (wrapper will change into the nested folder):

```powershell
python .\main.py
```

Options for hosting large files
------------------------------
- Git LFS (recommended if you must keep large binaries in the repo). Note: Git LFS requires setup and may incur storage/bandwidth costs on GitHub.
- GitHub Releases — upload model weights or sample videos as release attachments and reference the URLs in this file.
- Cloud storage (Google Drive, S3) — upload large files and add download scripts or links here.

If you want, I can:
- Add a small download script that fetches the model from a given URL and places it in the project tree.
- Configure Git LFS and migrate selected large files into LFS (this rewrites history; confirm before proceeding).

Contact / notes
---------------
If you tell me which large files you want tracked in the repo (for example: `yolov8n.pt` only), I can either add LFS tracking for those patterns or provide a simple script to download them at setup time and then push the updated README/instructions.
