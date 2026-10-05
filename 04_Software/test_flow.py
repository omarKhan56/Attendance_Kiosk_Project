"""End-to-end test: valid scan, duplicate, unknown code, backend DOWN -> queue, backend UP -> auto-sync.
Uses a free port each run and always stops its servers, so repeated or failed runs cannot block each other."""
import subprocess,time,os,sys,tempfile,socket,requests
here=os.path.dirname(os.path.abspath(__file__)); mock=os.path.join(here,"mock_backend"); app=os.path.join(here,"kiosk_app")
def free_port():
    s=socket.socket(); s.bind(("127.0.0.1",0)); p=s.getsockname()[1]; s.close(); return p
PORT=free_port(); BASE=f"http://127.0.0.1:{PORT}"
DB=os.path.join(tempfile.gettempdir(),f"kiosk_test_queue_{PORT}.db")      # works on Windows, Linux and Mac
env=dict(os.environ,KIOSK_QUEUE_DB=DB,KIOSK_SYNC_SECONDS="1",ATTENDEASE_API=BASE,PYTHONIOENCODING="utf-8")
if os.path.exists(DB): os.remove(DB)
servers=[]
def start():
    p=subprocess.Popen([sys.executable,"-m","uvicorn","mock_attendease:app","--port",str(PORT),"--log-level","error"],cwd=mock); servers.append(p)
    for _ in range(50):
        try: requests.get(BASE+"/docs",timeout=.3); return p
        except Exception: time.sleep(.2)
    raise SystemExit("server failed to start")
def stop(p):
    p.terminate()
    try: p.wait(timeout=5)
    except Exception: p.kill(); p.wait()
kiosk=None
try:
    srv=start()
    kiosk=subprocess.Popen([sys.executable,"-u","kiosk_app.py"],cwd=app,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1,encoding="utf-8")
    def send(s): kiosk.stdin.write(s+"\n"); kiosk.stdin.flush(); time.sleep(1.2)
    send("STU1001"); send("STU1001"); send("NOPE99")      # ok / duplicate / unknown
    stop(srv); time.sleep(.5)
    send("STU1002")                                        # backend down -> queued
    srv=start(); time.sleep(3)                             # backend back -> auto sync
    tok=requests.post(BASE+"/api/auth/login",json={"username":"x","password":"change-me"}).json()["access_token"]
    log=requests.get(BASE+"/api/attendance",headers={"Authorization":"Bearer "+tok}).json()
    kiosk.stdin.close(); kiosk.wait(timeout=10); out=kiosk.stdout.read()
finally:
    if kiosk and kiosk.poll() is None: kiosk.kill()
    for p in servers:
        if p.poll() is None: stop(p)
print(out); print("Backend log:",log)
# the mock keeps its log in memory, so the restart wipes STU1001 - only the synced record must be present
assert [r["qr"] for r in log]==["STU1002"], "offline record was not synced after backend came back"
for expect in ("Welcome Asha Patel","Already marked","unknown QR code","Offline - saved locally","sent queued record"):
    assert expect in out, "missing behaviour: "+expect
print("\nALL TESTS PASSED")