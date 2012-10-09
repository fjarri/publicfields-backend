from werkzeug.contrib.cache import SimpleCache
from flask import request, abort, send_file, jsonify

from backend import app
import backend.textmap.process as process


cache = SimpleCache()


def process_color_str(color_str):
    colors = color_str.split()
    if len(colors) != 4: raise ValueError

    result = []
    for color in colors:
        color = float(color)
        if color < 0 or color > 1: raise ValueError
        result.append(color)

    return result


@app.route('/textmap/eps')
def get_eps():
    """
    Returns an .eps file with custom colors and height.
    """

    color_names = process.get_thumbnail_colors().keys()

    colors = {}
    for color_name in color_names:
        color_str = request.args.get(color_name, '0,0,0,1')
        try:
            color = process_color_str(color_str)
        except ValueError:
            abort(400)
        colors[color_name] = color

    try:
        aspect = request.args.get('aspect', 'robinson')
        if aspect not in ('robinson', 'A', 'golden'):
            raise ValueError
    except ValueError:
        abort(400)

    name = "eps" + \
        "-".join(name + "=" + str(colors[name]) for name in sorted(colors)) + \
        "aspect=" + str(aspect)
    eps_io = cache.get(name)
    if eps_io is None:
        eps_io = process.get_eps(colors, aspect)
        cache.set(name, eps_io)

    return send_file(eps_io, mimetype='application/postscript',
        attachment_filename="textmap.eps", as_attachment=True)


@app.route('/textmap/colors')
def get_colors():
    """
    Returns a json with mapping from color names to colors in the thumbnail.
    """
    callback = request.args.get('callback', '')
    return callback + "(" + jsonify(process.get_thumbnail_colors()).data + ");"


@app.route('/textmap/thumbnail<int:width>-<aspect>.png')
def get_thumbnail(width, aspect):
    """
    Returns a .png file with a non-antialiased thumbnail.
    """
    name = "thumbnail" + str(width) + "-" + aspect + ".png"

    img_io = cache.get(name)
    if img_io is None:
        img_io = process.get_thumbnail(width, aspect)
        cache.set(name, img_io)

    return send_file(img_io, mimetype='image/png',
        attachment_filename=name, as_attachment=True)
