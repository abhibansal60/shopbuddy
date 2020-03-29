class Config(object):
    # Enter your database connection details below
    MYSQL_HOST = 'abhibansal.mysql.pythonanywhere-services.com'
    MYSQL_USER = 'abhibansal'
    MYSQL_PASSWORD = 'mysql@2019'
    MYSQL_DB = 'abhibansal$shopbuddy_db'
    SECRET_KEY = 'c0r0na-c0v!D-19'


class Schema(object):
    # Enter your database connection details below
    ACCOUNTS = 'accounts'
    STORE = 'store'
    CUSTOMER = 'customer'
    PRODUCT = 'product'
    ORDER = 'order'
    STORE_PRODUCT = 'store_product'
    ORDER_PRODUCT = 'order_product'
    PAYMENT = 'payment'

