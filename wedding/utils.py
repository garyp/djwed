import random
import sys, os, tempfile

def generate_invite_code():
    ic_allowed_chars = "23456789abcdefghjkmnpqrstuvwxzy"
    code = ""
    for i in range(0,6):
        code += ic_allowed_chars[random.randrange(0,len(ic_allowed_chars))]
        if len(code) == 3:
            code += '-'
    return code.upper()


class SVG2PDF:
    """ Converts a sequence of SVG files to PS/PDF. """
    def __init__(self, pdf_mode=False, orient="portrait"):
        self.dir = tempfile.mkdtemp()
        self.pdf_mode = pdf_mode  # otherwise postscript
        self.pdf_files = []
        self.ps_files = []
        self.pageno = 1
        self.orient = orient

    def add_svg(self, svg):
        svgfn = "%s/pg%d.svg"%(self.dir,self.pageno)
        pdffn = "%s/pg%d.pdf"%(self.dir,self.pageno)
        psfn = "%s/pg%d.ps"%(self.dir,self.pageno)
        f = open(svgfn,"w")
        f.write(svg.encode('UTF-8'))
        f.close()
        if self.pdf_mode:
            os.system("inkscape --without-gui -d 600 --export-pdf=%s %s 2>&1 >/dev/null"%(pdffn,svgfn))
            self.pdf_files.append(pdffn)
        else:
            os.system("inkscape --without-gui -d 60 --export-ps=%s %s 2>&1 >/dev/null"%(psfn,svgfn))
            self.ps_files.append(psfn)
        self.pageno += 1
        os.unlink(svgfn)
        
    def finish(self):
        if self.pdf_mode:
            outfn = "%s/out.pdf"%(self.dir,)
            os.system('pdfjoin --paper letterpaper --orient %s --trim "0 0 0 0" --offset "0 0" --turn false --noautoscale true --outfile %s %s'%(self.orient, outfn, " ".join(self.pdf_files)))
            for f in self.pdf_files:
                print f
                os.unlink(f)
        else:
            outfn = "%s/out.ps"%(self.dir,)
            orient_opt = "-sPAPERSIZE=letter"
            if self.orient == "landscape":
                orient_opt = '-dDEVICEWIDTHPOINTS=792 -dDEVICEHEIGHTPOINTS=612'
            elif self.orient == "a8-envelope":
                orient_opt = '-dDEVICEWIDTHPOINTS=585 -dDEVICEHEIGHTPOINTS=396'
            cmd = 'gs -q -dNOPAUSE -dBATCH  -sDEVICE=pswrite %s -sOutputFile=%s %s'%(orient_opt, outfn, " ".join(self.ps_files))
            print cmd
            os.system(cmd)
            for f in self.ps_files:
                print f
                os.unlink(f)
        out = file(outfn)
        outstr = out.read()
        out.close()
        os.unlink(outfn)
        os.rmdir(self.dir)
        return outstr
