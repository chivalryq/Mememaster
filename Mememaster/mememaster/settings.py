'''
@Author: chivalryq
@Date: 2019-09-17 08:06:08
@Description: settings for mememaster project
'''
import os
REAL_PATH = os.path.split(os.path.realpath(__file__))[0]
STATIC_DIR_PATH = r"/root"  # 改了
SECRET_KEY = '123456'
SQLALCHEMY_DATABASE_URI = 'mysql://root:123456qaz123@localhost/meme_db'  # 数据库设置
SQLALCHEMY_TRACK_MODIFICATIONS = True
UPLOAD_FOLDER = os.path.join(STATIC_DIR_PATH, 'pic')
IMAGE_FOLDER = os.path.join(STATIC_DIR_PATH, 'pic')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
JSON_AS_ASCII = False
