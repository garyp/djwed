#!/usr/bin/python

from reportlab.pdfgen import canvas
import time, os, sys
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
from cStringIO import StringIO
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


#precalculate some basics

class LabelSpecBasic:
    top_margin = letter[1] - 0.8*inch
    bottom_margin_safety = 1.0*inch
    left_margin = .3*inch
    right_margin = letter[0] - .3*inch
    frame_width = right_margin - left_margin
    columns = 3
    label_offset = 1.*inch
    column_offset = 2.75*inch




class LabelMaker:

    def __init__(self, label_spec):
        self.buffer = StringIO()
        self.spec = label_spec
        # Create the PDF object, using the StringIO object as its "file."
        canv = self.p = canvas.Canvas(self.buffer, pagesize=letter)
        self.p.setPageCompression(1)
        self.start_page()

    def start_page(self):
        self.p.setFont('Times-Bold',11)
        self.x = 0
        self.xpos = self.spec.left_margin
        self.y = 0
        self.ypos = self.spec.top_margin        
        
    def next_page(self):
        self.p.showPage()
        self.start_page()
        
    def add_label(self, text):
        maxline = 0
        for line in text.split("\n"):
            if len(line) > maxline:
                maxline = len(line)
        if maxline > 60:
            fontsize = 10
            hscale = 80
        elif maxline > 43:
            fontsize = 10
            hscale = 80
        elif maxline > 40:
            fontsize = 10
            hscale = 90
        elif maxline > 35:
            fontsize = 11
            hscale = 80
        elif maxline >= 32:
            fontsize = 11
            hscale = 90
        elif maxline < 20:
            fontsize = 12
            hscale = 100
        else:
            fontsize = 11
            hscale = 100
        #self.p.drawString(100, 100, "Hello world.")
        self.p.setFont('Times-Bold',fontsize)
        tx = self.p.beginText(self.xpos, self.ypos)
        tx.setHorizScale(hscale)
        for line in text.split("\n"):
            tx.textLine(line.replace('\r',''))
        self.p.drawText(tx)
        self.y += 1
        self.ypos -= self.spec.label_offset
        if self.ypos < self.spec.bottom_margin_safety:
            self.x += 1
            self.y = 0
            self.xpos += self.spec.column_offset
            self.ypos = self.spec.top_margin
        if self.x >= self.spec.columns:
            self.next_page()

    def finish(self):
        # Close the PDF object cleanly.
        self.p.showPage()
        self.p.save()
        # Get the value of the StringIO buffer and write it to the response.
        self.pdf = self.buffer.getvalue()
        self.buffer.close()
        return self.pdf

    def write_to_file(self, filename):
        f = file(filename, "w")
        f.write(self.pdf)
        f.close()

def main():
    lm = LabelMaker(LabelSpecBasic)
    for i in range(1,100):
        lm.add_label("Ben Bitdiddle and Alyssa P. Hacker\n555 Main St.\nAnytown, MA  55555")
    lm.finish()
    lm.write_to_file("/tmp/test.pdf")
    
if __name__ == "__main__":
    main()
