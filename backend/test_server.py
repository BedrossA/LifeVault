from fastapi import FastAPI
import face_recognition
import cv2
import numpy as np
import dlib
from picamera2 import Picamera2
import subprocess

app = FastAPI(title="LifeVault Test", version="1.0.0")

@app.get("/")
def root():
    return {
        "message": "LifeVault API - Python 3.13.5",
        "status": "operational",
        "face_recognition": "ready",
        "dlib_version": dlib.__version__
    }

@app.get("/test/face-recognition")
def test_face():
    """Test face recognition is working"""
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    locations = face_recognition.face_locations(test_img)
    return {
        "status": "working",
        "test": "blank image",
        "faces_found": len(locations)
    }

@app.get("/test/camera")
def test_camera():
    """Test camera access using the official rpicam-hello tool"""
    try:
        # Run rpicam-hello with specific flags:
        # --list-cameras : Quickly checks if hardware is detected without opening a window
        # --timeout 1    : Minimizes execution time (1ms)
        # --nopreview    : Ensures no GUI window tries to open (essential for headless servers)
        result = subprocess.run(
            ["rpicam-hello", "--list-cameras"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # If the command succeeds and lists a camera, it's working
        if result.returncode == 0 and "Available cameras" in result.stdout:
            # Optionally parse the output to get camera details
            cam_details = result.stdout.strip().split("\n")[-1]
            return {
                "status": "working",
                "camera_info": cam_details,
                "method": "official rpicam-apps"
            }
        
        return {
            "status": "camera not found",
            "error": result.stderr.strip() or "No cameras listed"
        }

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "rpicam-hello timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
