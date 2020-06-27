from collections import Counter

from flask import Blueprint, jsonify, request
from xpinyin import Pinyin

from ..extensions.OCRandJieba.OCRandJieba import cutWord2, loadStopWords
from ..models import db, sys_image, synonyms, sys_image_jiebaresult, find_user, sys_category, find_images

mod = Blueprint("search", __name__)


@mod.route('/search', methods=['POST'])
def search():
    task = 'search'
    sentence = request.form['sentence']
    openid = request.form['openid']
    # frame_num=request.form['10']
    me = find_user(openid)
    me.log_search(sentence)
    # 存储返回的图片路径
    result = []  # 最终查询结果的id
    # 全字段匹配
    resultFullMatch = db.session.query(sys_image.image_id).filter(
        sys_image.sentence.like("{0}".format(sentence))).all()
    if len(resultFullMatch):
        for datatemp in resultFullMatch:
            result.append(datatemp[0])
    # 类匹配结果
    categoryResult = []
    categoryPart = []
    categoryMatchTemp = db.session.query(sys_image.image_id). \
        join(sys_category). \
        filter(sys_category.category_name.like("%%{0}%%".format(sentence))). \
        all()

    if len(categoryMatchTemp):
        for datatemp in categoryMatchTemp:
            tmp = 0
            if (tmp > 4):
                categoryResult.append(datatemp[0])
            else:
                categoryPart.append(datatemp[0])
            tmp = tmp + 1

    if len(categoryPart):
        for datatemp in categoryPart:
            result.append(datatemp)

    # 分词
    stopWords = loadStopWords()
    wordJiebaList = cutWord2(sentence, stopWords)  # 搜索的句子的分词结果

    # for word in wordJieba:
    #   wordJiebaList.append(word)
    # 加入关键词同义词

    # 同义词查询结果
    wordSy = []

    for word_1 in wordJiebaList:
        wordSyTemp = db.session.query(synonyms.sy).filter(
            synonyms.word == "{0}".format(word_1)).all()
        if len(wordSyTemp):
            for datatemp in wordSyTemp:
                wordSy.append(datatemp[0])
            wordSyTemp = []

    # 关键词转换为拼音-----------------------------------

    wordPinyin = []
    p = Pinyin()
    for word_6 in wordJiebaList:
        wordPinyin.append(p.get_pinyin(word_6, ''))

    # 数据库查询分词结果，最终结果是若干图片id

    sortTemp = []

    for word_2 in wordJiebaList:
        resultJieba = db.session.query(sys_image_jiebaresult.image_id).filter(
            sys_image_jiebaresult.result == "{0}".format(word_2)).all()
        if len(resultJieba):
            for datatemp in resultJieba:
                sortTemp.append(datatemp[0])

    # 取最匹配的100张图片的id以及其匹配的次数，第一行是元组的列表
    sortResult = Counter(sortTemp).most_common(100)
    # 转为列表的列表
    sortResult = [list(i) for i in sortResult]
    for data in sortResult:
        # 查一下有多少个分词
        resultJiebaNum = db.session.query(sys_image.jieba_num).filter(
            sys_image.image_id == "{0}".format(data[0])).all()
        if len(resultJiebaNum):
            for datatemp in resultJiebaNum:
                if (datatemp[0]) == 0:
                    data[1] = 0
                else:
                    # 现在date[1]表示匹配上的多少分词与这个图所有分词数的比值，这是个权重
                    data[1] = (data[1]) / (datatemp[0])
    sortResult = sorted(sortResult, key=lambda val: val[1], reverse=True)

    for data in sortResult:
        result.append(data[0])

    sortTemp = []

    for word_3 in wordSy:
        resultSy = db.session.query(sys_image_jiebaresult.image_id).filter(
            sys_image_jiebaresult.result == "{0}".format(word_3)).all()
        if len(resultSy):
            for datatemp in resultSy:
                sortTemp.append(datatemp[0])

    sortResult = Counter(sortTemp).most_common(100)
    sortResult = [list(i) for i in sortResult]
    for data in sortResult:
        resultJiebaNum = db.session.query(sys_image.jieba_num).filter(
            sys_image.image_id == "{0}".format(data[0])).all()
        if len(resultJiebaNum):
            for datatemp in resultJiebaNum:
                if (datatemp[0]) == 0:
                    data[1] = 0
                else:
                    data[1] = data[1] / datatemp[0]
    sortResult = sorted(sortResult, key=lambda val: val[1], reverse=True)

    for data in sortResult:
        result.append(data[0])

    sortTemp = []

    # for (word_4, word_5) in zip(wordPinyin, wordJiebaList):
    #     resultPinyin = [i for i in db.engine.execute(
    #         "SELECT  image_id  FROM  sys_image_jiebaresult   WHERE   pinyin like '{0}' AND result<> '{1}' ".format(
    #             word_4,
    #             word_5))]
    for (word_4, word_5) in zip(wordPinyin, wordJiebaList):
        for (word_4, word_5) in zip(wordPinyin, wordJiebaList):
            resultPinyin = db.session.query(sys_image_jiebaresult.image_id). \
                filter(sys_image_jiebaresult.pinyin.like('{0}'.format(word_4))). \
                filter(sys_image_jiebaresult.result != '{0}'.format((word_5))). \
                all()

        # (jiebaresult.imageid).filter(
        # jiebaresult.pinyin_result == "%%{0}%%".format(word_4), jiebaresult.result != "{0}".format(word_5)).all()
        # results=db.engine.execute("select * from image")
        # for result in  results:
        #   print(result[0],result[1])
        # 需要修改
        if len(resultPinyin):
            for datatemp in resultPinyin:
                sortTemp.append(datatemp[0])
            resultPinyin = []

    sortResult = Counter(sortTemp).most_common(100)
    sortResult = [list(i) for i in sortResult]
    for data in sortResult:
        resultJiebaNum = db.session.query(sys_image.jieba_num).filter(
            sys_image.image_id == "{0}".format(data[0])).all()
        if len(resultJiebaNum):
            for datatemp in resultJiebaNum:
                if (datatemp[0]) == 0:
                    data[1] = 0
                else:
                    data[1] = data[1] / datatemp[0]
    sortResult = sorted(sortResult, key=lambda val: val[1], reverse=True)
    for data in sortResult:
        result.append(data[0])

    for datatemp in categoryResult:
        result.append(datatemp)

    print(result)
    images = find_images(result)
    # print(images)
    # image_ids = list(set(result))
    # image_ids.sort(key=result.index)
    #
    # current_app.logger.info(image_ids)
    # json_result=[]
    # results = db.session.query(sys_image).filter(sys_image.image_id.in_(image_ids),).all()
    # results = sorted(results, key=lambda o: image_ids.index(o.image_id))
    # print(results)
    # for image_id in ids:
    #     image=sys_image.query.get(image_id)
    #     if image.search_able:
    #         json_result.append(dict(image_id=image.image_id,path=image.path,
    #                             category_name=image.sys_category_name,sentence=image.sentence,like=me.if_like(image_id)))
    data = [dict(image_id=image.image_id, path=image.path,
                 category_name=image.sys_category_name, sentence=image.sentence, like=me.if_like(image.image_id))
            for image in images if image.search_able]
    if len(images) == 0:
        return jsonify(success=1, msg="查询成功,没有结果", task=task, data=data)
    return jsonify(success=1, msg="查询成功", task=task, data=data)
