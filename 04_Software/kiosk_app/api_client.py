"""Talks to the AttendEase backend over HTTPS/REST with JWT auth."""
import requests, config
class BackendDown(Exception): pass
class ApiClient:
    def __init__(self): self.token=None; self.s=requests.Session()
    def login(self):
        try:
            r=self.s.post(config.API_BASE+config.LOGIN_PATH,json={"username":config.KIOSK_USER,"password":config.KIOSK_PASS},timeout=config.HTTP_TIMEOUT)
        except requests.RequestException as e: raise BackendDown(str(e))
        r.raise_for_status(); self.token=r.json()["access_token"]
    def post_attendance(self, payload, _retry=True):
        if not self.token: self.login()
        try:
            r=self.s.post(config.API_BASE+config.ATTEND_PATH,json=payload,headers={"Authorization":f"Bearer {self.token}"},timeout=config.HTTP_TIMEOUT)
        except requests.RequestException as e: raise BackendDown(str(e))
        if r.status_code==401 and _retry: self.token=None; return self.post_attendance(payload,False)   # token expired
        if r.status_code>=500: raise BackendDown(f"server error {r.status_code}")
        return r.status_code, r.json()
