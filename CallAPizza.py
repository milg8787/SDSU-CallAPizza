from os import SEEK_CUR
import re
from flask import Flask, render_template, url_for, request, redirect, session

import uuid, sys, datetime

from werkzeug.wrappers import response
from customerTO import customerTO

import pymssql

app = Flask(__name__)
app.secret_key = "CallAPizzaSecret"


@app.route("/")
def main(name=None):
    return render_template('main.html', name=name)

@app.route("/products")
def products(name=None):
    return render_template('products.html', name=name)

@app.route("/order", methods = ["POST", "GET"])
def order(name=None):
    conn = pymssql.connect(server='callapizza.database.windows.net:1433', user='SanDiegoAdmin', password='Tiftpasdsu1', database='callapizza')
    cursor = conn.cursor()
    orderList = []
    pizzaList = []
    

    customerID = session['customerID']
    cursor.execute("Select * from products")
    products = cursor.fetchall()
        
    for item in products:
        tempList = [item[1], item[2], item[3]]
        pizzaList.append(tempList)

    if request.method == "POST":
        orderList.append(request.form.get)

        if request.form.get("goToCart"):
            orderInsert = """INSERT INTO orders (customerID, orderDate, orderStatus, delivery) 
                            VALUES (%s, %s, %s, %s) """
            # Fix delivery with a button in customerInput
            orderInsertRecord = (customerID, datetime.datetime.now(), 0, 0)
            cursor.execute(orderInsert, orderInsertRecord)
            conn.commit()

            orderDetailsInsert = """INSERT INTO orderDetails (orderID, productID, price, quantity, salami, ham, pepperoni, jalapenos, blackOlives, redOnions)
                            VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
    ##cursor.execute("Insert into orders")
        
    conn.close()
    return render_template('order.html', pizzaList=pizzaList)

@app.route("/customerInput", methods = ["POST", "GET"])
def customerInput(name=None):
    if request.method == "POST":
        conn = pymssql.connect(server='callapizza.database.windows.net:1433', user='SanDiegoAdmin', password='Tiftpasdsu1', database='callapizza')
        cursor = conn.cursor()

        customerInsertQuery = """INSERT INTO customers (customerLastName, customerFirstName, address, zipCode, city, phoneNumber, addressComments, email) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """

        customerInputRecord = (request.form.get("customerLastName"), request.form.get("customerFirstName"),
        request.form.get("address"), request.form.get("zipCode"), request.form.get("city"), request.form.get("phoneNumber"),
        request.form.get("addressComments"), request.form.get("email"))

        print(customerInputRecord, file=sys.stderr)

        cursor.execute(customerInsertQuery, customerInputRecord)
        conn.commit()

        customerQuery = """Select customerID from customers where customerLastName = %s and customerFirstName = %s"""
        customerInput = (request.form.get("customerLastName"), request.form.get("customerFirstName"))
        cursor.execute(customerQuery, customerInput)
        customerID = cursor.fetchone()
        print(customerID[0], file=sys.stderr)
        session['customerID'] = customerID[0]

        conn.close()
        return redirect(url_for("order", none=None))
    
    return render_template('customerInput.html', name=name)

@app.route("/<firstName>")
def success(firstName):
    return render_template('success.html', value=firstName)
