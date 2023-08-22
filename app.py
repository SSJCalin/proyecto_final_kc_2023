from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

API_KEY = '9F853224-721A-4CB4-B96F-A389898A5023'

# Modelo para la tabla "transactions"
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    crypto = db.Column(db.Text)
    amount = db.Column(db.Float)
    type = db.Column(db.Text)
    fecha = db.Column(db.Date)
    hora = db.Column(db.Time)
    moneda_from = db.Column(db.Text)

# Modelo para la tabla "movimientos"
class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date)
    hora = db.Column(db.Time)
    moneda_from = db.Column(db.Text)
    moneda_to = db.Column(db.Text)
    cantidad = db.Column(db.Float)

# Función para consultar el valor de una criptomoneda respecto a EUR
def get_crypto_value(crypto):
    base_url = 'https://rest.coinapi.io/v1/exchangerate'
    endpoint = f'{base_url}/EUR/{crypto}?apikey={API_KEY}'
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        return data['rate']
    return None

# Función para insertar una nueva transacción en la base de datos
def insert_transaction(crypto, amount, transaction_type, moneda_from):
    with app.app_context():
        fecha = datetime.date.today()
        hora = datetime.datetime.now().time()
        print("Datos a insertar:", crypto, amount, transaction_type,
              moneda_from)  # Agregar este mensaje de depuración
        new_transaction = Transaction(
            crypto=crypto, amount=amount, type=transaction_type, fecha=fecha, hora=hora, moneda_from=moneda_from)
        db.session.add(new_transaction)
        
        # Insertar la transacción en la tabla "movimientos"
        new_movimiento = Movimiento(
            fecha=fecha, hora=hora, moneda_from=moneda_from, moneda_to=crypto, cantidad=amount)
        db.session.add(new_movimiento)
        
        db.session.commit()
        # Agregar este mensaje de depuración
        print("Transacción insertada correctamente en la base de datos.")

@app.route('/')
def index():
    movimientos = Transaction.query.order_by(
        Transaction.fecha.desc(), Transaction.hora.desc()).all()
    print("Transacciones recuperadas:", movimientos)
    return render_template('inicio.html', movimientos=movimientos)

@app.route('/compra', methods=['GET', 'POST'])
def compra():
    if request.method == 'POST':
        crypto = request.form['comprar_from']
        amount = float(request.form['cantidad_comprar'])
        moneda_from = "EUR"
        transaction_type = "Compra"
        print("Insertando transacción en la base de datos...")
        insert_transaction(crypto, amount, transaction_type, moneda_from)
        print("Transacción insertada correctamente en la base de datos.")
        return redirect(url_for('index'))
    else:
        monedas = Transaction.query.with_entities(
            Transaction.moneda_from).distinct().all()
        monedas = [m[0] for m in monedas]
        return render_template('compra.html', monedas=monedas)

@app.route('/status')
def status():
    return "Página de status"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
