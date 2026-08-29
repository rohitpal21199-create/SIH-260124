import cv2
import numpy as np
import os

# Create folder
os.makedirs('data/test_images', exist_ok=True)

print("📸 Creating test images...")

# ============================================
# Image 1: Road with car and person
# ============================================
img1 = 200 * np.ones((480, 640, 3), dtype=np.uint8)

# Road
cv2.rectangle(img1, (0, 350), (640, 480), (100, 100, 100), -1)
cv2.line(img1, (0, 350), (640, 350), (255, 255, 255), 2)

# Car
cv2.rectangle(img1, (150, 200), (350, 330), (0, 255, 0), -1)
cv2.rectangle(img1, (170, 220), (200, 280), (200, 200, 200), -1)
cv2.rectangle(img1, (300, 220), (330, 280), (200, 200, 200), -1)
cv2.circle(img1, (180, 340), 15, (50, 50, 50), -1)
cv2.circle(img1, (320, 340), 15, (50, 50, 50), -1)

# Person
cv2.rectangle(img1, (450, 250), (480, 380), (0, 0, 255), -1)
cv2.circle(img1, (465, 230), 20, (0, 0, 255), -1)

# Labels
cv2.putText(img1, "CAR", (200, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.putText(img1, "PERSON", (440, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.putText(img1, "ROAD SCENE", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

cv2.imwrite('data/test_images/scene1.jpg', img1)
print("✅ Created: scene1.jpg")

# ============================================
# Image 2: Traffic with bus
# ============================================
img2 = 200 * np.ones((480, 640, 3), dtype=np.uint8)

# Road
cv2.rectangle(img2, (0, 350), (640, 480), (100, 100, 100), -1)
cv2.line(img2, (0, 350), (640, 350), (255, 255, 255), 2)

# Bus
cv2.rectangle(img2, (100, 150), (350, 330), (0, 255, 255), -1)
cv2.rectangle(img2, (120, 170), (160, 250), (200, 200, 200), -1)
cv2.rectangle(img2, (180, 170), (220, 250), (200, 200, 200), -1)
cv2.rectangle(img2, (240, 170), (280, 250), (200, 200, 200), -1)
cv2.rectangle(img2, (300, 170), (330, 250), (200, 200, 200), -1)
cv2.circle(img2, (150, 340), 15, (50, 50, 50), -1)
cv2.circle(img2, (300, 340), 15, (50, 50, 50), -1)

# Car
cv2.rectangle(img2, (450, 220), (580, 330), (0, 255, 0), -1)

# Person
cv2.rectangle(img2, (420, 280), (440, 380), (0, 0, 255), -1)
cv2.circle(img2, (430, 260), 15, (0, 0, 255), -1)

# Labels
cv2.putText(img2, "BUS", (180, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.putText(img2, "CAR", (480, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.putText(img2, "PERSON", (400, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.putText(img2, "TRAFFIC SCENE", (220, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

cv2.imwrite('data/test_images/scene2.jpg', img2)
print("✅ Created: scene2.jpg")

# ============================================
# Image 3: Night scene
# ============================================
img3 = 50 * np.ones((480, 640, 3), dtype=np.uint8)

# Road
cv2.rectangle(img3, (0, 350), (640, 480), (30, 30, 30), -1)
cv2.line(img3, (0, 350), (640, 350), (100, 100, 100), 2)

# Car with headlights
cv2.rectangle(img3, (200, 220), (400, 340), (100, 100, 100), -1)
cv2.circle(img3, (180, 300), 10, (255, 255, 200), -1)
cv2.circle(img3, (420, 300), 10, (255, 255, 200), -1)

# Light effect
cv2.circle(img3, (180, 300), 30, (255, 255, 150), 1)
cv2.circle(img3, (300, 300), 30, (255, 255, 150), 1)
cv2.circle(img3, (420, 300), 30, (255, 255, 150), 1)

cv2.putText(img3, "NIGHT SCENE", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
cv2.imwrite('data/test_images/scene3.jpg', img3)
print("✅ Created: scene3.jpg")

print("\n✅ All test images created successfully!")
print("📁 Location: data/test_images/")
print("📸 Images: scene1.jpg, scene2.jpg, scene3.jpg")