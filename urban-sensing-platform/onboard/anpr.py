import cv2
import numpy as np

class ANPR:
    def __init__(self):
        print("📋 Initializing ANPR...")
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            self.use_paddle = True
            print("✅ PaddleOCR initialized")
        except ImportError:
            self.use_paddle = False
            print("⚠️ PaddleOCR not available")
    
    def detect_plates(self, image):
        if image is None:
            return []
        
        plates = []
        if self.use_paddle:
            try:
                result = self.ocr.ocr(image, cls=True)
                if result:
                    for line in result:
                        if line:
                            for box in line:
                                text = box[1][0] if box[1] else ""
                                confidence = box[1][1] if box[1] else 0
                                if text and confidence > 0.6:
                                    plates.append({
                                        'plate': text.upper(),
                                        'confidence': confidence,
                                        'bbox': box[0]
                                    })
            except:
                pass
        
        return plates