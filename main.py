from flask import Flask,current_app, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
from config import Config,Schema

app = Flask(__name__)
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = Config.SECRET_KEY

# Enter your database connection details below
app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB

#Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/shopbuddy/login', methods=['POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM '+Schema.ACCOUNTS+' WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['acc_id'] = account['acc_id']
            session['username'] = account['username']
            session['usertype'] = account['usertype']
            # Redirect to home page
            msg='Logged In'
            ##return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    print(msg)
    return msg
    ##return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/shopbuddy/logout',methods=['GET','POST'])
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
   # Redirect to login page
    return 'logged out successfully'
  # return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/shopbuddy/register', methods=['POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "phone" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'phone' in request.form:
        # Create variables for easy access
        username = request.form['username']
        fullname= request.form['fullname']
        password = request.form['password']
        phone = request.form['phone']
        pincode = request.form['pincode']
        address = request.form['address']
        usertype = request.form['usertype']
        if usertype=='S':
             store_name=request.form['store_name']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #insert_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM '+Schema.ACCOUNTS+' WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        # elif not re.match(r'[6-9]{2}\d{8}', phone):
        #     msg = 'Invalid phone number!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not phone:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO '+Schema.ACCOUNTS+' VALUES (NULL, %s, %s, %s, %s)', [username, password, phone, usertype])
            mysql.connection.commit()
            cursor.execute('SELECT * FROM ' + Schema.ACCOUNTS + ' WHERE username = %s', [username])
            acc_id = cursor.fetchone()['acc_id']
            if acc_id:
                if usertype=='C':
                    cursor.execute('INSERT INTO '+Schema.CUSTOMER+' VALUES (NULL, %s, %s, %s, %s, %s)', [fullname, pincode,address, phone,acc_id])
                elif usertype=='S' and store_name != '':
                    cursor.execute('INSERT INTO '+Schema.STORE+' VALUES (NULL, %s, %s, %s, %s, %s, %s)', [store_name,fullname, pincode,address, phone,acc_id])
                mysql.connection.commit()
                msg = 'You have successfully registered! '
            else:
                msg='Problem registering user! Please try again'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return msg
    #return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/shopbuddy/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/shopbuddy/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/shopbuddy/product/add', methods=['POST'])
def add_product():
    # Check if user is loggedin as a Store owner
    if 'loggedin' in session and session['usertype']=='S':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT prod_name FROM '+Schema.PRODUCT)
        existing_products = [item['prod_name'] for item in cursor.fetchall()]
        cursor.execute('select S.store_id from store S join accounts A on s.acc_id=a.acc_id where a.username= %s',[session['username']])
        store_id=cursor.fetchone()['store_id']
        if request.method == 'POST' and 'prod_name' in request.form:
            #product to add
            prod_name = request.form.get('prod_name')
            qty_in_stock = request.form.get('qty_in_stock')
            price = request.form.get('price')
            unit_desc = request.form.get('unit_desc','1 unit')
            #If product does not exist
            if prod_name not in existing_products:
                cursor.execute('INSERT INTO ' + Schema.PRODUCT + ' VALUES (NULL, %s, %s)',[prod_name, unit_desc])
                mysql.connection.commit()
                #msg = '%s is successfully added to the products!', prod_name
                cursor.execute('SELECT prod_id FROM ' + Schema.PRODUCT + '  WHERE prod_name=%s', [prod_name])
                prod_id = cursor.fetchone()['prod_id']
                # check if product exist in store
                cursor.execute('SELECT * FROM ' + Schema.STORE_PRODUCT + '  WHERE store_id=%s AND prod_id=%s', [store_id, prod_id])
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO ' + Schema.STORE_PRODUCT + ' VALUES (%s, %s, %s, %s)',
                                   [store_id, prod_id, qty_in_stock, price])
                    mysql.connection.commit()
                    msg = '{} is successfully added to the store'.format(prod_name)
                else:msg = '{} already exist in the store!!'.format(prod_name)
            else: #when product exists
                #fetch product id from the product table
                cursor.execute('SELECT prod_id FROM ' + Schema.PRODUCT + '  WHERE prod_name=%s',[prod_name])
                prod_id =cursor.fetchone()['prod_id']
                #check if product exist in store
                cursor.execute('SELECT * FROM ' + Schema.STORE_PRODUCT + '  WHERE store_id=%s AND prod_id=%s', [store_id,prod_id])
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO ' + Schema.STORE_PRODUCT + ' VALUES (%s, %s, %s, %s)', [store_id, prod_id, qty_in_stock, price])
                    mysql.connection.commit()
                    msg = '{} is successfully added to the store!'.format(prod_name)
                else:msg= 'Product {} already exist in the store!'.format(prod_name)
        else:msg = 'Please fill out the form!'
    else:msg='Only a logged in store owner can add the products!'
    return msg

@app.route('/shopbuddy/product/delete', methods=['GET', 'POST'])
def delete_product():
    if 'loggedin' in session and session['usertype']=='S':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        store_id=cursor.execute('select S.store_id from '+Schema.STORE+' S join '+Schema.ACCOUNTS+' A on s.acc_id=a.acc_id where a.username= %s',[session['username']])
        if request.method == 'POST' and 'prod_name' in request.form:
            #check if product exists
            prod_name = request.form['prod_name']
            if cursor.execute('Select * from ' + Schema.PRODUCT + ' WHERE prod_name=%s',[prod_name])>0:
                prod_id =cursor.fetchone()['prod_id']
                #Check if product exists in store
                product_in_store = cursor.execute('Select * from ' + Schema.STORE_PRODUCT + ' WHERE prod_id=%s and store_id=%s',[prod_id,store_id])
                if product_in_store>0:
                    cursor.execute('DELETE FROM '+Schema.STORE_PRODUCT+' WHERE prod_id=%s and store_id=%s',[prod_id,store_id])
                    mysql.connection.commit()
                    msg = '{} succesfully removed from the store'.format(prod_name)
                else:msg='Cannot Remove! as {} is not available in the store!'.format(prod_name)
            else: msg='{} does not exist in Products'.format(prod_name)
        else:msg = 'Please fill out the form!'
    else:msg = 'Only a logged in store owner can add the products!'
    return msg

@app.route('/shopbuddy/product/update', methods=['POST'])
def update_product():
    if 'loggedin' in session and session['usertype']=='S':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        store_id=cursor.execute('select S.store_id from '+Schema.STORE+' S join '+Schema.ACCOUNTS+' A on s.acc_id=a.acc_id where a.username= %s',[session['username']])
        if request.method == 'POST' and 'prod_name' in request.form:
            #check if product exists
            prod_name = request.form['prod_name']
            qty_in_stock = request.form.get('qty_in_stock')
            price = request.form.get('price')

            if cursor.execute('Select * from ' + Schema.PRODUCT + ' WHERE prod_name=%s',[prod_name]) >0:
                prod_id =cursor.fetchone()['prod_id']
                #Check if product exists in store
                product_in_store = cursor.execute('Select * from ' + Schema.STORE_PRODUCT + ' WHERE prod_id=%s and store_id=%s',[prod_id,store_id])
                if product_in_store>0:
                    if qty_in_stock and price:
                        cursor.execute('UPDATE '+Schema.STORE_PRODUCT+' SET qty_in_stock = %s , price = %s  WHERE prod_id=%s and store_id=%s',[qty_in_stock,price,prod_id,store_id])
                        msg = '{} quantity is succesfully updated to {} and price is succesfully updated to Rs. {} in the store'.format(prod_name,qty_in_stock,price)
                    elif qty_in_stock:
                        cursor.execute(
                            'UPDATE ' + Schema.STORE_PRODUCT + ' SET qty_in_stock =%s  WHERE prod_id=%s and store_id=%s',
                            [qty_in_stock,prod_id, store_id])
                        msg = '{} quantity is succesfully updated to {} in the store'.format(
                            prod_name, qty_in_stock)
                    elif price:
                        cursor.execute(
                            'UPDATE ' + Schema.STORE_PRODUCT + ' SET price =%s  WHERE prod_id=%s and store_id=%s',
                            [price,prod_id, store_id])
                        msg = '{} price is succesfully updated to Rs. {} in the store'.format(
                            prod_name, price)
                    mysql.connection.commit()
                else:msg = '{} is not available in the store, please add it before updating'.format(prod_name)
            else:msg='{} does not exist in Products'.format(prod_name)
        else:msg = 'Please fill out the form!'
    else:msg = 'Only a logged in store owner can add the products!'
    return msg

@app.route('/shopbuddy/view/stores', methods=['GET'])
def view_stores():
    if 'loggedin' in session and session['usertype'] == 'C':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #view all the stores in customer's pincode
        cursor.execute('SELECT * FROM store WHERE pincode=(SELECT pincode FROM customer WHERE acc_id=%s)',[session['acc_id']])
        store_dict=cursor.fetchall()
        if store_dict:
            return json.dumps(store_dict)
        else:msg='Sorry, No stores found in your area!'
    else:msg = 'Only a logged in customers can view stores!'
    return msg

@app.route('/shopbuddy/view/products', methods=['GET','POST'])
def view_products_in_store():
    if 'loggedin' in session and session['usertype'] == 'C':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        store_name = request.args.get('store')
        #view all the products for a given store
        cursor.execute('Select p.prod_name,sp.qty_in_stock from product p join store_product sp on p.prod_id=sp.prod_id where sp.store_id=(Select store_id from store where store_name=%s)',[store_name])
        products_in_store_dict=cursor.fetchall()
        if products_in_store_dict:
            return json.dumps(products_in_store_dict)
        else:msg='Sorry, No products found in store!'
    else:msg = 'Only a logged in customers can view products in store!'
    return msg

@app.route('/shopbuddy/order', methods=['GET','POST'])
def place_order():
    if 'loggedin' in session and session['usertype'] == 'C':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        product_list= request.args.getlist('prod_name')
        qty_list=request.args.getlist('qty')
        store_name = request.args.get('store')
        ord_dict = dict(zip(product_list, qty_list))
        bill_amt=0
        store_id=''
        cursor.execute('select MAX(ord_id) as max_id from orders')
        order_id = cursor.fetchone()['max_id']+1
        # for every item in dictionary check if the qty ordered is greater than or equal to qty available
        product_list_query=[]
        update_prod_qty_query=[]
        for product,qty_ordered in ord_dict.items():
            #checking if product and store are valid and fetching qty
            if cursor.execute('select * from store_product sp where prod_id=(Select prod_id from product where prod_name=%s) AND sp.store_id=(Select store_id from store where store_name=%s)',[product,store_name])>0:
                result=cursor.fetchone()
                qty_in_stock=int(result['qty_in_stock'])
                prod_id=result['prod_id']
                store_id=result['store_id']
                price=result['price']
                qty_ordered=int(qty_ordered)
                if qty_ordered>=0 and qty_in_stock-qty_ordered>=0:
                    order_item=(order_id,prod_id,qty_ordered)
                    qty_update=(qty_in_stock-qty_ordered, prod_id, store_id)
                    update_prod_qty_query.append(qty_update)
                    product_list_query.append(order_item)
                    bill_amt+=int(qty_ordered)*price
                else:
                    msg= '{} is in limited  quantity, please reduce the quantity in your order and place the order again'.format(product)
                    return msg
            else:
                msg= 'Store/Product is not valid!'
                return msg
        cursor.execute('select C.cust_id from customer C join accounts A on c.acc_id=a.acc_id where a.username= %s',
                       [session['username']])
        cust_id = cursor.fetchone()['cust_id']
        if cursor.execute('INSERT into orders VALUES (NULL,%s, %s, %s)', [cust_id, store_id, bill_amt])>0:
            mysql.connection.commit()
            if cursor.executemany('INSERT into orders_product VALUES (%s,%s, %s)' ,product_list_query)>0:
                if cursor.executemany('UPDATE ' + Schema.STORE_PRODUCT + ' SET qty_in_stock =%s  WHERE prod_id=%s and store_id=%s',update_prod_qty_query)>0:
                    mysql.connection.commit()
                else:msg='Error updating product quantities!'
            else:msg='Unable to place order for all items, please try again after sometime'
        else: msg='Unable to place order, please try again after sometime'
        msg='Order Succefully Placed!!'
    else:
        msg = 'Only a logged in customers can view products in store!'
    return msg

if __name__=="__main__":
    print ("Running")
    app.run()
