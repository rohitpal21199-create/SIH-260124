"""
Urban Sensing Platform - Demo
Laptop Camera + YOLO Detection
"""

import cv2
import json
from datetime import datetime
from camera_manager import CameraManager
from ultralytics import YOLO
import numpy as np

class BusSensingDemo:
    def __init__(self):
        print("🚍 Initializing Urban Sensing Demo...")
        
        # Camera
        self.camera = CameraManager(0)
        
        # YOLO Model
        try:
            self.model = YOLO('yolov8n.pt')
            print("✅ YOLO model loaded")
        except:
            print("❌ YOLO model not found!")
            self.model = None
        
        # Events storage
        self.events = []
        self.frame_count = 0
        
        # GPS Simulator
        self.lat = 19.0760
        self.lon = 72.8777
        
        print("✅ Demo ready!")
        print("📸 Press 'q' to quit, 's' to save events")
    
    def get_gps(self):
        """Simulate GPS movement"""
        self.lat += 0.00001
        self.lon += 0.00001
        return {
            'latitude': self.lat,
            'longitude': self.lon,
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_objects(self, image):
        """Detect objects using YOLO"""
        if self.model is None or image is None:
            return []
        
        results = self.model(image, conf=0.5)
        detections = []
        
        for result in results:
            if result.boxes:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    class_name = self.model.names[cls_id]
                    
                    # Vehicle classes
                    vehicle_classes = ['car', 'bus', 'truck', 'motorcycle', 'bicycle', 'person']
                    if class_name in vehicle_classes:
                        detections.append({
                            'class_name': class_name,
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].tolist()
                        })
        
        return detections
    
    def draw_detections(self, image, detections, gps_data):
        """Draw bounding boxes and info"""
        img = image.copy()
        
        for d in detections:
            x1, y1, x2, y2 = map(int, d['bbox'])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{d['class_name']} {d['confidence']:.2f}"
            cv2.putText(img, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Info overlay
        cv2.putText(img, f"GPS: {gps_data['latitude']:.6f}, {gps_data['longitude']:.6f}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(img, f"Objects: {len(detections)}",
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(img, f"Frame: {self.frame_count}",
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        cv2.putText(img, "URBAN SENSING DEMO", (img.shape[1]-200, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return img
    
    def run(self):
        """Main loop"""
        print("\n🔄 Running... Press 'q' to quit\n")
        
        while True:
            frame = self.camera.capture_frame()
            
            if frame is None:
                print("⚠️ No camera found! Creating blank frame...")
                frame = 255 * np.ones((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "No Camera Found", 
                           (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            detections = self.detect_objects(frame)
            gps_data = self.get_gps()
            
            # Store events
            for d in detections:
                self.events.append({
                    'timestamp': gps_data['timestamp'],
                    'bus_id': 'BUS-DEMO',
                    'event_type': 'object_detection',
                    'latitude': gps_data['latitude'],
                    'longitude': gps_data['longitude'],
                    'data': d
                })
            
            annotated = self.draw_detections(frame, detections, gps_data)
            cv2.imshow("Urban Sensing Platform", annotated)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                with open('events.json', 'w') as f:
                    json.dump(self.events, f, indent=2)
                print(f"💾 Saved {len(self.events)} events to events.json")
            
            self.frame_count += 1
        
        self.camera.release()
        cv2.destroyAllWindows()
        
        print("\n📊 Summary:")
        print(f"  Frames processed: {self.frame_count}")
        print(f"  Events detected: {len(self.events)}")
        print("\n✅ Demo complete!")

if __name__ == "__main__":
    demo = BusSensingDemo()
    demo.run()