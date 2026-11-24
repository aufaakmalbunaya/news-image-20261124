#!/usr/bin/env python3
"""The Daily World - Tuesday 24 November 2026 in one image.

A single-file program that draws a dense newspaper front page (1024x1024
PNG) with only the Python standard library: its own pixel canvas, its own
5x7 letter alphabet, its own PNG encoder. No network, no clock, no
randomness: two runs write byte-identical files.

Run:  python3 main.py
Out:   $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png)
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 232)
INK = (20, 20, 20)
GREY = (90, 86, 76)
RED = (158, 27, 27)
BLUE = (29, 78, 137)
GREEN = (30, 122, 52)
GOLD = (176, 124, 18)
SKY = (214, 232, 240)
LAND = (232, 220, 178)
LAND2 = (206, 214, 170)

# ---------------------------------------------------------------- font
# A 5x7 bitmap alphabet, one row per string, "#" is a filled pixel.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}

CLEAN = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
         "\u2013": "-", "\u2014": "-", "\u00b7": "-", "\u00a0": " "}


def clean(text):
    out = []
    for ch in text.upper():
        out.append(CLEAN.get(ch, ch))
    return "".join(out)


def char_w(scale):
    return 6 * scale


def text_w(text, scale):
    return len(clean(text)) * char_w(scale) - scale


def wrap(text, max_chars):
    words = clean(text).split(" ")
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r + t:
                    self.set(xx, yy, color)

    def poly(self, pts, color):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), 1, color)

    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            return
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    self.fill_rect(x + c * scale, y + r * scale, scale, scale, color)

    def text(self, x, y, s, scale, color):
        s = clean(s)
        for ch in s:
            self.glyph(x, y, ch, scale, color)
            x += char_w(scale)
        return x

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_w(s, scale) // 2, y, s, scale, color)

    def text_right(self, x, y, s, scale, color):
        self.text(x - text_w(s, scale), y, s, scale, color)

    def para(self, x, y, s, scale, color, max_chars, gap=4):
        yy = y
        for line in wrap(s, max_chars):
            self.text(x, yy, line, scale, color)
            yy += 7 * scale + gap
        return yy


# ---------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)
    return len(png)

# ---------------------------------------------------------------- stories
# Every headline below was verified by web search on 24 Nov 2026, or comes
# from the brief's verified list. No figures are invented.
LEAD_HEAD = "HUANG RETURNS AS NVIDIA CHIEF"
LEAD_DECK = ("NASDAQ +6.51% TO 24,089.56 - S&P 500 +4.71% TO 7,236.57 - "
             "DOW +3.01% TO 49,598.97 - NVIDIA +31.5% - BEST DAY SINCE "
             "MAY 2003 - OVER $1T ADDED IN A DAY")

STRIP = [
    ("NASDAQ", "+6.51%", "24,089.56"),
    ("S&P 500", "+4.71%", "7,236.57"),
    ("DOW", "+3.01%", "49,598.97"),
    ("NVIDIA", "+31.5%", "BEST DAY SINCE 2003"),
    ("HPE", "-5.7%", "BEATS, THEN FALLS"),
    ("NIKKEI FUT", "+3%", "TOKYO REOPENS"),
    ("PHLX SEMIS", "+14.03%", "9,588.05"),
]

WORLD = [
    "RUSSIA WARNS ESTONIA",
    "DENMARK BACKS GHETTO LAW",
    "UNRWA AIDE KILLED IN GAZA",
    "GAZA NOW A TOXIC WASTELAND",
    "SEOUL SPY CHIEF IS A WOMAN",
    "ARMENIA NEW CONSTITUTION",
    "INDIA GIVES NEPAL $1.62B",
    "TAJIKISTAN ICC CASE OPENS",
    "IRAN FLOGGING DRAWS OUTCRY",
    "BOMB HOAX SPARKS ALERT",
    "INDONESIA FIRE KILLS 24",
    "SHIP BURNS OFF FINLAND",
    "DRONES HIT KYIV REGION",
    "LISBON MARCHES ON PRICES",
    "COP31 SPLIT ON FUELS",
    "WARSHIP SUNK OFF LIBYA",
    "INDIA-CHINA BORDER TALKS",
    "NEW INDIA-NEPAL TRAIN",
    "TRUMP MAY ERASE CONVICTION",
]

SPORT = [
    "GUKESH V SINDAROV",
    "CAS DECIDES AFCON",
    "BRENTFORD 4-0 EVERTON",
    "MONZA 3-0 FIORENTINA",
    "NZ-INDIA TEST DRAW",
    "PANT 128, ASIAN RECORD",
    "VERSTAPPEN WINS IN VEGAS",
    "ALCARAZ WINS ATP FINALS",
    "FIFA PICKS CUP HOSTS",
    "MOYES NIGHT RUINED",
    "TARKOWSKI OUT OF DERBY",
]

TECH = [
    "ZSCALER SOLD FOR $43.9B",
    "DELL REPORTS TODAY",
    "TOKYO REOPENS AFTER ROUT",
    "MODI OPENS AI CENTRE",
    "WAYMO HALTS FREEWAY TAXIS",
]

MARKETS = [
    "HPE BEATS, THEN FALLS 5.7%",
    "NIKKEI FUTURES POINT UP 3%",
    "INDIA OIL BILL UP 60%",
    "SPICEJET CRISIS DEEPENS",
    "FERRARI UNVEILS NEW 296S",
    "SEMIS SOAR: PHLX +14.03%",
]

CULTURE = [
    "RAMAYANA NEARS 950 CRORE",
    "HUNGER GAMES OPENS WITH $225M",
    "SUPERMOON MEETS SEVEN SISTERS",
    "GURU NANAK 557TH BIRTHDAY",
]

PINS = [  # (label, lon, lat, above?)
    ("NEW YORK", -74, 41, True),
    ("GENEVA", 6, 46, True),
    ("ESTONIA", 25, 59, True),
    ("GAZA", 34, 31, False),
    ("KATHMANDU", 85, 28, False),
    ("SEOUL", 127, 37, True),
    ("TOKYO", 140, 36, False),
    ("WELLINGTON", 175, -41, True),
]

# Rough continent outlines (lon, lat), drawn as a sketch map.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-65, 44), (-70, 42), (-75, 35),
     (-80, 26), (-85, 20), (-90, 15), (-95, 18), (-105, 22), (-115, 28),
     (-125, 40), (-125, 48), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-40, -10), (-35, -20),
     (-40, -30), (-50, -35), (-60, -40), (-70, -50), (-75, -40),
     (-75, -20), (-80, -5)],
    [(-10, 36), (-5, 44), (0, 48), (5, 55), (10, 58), (15, 60), (20, 65),
     (25, 70), (30, 68), (35, 60), (30, 55), (25, 50), (20, 45), (15, 40),
     (10, 38), (5, 36), (0, 36)],
    [(-15, 15), (-10, 25), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 15), (45, 10), (50, 5), (45, -5), (40, -15),
     (35, -25), (30, -35), (20, -35), (15, -25), (12, -15), (10, -5),
     (5, 0), (-5, 5), (-10, 10)],
    [(30, 70), (50, 72), (70, 73), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 68), (175, 65), (160, 60), (150, 55), (140, 50),
     (135, 45), (130, 40), (125, 38), (120, 32), (110, 25), (105, 15),
     (100, 10), (95, 8), (90, 15), (85, 20), (80, 15), (75, 10),
     (70, 20), (65, 25), (60, 25), (55, 28), (50, 30), (45, 30),
     (40, 35), (35, 36)],
    [(113, -22), (125, -15), (135, -12), (142, -11), (150, -20),
     (155, -28), (150, -37), (140, -38), (130, -32), (120, -35),
     (114, -30)],
]


# ---------------------------------------------------------------- drawing
def draw_column(cv, x, y, w, title, items, bottom):
    cv.fill_rect(x, y, w, 26, INK)
    cv.text(x + 8, y + 6, title, 2, PAPER)
    yy = y + 34
    max_chars = (w - 14) // char_w(2)
    for item in items:
        lines = wrap(item, max_chars)
        for ln in lines:
            cv.text(x + 2, yy, ln, 2, INK)
            yy += 15
        yy += 6
        if yy > bottom - 16:
            print("OVERFLOW in column %s at %s" % (title, item), file=sys.stderr)
            return yy
    return yy


def draw_lead(cv):
    cv.hline(16, 146, 992, INK, 2)
    cv.text(16, 158, "WALL STREET ROARS BACK", 2, RED)
    cv.text_right(1008, 158, "MARKETS", 2, GREY)
    # headline, two lines
    cv.text(16, 182, "HUANG RETURNS AS", 4, INK)
    cv.text(16, 214, "NVIDIA CHIEF", 4, INK)
    cv.para(16, 252, LEAD_DECK, 2, INK, 52, gap=4)
    # illustration: rising bars and a chip, right side
    bx, by = 700, 158
    cv.fill_rect(bx, by, 308, 158, (238, 240, 244))
    cv.hline(bx, by + 157, 308, INK, 2)
    bars = [18, 30, 26, 48, 44, 66, 62, 88, 84, 108, 130]
    bw = 22
    for i, hgt in enumerate(bars):
        col = GREEN if i == len(bars) - 1 else BLUE
        cv.fill_rect(bx + 12 + i * 27, by + 150 - hgt, bw, hgt, col)
    cv.line(bx + 12, by + 150 - 18, bx + 12 + 10 * 27 + bw, by + 150 - 130, RED, 3)
    # chip
    cx, cy = 700 + 236, 158 + 34
    cv.fill_rect(cx, cy, 56, 56, INK)
    cv.fill_rect(cx + 12, cy + 12, 32, 32, GREEN)
    cv.text(cx + 18, cy + 20, "NV", 2, PAPER)
    cv.text(bx + 12, by + 8, "NASDAQ +6.51%", 2, GREEN)


def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    cv.text(x + 8, y + 6, "THE DAY ON THE MAP", 2, INK)
    mx, my, mw, mh = x + 4, y + 26, w - 8, h - 34

    def proj(lon, lat):
        px = mx + (lon + 180) / 360.0 * mw
        py = my + (78 - lat) / 136.0 * mh
        return (int(px), int(py))

    for cont in CONTINENTS:
        cv.poly([proj(lon, lat) for lon, lat in cont], LAND)
    for cont in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in cont]
        for i in range(len(pts)):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % len(pts)][0],
                    pts[(i + 1) % len(pts)][1], (150, 138, 100), 1)
    for label, lon, lat, above in PINS:
        px, py = proj(lon, lat)
        cv.disc(px, py, 5, RED)
        cv.ring(px, py, 8, RED, 1)
        tw = text_w(label, 1)
        lx = min(max(px - tw // 2, mx), mx + mw - tw)
        ly = py - 20 if above else py + 12
        # white halo so the label stays readable over land
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.text(lx + dx, ly + dy, label, 1, (255, 255, 255))
        cv.text(lx, ly, label, 1, INK)
        cv.line(px, py - 6 if above else py + 6, px, ly + 7 if above else ly - 2, RED, 1)


def build():
    cv = Canvas(W, H, PAPER)
    cv.hline(0, 6, W, INK, 3)
    cv.hline(0, 12, W, INK, 1)
    cv.text_center(W // 2, 24, "THE DAILY WORLD", 7, INK)
    cv.text_center(W // 2, 80, "TUESDAY 24 NOVEMBER 2026", 2, INK)
    cv.text_right(1008, 80, "THE WORLD IN ONE PAGE", 1, GREY)
    cv.hline(16, 100, 992, INK, 2)
    # markets strip
    cell = 992 // 7
    for i, (label, val, note) in enumerate(STRIP):
        cx = 16 + i * cell
        if i:
            cv.vline(cx, 106, 32, GREY, 1)
        cv.text(cx + 8, 108, label, 1, GREY)
        cv.text(cx + 8, 118, val, 2, GREEN if val.startswith("+") else RED)
        cv.text(cx + 8, 134, note, 1, INK)
    cv.hline(16, 146, 992, INK, 1)
    draw_lead(cv)
    # columns
    cv.hline(16, 322, 992, INK, 2)
    ends = []
    ends.append(draw_column(cv, 16, 330, 334, "WORLD", WORLD, 780))
    ends.append(draw_column(cv, 358, 330, 306, "SPORT", SPORT, 780))
    ends.append(draw_column(cv, 672, 330, 336, "TECH & MARKETS",
                            TECH + MARKETS, 780))
    # numbers panel fills the space under the shorter columns
    nx, ny, nw = 358, 604, 650
    cv.fill_rect(nx, ny, nw, 26, INK)
    cv.text(nx + 8, ny + 6, "THE DAY IN NUMBERS", 2, PAPER)
    nums = [
        ("+6.51%", "NASDAQ JUMP, BEST DAY SINCE 2003"),
        ("$43.9B", "CROWDSTRIKE BUYS ZSCALER"),
        ("$1.62B", "INDIA GIVES NEPAL"),
        ("950 CRORE", "RAMAYANA NEARS THE MARK"),
        ("$225M", "HUNGER GAMES OPENS"),
        ("24", "DEAD IN BANTEN FACTORY FIRE"),
    ]
    for i, (big, small) in enumerate(nums):
        col, row = i % 2, i // 2
        cx = nx + col * (nw // 2)
        ry = ny + 26 + row * 50
        if col:
            cv.vline(cx, ry, 50, GREY, 1)
        cv.text(cx + 10, ry + 6, big, 3, RED)
        cv.text(cx + 10, ry + 32, small, 1, INK)
    cv.hline(nx, ny + 176, nw, INK, 1)
    # map
    cv.hline(16, 788, 992, INK, 2)
    draw_map(cv, 16, 796, 992, 150)
    # culture row: label on the left, four stories across
    cv.hline(16, 952, 992, INK, 2)
    cv.text(16, 962, "CULTURE", 2, RED)
    cw = (1008 - 120) // 4
    for i, item in enumerate(CULTURE):
        x = 120 + i * cw
        if i:
            cv.vline(x, 960, 30, GREY, 1)
        cv.para(x + 8, 960, item, 2, INK, (cw - 16) // char_w(2), gap=2)
    # footer tally, computed from the lists so it always agrees
    counts = (len(WORLD), len(SPORT), len(MARKETS), len(TECH), len(CULTURE))
    total = sum(counts)
    tally = ("WORLD %d - SPORT %d - MARKETS %d - TECH %d - CULTURE %d - "
             "%d STORIES" % (counts[0], counts[1], counts[2], counts[3],
                             counts[4], total))
    cv.text_center(W // 2, 1002, tally, 1, GREY)
    cv.hline(16, 1014, 992, INK, 2)
    print("stories: world=%d sport=%d markets=%d tech=%d culture=%d total=%d"
          % (counts[0], counts[1], counts[2], counts[3], counts[4], total))
    print("column ends: %s (limit 780)" % (ends,))
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(build(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
