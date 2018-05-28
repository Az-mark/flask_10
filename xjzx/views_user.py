from flask import Blueprint, make_response, jsonify
from utills.captcha.captcha import captcha
from flask import request, session, current_app
import random
from utills.ytx_sdk.ytx_send import sendTemplateSMS
import re
from models import db, UserInfo

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/image_yzm')
def image_yzm():
    name, yzm, image = captcha.generate_captcha()
    session['image_yzm'] = yzm
    response = make_response(image)

    response.mimetype = 'image/png'
    return response


@user_blueprint.route('/sms_yzm')
def sms_yzm():
    dict1 = request.args
    mobile = dict1.get('mobile')
    yzm = dict1.get('yzm')

    if yzm.upper() != session['image_yzm'].upper():
        return jsonify(result=1)
    yzm2 = random.randint(1000, 9999)
    session['sms_yzm'] = yzm2
    print('短信码:%s' % yzm2)
    sendTemplateSMS(mobile, {yzm2,5}, 1)

    return jsonify(result=2)


@user_blueprint.route('/register', methods=['POST'])
def register():
    dict1 = request.form
    mobile = dict1.get('mobile')
    yzm_image = dict1.get('yzm_image')
    yzm_sms = dict1.get('yzm_sms')
    pwd = dict1.get('pwd')

    if not all([mobile, yzm_image, yzm_sms, pwd]):
        return jsonify(result=1)
    if yzm_image.upper() != session['image_yzm'].upper():
        return jsonify(result=2)
    if int(yzm_sms)!=session['sms_yzm']:
        return jsonify(result=3)

    if not re.match(r'[a-zA-Z0-9_]{6,20}', pwd):
        return jsonify(result=4)
    mobile_count = UserInfo.query.filter_by(mobile=mobile).count()
    if mobile_count > 0:
        return jsonify(result=5)
    user = UserInfo()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd

    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('用戸注册访问数据库失败')
        return jsonify(result=7)


    return jsonify(result=6)

@user_blueprint.route('/login',methods=['POST'])
def login():
    dict1 =request.form
    mobile =dict1.get('mobile')
    pwd =dict1.get('pwd')

    if not all([mobile,pwd]):
        return jsonify(result=1)
    user =UserInfo.query.filter_by(mobile=mobile).first()

    if user:
        if user.ckeck_pwd(pwd):
            session['user_id'] =user.id
            return jsonify(result=4,avatar=user.avatar,nick_name=user.nick_name)

        else:
            return jsonify(result=3)
    else:
        return jsonify(result=2)

@user_blueprint.route('/logout',methods=['POST'])
def logout():
    del session['user_id']
    return jsonify(result=1)







