import math
import cgi

def render_title(title):
    return "<b>%s</b>" % cgi.escape(title)


def render_table(data, labels, html=set(), ncol=1, links=None):
    txt = """<table style="border: 1px; text-align: left">
        <tr style="border: 0px; border-bottom: 1px double; text-align: center">
    """
    if not data:
        return "no content"
    for icol in range(ncol):
        txt += """<th style="border: 0px; border-bottom: 1px double; text-align: center">#</th>"""
        for ilab, lab in enumerate(labels):
            txt += """<th style="text-align: center; border: 0px; border-bottom: 1px double;"""
            if ncol > 1 and icol < ncol - 1 and ilab == len(labels) - 1:
                txt += "border-right: 1px double; padding-right: 10px"
            txt += "\">%s</th>\n" % lab
    txt += "</tr>\n"
    nrow = int(math.ceil(len(data) / float(ncol)))
    for irow in range(nrow):
        txt += """<tr style="border: 0px; text-align: left">\n"""
        for icol, idatum in enumerate(range(irow, len(data), nrow)):
            datum = data[idatum]
            txt += """<td style="border: 0px">%d</td>""" % idatum
            for i, col in enumerate(datum):
                if not str(col).upper().startswith("<HTML>") and not i in html and not labels[i] in html:
                    col = cgi.escape(str(col))
                txt += """<td style="border: 0px; """
                if ncol > 1 and icol < ncol - 1 and i == len(datum) - 1:
                    txt += "border-right: 1px double; padding-right: 10px"
                link = links and links[idatum][i]
                if link:
                    txt += """"><A HREF=/files/%s>%s</A></td>""" % (link, col)
                else:
                    txt += """">%s</td>""" % col
        txt += """</tr>\n"""
    txt += "</table>"
    return txt
