from flask import Flask, render_template, url_for, request, redirect, session

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
    return render_template('order.html', name=name)

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
