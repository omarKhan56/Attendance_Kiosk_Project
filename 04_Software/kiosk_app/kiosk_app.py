"""Attendance kiosk main loop (runs on the Raspberry Pi / mini-PC inside the kiosk column).
scan QR -> (optional photo) -> POST to backend -> show result on the touch display. Offline? queue and sync later."""
import threading, datetime
import config, scanner
from api_client import ApiClient, BackendDown
from offline_queue import OfflineQueue

api=ApiClient(); queue=OfflineQueue(config.QUEUE_DB)
def show(msg): print(f"[DISPLAY] {msg}",flush=True)       # replace with Tkinter/web UI on the touch screen

def sync_loop(stop):
    while not stop.is_set():
        for qid,payload in queue.pending():
            try:
                code,_=api.post_attendance(payload)
                if code<500: queue.remove(qid); print(f"[SYNC] sent queued record {qid} (HTTP {code})",flush=True)
            except BackendDown: break                    # still offline, try again later
        stop.wait(config.SYNC_SECONDS)

def handle_scan(code):
    payload={"kiosk_id":config.KIOSK_ID,"qr_payload":code,"scanned_at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if config.CAPTURE_PHOTO: payload["photo_b64"]=scanner.capture_photo_b64()
    try:
        status,body=api.post_attendance(payload)
        if status==200: show(f"Welcome {body.get('name','')}! Attendance marked.")
        elif status==409: show(f"Already marked: {body.get('detail','')}")
        else: show(f"Rejected ({status}): {body.get('detail','invalid QR')}")
    except BackendDown:
        queue.push(payload); show(f"Offline - saved locally ({queue.size()} waiting).")

def main():
    stop=threading.Event(); threading.Thread(target=sync_loop,args=(stop,),daemon=True).start()
    show(f"{config.KIOSK_ID} ready. Waiting for scans...")
    try:
        while True:
            code=scanner.read_scan()
            if code: handle_scan(code)
    except (KeyboardInterrupt,EOFError): stop.set()
if __name__=="__main__": main()
