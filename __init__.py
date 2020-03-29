from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from config import Config

app = Flask(__name__)
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = Config.SECRET_KEY

# Enter your database connection details below
app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB

