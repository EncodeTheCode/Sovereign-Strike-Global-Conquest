from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import math

OUT=Path('/mnt/data')
S=3
CW,CH=256,208
COLS,ROWS=4,2
ATLAS=Image.new('RGBA',(CW*COLS,CH*ROWS),(0,0,0,0))

# Palette: weathered Westwood-inspired gunmetal, concrete, muted yellow trim.
DARK=(28,34,36,255); EDGE=(17,22,24,255); STEEL=(73,82,83,255)
MID=(105,114,112,255); LIGHT=(157,163,154,255); TOP=(126,135,129,255)
YELLOW=(192,155,48,255); YLIGHT=(226,193,83,255); YDARK=(106,83,31,255)
WINDOW=(23,39,42,255); GLASS=(71,111,119,255); CONCRETE=(113,119,113,255)

class Painter:
    def __init__(self):
        self.im=Image.new('RGBA',(CW*S,CH*S),(0,0,0,0))
        self.d=ImageDraw.Draw(self.im,'RGBA')
    def xy(self,p): return tuple(int(round(v*S)) for v in p)
    def poly(self,pts,fill,outline=EDGE,width=1):
        pts=[self.xy(p) for p in pts]
        self.d.polygon(pts,fill=fill)
        if outline:self.d.line(pts+[pts[0]],fill=outline,width=max(1,int(width*S)),joint='curve')
    def line(self,pts,fill,width=1):
        self.d.line([self.xy(p) for p in pts],fill=fill,width=max(1,int(width*S)),joint='curve')
    def rect(self,box,fill,outline=EDGE,width=1):
        b=tuple(int(round(v*S)) for v in box); self.d.rectangle(b,fill=fill,outline=outline,width=max(1,int(width*S)) if outline else 1)
    def ellipse(self,box,fill,outline=EDGE,width=1):
        b=tuple(int(round(v*S)) for v in box); self.d.ellipse(b,fill=fill,outline=outline,width=max(1,int(width*S)) if outline else 1)
    def rounded(self,box,r,fill,outline=EDGE,width=1):
        b=tuple(int(round(v*S)) for v in box); self.d.rounded_rectangle(b,radius=int(r*S),fill=fill,outline=outline,width=max(1,int(width*S)) if outline else 1)
    def arc(self,box,start,end,fill,width=1):
        b=tuple(int(round(v*S)) for v in box); self.d.arc(b,start=start,end=end,fill=fill,width=max(1,int(width*S)))
    def text(self,xy,text,fill=LIGHT,stroke=EDGE):
        self.d.text(self.xy(xy),text,fill=fill,stroke_width=1,stroke_fill=stroke)
    def finish(self):
        return self.im.resize((CW,CH),Image.Resampling.LANCZOS)

def base(p, kind, width=148, depth=78):
    cx=128; y=168
    # Soft ground shadow is a separate transparent patch, not a hard rectangle.
    sh=Image.new('RGBA',p.im.size,(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.ellipse(((cx-width/2+5)*S,(y-depth/2+9)*S,(cx+width/2+12)*S,(y+depth/2+16)*S),fill=(11,15,16,92))
    sh=sh.filter(ImageFilter.GaussianBlur(7*S));p.im.alpha_composite(sh);p.d=ImageDraw.Draw(p.im,'RGBA')
    # Iso pad, with front edge thicker/darker for clear ground contact.
    a=(cx,y-depth/2); b=(cx+width/2,y); c=(cx,y+depth/2); d=(cx-width/2,y)
    p.poly([a,b,c,d],(91,98,94,255),EDGE,2)
    p.poly([a,b,(cx,y+depth/2-5),(cx-width/2,y-5)],(145,151,143,255),(44,50,50,255),1)
    p.poly([(cx-width/2,y-5),(cx,y+depth/2-5),c,d],(75,82,80,255),EDGE,1)
    p.line([(cx-width/2+8,y),(cx,y+depth/2-10),(cx+width/2-8,y)],(190,190,170,130),1)
    # Yellow-black safety perimeter markings.
    for i in range(5):
        xx=cx-width/2+20+i*25
        p.line([(xx,y+depth/2-8),(xx+8,y+depth/2-4)],YELLOW,2)
    return cx,y

def box_iso(p,cx,frontY,w,d,baseH,wallH,topColor=TOP,frontColor=STEEL,sideColor=(57,66,68,255),trim=True):
    # Coordinates describe a 3/4 isometric industrial building: visible roof,
    # front wall and right side wall, with distinct light and shade planes.
    y=frontY-wallH
    front=[(cx-w/2,y+d/2),(cx+w/2,y+d/2),(cx+w/2,frontY),(cx-w/2,frontY)]
    side=[(cx+w/2,y+d/2),(cx+w/2+d*.40,y),(cx+w/2+d*.40,frontY-d*.12),(cx+w/2,frontY)]
    roof=[(cx-w/2,y+d/2),(cx,y),(cx+d*.40,y-d*.12),(cx+w/2+d*.40,y),(cx+w/2,y+d/2)]
    p.poly(side,sideColor,EDGE,2)
    p.poly(front,frontColor,EDGE,2)
    p.poly(roof,topColor,EDGE,2)
    # Raised parapet along roof perimeter.
    p.line([(cx-w/2+4,y+d/2-2),(cx,y+3),(cx+d*.40-2,y-d*.12+3)],LIGHT,2)
    if trim:
        p.poly([(cx-w/2,y+d/2-5),(cx+w/2,y+d/2-5),(cx+w/2,frontY-wallH+wallH*.14),(cx-w/2,frontY-wallH+wallH*.14)],(YELLOW[0],YELLOW[1],YELLOW[2],255),None)
        p.line([(cx-w/2,y+d/2-4),(cx+w/2,y+d/2-4)],YLIGHT,2)
    return {'cx':cx,'y':y,'frontY':frontY,'w':w,'d':d,'front':front,'side':side,'roof':roof}

def vent(p,x,y,r=7):
    p.ellipse((x-r,y-r*.45,x+r,y+r*.45),DARK,EDGE,2)
    p.ellipse((x-r+2,y-r*.45+1,x+r-2,y+r*.45-1),MID,EDGE,1)
    p.line([(x-r+3,y),(x+r-3,y)],LIGHT,1)

def pipe(p,pts,width=5,color=YELLOW):
    p.line(pts,(25,30,30,255),width+2);p.line(pts,color,width)
    for x,y in pts[1:-1]: p.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),YLIGHT,EDGE,1)

def draw_power():
    p=Painter();cx,y=base(p,'power',142,78)
    b=box_iso(p,cx,154,104,43,0,55,(108,119,113,255),(64,74,75,255),(42,51,54,255))
    # Large thermal exhaust stacks with striped warning collars.
    for x,top in [(95,54),(157,44)]:
        p.ellipse((x-12,top-4,x+12,top+5),DARK,EDGE,2)
        p.rect((x-11,top,x+11,125),MID,EDGE,2)
        p.poly([(x-11,top+2),(x-5,top+6),(x-5,125),(x-11,121)],(59,68,68,255),EDGE,1)
        p.rect((x-11,top+15,x+11,top+22),YELLOW,EDGE,1)
        p.ellipse((x-11,top-4,x+11,top+4),LIGHT,EDGE,1)
        p.ellipse((x-6,top-2,x+6,top+2),WINDOW,None)
    # Transformer banks and insulators.
    for x in [66,184]:
        p.rect((x-15,129,x+15,149),STEEL,EDGE,2)
        p.rect((x-12,132,x+12,145),DARK,None)
        for k in range(3):
            xx=x-9+k*9
            p.rect((xx-2,120,xx+2,132),YELLOW,EDGE,1)
            p.ellipse((xx-4,116,xx+4,123),LIGHT,EDGE,1)
    # Yellow power conduits and lit status panels.
    pipe(p,[(80,135),(92,140),(100,146)],4)
    p.rect((119,130,137,146),WINDOW,EDGE,1);p.rect((122,133,134,135),YLIGHT,None)
    p.rect((122,138,132,141),GLASS,None)
    # Transformer cabinets, riveted cladding and insulator wiring give the plant
    # a readable electrical-generation silhouette at normal gameplay scale.
    for xx in [56,200]:
        p.rect((xx-7,144,xx+7,156),DARK,EDGE,1);p.rect((xx-5,146,xx+5,150),YELLOW,None)
        for yy in [132,139,146]: p.ellipse((xx-2,yy-1,xx+2,yy+2),LIGHT,EDGE,1)
    p.line([(77,151),(91,151),(98,146)],YLIGHT,2)
    p.rect((107,78,119,88),DARK,EDGE,1);p.rect((109,80,117,83),GLASS,None)
    for xx in [110,145]:
        for yy in [101,110,119]: p.ellipse((xx,yy,xx+2,yy+2),LIGHT,EDGE,1)
    return p.finish()

def draw_barracks():
    p=Painter();cx,y=base(p,'barracks',142,78)
    b=box_iso(p,cx,157,120,43,0,55,(94,106,106,255),(66,76,77,255),(42,51,53,255))
    # Main personnel entrance with yellow sliding gate and lit lintel.
    p.rect((104,117,152,157),DARK,EDGE,2)
    p.rect((108,121,148,156),(30,42,44,255),None)
    p.rect((111,124,145,153),STEEL,EDGE,1)
    for xx in [114,121,128,135,142]: p.line([(xx,127),(xx,151)],(90,103,101,255),1)
    p.rect((103,113,153,119),YELLOW,EDGE,1);p.rect((109,115,147,117),YLIGHT,None)
    # Side watch/office windows, rooftop ventilation and unit emblem panel.
    for xx in [72,84,172,184]:
        p.rect((xx-4,130,xx+4,143),WINDOW,EDGE,1);p.line([(xx,131),(xx,141)],GLASS,2)
    for xx in [91,158]: vent(p,xx,101,8)
    p.rect((84,86,112,98),STEEL,EDGE,1);p.rect((88,89,108,94),YELLOW,None)
    p.rect((150,90,174,101),DARK,EDGE,1);p.line([(153,96),(171,96)],YLIGHT,2)
    # Small roof parapet and antenna.
    p.line([(68,105),(127,79),(190,105)],LIGHT,2)
    p.line([(181,91),(181,75)],STEEL,2);p.ellipse((178,71,184,77),YELLOW,EDGE,1)
    return p.finish()

def draw_warfactory():
    p=Painter();cx,y=base(p,'warfactory',176,90)
    b=box_iso(p,cx,158,148,50,0,73,(93,105,106,255),(58,69,72,255),(35,45,49,255))
    # Tall vehicle hangar opening, segmented shutter and amber warning lights.
    p.poly([(85,111),(171,111),(171,158),(85,158)],DARK,EDGE,2)
    p.poly([(91,117),(165,117),(165,157),(91,157)],(26,36,39,255),None)
    p.rect((96,120,160,156),STEEL,EDGE,1)
    for yy in range(124,155,6):
        p.line([(98,yy),(158,yy)],(51,62,65,255),2)
    p.rect((91,113,165,120),YELLOW,EDGE,1)
    p.rect((98,114,158,117),YLIGHT,None)
    # Crane gantry crossing the roof with a hanging hook.
    p.poly([(74,93),(181,93),(195,101),(87,101)],DARK,EDGE,2)
    p.line([(84,96),(183,96)],YLIGHT,3)
    p.line([(178,97),(178,112),(173,117)],LIGHT,2)
    p.ellipse((169,114,177,122),YELLOW,EDGE,1)
    # Side workshops, vents and hazard-striped loading apron.
    for xx in [64,192]:
        p.rect((xx-10,119,xx+10,145),MID,EDGE,2)
        p.rect((xx-7,123,xx+7,138),DARK,None)
        p.line([(xx-6,141),(xx+6,141)],YLIGHT,2)
    p.poly([(80,160),(177,160),(198,174),(101,174)],(76,82,78,255),EDGE,1)
    for k in range(7):
        xx=105+k*12
        p.line([(xx,164),(xx+7,168)],YELLOW,3)
    # Roof machinery: skylights, service ducts, exhaust stacks and gantry legs.
    p.poly([(76,83),(111,70),(126,76),(91,90)],(49,59,61,255),EDGE,1)
    p.poly([(82,82),(110,72),(118,76),(90,86)],GLASS,EDGE,1)
    for xx in [134,148,162]: vent(p,xx,88,5)
    for xx in [72,185]:
        p.rect((xx-3,100,xx+3,113),YELLOW,EDGE,1);p.rect((xx-5,110,xx+5,114),DARK,EDGE,1)
    p.rect((115,103,141,109),DARK,EDGE,1);p.rect((119,105,137,107),YLIGHT,None)
    return p.finish()

def draw_refinery():
    p=Painter();cx,y=base(p,'refinery',174,92)
    b=box_iso(p,cx,159,145,52,0,65,(99,109,105,255),(60,72,72,255),(35,45,47,255))
    # Processing hall and ore intake bay.
    p.rect((91,122,166,157),DARK,EDGE,2)
    p.rect((96,126,160,154),(45,57,57,255),None)
    p.rect((104,134,153,153),WINDOW,EDGE,1)
    p.line([(106,139),(151,139)],YLIGHT,2)
    # Twin cylindrical silos with rounded caps, hoops and access ladders.
    for x,top,bottom,r in [(80,47,130,17),(176,58,131,15)]:
        p.ellipse((x-r,top-7,x+r,top+8),LIGHT,EDGE,2)
        p.rect((x-r,top,x+r,bottom),STEEL,EDGE,2)
        p.poly([(x-r,top+2),(x-4,top+8),(x-4,bottom),(x-r,bottom-7)],(53,64,66,255),EDGE,1)
        p.ellipse((x-r,top-7,x+r,top+7),TOP,EDGE,1)
        p.arc((x-r+3,top-4,x+r-3,top+3),190,345,fill=YLIGHT,width=2*S)
        for yy in [top+17,bottom-12]: p.line([(x-r,yy),(x+r,yy)],YELLOW,3)
        p.line([(x+r-3,top+8),(x+r-3,bottom-2)],LIGHT,2)
        for yy in range(top+13,bottom-3,10): p.line([(x+r-7,yy),(x+r-1,yy)],YLIGHT,2)
    # Ore conveyor with belt rollers and loading hopper.
    p.poly([(91,96),(130,83),(149,91),(108,106)],(35,43,43,255),EDGE,2)
    p.poly([(93,94),(131,81),(148,88),(108,102)],(103,111,104,255),EDGE,1)
    for k in range(5): p.ellipse((102+k*8,91-k*2,107+k*8,96-k*2),DARK,EDGE,1)
    p.poly([(127,79),(148,74),(160,87),(139,94)],YELLOW,EDGE,2)
    # Exhaust vents and hazard-marked piping.
    for x in [120,136]: vent(p,x,113,6)
    pipe(p,[(80,131),(88,139),(100,139)],3)
    # External pump assembly, service catwalks, riveted tank bands and hazard marks.
    p.rect((53,135,75,151),DARK,EDGE,1);p.rect((57,139,71,147),STEEL,EDGE,1)
    for xx in [61,67]: p.line([(xx,140),(xx,146)],YLIGHT,1)
    p.poly([(160,112),(194,103),(204,109),(170,120)],DARK,EDGE,1)
    p.line([(166,113),(193,106)],YLIGHT,2)
    p.rect((183,122,198,145),MID,EDGE,1);p.rect((186,126,195,139),WINDOW,EDGE,1)
    for xx in [102,110,118,126,134,142,150]: p.ellipse((xx,152,xx+2,154),LIGHT,EDGE,1)
    return p.finish()

def draw_radar():
    p=Painter();cx,y=base(p,'radar',142,82)
    b=box_iso(p,cx,159,112,44,0,49,(97,108,106,255),(57,68,70,255),(37,46,49,255))
    # Circular radar dome with panel seams and support ring.
    p.ellipse((86,70,170,141),DARK,EDGE,3)
    p.ellipse((91,66,165,135),(133,143,139,255),EDGE,2)
    p.ellipse((98,70,158,126),(166,171,159,255),STEEL,1)
    p.arc((98,70,158,126),190,350,fill=YLIGHT,width=2*S)
    p.line([(128,69),(128,126)],(93,104,103,255),1)
    p.arc((98,70,158,126),5,175,fill=(82,93,92,255),width=2*S)
    p.ellipse((113,119,143,133),YELLOW,EDGE,2)
    p.ellipse((118,121,138,130),DARK,EDGE,1)
    # Dish struts, antenna mast, coax and a small console wing.
    p.line([(128,128),(128,150)],LIGHT,3)
    p.line([(117,131),(106,149)],STEEL,3);p.line([(139,131),(150,149)],STEEL,3)
    p.rect((72,135,100,151),DARK,EDGE,1);p.rect((76,139,96,146),GLASS,None)
    p.line([(181,112),(181,87)],LIGHT,2);p.line([(175,91),(187,91)],YLIGHT,2)
    p.ellipse((177,82,185,90),YELLOW,EDGE,1)
    # Radar support gantry, concentric reflector panels, equipment lockers.
    for a in range(0,360,30):
        xx=128+math.cos(math.radians(a))*29; yy=99+math.sin(math.radians(a))*24
        p.ellipse((xx-1.6,yy-1.6,xx+1.6,yy+1.6),YLIGHT,EDGE,1)
    p.arc((103,75,153,125),200,340,fill=(222,224,208,220),width=1)
    p.rect((154,137,181,153),DARK,EDGE,1);p.rect((158,141,177,148),GLASS,None)
    p.rect((78,153,91,160),YELLOW,EDGE,1)
    return p.finish()

def draw_turret():
    p=Painter();cx,y=base(p,'turret',116,72)
    # A low-profile reinforced circular gun emplacement. The weapon mount is
    # kept visually separate by leaving a clear pivot point at the centre.
    p.ellipse((72,93,184,165),DARK,EDGE,3)
    p.ellipse((78,88,178,155),STEEL,EDGE,3)
    p.ellipse((88,91,168,148),(83,93,91,255),LIGHT,2)
    p.ellipse((97,96,159,141),(50,59,61,255),EDGE,2)
    # Six radial armour plates and yellow safety tabs.
    for a in range(0,360,60):
        r=36; x=128+math.cos(math.radians(a))*r; yy=120+math.sin(math.radians(a))*r*.55
        p.ellipse((x-5,yy-3,x+5,yy+3),YELLOW,EDGE,1)
    p.ellipse((108,102,148,137),MID,EDGE,2)
    p.ellipse((118,108,138,128),DARK,EDGE,1)
    # Clear top pivot for the independent rotating cannon rendered by the game.
    p.ellipse((111,104,145,139),MID,EDGE,2)
    p.ellipse((117,109,139,132),YELLOW,EDGE,2)
    p.ellipse((121,113,135,128),DARK,EDGE,1)
    p.rect((117,130,139,137),STEEL,EDGE,1)
    # Armour ring bolts, access panels and twin ammunition hatches.
    for a in range(0,360,30):
        xx=128+math.cos(math.radians(a))*44; yy=126+math.sin(math.radians(a))*29
        p.ellipse((xx-1.5,yy-1.5,xx+1.5,yy+1.5),YLIGHT,EDGE,1)
    p.rect((91,146,110,155),DARK,EDGE,1);p.rect((146,146,165,155),DARK,EDGE,1)
    p.rect((95,148,106,151),YELLOW,None);p.rect((150,148,161,151),YELLOW,None)
    return p.finish()

def draw_sam():
    p=Painter();cx,y=base(p,'sam',132,78)
    b=box_iso(p,cx,160,112,44,0,43,(91,104,101,255),(60,70,72,255),(36,46,48,255))
    # Twin angled elevated missile launch rails on a rotating reinforced pedestal.
    p.ellipse((85,111,171,158),DARK,EDGE,3)
    p.ellipse((91,107,165,151),STEEL,EDGE,2)
    p.ellipse((104,111,152,143),(49,59,62,255),EDGE,2)
    p.rect((118,103,138,133),MID,EDGE,2)
    for side in [-1,1]:
        x=128+side*19
        p.poly([(x-8,107),(x+4,101),(x+side*9,38),(x+side*1,34)],(75,86,86,255),EDGE,2)
        p.poly([(x-5,99),(x+2,96),(x+side*5,43),(x-1,40)],(156,161,151,255),EDGE,1)
        p.line([(x-2,91),(x+side*3,50)],YLIGHT,2)
        p.ellipse((x+side*4-5,30,x+side*4+5,42),YELLOW,EDGE,2)
        p.poly([(x+side*4,20),(x+side*9,32),(x+side*4,38),(x-1,32)],(186,190,178,255),EDGE,1)
        p.line([(x+side*4,19),(x+side*4,12)],YLIGHT,2)
    # Radar/targeting box on the deck.
    p.rect((91,131,108,143),DARK,EDGE,1);p.rect((94,134,105,138),GLASS,None)
    # Launch rails carry visible missile bodies, fins, retaining clamps and cables.
    for side in [-1,1]:
        xx=128+side*22
        p.line([(xx,45),(xx+side*5,91)],YLIGHT,2)
        p.rect((xx-3,47,xx+3,87),STEEL,EDGE,1)
        p.poly([(xx-3,48),(xx,38),(xx+3,48)],LIGHT,EDGE,1)
        p.poly([(xx-3,83),(xx-8,91),(xx-2,89)],YELLOW,EDGE,1)
        p.rect((xx-5,65,xx+5,69),DARK,EDGE,1)
    p.rect((108,145,148,153),DARK,EDGE,1);p.line([(113,149),(143,149)],YLIGHT,2)
    return p.finish()

def draw_wall():
    p=Painter();cx,y=base(p,'wall',116,78)
    # Single reinforced concrete segment with chamfered end caps, block joints,
    # top coping and embedded yellow anti-climb warning plates.
    p.poly([(61,111),(161,111),(190,132),(90,132)],(142,148,138,255),EDGE,2)
    p.poly([(90,132),(190,132),(190,159),(90,159)],(83,91,88,255),EDGE,2)
    p.poly([(61,111),(90,132),(90,159),(61,137)],(104,112,105,255),EDGE,2)
    # Individual concrete blocks and visible mortar channels.
    for i in range(4):
        x=91+i*24
        p.poly([(x,135),(x+20,135),(x+20,148),(x,148)],(110,118,109,255),EDGE,1)
        p.line([(x+2,138),(x+18,138)],(160,164,151,255),1)
        p.line([(x+12,139),(x+12,146)],(58,66,64,255),1)
    p.poly([(61,107),(161,107),(190,128),(90,128)],(181,184,170,255),EDGE,2)
    p.line([(67,111),(160,111),(184,126)],YLIGHT,2)
    for x in [78,110,142,174]:
        p.rect((x-4,111+(x-78)*.16,x+4,128+(x-78)*.16),YELLOW,EDGE,1)
    # Reinforcing buttresses, embedded tie plates and chipped concrete texture.
    for x in [68,95,122,149,176]:
        y0=114+(x-68)*.16
        p.line([(x,y0+5),(x,y0+28)],(176,178,166,255),1)
        p.ellipse((x-1.5,y0+9,x+1.5,y0+12),DARK,EDGE,1)
    p.line([(96,153),(184,153)],(159,164,152,255),1)
    return p.finish()

builders=[('power',draw_power),('barracks',draw_barracks),('warfactory',draw_warfactory),('refinery',draw_refinery),('radar',draw_radar),('turret',draw_turret),('sam',draw_sam),('wall',draw_wall)]
for i,(name,fn) in enumerate(builders):
    im=fn()
    row,col=divmod(i,COLS)
    ATLAS.alpha_composite(im,(col*CW,row*CH))
    im.save(OUT/f'building_{name}.png',optimize=True)
ATLAS.save(OUT/'rts_building_sprite_sheet.png',optimize=True)
# Enemy structures reuse the same industrial geometry but swap yellow team
# markings for restrained red/orange so ownership remains obvious in battle.
enemy=ATLAS.copy(); px=enemy.load()
for yy in range(enemy.height):
    for xx in range(enemy.width):
        r,g,b,a=px[xx,yy]
        if a and r>130 and g>90 and b<135 and r>g*1.10:
            if r>205: px[xx,yy]=(224,112,84,a)
            elif r>170: px[xx,yy]=(179,66,54,a)
            else: px[xx,yy]=(117,48,42,a)
enemy.save(OUT/'rts_building_sprite_sheet_enemy.png',optimize=True)
print('saved',ATLAS.size, 'bytes', (OUT/'rts_building_sprite_sheet.png').stat().st_size)
