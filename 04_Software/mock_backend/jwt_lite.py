"""Tiny HS256 JWT so the mock needs no extra packages (use PyJWT in the real backend)."""
import hmac,hashlib,base64,json,time
b=lambda x: base64.urlsafe_b64encode(x).rstrip(b"=").decode()
def _d(s): return base64.urlsafe_b64decode(s+"="*(-len(s)%4))
def encode(p,k):
    h=b(json.dumps({"alg":"HS256","typ":"JWT"}).encode()); pl=b(json.dumps(p).encode())
    return f"{h}.{pl}.{b(hmac.new(k.encode(),f'{h}.{pl}'.encode(),hashlib.sha256).digest())}"
def decode(t,k):
    h,pl,sig=t.split(".")
    if not hmac.compare_digest(sig,b(hmac.new(k.encode(),f"{h}.{pl}".encode(),hashlib.sha256).digest())): raise ValueError("sig")
    d=json.loads(_d(pl))
    if d["exp"]<time.time(): raise ValueError("expired")
    return d
