from ConstantsNFunctions import *


@APP.route('/start', methods=['GET'])
def index():
    return render_template('index.html')


@APP.route('/', methods=['GET'])
def default():
    return redirect('/start')


@APP.errorhandler(404)
def error_404(error):
    return render_template('not-found.html')


@APP.route('/profile', methods=['GET', 'POST', 'DELETE'])
def profile():
    if request.method == 'GET':
        if session.get('signin'):
            # получили пользователя, отфильтровав базу данных
            user = DB.session.query(User.id, User.experience, User.nickname, User.level, User.email).filter_by(
                nickname=session.get('nickname')).first()
            identification = user[0]
            exp = user[1]
            nickname = user[2]
            level = user[3]
            email = user[4]

            return render_template('profile.html', nickname=nickname, exp=exp, level=level, id=identification)
        else:
            return redirect('/signin')

    elif request.method == 'POST':
        if request.form.get('delete-account'):
            if session['signin'] == 1:
                User.query.filter_by(nickname=session['nickname']).delete()
                DB.session.commit()
            return redirect('/signin')
        elif request.form.get('sign-out'):
            session['signin'] = 0
            session['nickname'] = None
            return redirect('/signin')


@APP.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        if DB.session.query(User.id).filter_by(nickname=nickname, password=password).scalar():
            session['signin'] = 1
            session['nickname'] = nickname
            return redirect('/profile')
        else:
            alert = '''<div class="alert alert-danger text-left mt-md-2 pd-1" role="alert">
                    This user does not exist!
                    </div>'''
            return render_template('signin.html', response=alert)


@APP.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # получили все поля, в которые пользователь ввел какие-либо данные
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        password_submit = request.form.get('password_submit')

        # прописал все условия в разных строчках, чтобы не загромождать код
        conditional_1 = DB.session.query(User.id).filter_by(nickname=nickname).scalar()
        conditional_2 = password != password_submit
        conditional_3 = DB.session.query(User.id).filter_by(email=email).scalar()

        conditionals = []  # записываем все условия в массив строк
        if conditional_1:
            conditionals.append('<li> Такого никнейм уже занят! </li>')
        if conditional_2:
            conditionals.append('<li> Пароли не совпадают! </li>')
        if conditional_3:
            conditionals.append('<li> Почта уже привязана к другому аккаунту! </li>')

        # если что-либо пошло не так, возвращаемся на туже страничку, но уже с вписанной ошибкой
        response = '''
        <div class="alert alert-danger text-left mt-md-5 pd-1" role="alert">
                <ul>
                     {conditionals}
                </ul>
        </div>'''.format(conditionals=' '.join(conditionals))
        if conditionals:
            return render_template('signup.html', response=response)

        user = User(nickname=nickname, email=email, password=password)
        DB.session.add(user)
        DB.session.commit()

        session['nickname'] = nickname
        session['signin'] = 1

        return redirect('/profile')
    elif request.method == 'GET':
        return render_template('signup.html')


if __name__ == '__main__':
    DB.create_all()
    APP.run(port=8080, host='127.0.0.1')
