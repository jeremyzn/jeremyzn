from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random
from datetime import datetime, timezone

W, H = 846, 292
FRAMES = 64
DURATION = 60
OUT = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)

TECH = [
    ("NEXT.JS", 0.00), ("TYPESCRIPT", 0.12), ("REACT", 0.24), ("NODE", 0.36),
    ("FLUTTER", 0.48), ("AWS", 0.60), ("DOCKER", 0.72), ("K8S", 0.84)
]

def get_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE = get_font(38, True)
F_SUB = get_font(16)
F_META = get_font(10)

def gradient(c1, c2):
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            t = (x / W) * 0.72 + (y / H) * 0.28
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return im.convert("RGBA")

def label(draw, x, y, text, panel, outline, fg, scale):
    f = get_font(max(9, int(10 * scale)), True)
    box = draw.textbbox((0, 0), text, font=f)
    tw, th = box[2]-box[0], box[3]-box[1]
    px, py = int(8*scale), int(5*scale)
    draw.rounded_rectangle(
        (x-tw//2-px, y-th//2-py, x+tw//2+px, y+th//2+py),
        radius=max(6, int(9*scale)), fill=panel, outline=outline, width=1
    )
    draw.text((x-tw//2, y-th//2-1), text, font=f, fill=fg)

def render(name, bg1, bg2, fg, muted, panel, violet, cyan, grid):
    rnd = random.Random(9)
    stars = [(rnd.randint(0, W), rnd.randint(0, H), rnd.choice([1,1,1,2])) for _ in range(48)]
    date = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    frames = []

    for i in range(FRAMES):
        phase = i / FRAMES
        im = gradient(bg1, bg2)

        glow = Image.new("RGBA", (W, H), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((500,-90,930,340), fill=(*violet,55))
        gd.ellipse((430,40,790,360), fill=(*cyan,35))
        glow = glow.filter(ImageFilter.GaussianBlur(70))
        im = Image.alpha_composite(im, glow)
        d = ImageDraw.Draw(im)

        for s, (sx, sy, r) in enumerate(stars):
            drift = (i * (0.18 + (s % 5)*0.04)) % (W+30)
            x = (sx + drift) % (W+30) - 15
            d.ellipse((x-r,sy-r,x+r,sy+r), fill=(*muted,45 + (s%4)*18))

        horizon = 195
        for n in range(-7,8):
            d.line((640,horizon,640+n*78,H+18), fill=grid, width=1)
        for yy in range(horizon,H+17,16):
            d.line((395,yy,W-16,yy), fill=grid, width=1)

        d.rounded_rectangle((42,38,238,64), radius=13, fill=panel, outline=(*violet,100), width=1)
        pulse = 150 + int(80*(0.5 + 0.5*math.sin(phase*math.tau)))
        d.ellipse((55,47,63,55), fill=(*cyan,pulse))
        d.text((72,45), "PROFILE SYSTEM // ONLINE", font=F_META, fill=muted)

        d.text((42,88), "JÉRÉMY", font=F_TITLE, fill=fg)
        d.text((42,131), "ZENOX", font=F_TITLE, fill=(*violet,255))
        d.text((44,181), "FULL-STACK  •  CLOUD / DEVOPS", font=F_SUB, fill=fg)
        d.text((44,207), "MOBILE  •  AI INTEGRATIONS", font=F_SUB, fill=muted)
        d.text((44,251), f"BUILD {date}  //  PARIS", font=F_META, fill=muted)

        cx, cy, rx, ry = 650, 137, 148, 62
        for extra, alpha in [(0,80),(20,44),(-18,36)]:
            d.ellipse((cx-rx-extra,cy-ry-extra*.25,cx+rx+extra,cy+ry+extra*.25),
                      outline=(*violet,alpha),width=1)

        rr = 34 + int(2*math.sin(phase*math.tau))
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr), fill=panel, outline=(*cyan,165), width=2)
        ff = get_font(15, True)
        tb = d.textbbox((0,0),"SHIP",font=ff)
        d.text((cx-(tb[2]-tb[0])/2,cy-(tb[3]-tb[1])/2-1),"SHIP",font=ff,fill=fg)

        nodes = []
        for name_, base in TECH:
            a = (base + phase) * math.tau
            z = (math.sin(a)+1)/2
            x = cx + math.cos(a)*rx
            y = cy + math.sin(a)*ry
            scale = 0.72 + z*0.38
            nodes.append((z,int(x),int(y),name_,scale))

        for z,x,y,name_,scale in sorted(nodes):
            d.line((cx,cy,x,y), fill=(*violet,int(24+z*70)), width=1)
            label(d,x,y,name_,panel,(*cyan,int(70+z*100)),fg,scale)

        frames.append(im.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))

    frames[0].save(
        OUT / f"hero.{name}.gif",
        save_all=True,
        append_images=frames[1:],
        duration=DURATION,
        loop=0,
        optimize=True,
        disposal=2,
    )

render(
    "dark",
    (8,10,18),(15,12,34),
    (245,247,255,255),(168,174,198),(20,22,36,225),
    (124,92,255),(34,211,238),(103,92,180,34)
)

render(
    "light",
    (246,247,252),(231,232,246),
    (24,25,33,255),(83,87,110),(255,255,255,230),
    (91,69,224),(8,145,178),(89,82,145,28)
)
