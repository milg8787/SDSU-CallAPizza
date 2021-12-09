from itertools import count
from os import SEEK_CUR
import os
import re
from types import MethodType
from flask import Flask, render_template, url_for, request, redirect, session

import uuid, sys, datetime

from werkzeug.wrappers import response
from customerTO import customerTO

import pymssql
# import pyodbc

app = Flask(__name__)
app.secret_key = os.urandom(32)

orderList = []
cartList = []

@app.route("/")
def main(name=None):
    return render_template('main.html', name=name)

@app.route("/products")
def products(name=None):
    return render_template('products.html', name=name)



@app.route("/customerInput", methods = ["POST", "GET"])
def customerInput(name=None):

    if session.get('customerID') != None:
        return redirect(url_for("order", none=None))

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

        if request.form['delivery'] == "yes":
            isDelivery = 1
        else:
            isDelivery = 0

        orderInsert = """INSERT INTO orders (customerID, orderDate, orderStatus, delivery) 
                            VALUES (%s, %s, %s, %s) """
        orderInsertRecord = (customerID[0], datetime.datetime.now(), 0, isDelivery)
        cursor.execute(orderInsert, orderInsertRecord)
        conn.commit()

        orderQuery = """Select orderID from orders where customerID = %s order by orderDate desc"""
        orderInput = (session['customerID'])
        cursor.execute(orderQuery, orderInput)
        orderID = cursor.fetchone()
        session['orderID'] = orderID[0]


        conn.close()
        return redirect(url_for("order", none=None))
    
    return render_template('customerInput.html', name=name)

@app.route("/order", methods = ["POST", "GET"])
def order(name=None):
    conn = connectToDatabase()
    cursor = conn.cursor()

    pizzaList = []
    
    cursor.execute("Select * from products")
    products = cursor.fetchall()
        
    for item in products:
        tempList = [item[0], item[1], item[2], item[3]]
        pizzaList.append(tempList)

    if request.method == "POST":

        if request.form['addToCart'] == 'Add to cart':
            additionalItemList = [request.form.get("checkBoxSalami"), request.form.get("checkBoxHam"), request.form.get("checkBoxPepperoni"), 
            request.form.get("checkBoxJalapenos"), request.form.get("checkBoxBlackOlives"), request.form.get("checkBoxRedOnions")]

            price = float(request.form.get("basicPrice"))

            if price is not None:
                if request.form.get("size") == "small":
                    price = (price + 0.5 * additionalItemList.count("on")) * float(request.form.get("quantity")) - 3
                elif request.form.get("size") == "large":
                    price = (price + 0.5 * additionalItemList.count("on")) * float(request.form.get("quantity")) + 3
                else:
                    price = (price + 0.5 * additionalItemList.count("on")) * float(request.form.get("quantity"))
                
            orderList.append([session['orderID'], request.form.get("productID"), request.form.get("productName"), 
            price, request.form.get("size"), request.form.get("quantity"),replaceValue(request.form.get("checkBoxSalami")),
            replaceValue(request.form.get("checkBoxHam")),replaceValue(request.form.get("checkBoxPepperoni")), 
            replaceValue(request.form.get("checkBoxJalapenos")), replaceValue(request.form.get("checkBoxBlackOlives")),
            replaceValue(request.form.get("checkBoxRedOnions"))])
        
        
    conn.close()
    return render_template('order.html', pizzaList=pizzaList)




@app.route("/cart", methods = ["POST", "GET"])
def cart(name=None):
    cartList = []
    
    price = 0.0
    for count, item in enumerate(orderList):
        addtionalItem = ""    
        dict = {'Salami': item[6], 'Ham': item[7], 'Pepperoni': item[8], 'Jalapenos': item[9], 'BlackOlives': item[10], 'RedOnions': item[11]} 
    
        if dict['Salami'] == 1:
            addtionalItem = addtionalItem + 'Salami, '
        if dict['Ham'] == 1:
            addtionalItem = addtionalItem + 'Ham, '
        if dict['Pepperoni'] == 1:
            addtionalItem = addtionalItem + 'Pepperoni, '
        if dict['Jalapenos'] == 1:
            addtionalItem = addtionalItem + 'Jalapenos, '
        if dict['BlackOlives'] == 1:
            addtionalItem = addtionalItem + 'Black olives, '
        if dict['RedOnions'] == 1:
            addtionalItem = addtionalItem + 'Red onions, '
        
        if len(addtionalItem) > 1:            
            addtionalItem = addtionalItem.rstrip(", ")

        cartList.append([count, item[2], item[4], item[5], addtionalItem, item[3]])
        price = price + item[3]
    

    if request.method == "POST":
        conn = connectToDatabase()
        cursor = conn.cursor()
        for item in orderList:
            orderDetailsQuery = """INSERT INTO orderDetails (orderID, productID, price, [size], quantity, salami, ham, pepperoni, jalapenos, blackOlives, redOnions) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            orderDetailsInput = (item[0], item[1], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11])
            cursor.execute(orderDetailsQuery, orderDetailsInput)
        conn.commit()

        conn.close()
        return redirect(url_for("payment", none=None))

    return render_template('cart.html', orderList=cartList, price=price)


@app.route("/deleteItem/<int:id>", methods = ["GET"])
def deleteItem(id):
    del orderList[id]
    return redirect(url_for("cart", none=None))
    

@app.route("/payment", methods = ["POST", "GET"])
def payment(name=None):
    if request.method == "POST":
        return redirect(url_for("success", none=None))
    #Need to call success.html when button is pushed
    return render_template('payment.html', name=name)


@app.route("/success",methods = ["POST", "GET"])
def success(name=None):
    firstName = session['firstName']
    orderList = []
    session.clear()
    return render_template('success.html', value=firstName)



def replaceValue(value):
    if value == "on":
        return 1
    else:
        return 0
    
## Use this as mac OS
def connectToDatabase():
    conn = pymssql.connect(server='callapizza.database.windows.net:1433',
    user='SanDiegoAdmin', 
    password='Tiftpasdsu1', 
    database='callapizza')
    return conn


# ## Use this as windows and linux
# def connectToDatabase():
#     conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};'
#     'SERVER=tcp:callapizza.database.windows.net,1433;'
#     'DATABASE=CallAPizza;Uid=SanDiegoAdmin;'
#     'PWD=Tiftpasdsu1;'
#     'ENCRYPT=yes;TrustServerCertificate=no;'
#     'Connection Timeout=30;')
#     return conn
