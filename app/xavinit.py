# based on avinit (https://github.com/CraveFood/avinit)

import re

from base64 import b64encode
from xml.sax.saxutils import escape as xml_escape

try:
    import cairosvg
except ImportError:
    cairosvg = None

DEFAULT_TEXT = '=)'

DEFAULT_FONTS = [
    'HelveticaNeue-Light',
    'Helvetica Neue Light',
    'Helvetica Neue',
    'Helvetica',
    'Arial',
    'Lucida Grande',
    'sans-serif',
]

DEFAULT_SETTINGS = {
    'width': '64',
    'height': '64',
    'color': '#ffffff',
    'font-family': ','.join(DEFAULT_FONTS),
    'font-size': '32',
    'font-weight': '400',
    'x-axis': '32',
    'y-axis': '32',
    'radius': '32',
}

SVG_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" pointer-events="none"
     width="{width}" height="{height}">
  <rect width="{width}" height="{height}" style="{style}"></rect>
  <text text-anchor="middle" y="50%" x="50%" dy="0.35em"
        pointer-events="auto" fill="{color}" font-family="{font-family}"
        style="{text-style}">{text}</text>
</svg>
""".strip()
SVG_TEMPLATE = re.sub('(\s+|\n)', ' ', SVG_TEMPLATE)

SVG_TEMPLATE_ROUNDED = """
<svg xmlns="http://www.w3.org/2000/svg" pointer-events="none"
     width="{width}" height="{height}">
  <circle cx="{x-axis}" cy="{y-axis}" r="{radius}" style="{circle-style}"></circle>
  <text text-anchor="middle" y="50%" x="50%" dy="0.35em"
        pointer-events="auto" fill="{color}" font-family="{font-family}"
        style="{text-style}">{text}</text>
</svg>
""".strip()
SVG_TEMPLATE_ROUNDED = re.sub('(\s+|\n)', ' ', SVG_TEMPLATE_ROUNDED)

DEFAULT_COLORS = [
    "#1abc9c", "#16a085", "#f1c40f", "#f39c12", "#2ecc71", "#27ae60",
    "#e67e22", "#d35400", "#3498db", "#2980b9", "#e74c3c", "#c0392b",
    "#9b59b6", "#8e44ad", "#bdc3c7", "#34495e", "#2c3e50", "#95a5a6",
    "#7f8c8d", "#ec87bf", "#d870ad", "#f69785", "#9ba37e", "#b49255",
    "#b49255", "#a94136",
]


def _from_dict_to_style(style_dict):
    return '; '.join(['{}: {}'.format(k, v) for k, v in style_dict.items()])


def _get_color(text, colors=None):
    if not colors:
        colors = DEFAULT_COLORS
    color_index = sum(map(ord, text)) % len(colors)
    return colors[color_index]


def get_initials(text):
    initials = DEFAULT_TEXT

    text = text.strip()
    if text:
        split_text = text.split(' ')
        if len(split_text) > 1:
            initials = split_text[0][0] + split_text[-1][0]
        elif len(split_text[0]) > 1:
            initials = split_text[0][:2]
        else:
            initials = split_text[0][0]

    return initials


def get_svg_avatar(text, rounded=False, **kwargs):

    initials = get_initials(text)

    opts = DEFAULT_SETTINGS.copy()
    opts.update(kwargs)

    style = {
        'fill': _get_color(text, opts.get('colors')),
        'width': opts.get('width') + 'px',
        'height': opts.get('height') + 'px',
    }

    circle_style = {
        'fill': _get_color(text, opts.get('colors')),
    }

    text_style = {
        'font-weight': opts.get('font-weight'),
        'font-size': opts.get('font-size') + 'px',
    }

    svg_template = SVG_TEMPLATE_ROUNDED if rounded else SVG_TEMPLATE

    return svg_template.format(**{
        'height': opts.get('height'),
        'width': opts.get('width'),
        'x-axis': opts.get('x-axis'),
        'y-axis': opts.get('y-axis'),
        'radius': opts.get('radius'),
        'color': opts.get('color'),
        'style': _from_dict_to_style(style),
        'circle-style': _from_dict_to_style(circle_style),
        'font-family': opts.get('font-family'),
        'text-style': _from_dict_to_style(text_style),
        'text': xml_escape(initials.upper()),
    }).replace('\n', '')


def get_png_avatar(text, rounded=False, output_file=None, **kwargs):
    if not cairosvg:
        raise Exception('CairoSVG is required to png conversions.')

    svg_avatar = get_svg_avatar(text, rounded, **kwargs)
    cairosvg.svg2png(svg_avatar, write_to=output_file)


def get_avatar_data_url(text, rounded=False, **kwargs):
    svg_avatar = get_svg_avatar(text, rounded, **kwargs)
    b64_avatar = b64encode(svg_avatar.encode('utf-8'))
    return 'data:image/svg+xml;base64,' + b64_avatar.decode('utf-8')
