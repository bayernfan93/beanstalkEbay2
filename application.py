from flask import Flask, render_template

application = Flask(__name__)


@application.route('/')
def hello_world():
    return render_template('home.html')

@application.route('/get-items')
def get_items():
    return render_template('get-items.html')

if __name__ == '__main__':
    application.run()
