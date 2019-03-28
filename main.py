import os
from shutil import copyfileobj

from flask import render_template, redirect, request, session, jsonify
from flask_restful import reqparse
from requests import post
from datetime import datetime

from sqlalchemy import desc

from ConstantsNFunctions import *


# стартовая страничка
@APP.route('/start', methods=['GET'])
def index():
    return render_template('index.html')


# дефолтная страница
@APP.route('/', methods=['GET'])
def default():
    return redirect('/start')


# обработчик 404-ошибки
@APP.errorhandler(404)
def error_404(error):
    return render_template('not-found.html')


# обработчик 500-ошибки
@APP.errorhandler(500)
def error_500(error):
    return render_template('505-error.html')


# обработчик окна профиля пользователя
@APP.route('/profile', methods=['GET', 'POST'])
def profile():
    # обработчик метода get
    if request.method == 'GET':
        # если пользователь залогинен
        if session.get('signin'):
            # получили пользователя, отфильтровав базу данных
            user = DB.session.query(User).filter_by(
                nickname=session.get('nickname')).first()
            # получили все параметры пользователя
            identification = user.id  # id
            exp = user.experience  # опыт
            nickname = user.nickname  # имя
            level = user.level  # уровень
            email = user.email  # почта пользователя
            profile_image = user.profile_image  # изображение профиля пользователя

            min_exp, max_exp = LEVELS[level]  # максимальное и минимальное кол-во опыта текущего уровня пользователя

            # расчитываем опыт и максимальный опыт на основе данных пользователя
            max_exp -= min_exp
            exp -= min_exp
            exp = exp / max_exp * 100

            # отрисовываем окно пользователю
            return render_template('profile.html', nickname=nickname, exp=exp, level=level, id=identification,
                                   image_file=profile_image, exp_point=user.experience)
        else:
            return redirect('/signin')

    # если же метод POST
    elif request.method == 'POST':
        # если была нажата кнопка "Удалить аккаунт/Delete Account"
        if request.form.get('delete-account'):
            # если пользователь залогинен
            if session.get('signin') == 1:
                # получаем пользователя, отфильтровав данные
                user = User.query.filter_by(nickname=session['nickname'])
                # удаляем изображение пользователя из папки
                try:
                    # если уже удалена, пассуем
                    os.remove(user.first().profile_image)
                except Exception as exc:
                    pass
                # удаляем самого пользователя
                user.delete()
                # коммитим изменения
                DB.session.commit()
            # редиректим юзера на страничку входа
            return redirect('/signin')

        # если была нажата кнопка "Выйти/Sign Out"
        elif request.form.get('sign-out'):
            session['signin'] = 0  # помечаем, что не залогинен
            session['nickname'] = None  # удаляем никнейм из настроек браузера
            return redirect('/signin')  # редиректим пользователя на страничку входа

        # если была нажата кнопка "Сохранить изображение/Save Photo"
        elif request.form.get('save-uploaded-image'):
            # если изображения нет в файлах запроса
            if 'image' not in request.files:
                # редиректим на текущую страницу
                return redirect('/profile')

            # получаем файл из запроса
            file = request.files['image']
            # получаем его формат
            extension = file.filename.split('.')[-1]

            # если файл существует и формат разрешен сервером
            if file and extension in ALLOWED_EXTENSIONS:
                # получаем пользователя
                user = DB.session.query(User).filter_by(nickname=session.get('nickname'))
                # получаем расположение изображения пользователя
                folder = APP.config[
                             'UPLOAD_FOLDER'] + '/images/' + user.first().nickname + '-profile-image.' + extension
                # если изображение пользователя не стандартное
                if user.first().profile_image != STANDARD_IMAGE:
                    # удаляем его предидущее изображение
                    os.remove(user.first().profile_image)
                # обновляем изображение пользователя
                user.update({'profile_image': folder})
                # коммитим изменения
                DB.session.commit()

                # сохраняем файл на сервере
                with open(folder, 'wb+') as file_copy:
                    copyfileobj(file, file_copy)
            # остаемся на текущей страничке
            return redirect('/profile')


# топ пользователей
@APP.route('/top', methods=['GET'])
def top():
    users = DB.session.query(User).order_by(desc(User.experience)).limit(20).all()  # отфильтровали список пользователей
    result = []  # результирующий список
    it = 1  # итератор для подсчета
    for user in users:
        temp = '<a href="user/{nickname}"<strong>{it}. </strong> {nickname} - {level}({exp} exp.)<br>'  # промежуточная
        result.append(temp.format(it=it, nickname=user.nickname, level=user.level, exp=user.experience))  # обновляем
        it += 1  # инкрементим
    return render_template('top.html', users=''.join(result))  # отрисовываем


# обработчик входа в приложение
@APP.route('/signin', methods=['POST', 'GET'])
def signin():
    # если GET запрос
    if request.method == 'GET':
        # отрисовываем окно авторизации
        return render_template('signin.html')
    # если же POST запрос
    elif request.method == 'POST':
        nickname = request.form.get('nickname')  # получаем никнейм из формы
        password = request.form.get('password')  # получаем пароль из формы
        # если пользователь есть в базе данных
        if DB.session.query(User.id).filter_by(nickname=nickname, password=password).scalar():
            # авторизовываем его в браузере
            session['signin'] = 1  # флаг коннекта
            session['nickname'] = nickname  # флаг никнейма
            return redirect('/profile')  # редиректим его на окно профиля
        else:
            alert = '''<div class="alert alert-danger text-left mt-md-2 pd-1" role="alert">
                    This user does not exist!
                    </div>'''  # если же пользователя нет, отрисовываем предупреждение
            return render_template('signin.html', response=alert)  # отрисовываем окно входа с предупреждением


# обработчик регистрации
@APP.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # получили все поля, в которые пользователь ввел какие-либо данные
        nickname = request.form.get('nickname')  # имя
        email = request.form.get('email')  # почта
        password = request.form.get('password')  # пароль
        password_submit = request.form.get('password_submit')  # подтверждение пароля

        # прописал все условия в разных строчках, чтобы не загромождать код
        # а существует ли пользователь
        conditional_1 = DB.session.query(User.id).filter_by(nickname=nickname).scalar()
        # пароли совпадают?
        conditional_2 = password != password_submit
        # проверяем, была ли такая почта уже зарегестрирована в базе данных
        conditional_3 = DB.session.query(User.id).filter_by(email=email).scalar()

        conditionals = []  # записываем все условия в массив строк
        # строковые представления условий
        if conditional_1:
            conditionals.append('<li> Такого никнейм уже занят! </li>')  # invalid nickname
        if conditional_2:
            conditionals.append('<li> Пароли не совпадают! </li>')  # invalid password confirmation
        if conditional_3:
            conditionals.append('<li> Почта уже привязана к другому аккаунту! </li>')  # invalid email

        # если что-либо пошло не так, возвращаемся на туже страничку, но уже с вписанной ошибкой
        response = '''
        <div class="alert alert-danger text-left mt-md-5 pd-1" role="alert">
                <ul>
                     {conditionals}
                </ul>
        </div>'''.format(conditionals=' '.join(conditionals))
        # если что-то пошло не так, возвращаемся с уже введенной ошибкой
        if conditionals:
            return render_template('signup.html', response=response)

        # регаем пользователя
        user = User(nickname=nickname, email=email, password=password)
        # добавляем пользователя в бд
        DB.session.add(user)
        # коммитим изменения
        DB.session.commit()

        # логинимся в браузере
        session['nickname'] = nickname  # забиваем имя
        session['signin'] = 1  # флаг коннекта

        # редиректимся на профиль
        return redirect('/profile')
    # если же GET запрос, просто отрисовываем окно регистрации
    elif request.method == 'GET':
        return render_template('signup.html')


# страничка пользователя для гостей
@APP.route('/user/<nickname>', methods=['GET', 'POST'])
def get_user(nickname):
    identification = User.query.filter_by(nickname=nickname).first().id
    if request.method == 'GET':
        # получаем пользователя, отфильтровав базу данных
        user = DB.session.query(User).filter_by(
            nickname=nickname).first()
        # если пользователь не найден, выводим сообщение об ошибке
        if not user:
            return render_template('not-fount.html')
        # получаем опыт пользователя
        exp = user.experience
        # вычисляем опыт для вывода в прогресс-бар
        min_exp, max_exp = LEVELS[user.level]
        max_exp -= min_exp
        exp -= min_exp
        exp = exp / max_exp * 100
        comments = post(build_url('/api/comment/get'), data={'peer_id': identification}).json()
        # отрисовываем, c учетом полученных комментариев
        if type(comments) == dict and comments.get('result'):
            return render_template('user.html', nickname=nickname, exp=exp, level=user.level,
                               image_file=user.profile_image, exp_point=user.experience)
        return render_template('user.html', nickname=nickname, exp=exp, level=user.level,
                               image_file=user.profile_image, exp_point=user.experience, comments=comments)
    elif request.method == 'POST':
        # получаем данные с полей ввода
        text = request.form.get('text')
        # получаем id пользователя
        result = post(build_url('/api/comment/set'), data={'peer_id': identification,
                                                           'text': text,
                                                           'author': session.get('nickname')
                                                           }).json()
        # выдаем опыт за комментарий(5)
        give_exp(session.get('nickname'), 5)
        return redirect('/user/' + nickname)


# страничка статьи
@APP.route('/article/<identification>', methods=['GET', 'POST'])
def get_article(identification):
    # если метод-гет
    if request.method == 'GET':
        # получаем статью фильтром
        article = [DB.session.query(Article).filter_by(id=identification).first()]
        # получаем комментарии
        comments = post(build_url('/api/comment/get'), data={'peer_id': identification}).json()
        # отрисовываем, c учетом полученных комментариев
        if type(comments) == dict and comments.get('result'):
            return render_template('article.html', article=article_to_dict(article)[0])
        return render_template('article.html', article=article_to_dict(article)[0], comments=comments)
    elif request.method == 'POST':
        # получаем данные с полей ввода
        text = request.form.get('text')
        result = post(build_url('/api/comment/set'), data={'peer_id': identification,
                                                           'text': text,
                                                           'author': session.get('nickname')
                                                           }).json()
        # выдаем опыт за комментарий(5)
        give_exp(session.get('nickname'), 5)
        return redirect('/article/' + identification)


# страничка форума
@APP.route('/forum', methods=['GET'])
def forum():
    if not session.get('signin'):
        return redirect('/signin')
    # получаем ответ с собственной апишки
    result = post('http://127.0.0.1:8080/api/article/get', data={'offset': 0, 'count': 1}).json()
    # если не пришло ничего или пришла ошибка, то переходим на форум бещ подгрузки результата
    if type(result) == list:
        # иначе подгружаем и отрисовываем
        return render_template('forum.html', articles=result, login=session.get('nickname'),
                               password=User.query.filter_by(nickname=session.get('nickname')).first().password)
    else:
        return render_template('forum.html')


# страничка создания статьи
@APP.route('/write-article', methods=['GET', 'POST'])
def write_article():
    # если метод-гет
    if request.method == 'GET':
        # если залогинен
        if session.get('signin'):
            # переходим на написание статьи
            return render_template('write-article.html')
        # иначе на страничку входа
        return redirect('/signin')
    # если метод-пост
    elif request.method == 'POST':
        # получаем данные с полей ввода
        title = request.form.get('title')
        text = request.form.get('text')
        # получаем текущее время и дату
        date = datetime.now()
        day, month, year = date.day, MONTHS[date.month][:3], date.year
        # получаем изображение профиля юзера
        profile_image = DB.session.query(User.profile_image).filter_by(nickname=session.get('nickname')).scalar()
        # заводим новую статью
        article = Article(read_time=int(len(text.split(' ')) / 265 + 1), title=title, text=text, create_day=day,
                          create_month=month, create_year=year, author=session.get('nickname'),
                          profile_image=profile_image)
        # выдаем опыт пользователю за статью(30 опыта)
        give_exp(session.get('nickname'), 30)
        # добавляем в базу данных
        DB.session.add(article)
        # коммитим изменения
        DB.session.commit()
        # если изображение было подгружено в файлы
        if 'image' in request.files:
            # получаем файл из запроса
            file = request.files['image']
            # получаем его формат
            extension = file.filename.split('.')[-1]
            folder = APP.config['UPLOAD_FOLDER'] + '/articles/' + str(article.id) + '.' + extension
            # если файл существует и формат разрешен сервером
            if file and extension in ALLOWED_EXTENSIONS:
                with open(folder, 'wb+') as file_copy:
                    copyfileobj(file, file_copy)
                article.article_image = folder
        else:
            # устанавливаем стандартное изображение
            article.article_image = STANDARD_IMAGE
            article.id = int('2000000' + str(article.id))
        # коммитим
        DB.session.commit()
        # переходим на форум
        return redirect('/forum')


# Далее идут REST-обработчики
# обрабатываем получение информации о пользовател(е/ях)
@APP.route('/api/user/get', methods=['POST'])
def get_user_information():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим никнэйм пользователя
    parser.add_argument('nicknames', required=True)
    parser.add_argument('count', required=True)
    args = parser.parse_args()
    # если один из параметров отсутствует, выводим сообщение об ошибках
    if not args.nicknames or not args.count:
        return jsonify({'error': 'Offset or nicknames is empty!'})
    # вытаскиваем информацию о пользователях из базы данных
    users = User.query.filter(User.nickname.in_(args.nicknames.split(';'))).all()
    if not users:
        return jsonify({'error': 'There are no such users!'})
    users = users[:int(args.count)]
    # если ничего не нашли, возвращаем соответствующий код

    # возвращаем json-схему пользователей
    return jsonify(user_to_dict(users))


# обрабатываем получение информации о статьи/статьях
@APP.route('/api/article/get', methods=['POST'])
def get_article_info():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим id статьи и кол-во статей
    parser.add_argument('count', required=True)
    parser.add_argument('offset', required=True)
    args = parser.parse_args()
    # если не были подгружены offset и count
    if not args.count and not args.offset:
        return jsonify({'result': 'Invalid article Count or Offset!'})
    # получаем статьи
    articles = Article.query.filter(Article.id <= args.count + args.offset, Article.id >= args.offset).all()
    if not articles:
        return jsonify({'result': 'There are no such articles!'})
    # по смещению
    return jsonify(article_to_dict(articles))


# обрабатываем получение лайков по идентификатору назначения
@APP.route('/api/like/get', methods=['POST'])
def get_like():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим id назначения
    parser.add_argument('peer_id', required=True)
    args = parser.parse_args()
    # если не был подгружен peer_id
    if not args.peer_id:
        return jsonify({'result': 'Invalid peer_id!'})
    # получаем все лайки по назначению
    likes = Like.query.filter(Like.peer_id.in_(args.peer_id)).all()
    if not likes:
        return jsonify({'result': 'There are no such likes!'})
    # по смещению
    return jsonify(likes_to_dict(likes))


# обрабатываем получение комментариев по идентификатору назначения
@APP.route('/api/comment/get', methods=['POST'])
def get_comment():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим id назначения
    parser.add_argument('peer_id', required=True)
    args = parser.parse_args()
    # если не был подгружен peer_id
    if not args.peer_id:
        return jsonify({'result': 'Invalid peer_id!'})
    # получаем все комментарии по назначению
    comments = Comment.query.filter(Comment.peer_id.in_(args.peer_id)).all()
    if not comments:
        return jsonify({'result': 'There are no such comments!'})
    # по смещению
    return jsonify(comments_to_dict(comments))


# обрабатываем установку лайка по идентификатору назначения
@APP.route('/api/like/set', methods=['POST'])
def set_like():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим id назначения, автора, пароль
    parser.add_argument('peer_id', required=True)
    parser.add_argument('author', required=True)
    args = parser.parse_args()
    if args.author != session.get('nickname'):
        return jsonify({'result': 'Author and session account does not match!'})
    # если не был подгружен peer_id
    if not args.peer_id:
        return jsonify({'result': 'Invalid peer_id!'})
    # если пользователя не существует
    if not args.author or not args.password or not User.query.filter_by(nickname=args.author).first():
        return jsonify({'result': 'Invalid author!'})
    if Like.query.filter_by(peer_id=args.peer_id, author=args.author):
        return jsonify({'result': 'Like already placed!'})
    like = Like(args.peer_id, args.author)
    DB.session.add(like)
    DB.session.commit()
    return jsonify({'result': 'Success'})


# обрабатываем установку комментария по идентификатору назначения
@APP.route('/api/comment/set', methods=['POST'])
def set_comment():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим id назначения, автора, текст комментария
    parser.add_argument('peer_id', required=True)
    parser.add_argument('author', required=True)
    parser.add_argument('text', required=True)
    # парсим
    args = parser.parse_args()
    # если отсутствует один из параметров
    if not args.peer_id or not args.author or not args.text:
        return jsonify({'result': 'One of required param lost!'})
    # если пользователь не существует
    if not User.query.filter_by(nickname=args.author).first():
        return jsonify({'result': 'Invalid author!'})
    # получаем текущую дату
    date = datetime.now()
    # получаем день, месяц, год
    day, month, year = date.day, MONTHS[date.month][:3], date.year
    comment = Comment(peer_id=args.peer_id, author=args.author, text=args.text, create_day=day, create_month=month,
                      create_year=year)
    DB.session.add(comment)
    DB.session.commit()
    return jsonify({'result': 'Success'})


# обрабатываем удаление лайка по идентификатору назначения
@APP.route('/api/like/remove', methods=['POST'])
def remove_like():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим id назначения, автора
    parser.add_argument('peer_id', required=True)
    parser.add_argument('author', required=True)
    args = parser.parse_args()
    if args.author != session.get('nickname'):
        return jsonify({'result': 'Author and session account does not match!'})
    # если не был подгружен peer_id
    if not args.peer_id:
        return jsonify({'result': 'Invalid peer_id!'})
    # если пользователя не существует
    if not args.author or not args.password or not User.query.filter_by(nickname=args.author).first():
        return jsonify({'result': 'Invalid author!'})
    like = Like.query.filter_by(peer_id=args.peer_id, author=args.author)
    if not like:
        return jsonify({'result': 'Like already removed!'})
    like.delete()
    DB.session.commit()
    return jsonify({'result': 'Success'})


if __name__ == '__main__':
    DB.create_all()
    APP.run(port=PORT, host=HOST)
