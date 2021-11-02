from flask import Flask, render_template, url_for, request, redirect, session

import uuid

app = Flask(__name__)
app.secret_key = "CallAPizzaSecret"

@app.route("/")
def main(name=None):
    return render_template('main.html', name=name)

@app.route("/products")
def products(name=None):
    return render_template('products.html', name=name)

@app.route("/order")
def order(name=None):
    session = uuid.uuid1
    pizzaList = ["Pizza Salami", "Pizza Ham", "Pizza Romana"]
    description = "Tomatoes and Cheese"
    return render_template('order.html', name=name, pizzaList=pizzaList, description=description)

@app.route("/customerInput", methods = ["POST", "GET"])
def customerInput(name=None):
    if request.method == "POST":
        result = request.form.get("CustomerFirstName")
        return redirect(url_for("success", firstName=result))
    else:
        return render_template('customerInput.html', name=name)

@app.route("/<firstName>")
def success(firstName):
    return render_template('success.html', value=firstName)
