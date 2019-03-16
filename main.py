from flask import render_template, Flask, redirect

app = Flask(__name__)


@app.route('/start', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['GET'])
def default():
    return redirect('/start')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
