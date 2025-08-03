from flask import Flask, render_template, request, redirect, send_file, flash, url_for
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

@app.route('/productos')
def listar_productos():
    productos = obtener_productos()
    return render_template('productos.html', productos=productos)

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
        flash("Debes agregar al menos un producto.", 'danger')
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
        flash("Producto agregado exitosamente.", 'success')
        return redirect('/')
    return render_template('agregar.html')

@app.route('/modificar/<nombre>', methods=['GET', 'POST'])
def modificar(nombre):
    productos = obtener_productos()
    producto = productos[productos['Nombre'] == nombre]
    if producto.empty:
        flash("Producto no encontrado.", 'danger')
        return redirect('/')
    producto = producto.iloc[0]

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        
        # Actualizar el producto
        idx = productos.index[productos['Nombre'] == nombre].tolist()
        if not idx:
            flash("Error: producto no encontrado para modificar.", 'danger')
            return redirect('/')
        idx = idx[0]
        productos.at[idx, 'Nombre'] = nuevo_nombre
        productos.at[idx, 'Descripción'] = descripcion
        productos.at[idx, 'Precio'] = precio
        
        productos.to_excel("productos.xlsx", index=False)
        flash("Producto modificado exitosamente.", 'success')
        return redirect('/')

    return render_template('modificar.html', producto=producto)

@app.route('/eliminar/<nombre>', methods=['POST'])
def eliminar(nombre):
    productos = obtener_productos()
    if nombre in productos['Nombre'].values:
        productos = productos[productos['Nombre'] != nombre]
        productos.to_excel("productos.xlsx", index=False)
        flash("Producto eliminado exitosamente.", 'success')
    else:
        flash("Producto no encontrado.", 'danger')
    return redirect(url_for('listar_productos'))

if __name__ == '__main__':
    app.run(debug=True)