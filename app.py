from flask import Flask, render_template, request, redirect, send_file, flash
import pandas as pd
import os
from utils import generar_pdf, guardar_nuevo_producto, obtener_productos
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta'

@app.route('/')
def index():
    productos = obtener_productos()
    return render_template('index.html', productos=productos)

@app.route('/cotizar', methods=['POST'])
def cotizar():
    cliente = request.form['cliente']
    anticipo_pct = float(request.form['anticipo']) / 100
    items = []

    for i in range(len(request.form.getlist('producto'))):
        nombre = request.form.getlist('producto')[i]
        cantidad = float(request.form.getlist('cantidad')[i])
        if cantidad <= 0:
            continue
        productos = obtener_productos()
        producto = productos[productos['Nombre'] == nombre].iloc[0]
        items.append({
            "Descripción": producto["Descripción"],
            "Cantidad": cantidad,
            "Precio Unitario": producto["Precio"],
            "Subtotal": producto["Precio"] * cantidad
        })

    if not items:
        flash("Debes agregar al menos un producto.")
        return redirect('/')

    filename = generar_pdf(cliente, items, anticipo_pct)
    return send_file(filename, as_attachment=True)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        guardar_nuevo_producto(nombre, descripcion, precio)
        flash("Producto agregado exitosamente.")
        return redirect('/')
    return render_template('agregar.html')

if __name__ == '__main__':
    app.run(debug=True)
