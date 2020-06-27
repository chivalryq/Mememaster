from ..extensions.get_similar import get_similar
from flask import Blueprint, request, jsonify
from ..extensions.utils import allowed_file
from random import sample
import string
import os
from ..settings import UPLOAD_FOLDER
import requests
mod = Blueprint("Similar", __name__)
@mod.route('/similar', methods=['POST'])
def similar():
    task = 'get_similar'
    file = request.files['file']
    if file and allowed_file(file.filename.replace('"', '')):
        # content = file.read()
        file.filename = file.filename.replace('"', '')
        filename = ''.join(sample(string.ascii_letters +
                                  string.digits, 4))+file.filename.replace('"', '')
        prefix, suffix = filename.rsplit('.')
        savepath = os.path.join(
            UPLOAD_FOLDER, 'find_similar', filename.replace('"', ''))
        file.save(savepath)  # 这里没存进去
        similar_pics = get_similar(savepath)
        print(similar_pics)
        if len(similar_pics) is not 0:
            simi_local_path = []

            for i in range(len(similar_pics)):
                res = requests.get(similar_pics[i])
                rename_pic = os.path.join(
                    'find_similar', '{}_{}.{}'.format(prefix, i, suffix))
                print(rename_pic)
                with open(os.path.join(UPLOAD_FOLDER, rename_pic), 'wb') as f:
                    f.write(res.content)
                    simi_local_path.append(rename_pic)
            print(simi_local_path)
            if len(simi_local_path) != 0:
                return jsonify(task=task, msg='获取相似图片', similar_pics=simi_local_path)
            else:
                return jsonify(task=task, msg='没有找到相似图片', success=1)
        else:
            return jsonify(task=task, msg='没有找到相似图片', success=1)
    else:
        print(file)
        print(file.filename)
        return jsonify(task=task, msg="上传图片失败", success=0)
