import os
from os import path

from django.http import HttpResponse
from django.views import View
from str2bool import str2bool

from abcavatar.settings import MEDIA_ROOT
from app import xavinit


def freeze(o):
    if isinstance(o, dict):
        return frozenset({k: freeze(v) for k, v in o.items()}.items())

    if isinstance(o, list):
        return tuple([freeze(v) for v in o])

    return o


def make_hash(o):
    """
    makes a hash out of anything that contains only list,dict and hashable types including string and numeric types
    """
    return hash(freeze(o))


class AvatarView(View):

    def get(self, request, *args, **kwargs):

        words = self.request.GET.get('words', '')
        size = self.request.GET.get('size')
        background = self.request.GET.get('bg-color', '')
        color = self.request.GET.get('fg-color')
        font_size = self.request.GET.get('font-size')
        font_family = self.request.GET.get('font-family')
        rounded = str2bool(self.request.GET.get('rounded'))
        bold = str2bool(self.request.GET.get('bold'))
        mime_type = self.request.GET.get('format', 'svg')

        args = xavinit.DEFAULT_SETTINGS.copy()

        if color:
            args.update({'color': '#' + color})
        if background:
            args.update({'colors': ['#' + color for color in background.split(',')]})
        if size:
            size = int(size)
            if size < 16:
                size = 16
            if size > 512:
                size = 512
            args.update({'width': str(size), 'height': str(size)})
            args.update({'font-size': str(size * 0.5)})
        if font_size:
            size = int(args.get('width'))
            font_size = float(font_size)
            if font_size < 0.1:
                font_size = 0.1
            if font_size > 1:
                font_size = 0.5
            args.update({'font-size': str(size * font_size)})
        if bold:
            args.update({'font-weight': '600'})
        if font_family:
            args.update({'font-family': font_family})
        if rounded:
            radius = str(int(args.get('width')) // 2)
            args.update({'radius': radius})
            args.update({'x-axis': radius, 'y-axis': radius})

        if mime_type not in ['svg', 'png', 'url']:
            mime_type = 'svg'

        if mime_type == 'svg':
            return HttpResponse(xavinit.get_svg_avatar(words, rounded, **args), 'image/svg+xml')
        elif mime_type == 'url':
            return HttpResponse(xavinit.get_avatar_data_url(words, rounded, **args), 'text/plain')
        elif mime_type == 'png':
            args_hash = make_hash(args)
            initials = xavinit.get_initials(words)

            sub_dir = '%s%s' % (MEDIA_ROOT, initials[0],)
            filename = '%s/%s_%s.png' % (sub_dir, initials, args_hash,)

            if not path.exists(filename):
                if not path.exists(sub_dir):
                    os.makedirs(sub_dir)
                xavinit.get_png_avatar(words, rounded, filename, **args)

            image_data = open(filename, "rb").read()

            return HttpResponse(image_data, 'image/png')
