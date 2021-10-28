from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def main(name=None):
    return render_template('main.html', name=name)

@app.route("/products")
def products(name=None):
    return render_template('products.html', name=name)

@app.route("/order")
def order(name=None):
    return render_template('order.html', name=name)

@app.route("/customerInput")
def customerInput(name=None):
    return render_template('customerInput.html', name=name)
