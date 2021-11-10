from flask import Flask, render_template, url_for, request, redirect, session

import uuid, sys

from orderTO import orderTo

import pymssql

app = Flask(__name__)
app.secret_key = "CallAPizzaSecret"



conn = pymssql.connect(server='callapizza.database.windows.net:1433', user='SanDiegoAdmin', password='Tiftpasdsu1', database='callapizza')
cursor = conn.cursor()


@app.route("/")
def main(name=None):
    return render_template('main.html', name=name)

@app.route("/products")
def products(name=None):
    return render_template('products.html', name=name)

@app.route("/order", methods = ["POST", "GET"])
def order(name=None):
    session = uuid.uuid1
    conn = pymssql.connect(server='callapizza.database.windows.net:1433', user='SanDiegoAdmin', password='Tiftpasdsu1', database='callapizza')
    cursor = conn.cursor()
    cursor.execute("Select * from products")
    products = cursor.fetchall()
    pizzaList = []

    for item in products:
        tempList = [item[1], item[2]]
        pizzaList.append(tempList)

    description = "Tomatoes and Cheese"
    if request.method == "POST":
        pizza = request.form.get
        
    conn.close()
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
