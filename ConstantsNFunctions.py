from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static/users_uploads'  # директория подгрузки изображений пользователей
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # доступные форматы подгрузки

SECRET_KEY = 'anthrone'  # секретка приложения
DATABASE_URI = 'sqlite:///main_database.db'  # Uri бдшки
TRACK_MODIFICATIONS = 'sqlite:///main_database.db'  # отслеживание изменений
SESSION_TYPE = 'filesystem'  #

HOST = 'pydocs.ru'  # хост коннекта на сервер
PORT = 80  # порт коннекта на сервер

# всевозможные уровни игры с минимальным и максимальным кол-вом опыта в них
LEVELS = {
    'Turtle': (0, 100),
    'Lizard': (101, 200),
    'Viper': (201, 300),
    'Iguana': (401, 500),
    'Triton': (501, 600),
    'Basilisk': (601, 700),
    'Dinosaur': (701, 800),
    'Dragon': (801, 900),
    'Python': (901, 1000),
    'Royal Python': (1001, 1100)
}

# все коды месяцев и их строковые названия
MONTHS = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

STANDARD_IMAGE = 'static/img/user/1.jpg'  # стандартное изображение для профиля пользователя
ADMIN_PASSWORD = 'aethertemplarA1'  # пароль администратора

APP = Flask(__name__)
# настраиваем конфиги
APP.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI  # ссылка на бд
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = TRACK_MODIFICATIONS  # отслеживание изменений
APP.config['SESSION_TYPE'] = SESSION_TYPE  # тип для сеанса
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # директория подгрузки пользовательских изображений
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # максимальная длительность жизни файлов на сервере( для обновления )
Api(APP)  # инициализируем API к приложению

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


# класс статьи
class Article(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)  # уникальный идентификатор статьи
    author = DB.Column(DB.String(120), nullable=False)  # никнейм автора статьи
    title = DB.Column(DB.String(120))  # заголовок статьи
    text = DB.Column(DB.Text)  # текст статьи
    create_day = DB.Column(DB.Integer)  # день создания статьи
    create_month = DB.Column(DB.String(20))  # месяц создания статьи
    create_year = DB.Column(DB.Integer)  # год создания статьи
    article_image = DB.Column(DB.String(120))  # изображение статьи
    profile_image = DB.Column(DB.String(120))  # изображение профиля автора
    read_time = DB.Column(DB.Integer)  # время прочтения статьи
    likes_count = DB.Column(DB.Integer, default=0)  # кол-во лайков статьи


# класс лайков
class Like(DB.Model):
    num = DB.Column(DB.Integer, primary_key=True, autoincrement=True)  # порядковый номер
    peer_id = DB.Column(DB.Integer, nullable=False)  # идентификатор назначения
    author = DB.Column(DB.String(120), nullable=False)  # никнейм автора лайка(отправителя)


# класс комментария
class Comment(DB.Model):
    num = DB.Column(DB.Integer, primary_key=True, autoincrement=True)  # порядковый номер
    peer_id = DB.Column(DB.Integer, nullable=False)  # идентификатор назначения
    author = DB.Column(DB.String(120), nullable=False)  # никнейм автора лайка(отправителя)
    text = DB.Column(DB.Text)  # текст комментария
    create_day = DB.Column(DB.Integer)  # день создания комментария
    create_month = DB.Column(DB.String(20))  # месяц создания комментария
    create_year = DB.Column(DB.Integer)  # год создания комментария


# функция выдачи опыта игроку
def give_exp(nickname, exp):
    # получаем пользователя из базы данных
    user = DB.session.query(User).filter_by(
        nickname=nickname)
    # первичный опыт, т.е. который пользователь имеет в данный момент

    pre_experience = user.first().experience
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
def user_to_dict(users):
    result = []  # результирующий список юзеров
    for user in users:
        # проходимся по юзерам, добавляем их в резалт
        result.append({
            'nickname': user.nickname,  # никнейм
            'experience': user.experience,  # опыт
            'level': user.level,  # уровень
            'id': user.id,  # персональный идентификатор
            'email': user.email  # почта пользователя
        })
    return result


# функция трансформации статьи из базы данных в словарь
def article_to_dict(articles):
    result = []  # результирующий список статей
    for article in articles:
        # проходимся по статьям, добавляем их в резалт
        result.append({
            'id': article.id,
            'author': article.author,
            'likes': article.id,
            'title': article.title,
            'text': article.text,
            'create-day': article.create_day,
            'create-month': article.create_month,
            'create-year': article.create_year,
            'read-time': article.read_time,
            'article-image': article.article_image,
            'profile-image': article.profile_image,
            'likes_count': article.likes_count
        })
    return result


# функция трансформации лайков из базы данных в словарь
def likes_to_dict(likes):
    result = []  # результирующий список лайков
    for like in likes:
        # проходимся по лайкам, добавляем их в резалт
        result.append({'peer_id': like.peer_id, 'author': like.author})
    return result


# функция трансформации комментариев из базы данных в словарь
def comments_to_dict(comments):
    result = []  # результирующий список комментариев
    for comment in comments:
        # проходимся по комментам, добавляем их в результат
        result.append({
            'peer_id': comment.peer_id,
            'author': comment.author,
            'create_day': comment.create_day,
            'create_month': comment.create_month,
            'create_year': comment.create_year,
            'text': comment.text,
        })
    return result


# функция построения запроса по локальному пути
def build_url(url):
    return 'http://' + HOST + url
