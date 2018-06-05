from flask import Blueprint, make_response, jsonify, redirect, render_template
from utills.captcha.captcha import captcha
from flask import request, session, current_app
import random
from utills.ytx_sdk.ytx_send import sendTemplateSMS
import re
from models import db, UserInfo, NewsInfo, NewsCategory
import functools
from datetime import datetime

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
    sendTemplateSMS(mobile, {yzm2, 5}, 1)

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
    if int(yzm_sms) != session['sms_yzm']:
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


@user_blueprint.route('/login', methods=['POST'])
def login():
    dict1 = request.form
    mobile = dict1.get('mobile')
    pwd = dict1.get('pwd')

    if not all([mobile, pwd]):
        return jsonify(result=1)
    user = UserInfo.query.filter_by(mobile=mobile).first()

    if user:
        if user.ckeck_pwd(pwd):
            session['user_id'] = user.id
            return jsonify(result=4, avatar=user.avatar_url, nick_name=user.nick_name)

        else:
            return jsonify(result=3)
    else:
        return jsonify(result=2)


@user_blueprint.route('/logout', methods=['POST'])
def logout():
    del session['user_id']
    return jsonify(result=1)


def login_required(view_fun):
    @functools.wraps(view_fun)
    def fun2(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return view_fun(*args, **kwargs)

    return fun2


@user_blueprint.route('/')
@login_required
def index():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    return render_template('news/user.html', user=user)


@user_blueprint.route('/base', methods=['GET', 'POST'])
@login_required
def base():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    if request.method == 'GET':
        return render_template('news/user_base_info.html', user=user)
    elif request.method == 'POST':
        dict1 = request.form
        signature = dict1.get('signature')
        nick_name = dict1.get('nick_name')
        gender = dict1.get('gender')
        if gender == 'True':
            gender = True
        else:
            gender = False

        user.signature = signature
        user.nick_name = nick_name
        user.gender = bool(gender)

        db.session.commit()

        return jsonify(result=1)


@user_blueprint.route('/pic', methods=['GET', 'POST'])
@login_required
def pic():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    if request.method == 'GET':
        return render_template('news/user_pic_info.html', user=user)
    elif request.method == 'POST':
        avatar = request.files.get('avatar')

        # if avatar == None:
        #     return jsonify(result=1, avatar=user.avatar_url)

        # 上传到七牛云
        from utills.qiniu_xjzx import upload_pic
        filename = upload_pic(avatar)
        user.avatar = filename
        db.session.commit()

        return jsonify(result=1, avatar=user.avatar_url)


@user_blueprint.route('/follow')
@login_required
def follow():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    page = int(request.args.get('page', '1'))
    pagination = user.follow_user.paginate(page, 1, False)
    user_list = pagination.items
    total_page = pagination.pages
    return render_template(
        'news/user_follow.html',
        user_list=user_list,
        total_page=total_page,
        page=page
    )


@user_blueprint.route('/pwd', methods=['GET', 'POST'])
@login_required
def pwd():
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    if request.method == 'POST':
        dict1 = request.form
        current_pwd = dict1.get('current_pwd')
        new_pwd = dict1.get('new_pwd')
        new_pwd2 = dict1.get('new_pwd2')

        if not re.match(r'[a-zA-Z0-9]{6,20}', new_pwd):
            return render_template(
                'news/user_pass_info.html',
                msg='新密码格式不对'
            )
        if new_pwd != new_pwd2:
            return render_template(
                'news/user_pass_info.html',
                msg='两个新密码不一样'
            )
        user = UserInfo.query.get(session['user_id'])
        if not user.ckeck_pwd(current_pwd):
            return render_template(
                'news/user_pass_info.html',
                msg='当前密码错误'
            )
        user.password = new_pwd
        db.session.commit()
        return render_template(
            'news/user_pass_info.html',
            msg='修改密码成功！'
        )


@user_blueprint.route('/collect')
@login_required
def collect():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    page = int(request.args.get('page', '1'))
    pagination = user.news_collect.order_by(NewsInfo.update_time.desc()).paginate(page, 1, False)
    news_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_collection.html', news_list=news_list, total_page=total_page, page=page)


@user_blueprint.route('/release', methods=['GET', 'POST'])
@login_required
def release():
    category_list = NewsCategory.query.all()
    if request.method == 'GET':
        return render_template(
            'news/user_news_release.html',
            category_list=category_list
        )
    if request.method == 'POST':
        dict1 = request.form
        title = dict1.get('title')
        category_id = int(dict1.get('category'))
        summary = dict1.get('summary')
        content = dict1.get('content')

        news_pic = request.files.get('news_pic')

        if not all([title, category_id, summary, content, news_pic]):
            return render_template(
                'news/user_news_release.html',
                category_list=category_list,
                msg='数据不能为空')
        from utills.qiniu_xjzx import upload_pic

        filename = upload_pic(news_pic)

        news = NewsInfo()
        news.category_id = category_id
        news.pic = filename
        news.title = title
        news.summary = summary
        news.content = content
        news.user_id = session['user_id']

        db.session.add(news)
        db.session.commit()

    return redirect('/user/newslist')

@user_blueprint.route('/newslist')
@login_required
def newslist():
    user_id = session['user_id']
    user =UserInfo.query.get(user_id)
    page =int(request.args.get('page','1'))
    pagination =user.news.order_by(NewsInfo.update_time.desc()).paginate(page,2,False)
    news_list =pagination.items
    total_page =pagination.pages
    return render_template(
        'news/user_news_list.html',
        news_list =news_list,
        page =page,
        total_page =total_page
    )

# @user_blueprint.route('/kkk/<int:news_id>')
# def kkk(news_id):
#     news =NewsInfo.query.get(news_id)
#
#     return news.content


@user_blueprint.route('/release_update/<int:news_id>',methods=['GET','POST'])
@login_required
def release_update(news_id):
    news =NewsInfo.query.get(news_id)
    category_list = NewsCategory.query.all()
    if request.method == 'GET':
        return render_template(
            'news/user_news_update.html',
            news =news,
            category_list =category_list
        )
    elif request.method == 'POST':
        dict1 =request.form
        title =dict1.get('title')
        category_id =int(dict1.get('category'))
        summary =dict1.get('summary')
        content =dict1.get('content')

        news_pic =request.files.get('news_pic')

        if not all([title,category_id,summary,content]):
            return render_template(
                'news/user_news_release.html',
                category_list =category_list,
                msg ='数据不能为空'
            )
        if news_pic:
            from utills.qiniu_xjzx import upload_pic
            filename =upload_pic(news_pic)

        news.category_id=category_id

        if news_pic:
            news.pic =filename

        news.title=title
        news.summary=summary
        news.content=content
        news.user_id=session['user_id']
        news.update_time= datetime.now()
        news.status =1
        db.session.commit()
        return redirect('/user/newslist')














