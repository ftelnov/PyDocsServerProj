import os

from shutil import copyfileobj
from werkzeug.utils import secure_filename
from requests import post

from ConstantsNFunctions import *


# стартовая страничка
@APP.route('/start', methods=['GET'])
def index():
    return render_template('index.html')


# дефолтная страница
@APP.route('/', methods=['GET'])
def default():
    return redirect('/start')


# обработчки 404-ошибки
@APP.errorhandler(404)
def error_404(error):
    return render_template('not-found.html')


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
                                   image_file=profile_image)
        else:
            return redirect('/signin')

    # если же метод POST
    elif request.method == 'POST':
        # если была нажата кнопка "Удалить аккаунт/Delete Account"
        if request.form.get('delete-account'):
            # если пользователь залогинен
            if session['signin'] == 1:
                # получаем пользователя, отфильтровав данные
                user = User.query.filter_by(nickname=session['nickname'])
                # удаляем изображение пользователя из папки
                os.remove(user.profile_image)
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
@APP.route('/user/<nickname>', methods=['GET'])
def get_user(nickname):
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
    # отрисовываем окно пользователя
    return render_template('user.html', nickname=nickname, exp=exp, level=user.level,
                           image_file=user.profile_image)


# страничка статьи
@APP.route('/article/<identification>', methods=['GET', 'POST'])
def get_article(identification):
    # если метод-гет
    if request.method == 'GET':
        # получаем статью фильтром
        article = DB.session.query(Article).filter_by(id=identification).first()
        # отрисовываем
        return render_template('article.html', title=article.title)


# страничка форума
@APP.route('/forum', methods=['GET'])
def forum():
    result = post('/api/user/get', data={'offset': 1, 'count': 1}).json()
    print(result)
    return render_template('forum.html', articles=result)


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
    users = DB.session.query(User).filter(User.nickname.in_(args.nicknames.split(';'))).all()
    if not users:
        return jsonify({'error': 'There are no such users!'})
    users = users[:int(args.count)]
    # если ничего не нашли, возвращаем соответствующий код

    # возвращаем json-схему пользователей
    return jsonify(user_to_dict(users))


# обрабатываем получение информации о статьи/статьях
@APP.route('/api/article/get', methods=['GET'])
def get_article_info():
    # парсим параметры POST-запроса
    parser = reqparse.RequestParser()
    # парсим id статьи и кол-во статей
    parser.add_argument('count', required=True)
    parser.add_argument('offset', required=True)
    args = parser.parse_args()
    # если не были подгружены offset и count
    if not args.count and not args.offset:
        return jsonify({'error': 'Invalid article Count or Offset!'})
    lis = args.ids.split(';')
    # получаем статьи
    articles = DB.session.query(Article).filter(args.offset <= Article.id <= args.count + args.offset).all()
    if not articles:
        return jsonify({'error': 'There are no such articles!'})
    # по смещению
    return jsonify(article_to_dict(articles))


if __name__ == '__main__':
    DB.create_all()
    APP.run(port=PORT, host=HOST)
