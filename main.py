#!/usr/bin/env python3
"""Draw the front page of "The World Today" for Wednesday 25 November 2026.

Everything here is drawn by hand with the Python 3 standard library only:
a small 5x7 bitmap face I designed myself, shape-built illustrations, and a
hand-rolled PNG writer (zlib + struct). No network, no external files, no
randomness, so two runs write byte-identical output.

Run it with:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

which writes out/entry.png, a 1024x1024 newspaper front page.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---- palette ---------------------------------------------------------------
PAPER = (246, 238, 220)
INK = (24, 24, 24)
RED = (176, 32, 32)
GREY = (226, 222, 208)
SKY = (186, 214, 234)
NAVY = (28, 40, 66)
MIDBLUE = (52, 110, 180)
GREEN = (46, 130, 70)
GOLD = (214, 164, 32)
WHITE = (250, 250, 248)
STREET = (150, 146, 138)
WINDOW = (200, 220, 235)

# ---- 5x7 bitmap face (my own glyphs; '#' is ink, '.' is clear) ------------
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.#..", "#....", ".###."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

# ---- canvas ----------------------------------------------------------------
buf = bytearray(W * H * 3)
buf[:] = bytes(PAPER) * (W * H)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    r, g, b = c
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for k in range(x1 - x0):
            i = base + k * 3
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b


def hline(x, y, length, c, thick=1):
    for t in range(thick):
        rect(x, y + t, length, 1, c)


def vline(x, y, length, c, thick=1):
    for t in range(thick):
        rect(x + t, y, 1, length, c)


def circle(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def fill_triangle(x0, y0, x1, y1, x2, y2, c):
    pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts

    def at(y, xa, ya, xb, yb):
        if yb == ya:
            return float(xa)
        return xa + (xb - xa) * (y - ya) / (yb - ya)

    for y in range(ay, cy + 1):
        if y < by:
            xa = at(y, ax, ay, bx, by)
            xb = at(y, ax, ay, cx, cy)
        else:
            xa = at(y, bx, by, cx, cy)
            xb = at(y, ax, ay, cx, cy)
        lo, hi = int(min(xa, xb)), int(max(xa, xb))
        rect(lo, y, hi - lo + 1, 1, c)


# ---- text ------------------------------------------------------------------
def draw_char(x, y, ch, scale, c):
    glyph = FONT.get(ch, FONT["?"])
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits[col] == "#":
                rect(x + col * scale, y + row * scale, scale, scale, c)


def text_width(s, scale):
    return len(s) * 6 * scale


def draw_text(x, y, s, scale, c):
    for i, ch in enumerate(s):
        draw_char(x + i * 6 * scale, y, ch, scale, c)


def draw_centered(cx, y, s, scale, c):
    draw_text(cx - text_width(s, scale) // 2, y, s, scale, c)


def wrap(s, width, scale):
    per = max(1, width // (6 * scale))
    lines = []
    cur = ""
    for word in s.split(" "):
        nxt = word if not cur else cur + " " + word
        if len(nxt) <= per:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, width, scale, c, gap=2):
    for line in wrap(s, width, scale):
        draw_text(x, y, line, scale, c)
        y += 7 * scale + gap
    return y


# ---- pictures (all drawn from plain shapes) --------------------------------
def market(x, y, w, h):
    """A supermarket front with a police car and a red stamp."""
    sky_h = h * 2 // 3
    rect(x, y, w, sky_h, SKY)
    rect(x, y + sky_h, w, h - sky_h, STREET)
    # shop block
    bx, bw = x + 14, w - 28
    rect(bx, y + 26, bw, sky_h - 26, (240, 232, 210))
    rect(bx, y + 26, bw, 26, RED)
    draw_centered(x + w // 2, y + 31, "MARKET", 2, WHITE)
    # windows (kept clear of the door in the middle) and door
    for wx in (bx + 12, bx + 66, bx + 230, bx + 284):
        rect(wx, y + 66, 44, 52, WINDOW)
        rect(wx, y + 66, 44, 3, INK)
        rect(wx, y + 115, 44, 3, INK)
    rect(bx + bw // 2 - 14, y + 66, 28, 52, (60, 52, 44))
    # police car
    cy = y + sky_h + 8
    rect(x + 28, cy + 12, 150, 24, (30, 30, 34))
    rect(x + 66, cy, 72, 14, (30, 30, 34))
    rect(x + 92, cy - 6, 20, 6, RED)
    rect(x + 114, cy - 6, 20, 6, MIDBLUE)
    circle(x + 56, cy + 38, 9, INK)
    circle(x + 150, cy + 38, 9, INK)
    # two officers standing in front of the shop, clear of the stamp
    for ox in (x + 226, x + 268):
        circle(ox + 7, y + 124, 6, INK)
        rect(ox, y + 132, 14, 18, NAVY)
    # red stamp
    sx, sy, sw, sh = x + w - 178, y + sky_h + 12, 168, 38
    rect(sx, sy, sw, 3, RED)
    rect(sx, sy + sh - 3, sw, 3, RED)
    rect(sx, sy, 3, sh, RED)
    rect(sx + sw - 3, sy, 3, sh, RED)
    draw_centered(x + w - 94, sy + 12, "25 STILL HELD", 2, RED)


def servers(x, y, w, h):
    """A rack of servers with a yellow warning triangle."""
    rect(x, y, w, h, NAVY)
    for col in range(3):
        for row in range(3):
            ux = x + 10 + col * ((w - 20) // 3)
            uy = y + 8 + row * ((h - 16) // 3)
            uw = (w - 20) // 3 - 6
            uh = (h - 16) // 3 - 6
            rect(ux, uy, uw, uh, (48, 62, 96))
            rect(ux + uw - 12, uy + 4, 4, 4, GREEN)
            rect(ux + uw - 12, uy + uh - 8, 4, 4,
                 RED if (col + row) % 2 else GREEN)
    tx = x + w // 2
    fill_triangle(tx, y + h - 40, tx - 22, y + h - 4, tx + 22, y + h - 4, GOLD)
    draw_text(tx - 3, y + h - 28, "!", 2, INK)


def tower(x, y, w, h):
    """A tower block in a financial district, smoking at the top."""
    rect(x, y, w, h, SKY)
    rect(x + 8, y + h - 48, 46, 48, (210, 214, 220))
    for r in range(4):
        for c in range(3):
            rect(x + 16 + c * 14, y + h - 42 + r * 11, 8, 6, GOLD)
    rect(x + 66, y + 12, 58, h - 12, (36, 36, 40))
    for r in range(6):
        for c in range(4):
            rect(x + 72 + c * 13, y + 20 + r * 12, 8, 6, GOLD)
    fill_triangle(x + 70, y + 12, x + 84, y + 12, x + 77, y + 2, (230, 120, 40))
    circle(x + 100, y + 8, 7, (170, 170, 170))
    circle(x + 112, y + 2, 5, (170, 170, 170))


def plane(x, y, w, h):
    """A jet crossing a blue sky."""
    rect(x, y, w, h, SKY)
    circle(x + 28, y + 18, 10, WHITE)
    circle(x + 42, y + 14, 12, WHITE)
    circle(x + w - 34, y + h - 26, 10, WHITE)
    circle(x + w - 20, y + h - 22, 8, WHITE)
    # fuselage, nose, tail, wing
    rect(x + 34, y + 44, 92, 14, WHITE)
    fill_triangle(x + 126, y + 44, x + 126, y + 58, x + 144, y + 51, WHITE)
    fill_triangle(x + 34, y + 44, x + 48, y + 44, x + 34, y + 26, WHITE)
    fill_triangle(x + 66, y + 58, x + 94, y + 58, x + 74, y + 80, WHITE)
    rect(x + 34, y + 54, 92, 3, RED)
    for i in range(4):
        rect(x + 46 + i * 20, y + 47, 8, 5, MIDBLUE)


def chip(x, y, w, h):
    """A processor with gold pins and an AI core."""
    rect(x, y, w, h, NAVY)
    for i in range(5):
        py = y + 10 + i * 16
        rect(x + 6, py, 10, 4, GOLD)
        rect(x + w - 16, py, 10, 4, GOLD)
    for i in range(5):
        px = x + 22 + i * 18
        rect(px, y + 6, 4, 10, GOLD)
        rect(px, y + h - 16, 4, 10, GOLD)
    rect(x + 48, y + 24, 64, 54, GREEN)
    rect(x + 54, y + 30, 52, 42, (32, 96, 54))
    draw_text(x + 62, y + 42, "AI", 3, WHITE)


def sea(x, y, w, h):
    """Houses on a shore with a rising sea."""
    rect(x, y, w, 56, SKY)
    circle(x + w - 34, y + 22, 12, GOLD)
    # house one
    rect(x + 22, y + 20, 44, 36, WHITE)
    fill_triangle(x + 20, y + 20, x + 68, y + 20, x + 44, y + 2, RED)
    rect(x + 38, y + 38, 12, 18, INK)
    # house two
    rect(x + 84, y + 28, 36, 28, (220, 220, 220))
    fill_triangle(x + 82, y + 28, x + 122, y + 28, x + 102, y + 12, INK)
    # water
    rect(x, y + 56, w, h - 56, MIDBLUE)
    for row in range(4):
        wy = y + 70 + row * 16
        off = 18 if row % 2 else 0
        for k in range(6):
            rect(x + 10 + off + k * 38, wy, 20, 3, WHITE)
    rect(x + w - 36, y + 66, 22, 22, GOLD)
    draw_text(x + w - 31, y + 70, "!", 2, INK)


# ---- page ------------------------------------------------------------------
MX = 36
RIGHT = W - MX


def rule(y, thick=1):
    hline(MX, y, RIGHT - MX, INK, thick)


def two_column(x, y, col_w, kicker, heads, body, picture, pic_w):
    """Kicker + headline across the column, then text left, picture right."""
    draw_text(x, y, kicker, 2, RED)
    hy = y + 20
    for line in heads:
        draw_text(x, hy, line, 3, INK)
        hy += 23
    ty = hy + 4
    draw_para(x, ty, body, col_w - pic_w - 12, 2, INK)
    picture(x + col_w - pic_w, ty, pic_w, 112)
    return ty + 112


def build_page():
    # masthead
    draw_centered(W // 2, 16, "THE WORLD TODAY", 7, INK)
    rule(74, 3)
    rule(80)
    draw_centered(W // 2, 90, "WEDNESDAY, 25 NOVEMBER 2026", 2, INK)
    rule(110)
    # ticker strip with the two briefs
    rect(MX, 116, RIGHT - MX, 42, GREY)
    hline(MX, 116, RIGHT - MX, INK)
    hline(MX, 157, RIGHT - MX, INK)
    draw_centered(W // 2, 122, "KRISTERSSON VOTE SET FOR NOV 30", 2, INK)
    draw_centered(W // 2, 138,
                  "N. KOREA MAY SHUT SWISS OFFICE IN PYONGYANG", 2, INK)
    rule(164)

    # lead story: Cartagena hostage siege
    draw_text(MX, 172, "CRIME - CARTAGENA, COLOMBIA", 2, RED)
    draw_text(MX, 192, "GUNMEN HOLD 25 HOSTAGE", 3, INK)
    draw_text(MX, 215, "IN CARTAGENA MARKET", 3, INK)
    draw_para(MX, 246,
              "GUNMEN SEIZED 30 SHOPPERS IN A CARTAGENA SUPERMARKET AFTER A "
              "BOTCHED ARMOURED-TRUCK RAID, THEN FREED FIVE WOMEN. SNIPERS "
              "RINGED THE STORE AS THE SIEGE STRETCHED INTO WEDNESDAY, WITH "
              "25 STILL HELD INSIDE.",
              560, 2, INK)
    # demands box
    rect(MX, 334, 560, 52, RED)
    rect(MX + 2, 336, 556, 48, PAPER)
    draw_text(MX + 12, 344, "DEMANDS: $2M, TWO ARMOURED CARS,", 2, RED)
    draw_text(MX + 12, 362, "SAFE PASSAGE TO BARRANQUILLA.", 2, RED)
    market(620, 172, 368, 214)
    rule(396)

    # second row: CIA hack | Riyadh tower
    two_column(MX, 404, 464, "CYBER - WASHINGTON",
               ["CIA AND SPY CHIEF'S", "OFFICE HIT BY HACK"],
               "THE CIA AND THE DIRECTOR OF NATIONAL INTELLIGENCE WERE HIT "
               "BY A HACK OF AN UNCLASSIFIED OPEN-SOURCE SYSTEM. NO "
               "CLASSIFIED DATA WAS AFFECTED, OFFICIALS SAID.",
               servers, 162)
    vline(512, 404, 178, INK)
    two_column(524, 404, 464, "MIDDLE EAST - RIYADH",
               ["HOUTHI STRIKE HITS", "RIYADH TOWER, 11 HURT"],
               "A HOUTHI STRIKE HIT A TOWER IN RIYADH'S FINANCIAL DISTRICT, "
               "INJURING 11 PEOPLE. IT WAS THE SECOND ATTACK ON THE TOWER "
               "IN A WEEK.",
               tower, 162)
    rule(594)

    # third row: Boeing order | Nvidia
    two_column(MX, 602, 464, "BUSINESS - AVIATION",
               ["BOEING WINS $7.4BN", "CHINA JET ORDER"],
               "XIAMEN AIRLINES ORDERED 50 BOEING 737-8 JETS AT A LIST PRICE "
               "OF ABOUT $7.4 BILLION, THE BIGGEST CHINESE ORDER FOR BOEING "
               "SINCE 2017.",
               plane, 162)
    vline(512, 602, 178, INK)
    two_column(524, 602, 464, "TECH - NVIDIA",
               ["HUANG SAYS SORRY,", "HE IS IN THERAPY"],
               "A DAY AFTER HIS RETURN AS CEO, JENSEN HUANG TOLD STAFF HE "
               "MADE TERRIBLE MISTAKES AND IS IN THERAPY. NVIDIA SHARES "
               "FELL 5.9% AFTER MONDAY'S 31.5% SURGE.",
               chip, 162)
    rule(792)

    # bottom story: California king tides
    sea(MX, 800, 244, 140)
    draw_text(300, 800, "WEATHER - CALIFORNIA", 2, RED)
    draw_text(300, 820, "CALIFORNIA BRACES FOR", 3, INK)
    draw_text(300, 843, "NEAR-RECORD TIDES", 3, INK)
    draw_para(300, 866,
              "AN ATMOSPHERIC RIVER STORM IS HITTING CALIFORNIA JUST AS KING "
              "TIDES, THE YEAR'S HIGHEST, PEAK ON WEDNESDAY. BAY WATER MAY "
              "COME CLOSE TO THE 1983 RECORD, WITH FLOODING ALREADY REPORTED "
              "AND THANKSGIVING TRAVEL DISRUPTED.",
              688, 2, INK)
    rule(950)
    draw_centered(W // 2, 958,
                  "SOURCES: REUTERS, AP, AFP, CNN, SCMP - 25 NOVEMBER 2026",
                  2, INK)


# ---- PNG writer ------------------------------------------------------------
def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", ihdr)
            + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + png_chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


def main():
    build_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    save_png(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
