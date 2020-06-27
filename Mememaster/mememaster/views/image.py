'''
@Author: chivalryq
@Date: 2019-09-17 08:06:10
@Description: file content
'''
import os
import random

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from ..extensions.inpaint import get_inpaint_image
from ..extensions.utils import allowed_file
from ..models import db, sys_image, find_user, find_image
from ..settings import UPLOAD_FOLDER

mod = Blueprint("image", __name__)


@mod.route('/getrandompic', methods=['GET', 'POST'])
def getrandompic():
    task = 'getrandompic'
    MAXID = db.session.query(db.func.max(sys_image.image_id)).scalar()
    randomset = [random.randint(1, MAXID) for i in range(35)]
    results = db.session.query(sys_image).filter(
        sys_image.image_id.in_(randomset)).limit(35).all()
    json_result = [{'image_id': result.image_id, 'path': result.path, }
                   for result in results]
    return jsonify(task=task, success=1, msg="查询成功", data=json_result)


@mod.route('/getrandompic_notgif', methods=['GET', 'POST'])
def getpic_not_gif():
    task = 'getrandompic_notgif'
    MAXID = db.session.query(db.func.max(sys_image.image_id)).scalar()
    randomset = [random.randint(1, MAXID) for i in range(50)]
    results = db.session.query(sys_image).filter(
        sys_image.image_id.in_(randomset)).limit(50).all()

    json_result = []
    for result in results:
        if result.path.split('.')[-1] != 'gif':
            json_result.append(
                {'image_id': result.image_id, 'path': result.path})

    return jsonify(task=task, success=1, msg="查询成功", data=json_result)


@mod.route('/like', methods=['POST'])
def like():
    task = 'like'
    image_id = request.form['image_id']
    openid = request.form['openid']
    me = find_user(openid)
    image = find_image(image_id)
    try:
        me.like(image)
        return jsonify(task=task, success=1, msg="收藏成功，成功写入收藏记录")
    except:
        return jsonify(task=task, success=1, msg="收藏失败，请勿重复收藏")


@mod.route('/unlike', methods=['POST'])
def unlike():
    task = 'unlike'
    image_id = request.form['image_id']
    openid = request.form['openid']
    me = find_user(openid)
    image = find_image(image_id)
    me.unlike(image)
    return jsonify(task=task, success=1, msg="取消收藏成功，成功写入收藏记录")


@mod.route('/inpaint', methods=['POST'])
def inpaint():
    task = "inpaint"
    file = request.files['file']
    start_x = request.form['start_x']
    start_y = request.form['start_y']
    end_x = request.form['end_x']
    end_y = request.form['end_y']
    # def get_inpaint_image(img_path, start_x, start_y, end_x, end_y, black_thresold=124.0):  # img_path
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        savepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(savepath)
    print(savepath, start_x, start_y, end_x, end_y)
    inpaint_img_path = get_inpaint_image(savepath, int(
        start_x), int(start_y), int(end_x), int(end_y))
    os.remove(savepath)
    file_name = os.path.basename(inpaint_img_path)
    if os.path.exists(str(inpaint_img_path)):
        print(inpaint_img_path)
        # new_inpaint_img = sys_image(path=file_name, category_id=1068, jieba_num=0, search_able=0)
        # db.session.add(new_inpaint_img)
        # db.session.flush()
        # db.session.commit()
        # 1068 去字生成模板
        # print(new_inpaint_img)
    else:
        return jsonify(task=task, success=0, msg="生成失败", error=inpaint_img_path)
    return jsonify(task=task, success=1, msg="成功去除文字", path=file_name)
