import cv2

class CameraManager:
    def __init__(self, camera_ids=[0]):
        self.cameras = {}
        for cam_id in camera_ids:
            cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            if cap.isOpened():
                self.cameras[cam_id] = cap
                print(f"✅ Camera {cam_id} initialized")
            else:
                print(f"❌ Camera {cam_id} not found")
    
    def capture_frame(self, camera_id=0):
        if camera_id not in self.cameras:
            return None
        ret, frame = self.cameras[camera_id].read()
        return frame if ret else None
    
    def release(self):
        for cap in self.cameras.values():
            cap.release()
        cv2.destroyAllWindows()