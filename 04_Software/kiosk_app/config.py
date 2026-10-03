"""Kiosk configuration. Override with environment variables - never hard-code secrets."""
import os
API_BASE      = os.getenv("ATTENDEASE_API", "http://127.0.0.1:8000")
LOGIN_PATH    = os.getenv("ATTENDEASE_LOGIN_PATH", "/api/auth/login")        # CHANGE to your real route
ATTEND_PATH   = os.getenv("ATTENDEASE_ATTEND_PATH", "/api/attendance")       # CHANGE to your real route
KIOSK_ID      = os.getenv("KIOSK_ID", "KIOSK-01")
KIOSK_USER    = os.getenv("KIOSK_USER", "kiosk01")
KIOSK_PASS    = os.getenv("KIOSK_PASS", "change-me")
QUEUE_DB      = os.getenv("KIOSK_QUEUE_DB", "kiosk_queue.db")
SYNC_SECONDS  = int(os.getenv("KIOSK_SYNC_SECONDS", "10"))
HTTP_TIMEOUT  = float(os.getenv("KIOSK_HTTP_TIMEOUT", "4"))
CAPTURE_PHOTO = os.getenv("KIOSK_CAPTURE_PHOTO", "0") == "1"                 # needs opencv-python
