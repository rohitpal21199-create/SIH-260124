from ultralytics import YOLO
import cv2

class YOLODetector:
    def __init__(self, model_path="yolov8n.pt", confidence=0.5):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.target_classes = ['car', 'bus', 'truck', 'motorcycle', 'bicycle', 'person']
    
    def detect(self, image):
        if image is None:
            return []
        
        results = self.model(image, conf=self.confidence, verbose=False)
        detections = []
        
        for result in results:
            if result.boxes:
                for box in result.boxes:
                    class_name = result.names[int(box.cls[0])]
                    if class_name in self.target_classes:
                        detections.append({
                            'class_name': class_name,
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].tolist()
                        })
        return detections
    
    def draw_detections(self, image, detections):
        img = image.copy()
        for d in detections:
            x1, y1, x2, y2 = map(int, d['bbox'])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{d['class_name']} {d['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return img