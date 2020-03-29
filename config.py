class Config(object):
    # Enter your database connection details below
    MYSQL_HOST = 'abhibansal.mysql.pythonanywhere-services.com'
    MYSQL_USER = 'abhibansal'
    MYSQL_PASSWORD = 'mysql@2019'
    MYSQL_DB = 'abhibansal$shopbuddy_db'
    SECRET_KEY = 'c0r0na-c0v!D-19'


class Schema(object):
    # Enter your database connection details below
    ACCOUNTS = 'Accounts'
    STORE = 'Store'
    CUSTOMER = 'Customer'
    PRODUCT = 'Product'
    ORDER = 'Order'
    STORE_PRODUCT = 'Store_Product'
    ORDER_PRODUCT = 'Order_Product'
    PAYMENT = 'Payment'

