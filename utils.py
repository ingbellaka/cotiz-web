import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from datetime import datetime
import os

def obtener_productos():
    return pd.read_excel("productos.xlsx")

def guardar_nuevo_producto(nombre, descripcion, precio):
    df = obtener_productos()
    nuevo = pd.DataFrame({"Nombre": [nombre], "Descripción": [descripcion], "Precio": [precio]})
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_excel("productos.xlsx", index=False)

def draw_wrapped_text(c, text, x, y, max_width, line_height):
    lines = []
    while text:
        if c.stringWidth(text, "Helvetica", 10) <= max_width:
            lines.append(text)
            break
        for i in range(len(text), 0, -1):
            if c.stringWidth(text[:i], "Helvetica", 10) <= max_width and text[i - 1] == " ":
                lines.append(text[:i].strip())
                text = text[i:].strip()
                break
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y

def generar_pdf(cliente, items, anticipo_pct):
    filename = f"Cotizacion_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    logo_path = "static/image.jpg"
    if os.path.exists(logo_path):
        img = utils.ImageReader(logo_path)
        iw, ih = img.getSize()
        aspect = iw / ih
        c.drawImage(logo_path, width - 100, height - 80, width=80, height=80 / aspect)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 50, "FABRICANTES LACCY")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 65, "Calle Cedro #3624 Col. Jardines del Pedregal")
    c.drawString(40, height - 80, "Culiacán, Sinaloa")
    c.drawString(40, height - 95, "Teléfono: 667-103-4026")
    c.drawString(40, height - 110, "Correo: fabricanteslaccy@gmail.com")

    c.drawString(40, height - 130, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(40, height - 145, f"Cliente: {cliente}")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, height - 170, "Descripción")
    c.drawString(300, height - 170, "Cantidad")
    c.drawString(380, height - 170, "Precio")
    c.drawString(480, height - 170, "Subtotal")
    c.line(40, height - 175, 560, height - 175)

    y = height - 190
    subtotal = 0
    for item in items:
        c.setFont("Helvetica", 10)
        y = draw_wrapped_text(c, item["Descripción"], 40, y, 250, 12)
        c.drawCentredString(330, y + 12, str(item["Cantidad"]))
        c.drawString(380, y + 12, f"${item['Precio Unitario']:.2f}")
        c.drawString(480, y + 12, f"${item['Subtotal']:.2f}")
        subtotal += item["Subtotal"]
        y -= 20

    anticipo = subtotal * anticipo_pct
    resto = subtotal - anticipo

    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(380, y, "Subtotal:")
    c.drawString(480, y, f"${subtotal:.2f}")
    y -= 15
    c.drawString(380, y, f"Anticipo ({anticipo_pct*100:.0f}%):")
    c.drawString(480, y, f"${anticipo:.2f}")
    y -= 15
    c.drawString(380, y, "Resto:")
    c.drawString(480, y, f"${resto:.2f}")

    c.save()
    return filename
