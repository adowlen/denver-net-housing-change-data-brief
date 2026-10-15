from PIL import Image, ImageDraw, ImageFont

SRC = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/permits-demolitions-brief-2026-10-15/hero_source/media-generation-hero-base-net-housing-0-daba1938-6cc3-488a-acb3-81622411cb4b.webp"
OUT = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/permits-demolitions-brief-2026-10-15/charts/hero.png"

img = Image.open(SRC).convert("RGB")
W, H = img.size
print("base size:", W, H)

# gradient scrim across the top sky band for text legibility
scrim = Image.new("L", (1, H))
for y in range(H):
    t = y / (H * 0.42)
    a = max(0, int(150 * (1 - t))) if t < 1 else 0
    scrim.putpixel((0, y), a)
scrim = scrim.resize((W, H))
dark = Image.new("RGB", (W, H), (10, 13, 16))
img = Image.composite(dark, img, scrim.point(lambda v: v))

d = ImageDraw.Draw(img)
AMBER = (245, 168, 0)
PAPER = (242, 239, 233)
DIM = (178, 188, 194)
x = int(W * 0.045)
y = int(H * 0.05)

f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(H * 0.115))
f_cap = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(H * 0.036))
f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(H * 0.0255))

d.text((x, y), "+7,748", font=f_big, fill=AMBER)
y += int(H * 0.135)
d.text((x, y), "net new structures permitted in Denver since 2020", font=f_cap, fill=PAPER)
y += int(H * 0.052)
d.text((x, y), "11,585 new buildings permitted, 3,837 demolished - Denver permit data, Jan 2020 - Oct 2026", font=f_sub, fill=DIM)

img.save(OUT)
print("saved", OUT)
