from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from datetime import datetime

def create(note, me):
    canvas = Canvas(f"{note.person}-{str(datetime.today()).split('.')[0][:-3]}.pdf", pagesize=A4)
    canvas.setFont("Times-Roman", 14)
    canvas.drawString()