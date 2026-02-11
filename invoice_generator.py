"""
Wasul Invoice Generator
Generates professional PDF invoices for delivery partners
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Try to register DM Serif Display if available, fall back to Liberation Serif
LOGO_FONT = "Helvetica-Bold"  # fallback

def _register_fonts():
    global LOGO_FONT
    # Try DM Serif Display first (should be placed in project root or fonts/ dir)
    font_paths = [
        "fonts/DMSerifDisplay-Regular.ttf",
        "DMSerifDisplay-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                font_name = "DMSerif" if "DMSerif" in path else "SerifLogo"
                pdfmetrics.registerFont(TTFont(font_name, path))
                LOGO_FONT = font_name
                break
            except:
                continue

_register_fonts()


def generate_invoice_pdf(filepath: str, data: dict):
    """
    Generate a Wasul invoice PDF.
    
    data keys:
        invoice_number: str (e.g. 'WAS-2026-0001')
        from_name: str
        from_address: str (newline separated)
        partner_name: str
        partner_address: str (newline separated, optional)
        invoice_date: str
        due_date: str
        billing_period: str
        line_items: list of dicts with keys: description, quantity, rate, amount
        subtotal: str
        tax: str (optional, defaults to '$0.00')
        total: str
        total_lookups: int
        deliveries_verified: int
        api_key_preview: str
        payment_instructions: str (newline separated)
    """
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Colors
    orange = HexColor('#e8682a')
    charcoal = HexColor('#1a1a1a')
    slate = HexColor('#4a4a4a')
    muted = HexColor('#7a7a7a')
    sand = HexColor('#f9f6f2')
    line_color = HexColor('#e8e4de')
    white = HexColor('#ffffff')

    # ---- HEADER ----
    c.setFillColor(orange)
    c.rect(0, height - 4, width, 4, fill=1, stroke=0)

    # Logo
    c.setFont(LOGO_FONT, 28)
    c.setFillColor(orange)
    c.drawString(60, height - 60, "Wasul")

    # Invoice label
    c.setFont("Helvetica", 11)
    c.setFillColor(muted)
    c.drawRightString(width - 60, height - 45, "INVOICE")

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(charcoal)
    c.drawRightString(width - 60, height - 62, data['invoice_number'])

    # Divider
    c.setStrokeColor(line_color)
    c.setLineWidth(0.5)
    c.line(60, height - 80, width - 60, height - 80)

    # ---- FROM / TO / DETAILS ----
    y = height - 110

    # From
    c.setFont("Helvetica", 7.5)
    c.setFillColor(muted)
    c.drawString(60, y, "FROM")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(charcoal)
    c.drawString(60, y - 16, data['from_name'])
    c.setFont("Helvetica", 9)
    c.setFillColor(slate)
    for i, line in enumerate(data['from_address'].split('\n')):
        c.drawString(60, y - 32 - (i * 14), line)

    # Bill To
    c.setFont("Helvetica", 7.5)
    c.setFillColor(muted)
    c.drawString(250, y, "BILL TO")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(charcoal)
    c.drawString(250, y - 16, data['partner_name'])
    c.setFont("Helvetica", 9)
    c.setFillColor(slate)
    if data.get('partner_address'):
        for i, line in enumerate(data['partner_address'].split('\n')):
            c.drawString(250, y - 32 - (i * 14), line)

    # Details
    detail_x = width - 180
    c.setFont("Helvetica", 7.5)
    c.setFillColor(muted)
    c.drawString(detail_x, y, "DETAILS")

    details = [
        ("Invoice Date", data['invoice_date']),
        ("Due Date", data['due_date']),
        ("Billing Period", data['billing_period']),
    ]
    for i, (label, value) in enumerate(details):
        row_y = y - 16 - (i * 22)
        c.setFont("Helvetica", 8)
        c.setFillColor(muted)
        c.drawString(detail_x, row_y + 9, label)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(charcoal)
        c.drawString(detail_x, row_y - 4, value)

    # ---- USAGE TABLE ----
    table_top = height - 240

    c.setFillColor(sand)
    c.roundRect(60, table_top - 6, width - 120, 24, 4, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(muted)
    c.drawString(72, table_top, "DESCRIPTION")
    c.drawString(340, table_top, "QUANTITY")
    c.drawString(420, table_top, "RATE")
    c.drawRightString(width - 72, table_top, "AMOUNT")

    row_y = table_top - 36
    c.setStrokeColor(line_color)
    c.setLineWidth(0.3)

    for item in data['line_items']:
        c.setFont("Helvetica", 9.5)
        c.setFillColor(charcoal)
        c.drawString(72, row_y, item['description'])
        c.setFillColor(slate)
        c.drawString(340, row_y, str(item['quantity']))
        c.drawString(420, row_y, item['rate'])
        c.drawRightString(width - 72, row_y, item['amount'])
        row_y -= 12
        c.line(72, row_y, width - 72, row_y)
        row_y -= 22

    # ---- TOTALS ----
    totals_x = 380
    totals_val_x = width - 72
    row_y -= 8

    c.setFont("Helvetica", 9.5)
    c.setFillColor(slate)
    c.drawString(totals_x, row_y, "Subtotal")
    c.drawRightString(totals_val_x, row_y, data['subtotal'])

    row_y -= 22
    c.drawString(totals_x, row_y, "Tax")
    c.drawRightString(totals_val_x, row_y, data.get('tax', '$0.00'))

    row_y -= 28
    c.line(totals_x, row_y + 16, totals_val_x, row_y + 16)

    c.setFillColor(charcoal)
    c.roundRect(totals_x - 12, row_y - 10, totals_val_x - totals_x + 24, 32, 6, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(white)
    c.drawString(totals_x, row_y, "Total Due")
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(totals_val_x, row_y, data['total'])

    # ---- USAGE SUMMARY ----
    summary_y = row_y - 60

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(charcoal)
    c.drawString(60, summary_y, "Usage Summary")
    c.setStrokeColor(line_color)
    c.line(60, summary_y - 10, width - 60, summary_y - 10)

    summary_items = [
        ("Total Lookups", str(data['total_lookups'])),
        ("Deliveries Verified", str(data['deliveries_verified'])),
        ("API Key", data['api_key_preview']),
        ("Account Status", "Active"),
    ]
    item_y = summary_y - 32
    for label, value in summary_items:
        c.setFont("Helvetica", 8.5)
        c.setFillColor(muted)
        c.drawString(72, item_y, label)
        c.setFont("Helvetica", 9)
        c.setFillColor(charcoal)
        c.drawString(250, item_y, value)
        item_y -= 20

    # ---- PAYMENT INSTRUCTIONS ----
    pay_y = item_y - 30
    c.setFillColor(sand)
    c.roundRect(60, pay_y - 80, width - 120, 100, 8, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(charcoal)
    c.drawString(80, pay_y, "Payment Instructions")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(slate)
    for i, line in enumerate(data['payment_instructions'].split('\n')):
        c.drawString(80, pay_y - 18 - (i * 14), line)

    # ---- FOOTER ----
    footer_y = 50
    c.setStrokeColor(line_color)
    c.line(60, footer_y + 16, width - 60, footer_y + 16)
    c.setFont("Helvetica", 8)
    c.setFillColor(muted)
    c.drawString(60, footer_y, "Wasul — Address registration and delivery infrastructure for Oman")
    c.drawRightString(width - 60, footer_y, "Thank you for your business")

    c.save()
    return filepath
