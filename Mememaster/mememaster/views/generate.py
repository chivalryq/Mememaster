
from flask import Blueprint, jsonify, request, current_app

from ..extensions.Generate.generate import generate_with_template
from ..extensions.OCRandJieba.OCRandJieba import cutWord2, loadStopWords
from ..models import db, sys_image, sys_category, sys_template_result
from ..extensions.generate_nokia.nokia import generate_nokia
mod = Blueprint("Generate", __name__)

@mod.route('/nokia',methods=['POST'])
def nokia():
    task='nokia'
    sentence=request.form['sentence']
    data=None
    try:
        path = generate_nokia(sentence)
        if path != 'write fail':
            new_img = sys_image(path=path, sentence='诺基亚有内鬼短信'+sentence, search_able=0, jieba_num=0)
            db.session.add(new_img)
            db.session.flush()
            data=dict(path=path, image_id=new_img.image_id, like=False)
    except Exception as e:
        current_app.logger.error(e)

    if data is None:
        return jsonify(task=task, success=0, msg='生成失败', data=data)
    else:
        db.session.commit()
        return jsonify(task=task, success=1, msg='生成短信图片', data=data)

# TODO 改造为新的生成函数
@mod.route('/generate', methods=['POST'])  # 未完成 #可能已经完成了 #用于主页上搜索完成以后的蓝色条幅的AI智能生成
def generate():
    task = 'Generate'
    sentence = request.form['sentence']
    result = []
    stopWords = loadStopWords()
    wordJiebaList = cutWord2(sentence, stopWords)

    # 数据库查询分词结果
    sortResult = []

    resultJibaCount = len(wordJiebaList)  # 没用到 就print了一下
    print(resultJibaCount)

    for word_2 in wordJiebaList:
        resultJieba = db.session.query(sys_template_result.category_id, sys_template_result.num). \
            filter(sys_template_result.template_result == word_2). \
            all()

        if len(resultJieba):
            sortResult+=resultJieba
            # 存的是类的id和sys_template_result.num，是由分词结果对应的
    print(sortResult)
    if len(sortResult) is 0:
        return jsonify(task=task, success=0, msg='数据库无分词查询结果',data=[])
    #去重函数
    naive_bayes=[]



    for data in sortResult:#去除sortResult中的重复category_id的元素
        mark = 0
        for data2 in naive_bayes:
            if data[0] == data2[0]:
                mark = 1
        if mark == 0:
            naive_bayes.append(data)

    naive_bayes = [list(i) for i in naive_bayes]  # 把里面的元素（原来是元组，不能修改）变成列表
    for data in naive_bayes:
        data[1] = 1

    for data in naive_bayes:
        resultJiebaNum = db.session.query(sys_category.jieba_num).filter(
            sys_category.category_id == data[0]).all()
        isZero = False
        jiebaNum = 1.0
        if len(resultJiebaNum):  # 这里判断一下这个字段查出来是不是null
            jiebaNum=resultJiebaNum[0][0]
            if jiebaNum==0:
                isZero=True
            '''
            resultJiebaNum是一个list，里面就一个元组 元组里面就一个元素就是data为id的模板的分词数 底下这个写法我醉了
            for datatemp in resultJiebaNum:
                jiebaNum = datatemp[0]
                if datatemp[0] == 0:
                    isZero = True
            '''

        if isZero == False:
            for data2 in sortResult:
                if data2[0] == data[0]:
                    data[1] = data2[1] * data[1]
            for i in range(resultJibaCount):
                data[1] = data[1] / jiebaNum
        else:
            data[1] = 0

    naive_bayes = sorted(naive_bayes, key=lambda val: val[1], reverse=True)
    print(naive_bayes)
    cnt = 0
    for data in naive_bayes:  # 最终的结果就是这个贝叶斯数组，data[0]是类别id
        cnt = cnt + 1
        if cnt > 6:
            break
        result.append(data[0])
    #底下就是看看生成的类都是啥名（data是id）
    if len(result) is 0:
        return jsonify(task=task, success=0, msg='经贝叶斯处理过程后无结果',data=[])

    for data in result:
        category_temp = db.session.query(sys_category.category_name). \
            filter(sys_category.category_id == data). \
            all()
        print(category_temp[0])
    print(result)

    template_ids = result
    priority = 1
    data = []
    for template_id in template_ids:
        template = sys_category.query.get(template_id)
        template_path = template.template_path
        current_app.logger.info(template_path)
        try:
            path = generate_with_template(template_path, sentence)
            if path != 'write fail':
                new_img = sys_image(path=path, sentence=sentence, search_able=0, jieba_num=0, category_id=template_id)
                db.session.add(new_img)
                db.session.flush()
                data.append(dict(path=path, image_id=new_img.image_id, like=False, priority=priority))
                priority += 1
        except Exception as e:
            current_app.logger.error(e)
    if len(data) == 0:
        return jsonify(task=task, success=0, msg='生成失败', data=data)
    else:
        db.session.commit()
        return jsonify(task=task, success=1, msg='生成结束', data=data)


