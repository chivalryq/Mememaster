from datetime import datetime
from collections import Counter
from  flask import  Blueprint,jsonify,request,current_app
from ..models import  db,user,user_image,user_link,sys_image,search_history,find_user,uis_jiebaresult,user_image_sentence,user_image_label,synonyms
from ..extensions import wx
from  xpinyin import Pinyin
from ..extensions.OCRandJieba.OCRandJieba import  jiebaPython
from ..extensions.OCRandJieba.OCRandJieba import cutWord2,loadStopWords
mod=Blueprint("user",__name__)


@mod.route('/getopenid', methods=["POST"])
def getopenid():
    task = 'getopenid'
    code = request.form['code']
    try:
        info = wx.getuserinfo(code)
        success=1
        openid = info['openid']
        msg= '用户已注册'

        registered=find_user(openid)
        if not registered:
            db.session.add(user(openid=openid))
            db.session.commit()
            msg= '新用户注册成功'
        return jsonify(task=task,success=success,msg=msg,openid=openid)
    except:
        return jsonify(task=task,success=0,msg="openid获取失败")

@mod.route('/likelst', methods=['POST'])
def likelst():
    task = 'likelst'
    openid = request.form['openid']
    me=find_user(openid)
    me.record_last_login()
    me_user_images=me.user_images

    if not me_user_images :
         return jsonify(task= task, success= 0, msg="无已收藏图片")

    data = [dict(image_id=result.image_id, path=result.path, label_name=result.label_name,
                 sentence=result.sentence,like=True,friend_visible=result.friend_visible ) for result in me_user_images]

    return jsonify(task=task, success= 1, msg= "查询收藏图片成功", data = data)

@mod.route('/getlabels', methods=['POST'])
def getlabels():
    task = 'getlabels'
    openid = request.form['openid']
    me=find_user(openid)
    results=[user_image_record.label_name for user_image_record in me.user_images]
    labels=list(set(results))
    labels.sort(key=results.index)
    print(labels)
    return jsonify(task=task, success= 1, msg= "成功查询标签",labels=labels)

@mod.route('/editlabel', methods=['POST'])
def editlabel():
    task = 'editlabel'
    image_id = request.form['image_id']
    openid = request.form['openid']
    label= request.form['label']
    me=find_user(openid)
    user_image_record = me.find_image_record(image_id)
    user_image_record.user_image_label.label_name = label
    db.session.commit()
    return jsonify(task=task, success= 1, msg="修改标签成功")

@mod.route('/getimages', methods=['POST'])
def getimages():
    task = 'getimages'
    openid = request.form['openid']
    label = request.form['label']

    me=find_user(openid)

    images=[image  for  image in me.user_images if image.label_name==label]

    if not images :
         return jsonify(task= task, success= 0, msg="无已收藏图片")

    data = [dict(image_id=result.image_id, path=result.path, label_name=result.label_name,sentence=result.sentence,like=True)
                    for result in images]
    return jsonify(task=task, success= 1, msg= "查询标签成功", data = data)


@mod.route('/editsentence', methods=['POST'])
def editsentence():
    task = 'editsentence'
    image_id = request.form['image_id']
    openid = request.form['openid']
    sentence= request.form['sentence']
    me=find_user(openid)

    user_image_record = me.find_image_record(image_id)
    print(user_image_record)
    [db.session.delete(record) for record in user_image_record.uis_jiebaresults]
    jieba_result = jiebaPython(sentence)

    user_image_record.user_image_sentence.sentence = sentence
    user_image_record.user_image_sentence.jieba_num=len(jieba_result)

    p = Pinyin()
    user_image_record.uis_jiebaresults = [uis_jiebaresult(result=result, num=num, pinyin=p.get_pinyin(result, ''))
                                for result, num in jieba_result.items()]
    db.session.commit()
    return jsonify(task=task, success= 1, msg="修改图片文字成功")

@mod.route('/editvisible', methods=['POST'])
def editvisible():
    task = 'editvisible'
    image_id = request.form['image_id']
    openid = request.form['openid']
    friend_visible= request.form['friend_visible']
    me=find_user(openid)
    user_image_record = me.find_image_record(image_id)
    user_image_record.friend_visible=friend_visible
    db.session.commit()
    return jsonify(task=task, success= 1, msg="修改可视状态成功")

@mod.route('/editattribute', methods=['POST'])
def editattribute():
    task = 'editattribute'
    image_id = request.form['image_id']
    openid = request.form['openid']
    friend_visible = request.form.get("friend_visible", default=1)
    label = request.form['label']
    sentence = request.form['sentence']

    me = find_user(openid)

    user_image_record = me.find_image_record(image_id)

    user_image_record.friend_visible = friend_visible

    user_image_record.user_image_label.label_name = label
    [db.session.delete(record) for record in user_image_record.uis_jiebaresults]
    jieba_result = jiebaPython(sentence)

    user_image_record.user_image_sentence.sentence = sentence
    user_image_record.user_image_sentence.jieba_num = len(jieba_result)
    p = Pinyin()
    user_image_record.uis_jiebaresults = [uis_jiebaresult(result=result, num=num, pinyin=p.get_pinyin(result, ''))
                                          for result, num in jieba_result.items()]
    db.session.commit()
    return jsonify(task=task, success=1, msg="修改属性成功")

@mod.route('/saveinfo', methods=['POST'])
def saveinfo():
    task = 'saveinfo'
    openid = request.form['openid']
    nickname = request.form['nickname']
    pic_url = request.form['pic_url']
    me=find_user(openid)
    me.nickname=nickname
    me.pic_url=pic_url
    db.session.commit()
    return jsonify(task=task, success=1, msg="成功添加用户信息")

@mod.route('/getinfo', methods=['POST'])
def getinfo():
    task = 'getinfo'
    openid = request.form['openid']
    me=find_user(openid)
    return jsonify(task= task, success=1, nickname= me.nickname, pic_url= me.pic_url, msg= "成功获取用户信息")

@mod.route('/befriend', methods=['POST'])
def befriend():
    task = 'befriend'
    openid1 = request.form['openid1']
    openid2 = request.form['openid2']
    me=find_user(openid1)
    newfriend=find_user(openid2)
    try:
        db.session.add_all([user_link(my_user_id=me.user_id, friend_user_id=newfriend.user_id),
                            user_link(friend_user_id=me.user_id, my_user_id=newfriend.user_id)])
        db.session.commit()
    except:
        return jsonify(task=task, success=0, msg="已经成为好友")
    return jsonify(task= task, success=1, msg="成功添加好友")

@mod.route('/getfriendlist', methods=['POST'])
def getfriendlist():
    task = 'getfriendlist'
    openid = request.form['openid']
    order_by='time'
    order_by ='images_num'
    me=find_user(openid)
    friendlist = [friend.friend_user_id for friend in db.session.query(user_link).filter(user_link.my_user_id == me.user_id).all()]
    print(friendlist)
    results = db.session.query(user).filter(user.user_id.in_(friendlist)).all()
    results = sorted(results, key=lambda o: friendlist.index(o.user_id))
    json_result = [dict(nickname= result.nickname, pic_url=result.pic_url, openid= result.openid,images_num=result.images_num)
                   for result in results if result.nickname]

    if order_by=='images_num':
        json_result=sorted(json_result,key=lambda k: k['images_num'],reverse=True)
        print(json_result)
    return jsonify(task=task, success=1, msg="好友列表", json_result=json_result)

@mod.route('/friendlikelst', methods=['POST'])
def friendlikelst():
    task = "friendlikelst"
    myopenid = request.form['myopenid']
    friendopenid = request.form['friendopenid']
    me = find_user(myopenid)
    friend=find_user(friendopenid)
    images=[image for image in friend.user_images if image.friend_visible]

    if not images:
        return jsonify(task= task, success=0, msg="无已收藏图片")
    json_result = [dict(image_id=result.image_id, path=result.path, label_name=result.label_name, sentence=result.sentence,
                 like=me.if_like(result.image_id))
            for result in images]

    return jsonify(task= task, success= 1, msg="好友图片", json_result= json_result)

@mod.route('/search',methods=['POST'])
def search_private():
    # 存储返回的图片路径
    result = []
    # 用户表情包的标签查询
    task = 'search'
    sentence = request.form['sentence']
    openid = request.form['openid']
    me=find_user(openid)
    me.log_search(sentence)
    user_id=me.user_id


    #标签查询
    image_private_labels_ui_id = db.session.query(user_image.ui_id). \
        join(user_image_label). \
        filter(user_image_label.label_name.like('%%{0}%%'.format(sentence))). \
        filter(user_image.user_id == '{0}'.format(user_id)). \
        all()

    if len(image_private_labels_ui_id):
        for datatemp in image_private_labels_ui_id:
            result.append(datatemp[0])

    #全字段匹配
    resultFullMatch = db.session.query(user_image.ui_id). \
        join(user_image_sentence). \
        filter(user_image_sentence.sentence == '{0}'.format(sentence)). \
        filter(user_image.user_id == '{0}'.format(user_id)). \
        all()

    if len(resultFullMatch):
        for datatemp in resultFullMatch:
            result.append(datatemp[0])

    # 分词
    wordJieba = []
    wordJiebaList = []
    stopWords = loadStopWords()
    wordJiebaList = cutWord2(sentence, stopWords)

    # 同义词查询结果
    wordSy = []

    for word_1 in wordJiebaList:
        wordSyTemp = db.session.query(synonyms.sy).filter(synonyms.word == "{0}".format(word_1)).all()
        if len(wordSyTemp):
            for datatemp in wordSyTemp:
                wordSy.append(datatemp[0])
            wordSyTemp = []
    for wordsy in wordSy:
        wordJiebaList.append(wordsy)

    # 数据库查询分词结果
    sortTemp = []
    sortResult = []

    for word_2 in wordJiebaList:
        resultJieba = db.session.query(user_image.ui_id). \
            join(uis_jiebaresult). \
            filter(user_image.user_id == '{0}'.format(user_id)). \
            filter(uis_jiebaresult.result == '{0}'.format(word_2)). \
            all()
        if len(resultJieba):
            for datatemp in resultJieba:
                sortTemp.append(datatemp[0])
            resultJieba = []

    sortResult = Counter(sortTemp).most_common(100)
    sortResult = [list(i) for i in sortResult]

    for data in sortResult:
        resultJiebaNum = db.session.query(user_image_sentence.jieba_num). \
            filter(uis_jiebaresult.ui_id == user_image_sentence.ui_id). \
            filter(user_image.ui_id == "{0}".format(data[0])).all()
        if len(resultJiebaNum):
            for datatemp in resultJiebaNum:
                if (datatemp[0]) == 0:
                    data[1] = 0
                else:
                    data[1] = (data[1]) / (datatemp[0])
    sortResult = sorted(sortResult, key=lambda val: val[1], reverse=True)

    for data in sortResult:
        result.append(data[0])

    ui_ids = list(set(result))
    ui_ids.sort(key=result.index)

    print("查询到的图片id",ui_ids)
    results = db.session.query(user_image).filter(user_image.ui_id.in_(ui_ids)).all()
    results = sorted(results, key=lambda o: ui_ids.index(o.ui_id))
    print(results)

    if len(results) == 0:
        return jsonify(success=1, msg="查询成功，没有图片", task=task, data=[])

    data = [dict(image_id=result.image_id, path=result.path, label_name=result.label_name,
                 sentence=result.sentence, like=True, friend_visible=result.friend_visible) for result in
            results]
    return jsonify(success=1, msg="查询成功", task=task, data=data)

