'''
@Author: chivalryq
@Date: 2019-09-17 08:06:12
@Description: file content
'''
import random
from flask import Blueprint, jsonify, request
from sqlalchemy.sql import func
from ..models import db, sys_image, sys_category, find_user

mod = Blueprint("category", __name__)


@mod.route('/getrandom', methods=['GET', 'POST'])
def getrandom():
    task = 'getrandom'

    MAXID = db.session.query(db.func.max(sys_category.category_id)).scalar()
    randomset = set([random.randint(1, MAXID)
                     for i in range(30) if i not in [1068]])
 # 1068 去字生成模板
    results = db.session.query(sys_category).filter(
        sys_category.category_id.in_(randomset)).limit(10).all()

    json_result = [dict(category_id=result.category_id,
                        category_name=result.category_name) for result in results]

    print(json_result)
    return jsonify(task=task, success=1, msg="获取随机模板成功", data=json_result)


@mod.route('/getgroup', methods=['POST'])
def getgroup():
    task = 'getgroup by id'
    category_id = request.form['category_id']
    openid = request.form['openid']
    me = find_user(openid)
    category = sys_category.query.get(category_id)

    if not category:
        return jsonify(task=task, success=0, msg="查询失败，数据库无该模板ID", category_id=category_id)

    images = category.sys_images

    print(images)

    group = [dict(image_id=image_record.image_id, path=image_record.path, like=me.if_like(image_record.image_id))
             for image_record in images if image_record.search_able]

    return jsonify(task=task, success=0, msg="查询成功", category_id=category_id, category_name=category.category_name, group=group)
