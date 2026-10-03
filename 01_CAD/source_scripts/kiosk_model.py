import cadquery as cq, math, itertools

def box(cx,cy,cz,dx,dy,dz):
    return cq.Workplane("XY").box(dx,dy,dz).translate((cx,cy,cz))
def cyl(r,h,p,d):
    return cq.Workplane("XY").newObject([cq.Solid.makeCylinder(r,h,cq.Vector(*p),cq.Vector(*d))])

BOLTS=[(sx*165,sy*100) for sx in(-1,1) for sy in(-1,1)]
HEAD_PARTS=["Head_Rear_Housing","Display_Bezel","Display_15in_Panel","Vent_Grille","Camera_Mount_Plate","Camera_Module"]

def build_parts(TILT=40.0):
    low=lambda t: 45*math.sin(math.radians(t))+170*math.cos(math.radians(t))
    HEAD_POS=(0,60,1010+low(TILT)-low(40.0))
    def head(wp): return wp.rotate((0,0,0),(1,0,0),-TILT).translate(HEAD_POS)
    def head_pt(x,y,z):
        a=math.radians(-TILT); return (x,y*math.cos(a)-z*math.sin(a)+HEAD_POS[1],y*math.sin(a)+z*math.cos(a)+HEAD_POS[2])
    P={}
    def add(n,wp,col,grp,mat): P[n]=(wp,col,grp,mat)
    # BASE
    base=cq.Workplane("XY").rect(620,280).extrude(20).union(cq.Workplane("XY").rect(280,520).extrude(20)).edges("|Z").fillet(55)
    for x,y in BOLTS: base=base.cut(cyl(4.5,30,(x,y,-1),(0,0,1)))
    add("Base_Plate",base,(.18,.18,.2),"Base","Steel, powder coat black")
    fl=box(0,0,24,360,240,8)
    for x,y in BOLTS: fl=fl.cut(cyl(4.5,30,(x,y,10),(0,0,1)))
    add("Column_Flange",fl,(.3,.3,.32),"Base","Steel, zinc plated")
    for i,(x,y) in enumerate([(-260,0),(260,0),(0,-210),(0,210)]):
        add(f"Rubber_Foot_{i+1}",cyl(15,6,(x,y,-6),(0,0,1)),(.05,.05,.05),"Base","EPDM rubber")
    for i,(x,y) in enumerate(BOLTS):
        b=cyl(4,28,(x,y,0),(0,0,1)).union(cq.Workplane("XY").workplane(offset=28).center(x,y).polygon(6,16).extrude(5))
        add(f"Bolt_M8_{i+1}",b,(.6,.6,.62),"Fasteners","Steel, zinc plated")
    # COLUMN
    add("Column_Front_Panel",box(0,-99,433,300,2,810).cut(box(0,-99,700,80,10,30)),(.9,.9,.92),"Column","Steel 2 mm, powder coat white")
    add("Column_Rear_Cover",box(0,99,433,300,2,810).cut(box(0,99,200,60,10,30)),(.25,.25,.28),"Column","Steel 2 mm, powder coat dark")
    add("Column_Side_Left",box(-149,0,433,2,196,810),(.25,.25,.28),"Column","Steel 2 mm, powder coat dark")
    add("Column_Side_Right",box(149,0,433,2,196,810),(.25,.25,.28),"Column","Steel 2 mm, powder coat dark")
    add("Column_Top_Plate",box(0,0,839,296,196,2),(.25,.25,.28),"Column","Steel 2 mm")
    for i,(sx,sy) in enumerate(itertools.product((-1,1),(-1,1))):
        add(f"Frame_Rail_{i+1}",box(sx*130,sy*80,433,20,20,810).faces(">Z").shell(-2),(.5,.5,.55),"Column","Steel tube 20x20x2")
    # HEAD
    hs=box(0,5,0,420,80,340).edges("|Y").fillet(15).faces("<Y").shell(-3).cut(cyl(28,20,(200,15,-60),(1,0,0)))
    add("Head_Rear_Housing",head(hs),(.25,.25,.28),"Head","Sheet steel / ABS, dark")
    bz=box(0,-41,0,420,12,340).edges("|Y").fillet(15).faces("<Y").edges().chamfer(3)
    bz=bz.cut(box(0,-41,5,300,20,225)).cut(cyl(6,30,(0,-30,148),(0,-1,0)))
    add("Display_Bezel",head(bz),(.8,.8,.83),"Head","Aluminium, brushed")
    add("Display_15in_Panel",head(box(0,-29,5,320,12,245)),(.1,.1,.12),"Head","LCD module, black glass")
    gr=cyl(30,4,(210,15,-60),(1,0,0))
    for dz in(-16,-8,0,8,16): gr=gr.cut(box(212,15,-60+dz,10,44,4))
    add("Vent_Grille",head(gr),(.1,.1,.1),"Head","ABS black")
    add("Camera_Mount_Plate",head(box(0,-33.5,151,50,3,32).cut(cyl(5.5,10,(0,-30,148),(0,-1,0)))),(.5,.5,.55),"Head","Steel 3 mm")
    add("Camera_Module",head(box(0,-27,148,30,10,12).union(cyl(5,14,(0,-32,148),(0,-1,0)))),(.05,.05,.3),"Head","Camera board + lens")
    pads=box(-100,5,-173,40,60,6).union(box(100,5,-173,40,60,6))
    px,py,pz=head_pt(0,5,-173); pdy=60*math.cos(math.radians(TILT))
    zt=pz+30; zb=846
    post=lambda x: box(x,py,(zb+zt)/2,40,pdy,zt-zb)
    br=box(0,-30,843,260,100,6).union(post(-100)).union(post(100)).union(head(pads))
    br=br.cut(head(box(0,0,80,1200,1200,500)))
    add("Tilt_Bracket",br,(.5,.5,.55),"Head","Steel 6 mm")
    # QR
    add("QR_Scanner_Module",box(0,-85.5,700,70,25,60),(.05,.05,.05),"Column","Scanner module")
    add("QR_Scanner_Bracket",box(0,-71.5,700,240,3,60),(.5,.5,.55),"Column","Steel 3 mm")
    # ELECTRONICS
    add("Electronics_Box",box(0,155,280,240,110,360).faces("<Y").shell(-2),(.25,.25,.28),"Electronics","Steel 2 mm, powder coat dark")
    add("Mounting_Plate",box(0,207,280,200,2,300),(.6,.6,.62),"Electronics","Steel 2 mm, galvanised")
    add("Raspberry_Pi_Block",box(-50,199,350,85,14,56),(.1,.5,.2),"Electronics","Raspberry Pi 4 (simplified)")
    add("Power_Supply_Block",box(40,191,250,100,30,60),(.7,.7,.1),"Electronics","5V/12V PSU (simplified)")
    for i,x in enumerate((-60,0,60)):
        add(f"Cable_Gland_{i+1}",cyl(9,10,(x,150,90),(0,0,1)),(.05,.05,.05),"Electronics","PG9 nylon")
    return P

def interference(P):
    names=list(P); bbs={k:P[k][0].val().BoundingBox() for k in names}; rep=[]
    for a,b in itertools.combinations(names,2):
        A,B=bbs[a],bbs[b]
        if A.xmax<B.xmin or B.xmax<A.xmin or A.ymax<B.ymin or B.ymax<A.ymin or A.zmax<B.zmin or B.zmax<A.zmin: continue
        try: v=P[a][0].intersect(P[b][0]).val().Volume()
        except Exception: v=0
        if v>1: rep.append((a,b,round(v/1000,2)))
    return rep
