import numpy as np

class VehicleTracker:
    def __init__(self, max_disappeared=10):
        self.next_object_id = 0
        self.objects = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared
        self.count = 0
    
    def update(self, detections):
        if len(detections) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    del self.objects[obj_id]
                    del self.disappeared[obj_id]
            return self.objects
        
        if len(self.objects) == 0:
            for i, det in enumerate(detections):
                obj_id = self.next_object_id
                self.next_object_id += 1
                self.objects[obj_id] = {
                    'center': det['bbox'][:2],
                    'class': det['class_name']
                }
                self.disappeared[obj_id] = 0
        
        return self.objects