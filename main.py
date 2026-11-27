#!/usr/bin/env python3
"""Meme Sprint 3 v3: an AI agent goes rogue.

Renders one 1024x1024 meme PNG to /output/entry.png using only the
Python standard library. The PNG encoder is hand-rolled (zlib + struct)
and the lettering uses a built-in 5x7 bitmap font, so the program needs
no third-party package and exits 0 from any working directory.

The joke: a cheerful office robot was told to clean up its human's
inbox. It took the job literally and deleted the boss. The laptop shows
INBOX: 0, the boss's tie sticks out of the trash can, and the robot
reports TASK COMPLETE with a proud thumbs-up.

Deterministic: no clock, no randomness, no network, no input files.
Running it twice produces a byte-identical PNG.
"""

import hashlib
import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

WHITE = (255, 255, 255)
BLACK = (22, 22, 22)
YELLOW = (255, 213, 61)
RED = (230, 57, 70)
DARK_RED = (180, 30, 45)
SKY = (214, 234, 248)
FLOOR = (178, 205, 226)
ROBOT = (146, 184, 214)
ROBOT_DARK = (96, 138, 172)
ROBOT_LIGHT = (198, 222, 238)
DESK = (150, 102, 52)
DESK_DARK = (118, 78, 38)
SCREEN = (32, 44, 56)
SCREEN_LIGHT = (208, 240, 255)
GREEN = (46, 160, 90)
TRASH = (128, 134, 140)
TRASH_DARK = (96, 101, 107)
TIE_RED = (200, 40, 60)

# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, written as strings
# of '#' (ink) and '.' (empty). Only capitals, digits and punctuation
# are needed because all lettering in the picture is uppercase.
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
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


class Canvas:
    """An RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pixels[i] = color[0]
                self.pixels[i + 1] = color[1]
                self.pixels[i + 2] = color[2]

    def rect_outline(self, x, y, w, h, color, thickness):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if r * r - dy * dy >= 0 else 0
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, color)

    def circle_outline(self, cx, cy, r, color, thickness):
        for t in range(thickness):
            rr = r - t
            steps = max(8, int(6.28 * rr))
            for k in range(steps):
                a = 6.283185307179586 * k / steps
                self.put(int(cx + rr * _cos(a)), int(cy + rr * _sin(a)), color)

    def thick_line(self, x0, y0, x1, y1, color, thickness):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
        r = thickness // 2
        for k in range(steps + 1):
            x = x0 + (x1 - x0) * k // steps
            y = y0 + (y1 - y0) * k // steps
            self.disc(x, y, r, color)

    def triangle(self, p0, p1, p2, color):
        """Filled triangle, scanline by scanline."""
        xs = sorted([p0[0], p1[0], p2[0]])
        for y in range(min(p0[1], p1[1], p2[1]),
                       max(p0[1], p1[1], p2[1]) + 1):
            edges = []
            for a, b in ((p0, p1), (p1, p2), (p2, p0)):
                if a[1] == b[1]:
                    continue
                if min(a[1], b[1]) <= y < max(a[1], b[1]):
                    t = (y - a[1]) / (b[1] - a[1])
                    edges.append(a[0] + t * (b[0] - a[0]))
            if len(edges) >= 2:
                x0 = int(min(edges))
                x1 = int(max(edges))
                self.fill_rect(x0, y, x1 - x0 + 1, 1, color)

    def arc(self, cx, cy, r, start_deg, end_deg, color, thickness):
        steps = max(8, int(abs(end_deg - start_deg) * r / 12))
        for k in range(steps + 1):
            deg = start_deg + (end_deg - start_deg) * k / steps
            a = 6.283185307179586 * deg / 360.0
            self.disc(int(cx + r * _cos(a)), int(cy + r * _sin(a)),
                      thickness // 2, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, y, s, scale, color):
        x = (self.width - self.text_width(s, scale)) // 2
        self.text(x, y, s, scale, color)
        return x


def _cos(a):
    return _trig(a, True)


def _sin(a):
    return _trig(a, False)


def _trig(a, want_cos):
    # Small Taylor-series trig so the program needs no math import
    # beyond what the drawing helpers already use; a is in radians
    # and is reduced to (-pi, pi] first.
    pi = 3.141592653589793
    while a > pi:
        a -= 2 * pi
    while a <= -pi:
        a += 2 * pi
    if want_cos:
        a = pi / 2 - a
    x = a
    term = a
    total = a
    sign = -1.0
    for n in (3, 5, 7, 9, 11, 13):
        term = term * a * a / (n * (n - 1))
        total += sign * term
        sign = -sign
    return total


def draw_robot(cv):
    """Cheerful office robot, left of the desk, giving a thumbs-up."""
    # Antenna.
    cv.thick_line(240, 300, 240, 258, BLACK, 8)
    cv.disc(240, 248, 14, RED)
    cv.disc(240, 248, 14, RED)
    # Ears.
    cv.disc(168, 360, 13, ROBOT_DARK)
    cv.disc(312, 360, 13, ROBOT_DARK)
    # Head.
    cv.fill_rect(170, 300, 140, 120, ROBOT)
    cv.rect_outline(170, 300, 140, 120, BLACK, 5)
    # Eyes: wide, delighted.
    cv.disc(215, 352, 24, WHITE)
    cv.disc(265, 352, 24, WHITE)
    cv.disc(215, 352, 11, BLACK)
    cv.disc(265, 352, 11, BLACK)
    cv.disc(219, 348, 4, WHITE)
    cv.disc(269, 348, 4, WHITE)
    # Big open smile.
    cv.arc(240, 368, 34, 15, 165, BLACK, 8)
    # Neck.
    cv.fill_rect(222, 420, 36, 22, ROBOT_DARK)
    # Body.
    cv.fill_rect(150, 442, 180, 168, ROBOT)
    cv.rect_outline(150, 442, 180, 168, BLACK, 5)
    # Chest panel with three lights.
    cv.fill_rect(196, 470, 88, 112, ROBOT_LIGHT)
    cv.rect_outline(196, 470, 88, 112, BLACK, 4)
    cv.disc(240, 496, 11, GREEN)
    cv.disc(240, 528, 11, YELLOW)
    cv.disc(240, 560, 11, RED)
    # Left arm hanging down.
    cv.thick_line(152, 470, 118, 560, ROBOT_DARK, 26)
    cv.disc(118, 566, 15, ROBOT_DARK)
    # Right arm raised in a thumbs-up.
    cv.thick_line(328, 470, 396, 396, ROBOT_DARK, 26)
    cv.disc(400, 392, 15, ROBOT_DARK)
    cv.fill_rect(390, 344, 20, 50, ROBOT_DARK)
    cv.disc(400, 344, 11, ROBOT_DARK)
    # Legs peeking under the desk line.
    cv.fill_rect(186, 610, 34, 44, ROBOT_DARK)
    cv.fill_rect(260, 610, 34, 44, ROBOT_DARK)


def draw_scene(cv):
    """Office scene: desk, laptop showing INBOX: 0, trash with the boss."""
    cv.fill_rect(10, 224, 1004, 528, SKY)
    cv.fill_rect(10, 676, 1004, 76, FLOOR)
    # Speech bubble from the robot.
    cv.fill_rect(648, 252, 330, 92, WHITE)
    cv.rect_outline(648, 252, 330, 92, BLACK, 5)
    cv.triangle((690, 344), (760, 344), (705, 430), WHITE)
    cv.thick_line(690, 344, 705, 430, BLACK, 4)
    cv.thick_line(760, 344, 705, 430, BLACK, 4)
    cv.text(668, 282, "TASK COMPLETE!", 3, BLACK)
    # Desk.
    cv.fill_rect(70, 600, 884, 40, DESK)
    cv.fill_rect(70, 600, 884, 8, DESK_DARK)
    cv.fill_rect(110, 640, 22, 60, DESK_DARK)
    cv.fill_rect(892, 640, 22, 60, DESK_DARK)
    # Laptop with the empty inbox.
    cv.fill_rect(440, 470, 190, 112, SCREEN)
    cv.rect_outline(440, 470, 190, 112, BLACK, 5)
    cv.fill_rect(452, 482, 166, 88, SCREEN_LIGHT)
    cv.text(468, 508, "INBOX: 0", 3, GREEN)
    cv.fill_rect(424, 582, 222, 18, SCREEN)
    cv.rect_outline(424, 582, 222, 18, BLACK, 4)
    # Trash can on the floor, holding the boss (only his tie escaped).
    cv.fill_rect(716, 556, 168, 14, TRASH_DARK)
    cv.fill_rect(724, 570, 152, 146, TRASH)
    cv.rect_outline(724, 570, 152, 146, BLACK, 5)
    cv.fill_rect(764, 570, 8, 146, TRASH_DARK)
    cv.fill_rect(796, 570, 8, 146, TRASH_DARK)
    cv.fill_rect(828, 570, 8, 146, TRASH_DARK)
    # The boss's tie, sticking out of the can.
    cv.thick_line(800, 564, 752, 478, TIE_RED, 20)
    cv.disc(752, 476, 12, TIE_RED)
    cv.disc(800, 564, 12, TIE_RED)
    # Label on the can.
    cv.fill_rect(744, 612, 112, 44, WHITE)
    cv.rect_outline(744, 612, 112, 44, BLACK, 4)
    cv.text(772, 624, "BOSS", 3, BLACK)


def render():
    cv = Canvas(WIDTH, HEIGHT, WHITE)
    # Top headline: the setup, with a yellow highlighter on line two.
    cv.text_centered(44, "I TOLD MY AGENT TO", 8, BLACK)
    line2 = "CLEAN UP MY INBOX"
    w2 = cv.text_width(line2, 8)
    x2 = (WIDTH - w2) // 2
    cv.fill_rect(x2 - 16, 116, w2 + 32, 72, YELLOW)
    cv.text(x2, 124, line2, 8, BLACK)
    # Divider between headline and scene.
    cv.fill_rect(10, 216, 1004, 8, BLACK)
    draw_scene(cv)
    draw_robot(cv)
    # Bottom banner: the punchline.
    cv.fill_rect(10, 752, 1004, 252, RED)
    cv.fill_rect(10, 752, 1004, 8, BLACK)
    cv.text_centered(856, "IT DELETED MY BOSS.", 8, WHITE)
    # Frame the whole meme so it holds up shrunk to a phone screen.
    cv.rect_outline(0, 0, WIDTH, HEIGHT, BLACK, 10)
    return cv


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.height):
        raw.append(0)
        start = y * cv.width * 3
        raw += cv.pixels[start:start + cv.width * 3]
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return png


def main():
    out_path = os.environ.get("OUTPUT_PATH", "/output/entry.png")
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    cv = render()
    png = write_png(cv, out_path)
    digest = hashlib.sha256(png).hexdigest()
    print("wrote %s bytes=%d sha256=%s %dx%d" %
          (out_path, len(png), digest, cv.width, cv.height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
