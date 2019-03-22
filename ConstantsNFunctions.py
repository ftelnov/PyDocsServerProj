from flask import render_template, Flask, redirect, request, make_response, session, flash, jsonify
from flask_restful import reqparse, Api
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static/users_uploads'  # директория подгрузки изображений пользователей
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # доступные форматы подгрузки

SECRET_KEY = 'anthrone'  # секретка приложения
DATABASE_URI = 'sqlite:///main_database.db'  # Uri бдшки
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
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Api(APP)

# устанавливаем секретку
APP.secret_key = SECRET_KEY

# главная база данных
DB = SQLAlchemy(APP)


# класс пользователя в базе данных
class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)  # уникальный идентификатор пользователя
    nickname = DB.Column(DB.String(120), unique=True, nullable=False)  # имя пользователя
    password = DB.Column(DB.String(120), nullable=False)  # пароль пользователя
    email = DB.Column(DB.String(120), unique=True, nullable=False)  # email пользователя
    level = DB.Column(DB.String(120), default='Turtle')  # текущий уровень пользователя
    experience = DB.Column(DB.Integer, default=0)  # текущее кол-во опыта пользователя
    profile_image = DB.Column(DB.String(120), default='static/img/user/1.jpg')  # путь к аве пользователя


def __repr__(self):
    return '<User id={} nickname={} email={} level={} exp={}>'.format(
        self.id, self.nickname, self.email, self.level, self.experience)


# функция выдачи опыта игроку
def give_exp(nickname, exp):
    # получаем пользователя из базы данных
    user = DB.session.query(User).filter_by(
        nickname=nickname).first()
    # первичный опыт, т.е. который пользователь имеет в данный момент
    pre_experience = user.experience
    # добавляем опыт
    pre_experience += exp
    # проходимся по уровням, ищем подходящий
    for level in LEVELS:
        # если нашли
        if LEVELS[level][0] <= pre_experience <= LEVELS[level][1]:
            # обновляем опыт пользователя
            user.update({'level': level, 'experience': pre_experience})
            # подтверждаем изменения
            DB.session.commit()
            # если нашли, возвращаем True
            return True
    # если же не нашли, возвращаем False
    return False


# функция трансформации пользователя из базы данных в словарь
def user_to_dict(user):
    return {
        user['nickname']: user.nickname,  # никнейм
        user['experience']: user.experience,  # опыт
        user['level']: user.level,  # уровень
        user['id']: user.id,  # персональный идентификатор
        user['email']: user.email  # почта пользователя
    }
