from flask import request,render_template,session,redirect
from models import UserInfo,NewsInfo
from flask import Blueprint,g,jsonify
from flask import current_app
from datetime import datetime


admin_blueprint =Blueprint('admin',__name__,url_prefix='/admin')

@admin_blueprint.route('/login',methods=['GET','POST'])
def login():
    if request.method =='GET':
        return render_template('admin/login.html')
    elif request.method=='POST':
        dict1 =request.form
        mobile =dict1.get('username')
        pwd =dict1.get('password')

        if  not all ([mobile,pwd]):
            return render_template(
                'admin/login.html',
                msg='请填写用户和密码'
            )
        user=UserInfo.query.filter_by(isAdmin=True,mobile=mobile).first()
        if user is None:
           return render_template(
               'admin/login.html',
               mobile=mobile,
               pwd=pwd,
               msg='用户名错误'
           )

        if not user.ckeck_pwd(pwd):
            return render_template(
                'admin/login.html',
                mobile=mobile,
                pwd=pwd,
                msg='密码错误'
            )
        session['admin_user_id'] =user.id
        return redirect('/admin/')
@admin_blueprint.route('/logout')
def logout():
    del session['admin_user_id']
    return redirect('/admin/login')



@admin_blueprint.route('/')
def index():
    return render_template('admin/index.html')
@admin_blueprint.before_request
def login_validate():
    if request.path !='/admin/login':
        if 'admin_user_id'not in session:
            return redirect('/admin/login')
        g.user =UserInfo.query.get(session['admin_user_id'])

@admin_blueprint.route('/user_count')
def user_count():
    user_total =UserInfo.query.filter_by(isAdmin=False).count()
    now =datetime.now()
    print('now-1',now)
    now_month =datetime(now.year,now.month,1)
    print(now_month)
    print(now.month)
    user_month =UserInfo.query.filter_by(isAdmin=False).filter(UserInfo.create_time>=now_month) .count()
    now_day = datetime(now.year,now.month,now.day)
    print(now_day)
    user_day =UserInfo.query.filter_by(isAdmin=False).filter(UserInfo.create_time>now_day).count()

    now =datetime.now()
    print('now2',now)

    login_key ='login%d_%d_%d'%(now.year,now.month,now.day)
    time_list =current_app.redis_client.hkeys(login_key)

    time_list =[time.decode() for time in time_list]

    count_list =current_app.redis_client.hvals(login_key)
    count_list=[int(count) for count in count_list]
    return render_template(
        'admin/user_count.html',
        user_total=user_total,
        user_month=user_month,
        user_day=user_day,
        time_list=time_list,
        count_list=count_list
    )


@admin_blueprint.route('/user_list')
def user_list():
    return render_template('admin/user_list.html')

@admin_blueprint.route('/user_list_json')
def user_list_json():
    page= int(request.args.get('page','1'))
    pagination = UserInfo.query.filter_by(isAdmin=False).order_by(UserInfo.id.desc()).paginate(page,9,False)
    user_list1=pagination.items
    total_page =pagination.pages
    user_list2 =[]
    for user in user_list1:
        user_dict={
            'nick_name':user.nick_name,
            'mobile':user.mobile,
            'create_time':user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time':user.update_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        user_list2.append(user_dict)
    return jsonify(user_list=user_list2,total_page=total_page)


@admin_blueprint.route('/news_review')
def news_review():
    return render_template('admin/news_review.html')

@admin_blueprint.route('/news_review_json')
def news_review_json():
    page =int(request.args.get('page',1))
    pagination =NewsInfo.query.filter_by(status=1).order_by(NewsInfo.id.desc()).paginate(page,10,False)
    news_list1= pagination.items
    total_page=pagination.pages
    news_lits2 =[]
    for news in news_list1:
        news_dict ={
            'id':news.id,
            'title':news.title,
            'create_time':news.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        news_lits2.append(news_dict)

    return jsonify(news_list=news_lits2,total_page=total_page)


@admin_blueprint.route('/news_edit')
def news_edit():
    return render_template('admin/news_edit.html')

@admin_blueprint.route('/news_type')
def news_type():
    return render_template('admin/news_type.html')