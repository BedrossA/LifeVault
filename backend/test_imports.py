#!/usr/bin/env python3
"""Test if all critical packages can be imported"""

import sys

def test_import(package_name, import_statement):
    try:
        exec(import_statement)
        print(f"✅ {package_name}: OK")
        return True
    except Exception as e:
        print(f"❌ {package_name}: FAILED - {e}")
        return False

print("Testing Python version...")
print(f"Python {sys.version}")
print()

print("Testing package imports...")
all_ok = True

# Core packages
all_ok &= test_import("FastAPI", "import fastapi")
all_ok &= test_import("Uvicorn", "import uvicorn")
all_ok &= test_import("SQLAlchemy", "import sqlalchemy")
all_ok &= test_import("Pydantic", "import pydantic")

# Security
all_ok &= test_import("Passlib", "import passlib")
all_ok &= test_import("Jose/JWT", "import jose")
all_ok &= test_import("Cryptography", "import cryptography")

# Database
all_ok &= test_import("Psycopg2", "import psycopg2")

# Face Recognition Stack
all_ok &= test_import("NumPy", "import numpy")
all_ok &= test_import("OpenCV", "import cv2")
all_ok &= test_import("dlib", "import dlib")
all_ok &= test_import("face_recognition", "import face_recognition")
all_ok &= test_import("PIL", "from PIL import Image")

print()
if all_ok:
    print("🎉 All packages imported successfully!")
else:
    print("⚠️  Some packages failed to import. Check errors above.")
    sys.exit(1)
