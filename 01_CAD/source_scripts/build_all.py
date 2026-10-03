import sys,math,csv,warnings; warnings.filterwarnings("ignore")
sys.path.insert(0,'/home/claude/kiosk')
from kiosk_model import *; from render import *
from PIL import Image
R="/mnt/user-data/outputs/Attendance_Kiosk_Project"
# ---------- CAD ----------
def save_asm(P,path):
    a=cq.Assembly(name="Attendance_Kiosk")
    for n,(wp,col,*_) in P.items(): a.add(wp,name=n,color=cq.Color(*col))
    a.save(path)
P=build_parts(40)
for n,(wp,*_) in P.items(): cq.exporters.export(wp,f"{R}/01_CAD/parts/{n}.step")
save_asm(P,f"{R}/01_CAD/Attendance_Kiosk_Assembly.step")
for t in (30,35,40):
    Pt=build_parts(t); assert not interference(Pt); save_asm(Pt,f"{R}/01_CAD/tilt_variants/Attendance_Kiosk_Tilt{t}deg.step")
with open(f"{R}/01_CAD/BOM.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["Item","Part","Sub-assembly","Material","Volume_cm3","Mass_kg_est"])
    dens={"Steel":7.85,"EPDM":1.1,"Alumin":2.7,"ABS":1.05,"Sheet":7.85}
    for i,(nm,(wp,c,g,m)) in enumerate(P.items(),1):
        v=wp.val().Volume()/1000; d=next((x for k,x in dens.items() if m.startswith(k)),1.5)
        w.writerow([i,nm,g,m,round(v,1),round(v*d/1000,2)])
with open(f"{R}/01_CAD/interference_report.txt","w") as f:
    f.write("Interference check (all part pairs, tilt 30/35/40 deg): no overlapping volumes found.\n")
# ---------- Flat patterns (DXF) ----------
def dxf(name,w,h,cuts):
    s=cq.Workplane("XY").rect(w,h)
    for cx,cy,cw,ch in cuts: s=s.moveTo(cx,cy).rect(cw,ch)
    cq.exporters.export(s,f"{R}/01_CAD/flat_patterns_DXF/{name}.dxf")
dxf("Column_Front_Panel_300x810",300,810,[(0,700-433,80,30)])
dxf("Column_Rear_Cover_300x810",300,810,[(0,200-433,60,30)])
dxf("Column_Side_Panel_196x810",196,810,[])
dxf("Column_Top_Plate_296x196",296,196,[])
# ---------- Renders ----------
it=tris_of(P,tol=1.0)
render(it,f"{R}/02_Renders/hero_view.png",size=(1400,1700),azim=-52,elev=22)
render(it,f"{R}/02_Renders/back_view.png",size=(1400,1700),azim=130,elev=22)
panels={"Column_Front_Panel","Column_Rear_Cover","Column_Side_Left","Column_Side_Right","Column_Top_Plate"}
render(tris_of(P,hide=panels,tol=1.0),f"{R}/02_Renders/internal_view_panels_hidden.png",size=(1400,1700),azim=-38,elev=20)
def N(k): return (0,-k*math.cos(math.radians(40)),k*math.sin(math.radians(40)))
ex={}
for i in range(1,5): ex[f"Rubber_Foot_{i}"]=(0,0,-80); ex[f"Bolt_M8_{i}"]=(0,0,220)
ex["Column_Flange"]=(0,0,60)
ex.update({"Column_Front_Panel":(0,-220,80),"Column_Rear_Cover":(0,220,80),"Column_Side_Left":(-220,0,80),"Column_Side_Right":(220,0,80)})
for i in range(1,5): ex[f"Frame_Rail_{i}"]=(0,0,120)
ex.update({"Column_Top_Plate":(0,0,260),"Tilt_Bracket":(0,0,330),"QR_Scanner_Module":(0,-340,80),"QR_Scanner_Bracket":(0,-160,80),
 "Electronics_Box":(0,320,80),"Mounting_Plate":(0,390,80),"Raspberry_Pi_Block":(0,350,210),"Power_Supply_Block":(0,350,60)})
for i in range(1,4): ex[f"Cable_Gland_{i}"]=(0,320,-40)
for k,d in {"Head_Rear_Housing":0,"Display_15in_Panel":140,"Display_Bezel":280,"Camera_Module":90,"Camera_Mount_Plate":60,"Vent_Grille":0}.items():
    n=N(d); ex[k]=(n[0]+(300 if k=="Vent_Grille" else 0),n[1],n[2]+420)
render(tris_of(P,offs=ex,tol=1.5),f"{R}/02_Renders/exploded_view.png",size=(1500,1700),azim=-48,elev=18,zoom=1.0)
# ---------- Animations ----------
frames=[]
import numpy as np
base_center=None
allv=np.concatenate([t.reshape(-1,3) for t,_ in tris_of(P,offs=ex,tol=2)])
ctr=(allv.min(0)+allv.max(0))/2
for i in range(36):
    ph=(1-math.cos(2*math.pi*i/36))/2
    o={k:tuple(x*ph for x in v) for k,v in ex.items()}
    im=render(tris_of(P,offs=o,tol=2.0),f"/tmp/f.png",size=(560,680),azim=-58+ph*12,elev=20,center=ctr+np.array([0,0,0]) ,zoom=0.85,ss=2)
    frames.append(im.convert("P",palette=Image.ADAPTIVE,colors=128))
frames[0].save(f"{R}/02_Renders/exploded_animation.gif",save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=True)
piv=np.array([0,60+45*math.cos(math.radians(40))+(-170)*math.sin(math.radians(40))*(-1)*0,0])
a=math.radians(-40); hp=(0,60+45*math.cos(a)-(-170)*math.sin(a),1010+45*math.sin(a)+(-170)*math.cos(a))
def rot(d):
    c,s=math.cos(math.radians(d)),math.sin(math.radians(d))
    def f(V):
        V=V.copy(); y=V[:,1]-hp[1]; z=V[:,2]-hp[2]
        V[:,1]=hp[1]+y*c-z*s; V[:,2]=hp[2]+y*s+z*c; return V
    return f
frames=[]
ct=np.array([0,0,560])
for i in range(36):
    tilt=37.5+7.5*math.sin(2*math.pi*i/36)          # 30..45 deg
    d=40-tilt
    er={k:rot(d) for k in HEAD_PARTS}
    im=render(tris_of(P,extra_rot=er,tol=2.0),"/tmp/f.png",size=(560,680),azim=-58,elev=18,center=ct,zoom=1.0,ss=2)
    frames.append(im.convert("P",palette=Image.ADAPTIVE,colors=128))
frames[0].save(f"{R}/02_Renders/head_tilt_animation.gif",save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=True)
print("done")
