'''
@Author: chivalryq
@Date: 2019-09-17 08:07:14
@Description: file content
'''
from .views import similar
from .views import category
from .views import image
from .views import search
from .views import generate
from .views import upload
from .views import index
from .views import user
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from .settings import REAL_PATH
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)


app.register_blueprint(index.mod)

app.register_blueprint(upload.mod)
app.register_blueprint(generate.mod)
app.register_blueprint(similar.mod)
app.register_blueprint(search.mod)
app.register_blueprint(image.mod,)
app.register_blueprint(category.mod,)
app.register_blueprint(user.mod,)
app.register_blueprint(user.mod, url_prefix='/user')
app.register_blueprint(image.mod, url_prefix='/image')
app.register_blueprint(category.mod, url_prefix='/category')
