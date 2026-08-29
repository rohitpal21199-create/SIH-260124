"""
ONBOARD PROCESSING - MAIN PIPELINE
Camera → YOLO → API → Alert
"""

import cv2
import requests
import json
import time
import numpy as np
from datetime import datetime
from ultralytics import YOLO

class OnboardProcessor:
    def __init__(self):
        print("🚍 Initializing Onboard Processor...")
        
        # Load YOLO
        self.model = YOLO('yolov8n.pt')
        print("✅ YOLO model loaded")
        
        # GPS
        self.lat = 19.0760
        self.lon = 72.8777
        self.bus_id = "BUS-001"
        
        # Frame counter
        self.frame_count = 0
        self.skip_frames = 5
        
        # API
        self.api_url = "http://localhost:8000/api/events"
        self.events = []
        
        # Test mode
        self.use_test_mode = True
        print("📸 TEST MODE: Using test images (No camera needed)")
    
    def get_gps(self):
        self.lat += 0.00001
        self.lon += 0.00001
        return {
            'latitude': self.lat,
            'longitude': self.lon,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_test_frame(self):
        frame = 255 * np.ones((480, 640, 3), dtype=np.uint8)
        
        # Road
        cv2.rectangle(frame, (0, 350), (640, 480), (100, 100, 100), -1)
        cv2.line(frame, (0, 350), (640, 350), (255, 255, 255), 2)
        
        # Car
        cv2.rectangle(frame, (150, 200), (350, 330), (0, 255, 0), -1)
        cv2.rectangle(frame, (170, 220), (200, 280), (200, 200, 200), -1)
        cv2.rectangle(frame, (300, 220), (330, 280), (200, 200, 200), -1)
        cv2.circle(frame, (180, 340), 15, (50, 50, 50), -1)
        cv2.circle(frame, (320, 340), 15, (50, 50, 50), -1)
        cv2.putText(frame, "CAR", (200, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Person
        cv2.rectangle(frame, (450, 250), (480, 380), (0, 0, 255), -1)
        cv2.circle(frame, (465, 230), 20, (0, 0, 255), -1)
        cv2.putText(frame, "PERSON", (440, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Pothole
        cv2.circle(frame, (300, 400), 30, (50, 50, 50), -1)
        cv2.putText(frame, "POTHOLE", (280, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return frame
    
    def detect_objects(self, frame):
        if frame is None:
            return []
        
        results = self.model(frame, conf=0.4, verbose=False)
        detections = []
        
        for result in results:
            if result.boxes:
                for box in result.boxes:
                    class_name = result.names[int(box.cls[0])]
                    detections.append({
                        'class_name': class_name,
                        'confidence': float(box.conf[0]),
                        'bbox': box.xyxy[0].tolist()
                    })
        
        return detections
    
    def detect_road_defects(self, frame):
        defects = []
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if np.mean(gray[300:400, 200:400]) < 100:
                defects.append('pothole')
            if np.mean(gray[350:450, 100:300]) < 80:
                defects.append('crack')
        return defects
    
    def send_to_api(self, detections, defects, gps_data):
        data = {
            'timestamp': gps_data['timestamp'],
            'bus_id': self.bus_id,
            'event_type': 'object_detection',
            'latitude': gps_data['latitude'],
            'longitude': gps_data['longitude'],
            'objects': [d['class_name'] for d in detections],
            'road_defects': defects,
            'location': f"{gps_data['latitude']}, {gps_data['longitude']}"
        }
        
        try:
            response = requests.post(self.api_url, json=data, timeout=5)
            if response.status_code == 200:
                print(f"✅ Sent: {len(detections)} objects, {len(defects)} defects")
                self.events.append(data)
            else:
                print(f"❌ API Error: {response.status_code}")
        except:
            print("❌ Backend not running! Start: python backend\api.py")
    
    def draw_detections(self, frame, detections, defects, gps_data):
        img = frame.copy()
        
        for d in detections:
            x1, y1, x2, y2 = map(int, d['bbox'])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{d['class_name']} {d['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        for defect in defects:
            h, w = img.shape[:2]
            x1, y1 = np.random.randint(100, w-100), np.random.randint(250, 400)
            x2, y2 = x1 + 80, y1 + 60
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(img, f"⚠️ {defect}", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.putText(img, f"📍 GPS: {gps_data['latitude']:.6f}, {gps_data['longitude']:.6f}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(img, f"📊 Objects: {len(detections)} | Defects: {len(defects)}",
                   (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(img, f"🔄 TEST MODE | Frame: {self.frame_count}",
                   (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return img
    
    def run(self):
        print("\n📸 TEST MODE: Processing test images... Press 'q' to quit\n")
        
        while True:
            frame = self.create_test_frame()
            self.frame_count += 1
            
            if self.frame_count % self.skip_frames != 0:
                cv2.imshow("Onboard Processing", frame)
                if cv2.waitKey(500) & 0xFF == ord('q'):
                    break
                continue
            
            gps_data = self.get_gps()
            detections = self.detect_objects(frame)
            defects = self.detect_road_defects(frame)
            
            if detections or defects:
                self.send_to_api(detections, defects, gps_data)
            
            annotated = self.draw_detections(frame, detections, defects, gps_data)
            cv2.imshow("Onboard Processing", annotated)
            
            key = cv2.waitKey(1000) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                with open('onboard_events.json', 'w') as f:
                    json.dump(self.events, f, indent=2)
                print(f"💾 Saved {len(self.events)} events")
        
        cv2.destroyAllWindows()
        
        print(f"\n📊 Summary:")
        print(f"  Total frames: {self.frame_count}")
        print(f"  Events sent: {len(self.events)}")
        print("✅ Onboard processing complete!")

if __name__ == "__main__":
    processor = OnboardProcessor()
    processor.run()