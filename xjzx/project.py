from flask_script import Manager

from config import DevelopConfig
from app import create_app

app =create_app(DevelopConfig)

manager =Manager(app)

from models import db

db.init_app(app)

from flask_migrate import Migrate,MigrateCommand
Migrate(app,db)
manager.add_command('db',MigrateCommand)

from super_command import CreateAdminCommand,RegisterUserCommand,LoginCountCommand
manager.add_command('admin',CreateAdminCommand())

manager.add_command('register',RegisterUserCommand())
manager.add_command('login',LoginCountCommand())


if __name__ == '__main__':
    manager.run()
