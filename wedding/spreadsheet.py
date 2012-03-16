import os
from pyExcelerator import * 
import StringIO




def font_style(position='left', colour=1, bold=0) : 
	font = Font()
	font.name = 'Verdana'
	font.bold = bold
	style = XFStyle()
	font.colour_index = colour
	style.font = font 
	return style 


class SpreadSheet:
    def __init__(self, name):
        self.cols = []
	self.workbook = Workbook()
	self.worksheet = self.workbook.add_sheet(name) 
        self.y = 1

    def add_column(self, name, width):        
        x = len(self.cols)
        self.cols.append(name)
        self.worksheet.col(x).width = width*100
        self.worksheet.write(0,x, name, font_style(colour=0, bold=1))

    def add_row(self, els):
        x=0
        for e in els:
            self.worksheet.write(self.y, x, e, font_style(colour=0))
            x += 1
        self.y += 1

    def finalize(self):
        #output = StringIO.StringIO()
        #self.workbook.write(output)
        #contents = output.getvalue()
        #output.close()
        return self.workbook.get_biff_data()

# Close object and discard memory buffer --
# .getvalue() will now raise an exception.
