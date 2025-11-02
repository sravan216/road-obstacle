from ultralytics import YOLO


class YOLODetector:
    def __init__(self, model_path='yolov8n.pt', conf=0.35, iou=0.45, device=None):
        # device: 'cpu' or 'cuda:0'
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        if device:
            self.model.to(device)

    def predict(self, frame):
        # returns list of boxes [{xmin,ymin,xmax,ymax,conf,class_id,class_name}]
        results = self.model.predict(source=frame, conf=self.conf, iou=self.iou, imgsz=640, verbose=False)
        # ultralytics returns a list of Results; we have one since source=frame
        r = results[0]
        boxes = []
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            name = self.model.names[cls]
            boxes.append({'xmin':x1, 'ymin':y1, 'xmax':x2, 'ymax':y2, 'conf':conf, 'class_id':cls, 'class_name':name})
        return boxes
