#!/usr/bin/env python3
import sys
import os
import yaml
import cv2
# utils helpers
from utils import ensure_dir, draw_boxes
from preprocessing import enhance_night
from detector import YOLODetector
import time
# ...existing code...

# Load config
cfg_path = 'config.yaml'
if not os.path.exists(cfg_path):
    print(f"ERROR: config file not found: {cfg_path}")
    sys.exit(1)
with open(cfg_path) as f:
    cfg = yaml.safe_load(f) or {}

video_src = cfg.get('video_path', 0)
out_path = cfg.get('output_path', 'output/annotated.mp4')
ensure_dir(os.path.dirname(out_path) or './')

# Init video capture
cap_src = video_src if not str(video_src).isdigit() else int(video_src)

# If the configured path is a directory, try to pick the first video file inside it.
if isinstance(cap_src, str) and os.path.isdir(cap_src):
    import glob
    candidates = []
    for ext in ('.mp4', '.mkv', '.avi', '.mov', '.wmv'):
        candidates.extend(glob.glob(os.path.join(cap_src, f'*{ext}')))
    candidates = sorted(candidates)
    if candidates:
        chosen = candidates[0]
        print(f"INFO: video_path is a directory; using first file: {chosen}")
        cap_src = chosen
    else:
        print(f"ERROR: video_path is a directory but contains no supported video files: {cap_src}")
        sys.exit(1)

def open_capture(path_or_index):
    """Try multiple OpenCV backends to open a capture. Returns a VideoCapture or None."""
    # If numeric index -> try webcam backends (DirectShow, MSMF, ANY)
    if isinstance(path_or_index, int):
        for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY):
            try:
                cap = cv2.VideoCapture(path_or_index, backend)
                if cap.isOpened():
                    print(f"INFO: opened camera index {path_or_index} with backend {backend}")
                    return cap
            except Exception:
                pass
    else:
        # file path: check existence first
        if not os.path.exists(path_or_index):
            print(f"ERROR: video file not found: {path_or_index}")
            return None
        # try FFMPEG first (better codec support), then default
        for backend in (cv2.CAP_FFMPEG, cv2.CAP_ANY):
            try:
                cap = cv2.VideoCapture(path_or_index, backend)
                if cap.isOpened():
                    print(f"INFO: opened file {path_or_index} with backend {backend}")
                    return cap
            except Exception:
                pass
    return None


cap = open_capture(cap_src)
if cap is None or not cap.isOpened():
    print(f"ERROR: cannot open video source: {cap_src}. Check path, permissions, or available codecs/backends.")
    sys.exit(1)

# quick read test to fail fast with a clear message
ret, _ = cap.read()
if not ret:
    print(f"ERROR: opened video source but cannot read frames from: {cap_src}. Try another backend or verify the file/device.")
    cap.release()
    sys.exit(1)

# warm-up camera (skip first few frames which may be dark/unstable)
warmup_frames = int(cfg.get('warmup_frames', 5))
for i in range(warmup_frames):
    r, _ = cap.read()
    if not r:
        break
    time.sleep(0.01)


def normalize_box(b):
    """Normalize different box dict shapes to the format draw_boxes expects.
    Returns a dict with keys: xmin,ymin,xmax,ymax,conf,class_id,class_name
    """
    return {
        'xmin': int(b.get('xmin') or b.get('x1') or b.get('x') or 0),
        'ymin': int(b.get('ymin') or b.get('y1') or b.get('y') or 0),
        'xmax': int(b.get('xmax') or b.get('x2') or b.get('w') or 0),
        'ymax': int(b.get('ymax') or b.get('y2') or b.get('h') or 0),
        'conf': float(b.get('conf') or b.get('confidence') or b.get('score') or 0.0),
        'class_id': int(b.get('class_id') or b.get('cls') or -1),
        'class_name': str(b.get('class_name') or b.get('name') or 'unknown')
    }

fps = cap.get(cv2.CAP_PROP_FPS) or cfg.get('fps', 25)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or cfg.get('frame_width', 1280) or 1280)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or cfg.get('frame_height', 720) or 720)

# Video writer
save_output = cfg.get('save_output', True)
if save_output:
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_vid = cv2.VideoWriter(out_path, fourcc, float(fps), (width, height))
    if not out_vid.isOpened():
        print(f"WARNING: cannot open VideoWriter for {out_path}. Disabling save_output.")
        save_output = False
# basic counters / state
frame_count = 0
detector = None
try:
    detector = YOLODetector(model_path=cfg.get('model','yolov8n.pt'),
                            conf=cfg.get('conf_thresh',0.35),
                            iou=cfg.get('iou_thresh',0.45),
                            device='cpu')
except Exception as e:
    print("ERROR initializing detector:", e)
    sys.exit(1)
# ...existing code...
while True:
    ret, frame = cap.read()
    if not ret:
        break
    # defensive: ensure frame shape
    if frame is None or frame.size == 0:
        print("WARNING: empty frame, skipping")
        continue
    # resize to expected writer/frame size if needed
    if (frame.shape[1], frame.shape[0]) != (width, height):
        frame = cv2.resize(frame, (width, height))

    # preprocessing / enhancement for night images
    enhanced = enhance_night(frame)

    try:
        boxes = detector.predict(enhanced)
    except Exception as e:
        print("ERROR during detection:", e)
        # try to continue or break depending on needs
        break
    # Sanity check and debug output for the detection result
    if frame_count == 0:
        print("DEBUG: detector.predict returned type:", type(boxes))
        if isinstance(boxes, dict) or hasattr(boxes, 'boxes'):
            print("DEBUG: result looks like a different API. Adjust detector wrapper or parsing.")

    # Print summary and normalize boxes for downstream code
    try:
        print('DEBUG: detections count =', len(boxes))
    except Exception:
        print('DEBUG: detections count = unknown')

    if isinstance(boxes, list) and len(boxes) > 0:
        print('DEBUG: first box raw =', boxes[0])
        # normalize format to what draw_boxes expects
        boxes = [normalize_box(b) for b in boxes]
        missing = {'xmin','ymin','xmax','ymax','conf','class_id','class_name'} - set(boxes[0].keys())
        if missing:
            print('WARNING: missing keys in normalized box:', missing)
    else:
        # ensure boxes is a list for downstream code
        boxes = []

    # Extra diagnostics when no detections — help debug night frames / preprocessing / model
    if len(boxes) == 0:
        try:
            # save the enhanced frame for inspection
            dbg_fname = os.path.join('output', f'debug_frame_{frame_count}.jpg')
            ensure_dir(os.path.dirname(dbg_fname) or '.')
            cv2.imwrite(dbg_fname, enhanced)
            print('DEBUG: saved enhanced frame to', dbg_fname)
            # basic pixel stats
            arr = enhanced
            print('DEBUG: frame stats min/max/mean/std =', float(arr.min()), float(arr.max()), float(arr.mean()), float(arr.std()))
        except Exception as e:
            print('DEBUG: failed saving or stats:', e)

        # Try running the underlying ultralytics model directly with different params
        try:
            res = detector.model.predict(source=enhanced, conf=cfg.get('conf_thresh', 0.35), iou=cfg.get('iou_thresh', 0.45), imgsz=640, verbose=False)
            r = res[0]
            print('DEBUG: raw model boxes (conf cfg):', len(r.boxes))
            for i, b in enumerate(r.boxes[:5]):
                try:
                    print(' raw box', i, 'xyxy=', b.xyxy[0].tolist(), 'conf=', float(b.conf[0]), 'cls=', int(b.cls[0]))
                except Exception:
                    print(' raw box', i, '->', b)
        except Exception as e:
            print('DEBUG: raw model.predict (cfg conf) failed:', e)

        try:
            res2 = detector.model.predict(source=enhanced, conf=0.2, iou=cfg.get('iou_thresh', 0.45), imgsz=640, verbose=False)
            r2 = res2[0]
            print('DEBUG: raw model boxes (conf=0.2):', len(r2.boxes))
        except Exception as e:
            print('DEBUG: raw model.predict (conf=0.2) failed:', e)

        try:
            rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
            res3 = detector.model.predict(source=rgb, conf=cfg.get('conf_thresh', 0.35), iou=cfg.get('iou_thresh', 0.45), imgsz=640, verbose=False)
            r3 = res3[0]
            print('DEBUG: raw model boxes on RGB (conf cfg):', len(r3.boxes))
        except Exception as e:
            print('DEBUG: raw model.predict on RGB failed:', e)
    # annotate and write
    annotated = draw_boxes(frame.copy(), boxes)
    # optional display
    if cfg.get('display', False):
        cv2.imshow('annotated', annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('INFO: user requested exit (q)')
            break
    frame_count += 1
    if save_output:
        out_vid.write(annotated)
# ...existing code...
if save_output:
    out_vid.release()
# ...existing code...