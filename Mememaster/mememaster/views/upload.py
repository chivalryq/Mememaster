import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from xpinyin import Pinyin

from ..extensions.MemeAi import meme_classify, meme_check, spam_check
from ..extensions.OCRandJieba.OCRandJieba import OCRandJieba
from ..extensions.utils import allowed_file
from ..models import db, sys_image, sys_image_jiebaresult, find_user
from ..settings import UPLOAD_FOLDER

mod = Blueprint("upload", __name__)


def is_gif(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'gif'


@mod.route('/upload_image', methods=['POST'])
def upload_image():
    task = 'upload_image'
    file = request.files['file']
    openid = request.form['openid']
    escape = request.form.get("escape", default=0)
    me = find_user(openid)

    if file and allowed_file(file.filename):
        content = file.read()
        try:  # 检测是否是表情包
            if not is_gif(file.filename) and not escape:
                if_emoji = meme_check(content)
                if not if_emoji:
                    return jsonify(task=task, success=0, msg='图片不是表情包')
        except:
            return jsonify(task=task, success=0, msg='网络不通畅')
        file.seek(0)
        filename = secure_filename(file.filename)
        savepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(savepath)
        # imgage_url = url_for('static', filename='img/{0}'.format(filename), _external=True)
        try:  # gif的特殊处理 图片分类
            if is_gif(file.filename):
                category_id = 1067  # gif tmeplate id
            else:
                category_id = meme_classify(content)
            # current_app.logger.info(template_id)
        except:
            return jsonify(task=task, success=0, msg='图片分类失败')
        # template_name = template.query.get(template_id).template_name

        try:  # 分词 OCR
            tempname, sentence, jieba_result = OCRandJieba(savepath, 2)
        except:
            # current_app.logger.info(e)
            return jsonify(task=task, success=0, msg='图片文字识别失败')
        spam_check_result = 0
        try:  # 检测违规信息
            if len(sentence) != 0:
                spam_check_result = spam_check(sentence)
        except Exception as e:
            # current_app.logger.info(spam_check_result)
            # current_app.logger.info(e)
            return jsonify(task=task, success=0, msg='检测违法违规内容出现错误')

        if spam_check_result == 1:
            return jsonify(task=task, success=0, msg='图片中含违法违规内容，请上传符合相关法律法规的图片')
        if spam_check_result == 2:
            search_able = 0
        if spam_check_result == 0:
            search_able = 1

        # 写入系统信息
        new_img = sys_image(path=filename, category_id=category_id, sentence=sentence, jieba_num=len(
            jieba_result), search_able=search_able)
        db.session.add(new_img)
        db.session.flush()
        p = Pinyin()
        new_img.sys_jiebaresults = [sys_image_jiebaresult(result=result, num=num, pinyin=p.get_pinyin(result, ''))
                                    for result, num in jieba_result.items()]
        db.session.commit()

        new_img.uploader = me
        me.like(new_img)

        return jsonify(task=task, success=1, msg="上传成功", path=filename, category=new_img.sys_category_name, sentence=sentence,
                       search_able=search_able, friend_visible=1)
    else:
        return jsonify(task=task, msg="上传图片失败", success=0)
