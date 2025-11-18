Night Road Obstacle Detector

A real-time system designed to detect road obstacles in low-light or nighttime conditions by enhancing video frames and applying YOLOv8 object detection.

📌 Overview

This project improves nighttime visibility using preprocessing techniques (denoising, gamma correction, CLAHE) and then performs object detection using the Ultralytics YOLOv8 model. It is suitable for applications such as driver assistance, surveillance, and automated navigation.

✨ Features

Night video enhancement (denoise, gamma correction, CLAHE)

YOLOv8-based obstacle detection

Real-time processing

Configurable through config.yaml

Support for both CPU and GPU

Video display and optional output video saving

🗂️ Project Structure
├── main.py               # Main application loop
├── detector.py           # YOLOv8 model wrapper
├── preprocessing.py      # Night enhancement functions
├── utils.py              # Drawing utilities and helpers
├── config.yaml           # Runtime configuration
├── yolov8n.pt            # Model weights
├── requirements.txt      # Dependencies
└── README.md

🛠️ Requirements

Python 3.10+

OpenCV

Ultralytics YOLOv8

PyTorch

NumPy

PyYAML

pandas, scipy, tqdm (optional helpers)

Install all dependencies:

pip install -r requirements.txt

▶️ How to Run

Activate your virtual environment (optional):

python -m venv .venv
.venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Run the program:

python main.py

⚙️ Configuration

Edit config.yaml to adjust:

Model path

Confidence threshold

Video input source

Preprocessing options (gamma, CLAHE, denoise)

Output video saving

🔍 Methodology

Capture input video frame-by-frame

Apply night enhancement (denoise, gamma, CLAHE)

Run YOLOv8 detection

Draw bounding boxes and labels

Display or save the processed frame

📈 Improvisations

Added advanced night-enhancement preprocessing

Improved accuracy using YOLOv8

Introduced configuration-driven design

Optimized for real-time performance

📌 Conclusion

The system successfully enhances low-light video and detects road obstacles accurately using deep learning. It provides a reliable approach for improving night-time driving safety and can be expanded with custom models or additional sensors.
