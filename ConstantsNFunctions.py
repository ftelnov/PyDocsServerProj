from flask import render_template, Flask, redirect, request, make_response, session, flash
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = '/users_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

SECRET_KEY = 'anthrone'
DATABASE_URI = 'sqlite:///main_database.db'
TRACK_MODIFICATIONS = 'sqlite:///main_database.db'
SESSION_TYPE = 'filesystem'

# всевозможные уровни игры с минимальным и максимальным кол-вом опыта в них
LEVELS = {
    'Turtle': (0, 100),
    'Lizard': (101, 200),
    'Iguana': (201, 300),
    'Basilisk': (301, 400),
    'Python': (401, 500),
}

APP = Flask(__name__)
# настраиваем конфиги
APP.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = TRACK_MODIFICATIONS
APP.config['SESSION_TYPE'] = SESSION_TYPE
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# устанавливаем секретку
APP.secret_key = SECRET_KEY

# главная база данных
DB = SQLAlchemy(APP)


# класс пользователя в базе данных
class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    nickname = DB.Column(DB.String(120), unique=True, nullable=False)
    password = DB.Column(DB.String(120), nullable=False)
    email = DB.Column(DB.String(120), unique=True, nullable=False)
    level = DB.Column(DB.String(120), default='Turtle')
    experience = DB.Column(DB.Integer, default=0)

    def __repr__(self):
        return '<User id={} nickname={} email={} level={} exp={}>'.format(
            self.id, self.nickname, self.email, self.level, self.experience)


# функция выдачи опыта игроку
def give_exp(nickname, exp):
    pre_experience = DB.session.query(User.experience).filter_by(
        nickname=nickname).scalar()
    pre_experience += exp
    for level in LEVELS:
        if LEVELS[level][0] <= pre_experience <= LEVELS[level][1]:
            DB.session.query.filter_by(nickname=nickname).update({'level': level, 'experience': pre_experience})
            DB.session.commit()
            return True
    return False
