from os import SEEK_CUR
import re
from flask import Flask, render_template, url_for, request, redirect, session

import uuid, sys, datetime

from werkzeug.wrappers import response
from customerTO import customerTO

#import pymssql
import pyodbc

app = Flask(__name__)
app.secret_key = "CallAPizzaSecret"


@app.route("/")
def main(name=None):
    return render_template('main.html', name=name)

@app.route("/products")
def products(name=None):
    return render_template('products.html', name=name)



@app.route("/customerInput", methods = ["POST", "GET"])
def customerInput(name=None):
    if request.method == "POST":
        conn = connectToDatabase()
        cursor = conn.cursor()

        customerInsertQuery = """INSERT INTO customers (customerLastName, customerFirstName, address, zipCode, city, phoneNumber, addressComments, email) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """

        customerInputRecord = (request.form.get("customerLastName"), request.form.get("customerFirstName"),
        request.form.get("address"), request.form.get("zipCode"), request.form.get("city"), request.form.get("phoneNumber"),
        request.form.get("addressComments"), request.form.get("email"))

        cursor.execute(customerInsertQuery, customerInputRecord)
        conn.commit()

        session['firstName'] = request.form.get("customerFirstName")

        customerQuery = """Select customerID from customers where customerLastName = %s and customerFirstName = %s"""
        customerInput = (request.form.get("customerLastName"), request.form.get("customerFirstName"))
        cursor.execute(customerQuery, customerInput)
        customerID = cursor.fetchone()
        session['customerID'] = customerID[0]


        orderInsert = """INSERT INTO orders (customerID, orderDate, orderStatus, delivery) 
                            VALUES (%s, %s, %s, %s) """
            # Fix delivery with a button in customerInput
        orderInsertRecord = (customerID[0], datetime.datetime.now(), 0, 1)
        cursor.execute(orderInsert, orderInsertRecord)
        conn.commit()

        conn.close()
        return redirect(url_for("order", none=None))
    
    return render_template('customerInput.html', name=name)




@app.route("/order", methods = ["POST", "GET"])
def order(name=None):
    conn = connectToDatabase()
    cursor = conn.cursor()

    orderList = []
    pizzaList = []
    

    cursor.execute("Select * from products")
    products = cursor.fetchall()
        
    for item in products:
        tempList = [item[1], item[2], item[3]]
        pizzaList.append(tempList)

    if request.method == "POST":
        orderList.append(request.form.get)

        if request.form.get("goToCart"):
            print(orderList[0], file=sys.stderr)

            orderDetailsInsert = """INSERT INTO orderDetails (orderID, productID, price, quantity, salami, ham, pepperoni, jalapenos, blackOlives, redOnions)
                            VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        
    ##cursor.execute("Insert into orders")
        
    conn.close()
    return render_template('order.html', pizzaList=pizzaList)




@app.route("/cart")
def cart(name=None):
    #conn, cursor = connectToDatabase())

    #orderDetailsQuery = """Select price, quantiy, salami, ham, pepperoni, jalapenos, blackOlives, redOnions from orderDetails where orderID = %s"""
    #orderDetailsInput = (session['orderID'])
    #cursor.execute(orderDetailsQuery, orderDetailsInput)

    orderItems = [("Pizza Salami", "Medium", "3", "Ham, Salami, Jalapenos, Pepperoni, black olives, red onions", "14.50"), ("Pizza Salami", "Small", "1", "AddtionalItem", "15.00"), 
    ("Pizza Ham", "Large", "2", "AddtionalItem", "13.00")]

    if request.method == "POST":
        return redirect(url_for("success", none=None))


    return render_template('cart.html', orderList=orderItems)



@app.route("/success")
def success(name=None):
    #firstName = session['firstName']
    firstName = "hugo"
    return render_template('success.html', value=firstName)



### Use this as mac OS
# def connectToDatabase():
#     conn = pymssql.connect(server='callapizza.database.windows.net:1433',
#     user='SanDiegoAdmin', 
#     password='Tiftpasdsu1', 
#     database='callapizza')
#     return conn


### Use this as windows and linux
def connectToDatabase():
    conn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};'
    'Server=tcp:callapizza.database.windows.net,1433;'
    'Database=CallAPizza;Uid=SanDiegoAdmin;'
    'Pwd=Tiftpasdsu1;'
    'Encrypt=yes;TrustServerCertificate=no;'
    'Connection Timeout=30;')
    return conn