from ..settings import ALLOWED_EXTENSIONS,UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def is_gif(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'gif'