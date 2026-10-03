import sys,math,re,warnings; warnings.filterwarnings("ignore")
sys.path.insert(0,'/home/claude/kiosk')
from kiosk_model import *
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from OCP.BRepLib import BRepLib
from OCP.HLRBRep import HLRBRep_Algo,HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from cadquery.occ_impl.shapes import Shape,TOLERANCE
R="/mnt/user-data/outputs/Attendance_Kiosk_Project"

def hlr(shape,N,Vx):
    algo=HLRBRep_Algo(); algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(),gp_Dir(*N),gp_Dir(*Vx)))); algo.Update(); algo.Hide()
    h=HLRBRep_HLRToShape(algo)
    vis=[c for c in (h.VCompound(),h.Rg1LineVCompound(),h.OutLineVCompound()) if not c.IsNull()]
    hid=[c for c in (h.HCompound(),h.OutLineHCompound()) if not c.IsNull()]
    for c in vis+hid: BRepLib.BuildCurves3d_s(c,TOLERANCE)
    def poly(comps):
        out=[]
        for c in comps:
            for e in Shape(c).Edges():
                cu=e._geomAdaptor(); pts=GCPnts_QuasiUniformDeflection(cu,0.05,cu.FirstParameter(),cu.LastParameter())
                if pts.IsDone(): out.append(np.array([[pts.Value(i+1).X(),pts.Value(i+1).Y()] for i in range(pts.NbPoints())]))
        return out
    return poly(vis),poly(hid)

def draw(ax,polys,ox,oy,s,lw=.45,c='k',ls='-'):
    for p in polys: ax.plot(ox+p[:,0]*s,oy+p[:,1]*s,c=c,lw=lw,ls=ls,solid_capstyle='round')
def bounds(polys):
    a=np.concatenate(polys); return a.min(0),a.max(0)
def place(ax,polys,cx,by,s,hid=None,lw=.45):
    mn,mx=bounds(polys); ox=cx-(mn[0]+mx[0])/2*s; oy=by-mn[1]*s
    draw(ax,polys,ox,oy,s,lw=lw)
    if hid: draw(ax,hid,ox,oy,s,lw=.25,c='#666',ls=(0,(3,2)))
    return ox,oy,mn,mx
def arrow(ax,a,b): ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="<->",lw=.4,color='k',shrinkA=0,shrinkB=0,mutation_scale=6))
def dimh(ax,x1,x2,y,label,off=8,fs=6):
    for x in(x1,x2): ax.plot([x,x],[y+(1 if off>0 else -1),y+off+(1.5 if off>0 else -1.5)],c='k',lw=.3)
    arrow(ax,(x1,y+off),(x2,y+off)); ax.text((x1+x2)/2,y+off+(1.2 if off>0 else -3.2),label,ha='center',fontsize=fs)
def dimv(ax,y1,y2,x,label,off=-8,fs=6):
    for y in(y1,y2): ax.plot([x+(-1 if off<0 else 1),x+off+(-1.5 if off<0 else 1.5)],[y,y],c='k',lw=.3)
    arrow(ax,(x+off,y1),(x+off,y2)); ax.text(x+off+(-1.2 if off<0 else 1.2),(y1+y2)/2,label,ha='right' if off<0 else 'left',va='center',rotation=90,fontsize=fs)

def sheet(pdf,title,dwg,scale,n,total=3,mat="See BOM"):
    fig=plt.figure(figsize=(420/25.4,297/25.4)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,420); ax.set_ylim(0,297); ax.axis('off')
    ax.plot([10,410,410,10,10],[10,10,287,287,10],c='k',lw=1.1)
    x0,y0=225,10
    ax.plot([x0,410],[y0+38,y0+38],c='k',lw=.8); ax.plot([x0,x0],[y0,y0+38],c='k',lw=.8)
    for yy in(y0+12,y0+24): ax.plot([x0,410],[yy,yy],c='k',lw=.4)
    ax.plot([x0+95,x0+95],[y0,y0+24],c='k',lw=.4)
    ax.text(x0+3,y0+30,title,fontsize=11,weight='bold',va='center')
    ax.text(x0+3,y0+18,"DWG NO: "+dwg,fontsize=7,va='center'); ax.text(x0+98,y0+18,"SCALE: "+scale,fontsize=7,va='center')
    ax.text(x0+3,y0+6,"UNITS: mm   3rd ANGLE PROJECTION",fontsize=6.5,va='center'); ax.text(x0+98,y0+6,f"SHEET {n} OF {total}",fontsize=7,va='center')
    ax.text(x0+3,y0+34.5,"AUTOMATED ATTENDANCE KIOSK  |  Drawn by: ______   Date: 30-Sep-2026   Material: "+mat,fontsize=5.2,va='center')
    return fig,ax

P=build_parts(40)
comp=cq.Compound.makeCompound([p[0].val() for p in P.values()])
pdf=PdfPages(f"{R}/03_Drawings/Attendance_Kiosk_Drawings.pdf")

# ================= SHEET 1 : assembly =================
fig,ax=sheet(pdf,"KIOSK ASSEMBLY - GENERAL ARRANGEMENT","KSK-000","1:10 (iso 1:12)",1)
s=0.1
fv,_=hlr(comp,(0,-1,0),(1,0,0)); sv,_=hlr(comp,(1,0,0),(0,1,0)); tv,_=hlr(comp,(0,0,1),(1,0,0))
ox,oy,mn,mx=place(ax,fv,60,58,s); 
ax.text(60,41,"FRONT VIEW",ha='center',fontsize=7,weight='bold')
dimv(ax,58,58+(mx[1]-mn[1])*s,60-(mx[0]-mn[0])*s/2,"1175 (overall height)",off=-9)
dimh(ax,60-(mx[0]-mn[0])*s/2,60+(mx[0]-mn[0])*s/2,58,"620 (base width)",off=-5)
ox2,oy2,mn2,mx2=place(ax,sv,150,58,s); ax.text(150,41,"RIGHT VIEW",ha='center',fontsize=7,weight='bold')
dimh(ax,150-(mx2[0]-mn2[0])*s/2,150+(mx2[0]-mn2[0])*s/2,58,"520 (base depth)",off=-5)
# tilt annotation
ax.text(105,225,"Head tilt 40 deg\n(design range 30-40 deg)",fontsize=6.5)
ox3,oy3,mn3,mx3=place(ax,tv,60,205,s); ax.text(60,197,"TOP VIEW",ha='center',fontsize=7,weight='bold')
# iso
n=np.array([math.cos(math.radians(22))*math.cos(math.radians(-52)),math.cos(math.radians(22))*math.sin(math.radians(-52)),math.sin(math.radians(22))])
vx=np.cross([0,0,1],n); vx/=np.linalg.norm(vx)
iv,_=hlr(comp,tuple(n),tuple(vx)); place(ax,iv,315,60,1/12,lw=.35); ax.text(315,52,"ISOMETRIC VIEW",ha='center',fontsize=7,weight='bold')
# BOM (grouped)
groups={}
for nm,(wp,c,g,m) in P.items(): groups.setdefault(re.sub(r"_\d+$","",nm),[nm,g,m,0])[3]+=1
rows=[("ITEM","QTY","PART NAME","SUB-ASSEMBLY","MATERIAL")]+[(str(i),str(v[3]),k,v[1],v[2]) for i,(k,v) in enumerate(groups.items(),1)]
bx,by,rh=178,283,5.2; cw=[10,10,52,26,0]; xs=[bx,bx+10,bx+20,bx+72,bx+98]
for i,r in enumerate(rows):
    y=by-i*rh
    ax.plot([bx,410],[y-rh,y-rh],c='k',lw=.3); 
    for xx,t in zip(xs,r): ax.text(xx+1,y-rh/2,t,fontsize=5.3 if i else 5.6,va='center',weight='bold' if i==0 else 'normal')
ax.plot([bx,410],[by,by],c='k',lw=.6)
for xx in xs[1:]+[]: ax.plot([xx,xx],[by,by-len(rows)*rh],c='k',lw=.3)
ax.plot([bx,bx],[by,by-len(rows)*rh],c='k',lw=.6); ax.plot([410,410],[by,by-len(rows)*rh],c='k',lw=.6)
ax.text(bx+1,by+2,f"BILL OF MATERIALS ({len(P)} components, grouped)",fontsize=6.5,weight='bold')
pdf.savefig(fig); plt.close(fig)

# ================= SHEET 2 : base plate + flange =================
fig,ax=sheet(pdf,"BASE PLATE & COLUMN FLANGE","KSK-100 / KSK-101","1:4",2,mat="Steel, powder coat black / zinc plated")
s=0.25
bp=P["Base_Plate"][0].val(); fl=P["Column_Flange"][0].val()
t,_=hlr(bp,(0,0,1),(1,0,0)); f,_=hlr(bp,(0,-1,0),(1,0,0))
cx,by=105,118
ox,oy,mn,mx=place(ax,t,cx,by,s); w=(mx[0]-mn[0])*s; h=(mx[1]-mn[1])*s
ax.text(cx,by-9,"BASE PLATE - TOP VIEW",ha='center',fontsize=7,weight='bold')
dimh(ax,cx-w/2,cx+w/2,by+h,"620",off=9); dimv(ax,by,by+h,cx-w/2,"520",off=-9)
# lobe widths
cyc=by+h/2
dimh(ax,cx-140*s,cx+140*s,by+h,"280",off=18)
dimv(ax,cyc-140*s,cyc+140*s,cx+w/2,"280",off=9)
for hx,hy in BOLTS:
    ax.add_patch(plt.Circle((cx+hx*s,cyc+hy*s),4.5*s,fill=False,lw=.4))
ax.annotate("4x dia 9 THRU\n(330 x 200 pattern)",xy=(cx+165*s,cyc+100*s),xytext=(cx+35,cyc+50),fontsize=6,arrowprops=dict(arrowstyle="-",lw=.3))
ax.annotate("R55 (all outer corners)",xy=(cx-w/2+8,by+h*0.2),xytext=(cx-w/2-5,by-2),fontsize=6,arrowprops=dict(arrowstyle="-",lw=.3),ha='left')
place(ax,f,cx,by-42,s); ax.text(cx,by-52,"FRONT VIEW",ha='center',fontsize=7,weight='bold')
dimv(ax,by-42,by-42+20*s,cx+w/2,"20",off=8)
ft,_=hlr(fl,(0,0,1),(1,0,0)); cx2,by2=335,190
ox,oy,mn,mx=place(ax,ft,cx2,by2,s); w2=(mx[0]-mn[0])*s; h2=(mx[1]-mn[1])*s
ax.text(cx2,by2-9,"COLUMN FLANGE - TOP VIEW",ha='center',fontsize=7,weight='bold')
dimh(ax,cx2-w2/2,cx2+w2/2,by2+h2,"360",off=8); dimv(ax,by2,by2+h2,cx2-w2/2,"240",off=-8)
for hx,hy in BOLTS: ax.add_patch(plt.Circle((cx2+hx*s,by2+h2/2+hy*s),4.5*s,fill=False,lw=.4))
ax.annotate("4x dia 9 THRU",xy=(cx2+165*s,by2+h2/2+100*s),xytext=(cx2+w2/2-8,by2+h2+14),fontsize=6,arrowprops=dict(arrowstyle="-",lw=.3))
ax.text(cx2,by2-18,"THICKNESS 8 mm",ha='center',fontsize=6.5)
ax.text(235,120,"NOTES\n1. Flange is bolted to base plate with 4x M8 hex bolts (see KSK-000).\n2. Deburr all edges. Break sharp corners 0.5 mm.\n3. Rubber feet (dia 30 x 6) fitted under base at 4 lobe ends.\n4. General tolerance +/-0.5 mm.",fontsize=6.3,va='top')
pdf.savefig(fig); plt.close(fig)

# ================= SHEET 3 : panels (flat patterns) =================
fig,ax=sheet(pdf,"COLUMN SHEET-METAL PANELS (FLAT)","KSK-200 to 204","1:5",3,mat="Steel sheet 2 mm, powder coat")
s=0.2; by=70
def panel(cx,w,h,label,slot=None,qty=1,name=""):
    ax.add_patch(plt.Rectangle((cx-w*s/2,by),w*s,h*s,fill=False,lw=.55))
    if slot:
        sw,sh,sz=slot; ax.add_patch(plt.Rectangle((cx-sw*s/2,by+(sz-sh/2)*s),sw*s,sh*s,fill=False,lw=.55))
        dimh(ax,cx-sw*s/2,cx+sw*s/2,by+(sz+sh/2)*s,f"{sw}",off=6); dimv(ax,by+(sz-sh/2)*s,by+(sz+sh/2)*s,cx+sw*s/2,f"{sh}",off=6)
        dimv(ax,by,by+sz*s,cx-w*s/2,f"{sz}",off=-16)
    dimh(ax,cx-w*s/2,cx+w*s/2,by,f"{w}",off=-8); dimv(ax,by,by+h*s,cx+w*s/2,f"{h}",off=9)
    ax.text(cx,by+h*s+8,label,ha='center',fontsize=6.6,weight='bold'); ax.text(cx,by-18,f"QTY {qty}",ha='center',fontsize=6)
panel(55,300,810,"FRONT PANEL (KSK-200)",slot=(80,30,672))
panel(150,300,810,"REAR COVER (KSK-201)",slot=(60,30,172))
panel(235,196,810,"SIDE PANEL (KSK-202)",qty=2)
panel(310,296,196,"TOP PLATE (KSK-203)")
ax.text(285,262,"NOTES\n1. Thickness 2 mm. Laser-cut from flat sheet.\n2. Slot positions measured from bottom edge.\n3. Front slot = QR scanner window.\n4. Rear slot = cable pass-through to\n    electronics enclosure.\n5. In SolidWorks add edge flanges and\n    bend reliefs for full sheet-metal model.",fontsize=6.3,va='top')
pdf.savefig(fig); plt.close(fig)
pdf.close(); print("ok")
