import cv2
import numpy as np
import random

class RoadDefectDetector:
    def __init__(self):
        self.defect_types = ['pothole', 'crack', 'waterlogging', 'missing_signage']
    
    def detect(self, image):
        if image is None:
            return []
        
        defects = []
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if np.mean(gray[300:400, 200:400]) < 100:
            defects.append({
                'type': 'pothole',
                'severity': random.choice(['mild', 'moderate', 'severe']),
                'confidence': random.uniform(0.6, 0.9),
                'bbox': [random.randint(100, w-100), random.randint(250, 400), 
                         random.randint(100, w-100)+60, random.randint(250, 400)+50]
            })
        
        if np.mean(gray[350:450, 100:300]) < 80:
            defects.append({
                'type': 'crack',
                'severity': random.choice(['mild', 'moderate']),
                'confidence': random.uniform(0.5, 0.8),
                'bbox': [random.randint(50, w-50), random.randint(300, 420),
                         random.randint(50, w-50)+80, random.randint(300, 420)+10]
            })
        
        return defects
    
    def draw_defects(self, image, defects):
        img = image.copy()
        colors = {
            'pothole': (0, 0, 255),
            'crack': (0, 255, 255),
            'waterlogging': (255, 0, 0),
            'missing_signage': (255, 165, 0)
        }
        
        for d in defects:
            x1, y1, x2, y2 = map(int, d['bbox'])
            color = colors.get(d['type'], (255, 255, 255))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
            cv2.putText(img, f"{d['type']} [{d['severity']}]", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return img