import os, os.path, math
import StringIO
import Image


# Colors that were set in the original Scribus-generated file
original_colors = dict(
    ocean="0.901961 0.643137 0.184314 0.407843", # ocean
    main1="0.576471 0.0784314 0.545098 0.0627451", # country (Russia)
    main2="0.0980392 0.827451 0.513725 0.0901961", # country (Canada)
    main3="0.552941 0.215686 0.341176 0.203922", # country (Brasil)
    main4="0.0823529 0.470588 0.509804 0.0509804", # country (USA)
    main5="0.282353 0.152941 0.631373 0.0823529", # country (Mexico)
    ice2="0.0431373 0.180392 0.0823529 0.00392157", # ice (Ross dependency)
    ice5="0.105882 0.0705882 0.141176 0.0117647", # ice (British antarctic)
    ice1="0.160784 0.0431373 0.137255 0.00784314", # ice (Terre Adelie)
    ice3="0.160784 0.0509804 0.0941176 0.00784314", # ice (Australian antarctic)
    iceneutral="0 0 0 0.0588235") # ice (Mary Byrd land)


def ps_setcolor(name):
    return "setcolor" + name


def ps_colordef(name, color_str):
    return "/" + ps_setcolor(name) + " {" + color_str + " cmyk} def"


def prepare_eps(infile):
    name, ext = os.path.splitext(infile)

    with open(infile) as f:
        eps = f.read()

    cmykdef = "/cmyk {setcmykcolor} def"
    pos = eps.find(cmykdef)
    before = eps[:pos + len(cmykdef)]
    after = eps[pos + len(cmykdef):]

    # replace boundingbox sizes by placeholders
    before = before.replace("1729.13", "BBOX_HEIGHT_PRECISE")
    before = before.replace("1729", "BBOX_HEIGHT_INTEGER")

    # replace colors by macro calls
    for name, color in original_colors.items():
        after = after.replace(color + " cmyk", ps_setcolor(name))

    # replace clipping box and ocean box sizes by macros
    # also translating coordinate system to half the increase of height
    original_boxes = """0 0 tr
0 0 m
3370.39 0 li
3370.39 1729.13 li
0 1729.13 li cl clip newpath
gs
1 sw
0 setlinecap
0 setlinejoin
[] 0 setdash
0 1729.13 tr
0 0 m
3370.39 0 li
3370.39 -1729.13 li
0 -1729.13 li
0 0 li
cl
setcolorocean eofill
gr"""

    replacement_boxes = """0 0 tr
0 0 m
3370.39 0 li
3370.39 posterheight li
0 posterheight li cl clip newpath
gs
1 sw
0 setlinecap
0 setlinejoin
[] 0 setdash
0 posterheight tr
0 0 m
3370.39 0 li
3370.39 0 posterheight sub li
0 0 posterheight sub li
0 0 li
cl
setcolorocean eofill
gr
0 posterheight 1729.13 sub 2 div tr"""

    after = after.replace(original_boxes, replacement_boxes)

    return before, after


def pick_colors():
    # Since eps is in CMYK, and PIL converts .eps to .png using some weird CMYK->RGB algorithm,
    # we are using a hacky approach with creating a simple .eps with the same colors
    # (in alphabetical order).

    color_picker = Image.open(os.path.join(os.path.split(__file__)[0], 'map_original.eps'))
    color_picker = color_picker.resize((110, 10))

    colors = {}
    for i, name in enumerate(sorted(original_colors)):
        colors[name] = color_picker.getpixel((5 + i * 10, 5))
    return colors


# Pre-load data
map_original = os.path.join(os.path.split(__file__)[0], 'map_original.eps')
orig_height = 1729.13
orig_width = 3370.39

# preapre eps template
before, after = prepare_eps(map_original)

# prepare map image
map_image = Image.open(map_original)

# Prepare RGB colors
rgb_colors = pick_colors()


def get_eps(colors, aspect):
    colordefs = []
    for name, color in newcolors.items():
        colordefs.append(ps_colordef(name, " ".join([str(x) for x in color])))

    if aspect == 'original':
        new_height = orig_height
    elif aspect == 'A':
        new_height = orig_width / math.sqrt(2.0)
    elif aspect == 'golden':
        new_height = orig_width / (math.sqrt(5.0) - 1) * 2

    before = before.replace("BBOX_HEIGHT_PRECISE", str(new_height))
    before = before.replace("BBOX_HEIGHT_INTEGER", str(int(new_height)))
    eps = before + "\n" + "\n".join(colordefs) + \
        "\n/posterheight {" + str(new_height) + "} def" + after

    eps_io = StringIO.StringIO()
    eps_io.write(eps)
    eps_io.seek(0)
    return eps_io


def get_thumbnail_colors():
    return rgb_colors


def get_thumbnail(width):
    img_io = StringIO.StringIO()
    resized = map_image.resize(((width, int(width / orig_width * orig_height))))
    resized.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io
