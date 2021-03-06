import os
import time
import math

from IPython.display import display, HTML

import radiopadre
from radiopadre.render import render_refresh_button


class FileBase(object):
    """Base class referring to a datafile. Sets up some standard attributes in the constructor.

    Attributes:
        fullpath:   the full path to the file, e.g. results/dir1/file1.txt
        path:       path to file relative to root padre directory, e.g. dir1/file1.txt
        name:       the filename (os.path.basename(path)), e.g. file1.txt
        ext:        extension with leading dot, e.g. .txt
        basename:   filename sans extension, e.g. file1
        basepath:   path+filename sans extension, e.g. dir1/file1
        mtime:      modification time
        mtime_str:  string version of mtime
        size:       size in bytes
        size_str:   human-readable size string
    """

    _unit_list = zip(['', 'k', 'M', 'G', 'T', 'P'], [0, 0, 1, 2, 2, 2])

    def __init__(self, path, root=""):
        """Construct a datafile and set up standard attributes.
        
        Args:
            path: path to the file
            root: root folder, will be stripped from beginning of file path if not empty

        """
        self.fullpath = path
        if root and path.startswith(root):
            path = path[len(root):]
            if path.startswith("/"):
                path = path[1:]
        self.path = path
        self.name = os.path.basename(self.path)
        self.basepath, self.ext = os.path.splitext(self.path)
        self.basename = os.path.basename(self.basepath)
        self.size = os.path.getsize(self.fullpath)
        self.update_mtime()
        
        # human-friendly size
        if self.size > 0:
            exponent = min(int(math.log(self.size, 1024)),
                           len(self._unit_list) - 1)
            quotient = float(self.size) / 1024 ** exponent
            unit, num_decimals = self._unit_list[exponent]
            format_string = '{:.%sf}{}' % (num_decimals)
            self.size_str = format_string.format(quotient, unit)
        else:
            self.size_str = '0'

    @staticmethod
    def sort_list(filelist, opt="xnt"):
        """
        Sort a list of FileBase objects by name, eXtension, Time, Size, optionally Reverse
        """
        opt = opt.lower()
        # build up order of comparison
        cmpattr = []
        for attr in opt:
            if attr in FileBase._sort_attributes:
                cmpattr.append(FileBase._sort_attributes[attr])

        def compare(a, b, attrs=cmpattr):
            for attr in attrs:
                result = cmp(getattr(a, attr), getattr(b, attr))
                if result:
                    return result
            return 0

        list.sort(filelist, cmp=compare, reverse='r' in opt)
        return filelist

    _sort_attributes = dict(x="ext", n="basepath", s="size", t="mtime")

    def update_mtime (self):
        """Updates mtime and mtime_str attributes according to current file mtime,
        returns mtime_str"""
        self.mtime = os.path.getmtime(self.fullpath)
        self.mtime_str = time.strftime(radiopadre.TIMEFORMAT,
                                       time.localtime(self.mtime))
        return self.mtime_str

    def is_updated (self):
        """Returns True if mtime of underlying file has changed"""
        return os.path.getmtime(self.fullpath) > self.mtime

    def __str__(self):
        return self.path

    def _repr_html_(self):
        return self.show() or self.path

    def show(self, *args, **kw):
        print self.path

    def watch(self, *args, **kw):
        display(HTML(render_refresh_button()))
        return self.show(*args, **kw)


def data_file(path, root=""):
    """
    Creates DataFile object of appropriate type, based on filename extension
    """
    from radiopadre.fitsfile import FITSFile
    from radiopadre.imagefile import ImageFile
    from radiopadre.textfile import TextFile
    ext = os.path.splitext(path)[1]
    if ext.lower() in [".fits", ".fts"]:
        return FITSFile(path, root=root)
    elif ext.lower() in [".png", ".jpg", ".jpeg"]:
        return ImageFile(path, root=root)
    elif ext.lower() in [".txt", ".log"]:
        return TextFile(path, root=root)
    return FileBase(path, root=root)


def compute_thumb_geometry(N, ncol, mincol, maxcol, width, maxwidth):
    """
    Works out thumbnail geometry.

    Given nfiles thumbsnails to display, how many rows and columns do we need
    to make, and how wide do we need to make the plot?

    args:
         N:  number of thumbnails to display
         ncol: use a fixed number of columns. If 0, uses mincol/maxcol.
         mincol: use a minimum of that many columns, even if N is fewer.
                 If N<mincol, will use mincol columns
         maxcol: use a maximum of that many columns. If 0, makes a single row
                 of N columns.
         width:  if non-zero, fixes width of individual thumbnail, in inches
         maxwidth: if width is 0, uses a width of maxwidth/ncol for each
                   thumbnail

    Returns:
        tuple of nrow, ncol, width
    """
    # figure out number of columns
    if not ncol:
        mincol = mincol or radiopadre.MINCOL or 0
        maxcol = maxcol or radiopadre.MAXCOL or 8
        ncol = max(mincol, min(maxcol, N))
    # number of rows
    nrow = int(math.ceil(N / float(ncol)))
    # individual thumbnail width
    width = width or ((maxwidth or radiopadre.WIDTH or 16) / float(ncol))
    return nrow, ncol, width
