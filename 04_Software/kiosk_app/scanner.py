"""Input devices.
QR scanner : most USB scanners act as a keyboard ('HID wedge') and type the code + Enter -> we just read a line.
Camera     : optional photo capture with OpenCV (base64 JPEG)."""
import base64
def read_scan(): return input("Scan QR > ").strip()
def capture_photo_b64():
    try:
        import cv2
    except ImportError: return None
    cam=cv2.VideoCapture(0); ok,frame=cam.read(); cam.release()
    if not ok: return None
    ok,buf=cv2.imencode(".jpg",frame,[cv2.IMWRITE_JPEG_QUALITY,70]); return base64.b64encode(buf).decode() if ok else None
