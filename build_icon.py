"""Create the Windows icon and a preview from vector-like Pillow shapes."""

from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
NAVY = "#0A1C2E"
WHITE = "#FFFFFF"
RED = "#D63023"
SIZE = 1024
SCALE = SIZE / 256


def box(coords):
    return tuple(round(value * SCALE) for value in coords)


def point(coords):
    return tuple((round(x * SCALE), round(y * SCALE)) for x, y in coords)


canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(canvas)

# A light outline keeps the dark tile visible in high-contrast dark themes.
draw.rounded_rectangle(box((6, 6, 250, 250)), radius=round(48 * SCALE), fill=NAVY,
                       outline=WHITE, width=round(9 * SCALE))

# Eighth note.
draw.ellipse(box((43, 154, 113, 209)), fill=WHITE)
draw.rounded_rectangle(box((99, 51, 119, 183)), radius=round(9 * SCALE), fill=WHITE)
draw.polygon(point(((109, 52), (166, 65), (185, 84), (189, 112),
                    (171, 123), (161, 103), (117, 88))), fill=WHITE)

# The X is a shape as well as a color cue, so it remains clear at small sizes.
draw.ellipse(box((123, 121, 245, 243)), fill=WHITE, outline=NAVY,
             width=round(7 * SCALE))
draw.line(point(((153, 151), (215, 213))), fill=RED, width=round(17 * SCALE))
draw.line(point(((215, 151), (153, 213))), fill=RED, width=round(17 * SCALE))
for x, y in ((153, 151), (215, 213), (215, 151), (153, 213)):
    draw.ellipse(box((x - 8.5, y - 8.5, x + 8.5, y + 8.5)), fill=RED)

preview = canvas.resize((256, 256), Image.Resampling.LANCZOS)
preview.save(ROOT / "music_off.png")
preview.save(ROOT / "music_off.ico", format="ICO",
             sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                    (128, 128), (256, 256)])


def luminance(hex_color):
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
              for channel in channels]
    return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))


def contrast(one, two):
    light, dark = sorted((luminance(one), luminance(two)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


assert contrast(NAVY, WHITE) >= 3
assert contrast(RED, WHITE) >= 3
assert contrast(RED, NAVY) >= 3
print(f"navy/white={contrast(NAVY, WHITE):.2f}, red/white={contrast(RED, WHITE):.2f}, red/navy={contrast(RED, NAVY):.2f}")
