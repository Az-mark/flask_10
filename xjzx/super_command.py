from flask_script.commands import Command
from models import UserInfo,db
from datetime import datetime
import random
from flask import current_app

class CreateAdminCommand(Command):
    def run(self):
        mobile =input('请输入帐号：')
        pwd =input('请输入密码：')
        user_exists = UserInfo.query.filter_by(mobile=mobile).count()
        if user_exists>0:
            print('此帐号已经存在')
            return
        user =UserInfo()
        user.mobile=mobile
        user.password=pwd
        user.isAdmin =True

        db.session.add(user)
        db.session.commit()
        print('管理员创建成功')

class RegisterUserCommand(Command):
    def run(self):
        user_list=[]
        now=datetime.now()
        for i in range(500):
            user=UserInfo()
            user.mobile='A0000'+str(i)
            user.nick_name='mark'+str(i)

            user.create_time=datetime(2018,random.randint(1,6),random.randint(1,28))
            user.update_time=datetime(2018,random.randint(1,6),random.randint(1,28))
            user_list.append(user)
        db.session.add_all(user_list)
        db.session.commit()


class LoginCountCommand(Command):
    def run(self):
        time_list=["08:15","09:15","10:15","11:15","12:15","13:15","14:15","15:15","16:15","17:15","18:15","19:15"]
        login_key='login2018_6_5'
        redis_client=current_app.redis_client
        for time in time_list:
            redis_client.hset(login_key,time,random.randint(50,300))

