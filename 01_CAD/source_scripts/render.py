import numpy as np, math
from PIL import Image

def mesh(wp, tol=0.8, maxedge=None):
    v,t=wp.val().tessellate(tol,0.3)
    V=np.array([[p.x,p.y,p.z] for p in v]); T=np.array(t)
    return V,T

def tris_of(P, hide=(), offs=None, extra_rot=None, tol=0.8):
    offs=offs or {}; out=[]
    for name,(wp,col,*_) in P.items():
        if name in hide: continue
        V,T=mesh(wp,tol)
        if len(T)==0: continue
        if extra_rot and name in extra_rot: V=extra_rot[name](V)
        V=V+np.array(offs.get(name,(0,0,0)))
        out.append((V[T],np.array(col)))
    return out

def render(items, path, size=(1100,1300), azim=-52, elev=22, ss=2, zoom=1.0, bg=(255,255,255), center=None):
    W,H=size[0]*ss,size[1]*ss
    a,e=math.radians(azim),math.radians(elev)
    # camera basis (orthographic)
    d=np.array([math.cos(e)*math.cos(a),math.cos(e)*math.sin(a),math.sin(e)])   # from scene to camera
    right=np.cross([0,0,1],d); right/=np.linalg.norm(right)
    up=np.cross(d,right)
    allv=np.concatenate([t.reshape(-1,3) for t,_ in items])
    c=(allv.min(0)+allv.max(0))/2 if center is None else np.array(center)
    def proj(P): 
        q=P-c; return np.stack([q@right,q@up,q@d],-1)
    pr=[proj(t) for t,_ in items]
    ext=np.concatenate([p.reshape(-1,3) for p in pr])
    span=max(ext[:,0].max()-ext[:,0].min(), ext[:,1].max()-ext[:,1].min())
    s=min(W,H)*0.9/span*zoom
    cx0=(ext[:,0].max()+ext[:,0].min())/2; cy0=(ext[:,1].max()+ext[:,1].min())/2
    img=np.zeros((H,W,3),np.float32); img[:]=np.array(bg)/255.
    zb=np.full((H,W),-1e9,np.float32)
    L1=np.array([.5,-.6,.75]); L1/=np.linalg.norm(L1)
    L2=np.array([-.7,.2,.4]); L2/=np.linalg.norm(L2)
    for (tri,col),p in zip(items,pr):
        n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); ln=np.linalg.norm(n,axis=1,keepdims=True); ln[ln==0]=1; n=n/ln
        sh=0.32+0.6*np.clip(np.abs(n@L1),0,1)*1.0+0.25*np.clip(np.abs(n@L2),0,1)
        sh=np.clip(sh,0,1.1)
        X=(p[:,:,0]-cx0)*s+W/2; Y=H/2-(p[:,:,1]-cy0)*s; Z=p[:,:,2]
        for i in range(len(tri)):
            x=X[i];y=Y[i];z=Z[i]
            x0=max(int(np.floor(x.min())),0);x1=min(int(np.ceil(x.max())),W-1)
            y0=max(int(np.floor(y.min())),0);y1=min(int(np.ceil(y.max())),H-1)
            if x1<x0 or y1<y0: continue
            den=(y[1]-y[2])*(x[0]-x[2])+(x[2]-x[1])*(y[0]-y[2])
            if abs(den)<1e-9: continue
            gx,gy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
            l0=((y[1]-y[2])*(gx-x[2])+(x[2]-x[1])*(gy-y[2]))/den
            l1=((y[2]-y[0])*(gx-x[2])+(x[0]-x[2])*(gy-y[2]))/den
            l2=1-l0-l1
            m=(l0>=-1e-4)&(l1>=-1e-4)&(l2>=-1e-4)
            if not m.any(): continue
            zz=l0*z[0]+l1*z[1]+l2*z[2]
            sub=zb[y0:y1+1,x0:x1+1]; upd=m&(zz>sub)
            if not upd.any(): continue
            sub[upd]=zz[upd]
            img[y0:y1+1,x0:x1+1][upd]=np.clip(col*sh[i],0,1)
    im=Image.fromarray((img*255).astype(np.uint8)).resize(size,Image.LANCZOS)
    im.save(path); return im
