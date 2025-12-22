# backend/routers/camera.py
from fastapi import APIRouter, WebSocket
from picamera2 import Picamera2
import cv2
import asyncio

router = APIRouter()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))

@router.websocket("/ws/camera/stream")
async def camera_stream(websocket: WebSocket):
    await websocket.accept()
    picam2.start()
    
    try:
        while True:
            frame = picam2.capture_array()
            # Convert to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(0.033)  # ~30 FPS
    except Exception as e:
        print(f"Stream error: {e}")
    finally:
        picam2.stop()
        await websocket.close()

@router.post("/api/camera/enroll")
async def enroll_face(user_id: str, image: bytes):
    """Enroll a new face for user"""
    # Decode image, extract embedding, encrypt, store
    pass

@router.post("/api/camera/recognize")
async def recognize_face(image: bytes):
    """Recognize face in image"""
    # Extract embedding, compare with stored embeddings
    pass