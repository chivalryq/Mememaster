from flask import Blueprint
from ..settings import UPLOAD_FOLDER

mod = Blueprint("index", __name__)


@mod.route('/', methods=['GET', 'POST'])
def index():
    return ("TEST Page")


@mod.route('/getsetting')
def getsetting():
    return UPLOAD_FOLDER
