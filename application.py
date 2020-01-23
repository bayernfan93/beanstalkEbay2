from flask import Flask, render_template, jsonify, request, session, send_file, redirect, url_for, flash
import boto3
import http.client
import tempfile
import os
import aws_controller
from flask_login import LoginManager, UserMixin


application = Flask(__name__)

UPLOAD_FOLDER = "additionalFiles"
BUCKET = "imgbucketebay2"
bucket = "imgbucketebay2"
image = "iphonexs64.jpeg"
currentUser = "seemannb@hs-pforzheim.de"

# Make sessions work
application.secret_key = os.urandom(24)

# AWS Polly is set here. It requires the newest version of Boto3
login = LoginManager(application)
polly = boto3.client('polly', region_name='us-east-1')
db = boto3.resource('dynamodb', region_name='us-east-1')
table = db.Table('signuptable')
client = boto3.client(('dynamodb'))


@application.route('/')
def hello_world():
    return render_template('home.html')


# Sign Up
@application.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = aws_controller.SignUpForm()
    if form.validate_on_submit():
        table.put_item(
            Item={
                'name': form.name.data, 'email': form.email.data,
                'mobile': form.mobile.data, 'username': form.username.data,
                'password': form.password.data, 'country': form.country.data
            }
        )
        return redirect(url_for('hello_world'))
    return render_template('signup.html', form=form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    global currentUser
    form = aws_controller.LoginForm()
    currentUser = form.email.data
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.email.data, form.password.data))
        return redirect(url_for('profile', currentUser=currentUser))
    return render_template('login.html', form=form)


@application.route('/profile')
def profile():
    respones = table.get_item(
        Key={
            'email': currentUser
        }
    )
    item = respones['Item']
    print(item)
    username = item["username"]
    name = item["name"]
    email = item["email"]
    mobile = item["mobile"]
    country = item["country"]
    return render_template('profile.html', currentUser=currentUser, username=username, name=name, email=email,
                           mobil=mobile, country=country)


@application.route('/get-items')
def get_items():
    response = client.scan(TableName='signuptable')
    return jsonify(response)


@application.route("/testS3")
def storage():
    contents = list_files("imgbucketebay2")
    return render_template('testS3.html', contents=contents)


@application.route('/auktion')
def auktion():
    contents = list_files("imgbucketebay2")
    return render_template('auktion.html', contents=contents, image=image)


@application.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        upload_file(f"additionalFiles/{f.filename}", BUCKET)

        return redirect("/auktion")


@application.route("/additionalFiles/<filename>", methods=['GET'])
def download(filename):
    print(filename)
    if request.method == 'GET':
        output = download_file(filename, bucket)
    return send_file(output, as_attachment=True)


@application.route('/inserttext/', methods=['GET', 'POST'])
def renderinserttext_page():
    if request.method == 'POST':
        if "texttospeech" in request.form and request.form["texttospeech"] != "":
            sentence = request.form["texttospeech"]
            session['sentence'] = sentence
            print(sentence)
    return render_template('inserttext.html')


@application.route('/say.mp3', methods=['GET'])
def say():
    sentence = session.pop("sentence", None)
    if sentence is None:
        return (http.client.NO_CONTENT, 204)  # sentence not set

    resultVoice = ConvertTextToVoice(sentence, 'Naja')
    soundResult = resultVoice['AudioStream']

    f = tempfile.TemporaryFile()
    f.write(soundResult.read())

    response = send_file(f, as_attachment=True,
                         attachment_filename='say.mp3',
                         add_etags=False)

    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)

    response.headers.extend({
        'Content-Length': size,
        'Cache-Control': 'no-cache'
    })

    return response


# The text is sent to AWS Polly and a StreamObject is returned
def ConvertTextToVoice(text, voice):
    result = polly.synthesize_speech(OutputFormat='mp3', Text=text, VoiceId=voice)
    return result


def upload_file(file_name, bucket):
    """
    Function to upload a file to an S3 bucket
    """
    global image
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    image = file_name
    return response


def download_file(file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3')
    output = f"download/{file_name}"
    s3.Bucket(bucket).download_file(file_name, output)

    return output


def list_files(bucket):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client('s3')
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)

    return contents

def operations():
    global isAuthenticated
    if currentUser != 'seemannb@hs-pforzheim.de':
        isAuthenticated = True


if __name__ == '__main__':
    application.run()
