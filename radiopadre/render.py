import math
import cgi
import os.path

import IPython.display 
from IPython.display import display, HTML, Javascript

# crude hack to set _notebook_dir to the notebook directory
_notebook_dir = ''
display(Javascript("""
    var kernel = IPython.notebook.kernel;
    kernel.execute("import radiopadre.render,os.path; radiopadre.render._notebook_dir=os.path.dirname(" + "\'"+IPython.notebook.notebook_path+"\')");
"""))

def render_url (fullpath):
    """Converts a path relative to the notebook (i.e. kernel) to a URL that 
    can be served by the notebook server, by prepending the notebook
    directory""";
    return os.path.join("/files",_notebook_dir,fullpath);

def render_title(title):
    return "<b>%s</b>" % cgi.escape(title)

def render_status_message(msg):
    return "<p style='background: lightblue;'><b>%s</b></p>" % cgi.escape(msg)

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
                    txt += """"><A HREF=%s>%s</A></td>""" % (link, col)
                else:
                    txt += """">%s</td>""" % col
        txt += """</tr>\n"""
    txt += "</table>"
    return txt


def render_refresh_button (full=False):
    """Renders a "refresh" button which re-executes the current sell.
    If full is True, a double-click will re-execute the entire notebook, and the button
    will visually indicate that this is necessary
    """
    # bid = button_id and "'%s'"%button_id
    # attrs = ( "id=%s onload='init(%s);' " % (bid, bid) )  if bid else ""
    txt = """<script type="text/Javascript">
            function refresh()  {  
                IPython.notebook.execute_cell(); 
            }
            function refresh_all()  { 
                var current =  IPython.notebook.get_selected_index();
                IPython.notebook.execute_cell_range(0,current+1);
            }
          </script>
          <button %s onclick="refresh();"
            style="position: absolute; right: 0; top: 0;
    """
    if full:
        title = "The underlying directories have changed so it is probably wise to " +\
            "rerun the notebook. Double-click to rerun the notebook up to and including " +\
            "this cell, or click to rerun this cell only"
        txt += """color:red;"
            title="%s" ondblclick="refresh_all();"
            >&#8635;</button>
        """ % title
    else:
        txt += """"
            title="Click to rerun this cell and refresh its contents."
            >&#8635;</button>
        """
    # if bid:
    #     txt += """
    #         function init() {
    #           document.getElementById(%s).nbcell = IPython.notebook.get_selected_cell();
    #         }
    #         function refresh1() {
    #           document.getElementById(%s).nbcell.execute();
    #         }
    #     """ % (bid,bid)
    return txt
