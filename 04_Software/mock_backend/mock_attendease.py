"""STAND-IN for the real AttendEase backend so the kiosk can be tested.
Replace the routes/fields with your real API when integrating (see kiosk_app/config.py)."""
import time, jwt_lite
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
app=FastAPI(title="Mock AttendEase"); SECRET="dev-secret"
STUDENTS={"STU1001":"Asha Patel","STU1002":"Rohan Mehta","STU1003":"Sara Khan"}
LOG=[]
class Login(BaseModel): username:str; password:str
class Att(BaseModel): kiosk_id:str; qr_payload:str; scanned_at:str; photo_b64:str|None=None
@app.post("/api/auth/login")
def login(b:Login):
    if b.password!="change-me": raise HTTPException(401,"bad credentials")
    return {"access_token":jwt_lite.encode({"sub":b.username,"exp":time.time()+3600},SECRET),"token_type":"bearer"}
def auth(h):
    try: return jwt_lite.decode((h or "").removeprefix("Bearer "),SECRET)
    except Exception: raise HTTPException(401,"invalid token")
@app.post("/api/attendance")
def mark(b:Att,authorization:str|None=Header(None)):
    auth(authorization)
    if b.qr_payload not in STUDENTS: raise HTTPException(404,"unknown QR code")
    if any(r["qr"]==b.qr_payload for r in LOG): raise HTTPException(409,"attendance already recorded")
    LOG.append({"qr":b.qr_payload,"kiosk":b.kiosk_id,"at":b.scanned_at}); return {"status":"ok","name":STUDENTS[b.qr_payload]}
@app.get("/api/attendance")
def listing(authorization:str|None=Header(None)): auth(authorization); return LOG
