from ..mememaster import db
from datetime import datetime
from werkzeug.utils import cached_property

upload_image = db.Table(
    "upload_image",
    db.Column("image_id", db.Integer, db.ForeignKey(
        'sys_image.image_id'), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id"), ),
    db.Column("upload_time", db.DateTime, default=datetime.now(), )
)


class synonyms(db.Model):  # 与原库相同只需要迁移
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255))
    sy = db.Column(db.String(255))


class user_link(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    my_user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), primary_key=True)
    friend_user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), primary_key=True)


class sys_image(db.Model):
    image_id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255))
    sentence = db.Column(db.String(255))
    jieba_num = db.Column(db.Integer)
    search_able = db.Column(db.Integer, default=1)
    category_id = db.Column(
        db.Integer, db.ForeignKey('sys_category.category_id'))

    sys_category = db.relationship("sys_category", backref="sys_images")

    @property
    def sys_category_name(self):
        return self.sys_category.category_name

    def to_dict(self):
        return dict(imgage_id=self.image_id, path=self.path, sys_category_id=self.category_id,
                    sys_category_name=self.sys_category_name, sentence=self.sentence, search_able=self.search_able)

    def __repr__(self):
        return str(self.to_dict())


class sys_category(db.Model):  # 差俩字段
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255))
    template_path = db.Column(db.String(255))
    jieba_num = db.Column(db.Integer)  # 这里还没填

    def __repr__(self):
        return "{0} {1}".format(self.category_id, self.category_name)


class sys_template_result(db.Model):  # 如果把智能合成去掉，这里可以不用管
    r_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey('sys_category.category_id'))
    template_result = db.Column(db.String(255))  # 仅用于生成图片，可以先不用管
    num = db.Column(db.Integer)

    # TODO 这里backref可能有问题 可能是sys_temsys_template_results
    sys_category = db.relationship(
        "sys_category", backref="sys_template_results")


class sys_image_jiebaresult(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey(
        'sys_image.image_id'))  # 对应的系统图片的主键
    result = db.Column(db.String(255))
    pinyin = db.Column(db.String(255))
    num = db.Column(db.Integer)  # 没用到

    sys_image = db.relationship("sys_image", backref="sys_jiebaresults")  # 关系


class user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(255))
    nickname = db.Column(db.String(255))
    pic_url = db.Column(db.String(255))
    register_time = db.Column(db.DateTime, default=datetime.now())
    last_login_time = db.Column(db.DateTime, default=datetime.now())
    upload_images = db.relationship(
        "sys_image", secondary=upload_image, backref=db.backref('uploader', uselist=False))

    def __repr__(self):
        return "{0} {1} {2} {3} ".format(self.user_id, self.nickname, self.openid, self.last_login_time)

    @cached_property
    def images_num(self):
        return len(self.user_images)

    def record_last_login(self):
        self.last_login_time = datetime.now()
        # print(self.user_id,self.last_login_time)
        db.session.commit()

    def like(self, sys_image):
        record = user_image(user_id=self.user_id, image_id=sys_image.image_id)
        record.user_image_sentence = user_image_sentence(
            sentence=sys_image.sentence, jieba_num=sys_image.jieba_num)
        record.user_image_label = user_image_label(
            label_name=sys_image.sys_category_name)
        record.uis_jiebaresults = [
            uis_jiebaresult(result=jiebaresult.result,
                            pinyin=jiebaresult.pinyin, num=jiebaresult.num)
            for jiebaresult in sys_image.sys_jiebaresults]
        db.session.add(record)
        db.session.commit()

    def unlike(self, image):
        records = user_image.query.filter_by(
            user_id=self.user_id, image_id=image.image_id).all()
        [db.session.delete(record) for record in records]
        db.session.commit()

    def if_like(self, image_id):
        if user_image.query.filter_by(image_id=image_id, user_id=self.user_id).first():
            return True
        else:
            return False

    def find_image_record(self, image_id):
        user_image_record = user_image.query.filter_by(
            user_id=self.user_id, image_id=image_id).first()
        return user_image_record

    def log_search(self, sentence):
        self.search_historys.append(search_history(sentence=sentence))
        db.session.commit()

# 这个库可以暂时不恢复


class user_image(db.Model):
    ui_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    image_id = db.Column(db.Integer, db.ForeignKey('sys_image.image_id'))
    like_time = db.Column(db.DateTime, default=datetime.now())
    friend_visible = db.Column(db.Integer, default=1)

    user = db.relationship("user", backref=db.backref(
        "user_images", order_by="desc(user_image.ui_id)"))
    sys_image = db.relationship("sys_image")  #

    @property
    def openid(self):
        return self.user.openid

    @property
    def sentence(self):
        return self.user_image_sentence.sentence

    @property
    def label_name(self):
        return self.user_image_label.label_name

    @property
    def path(self):
        return self.sys_image.path

    # def __repr__(self):
    #     print(self.user_id,self.image_id,self.path,self.label_name,self.sentence)
    def to_dict(self):
        return dict(ui_id=self.ui_id, openid=self.openid, image_id=self.image_id, path=self.path,
                    label_name=self.label_name, sentence=self.sentence)

    def __repr__(self):
        return str(self.to_dict())

# 同上


class user_image_sentence(db.Model):
    ui_id = db.Column(db.Integer, db.ForeignKey(
        "user_image.ui_id"), primary_key=True)
    sentence = db.Column(db.String(255))
    jieba_num = db.Column(db.Integer)
    user_image = db.relationship("user_image",
                                 backref=db.backref("user_image_sentence", uselist=False, cascade="all, delete-orphan"))

# 同上


class uis_jiebaresult(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    ui_id = db.Column(db.Integer, db.ForeignKey('user_image.ui_id'))
    result = db.Column(db.String(255))
    pinyin = db.Column(db.String(255))
    num = db.Column(db.Integer)
    user_image_sentence = db.relationship("user_image",
                                          backref=db.backref("uis_jiebaresults", cascade="all, delete-orphan"))

# 同上


class user_image_label(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    ui_id = db.Column(db.Integer, db.ForeignKey('user_image.ui_id'))
    label_name = db.Column(db.String(255))

    user_image = db.relationship("user_image", backref=db.backref("user_image_label", uselist=False,
                                                                  order_by="desc(user_image_label.r_id)",
                                                                  cascade="all, delete-orphan"))

# 同上


class search_history(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    sentence = db.Column(db.String(255))
    search_time = db.Column(db.DateTime, default=datetime.now())
    user = db.relationship("user", backref="search_historys")


def find_user(openid):
    me = user.query.filter_by(openid=openid).first()
    if (me):
        print(me)
        # me.record_last_login()
    return me


def find_image(image_id):
    image = sys_image.query.get(image_id)
    if (image):
        print(image)
    return image


def find_images(image_ids):
    new_image_ids = list(set(image_ids))
    new_image_ids.sort(key=image_ids.index)

    results = db.session.query(sys_image).filter(
        sys_image.image_id.in_(new_image_ids), ).all()
    results = sorted(results, key=lambda o: new_image_ids.index(o.image_id))
    return results
