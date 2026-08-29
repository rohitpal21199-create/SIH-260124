import cv2
import time

class CameraManager:
    def __init__(self, camera_id=0):
        self.cap = None
        self.camera_id = camera_id
        
        # Try to open camera with DirectShow (Windows)
        print(f"📸 Trying to open camera {camera_id}...")
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            print("❌ Camera not found!")
            self.cap = None
        else:
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Test capture
            ret, frame = self.cap.read()
            if ret:
                print("✅ Camera initialized successfully!")
            else:
                print("⚠️ Camera opened but cannot capture frames")
                self.cap = None
    
    def capture_frame(self):
        """Capture a frame"""
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def release(self):
        """Release camera"""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            print("✅ Camera released")

# Test function
if __name__ == "__main__":
    print("Testing CameraManager...")
    cam = CameraManager(0)
    
    if cam.cap is not None:
        frame = cam.capture_frame()
        if frame is not None:
            cv2.imshow("Test Camera", frame)
            print("✅ Camera working! Press any key to close...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("❌ Cannot capture frame")
    else:
        print("❌ No camera found")
    
    cam.release()