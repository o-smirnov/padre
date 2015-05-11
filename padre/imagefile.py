import os

import IPython.display
from IPython.display import HTML, display

import padre
import padre.file


class ImageFile(padre.file.FileBase):
    @staticmethod
    def _show_thumbs(images, width=None, ncol=None, maxwidth=None, mincol=None,
                     maxcol=None, title=None, **kw):

        if not images:
            return None
        nrow, ncol, width = padre.file.compute_thumb_geometry(len(images), ncol,
                                                              mincol, maxcol,
                                                              width, maxwidth)
        npix = int(padre.DPI * width)

        # make list of thumbnail,filename pairs
        filelist = [(os.path.basename(img.path),
                     "%s/padre-thumbnails/%d.%s" % (os.path.dirname(img.path),
                                                    npix,
                                                    os.path.basename(img.path)),
                     img.path)
                    for img in images]
        filelist.sort()

        # (re)generate thumbs if needed
        fails = 0
        for _, thumb, image in filelist:
            if not os.path.exists(os.path.dirname(thumb)):
                if os.system("mkdir %s" % os.path.dirname(thumb)):
                    fails += 1
            if not os.path.exists(thumb) or os.path.getmtime(
                    thumb) < os.path.getmtime(image):
                if os.system("convert -thumbnail %d %s %s" % (npix, image,
                                                              thumb)):
                    fails += 1

        html = padre.render_title(title) + \
                   """<br>
                   <table style="border: 0px; text-align: left">\n
                   """
        if fails:
            html += "(WARNING: %d thumbnails failed to generate, check console for errors)<br>\n" % fails

        for row in range(nrow):
            html += """<tr style="border: 0px; text-align: left">\n"""
            filelist_row = filelist[row * ncol:(row + 1) * ncol]
            for _, thumb, image in filelist_row:
                html += """<td style="border: 0px; text-align: center">"""
                html += os.path.basename(image)
                html += "</td>\n"
            html += """</tr><tr style="border: 0px; text-align: left">\n"""
            for _, thumb, image in filelist_row:
                html += """<td style="border: 0px; text-align: left">"""
                html += "<a href=/files/%s><img src=/files/%s alt='?'></a>" % (image, thumb)
                html += "</td>\n"
            html += "</tr>\n"
        html += "</table>"

        display(HTML(html))

    def show(self, width=None):
        IPython.display.display(IPython.display.Image(self.fullpath,
                                                      width=width * 100))
