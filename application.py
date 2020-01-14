from flask import Flask, render_template, jsonify, request, session, send_file, redirect, url_for
import boto3
import http.client
import tempfile
import os
import aws_controller

# import flask-wtf import flask-form

application = Flask(__name__)

UPLOAD_FOLDER = "additionalFiles"
BUCKET = "imgbucketebay2"
bucket = "imgbucketebay2"

# Make sessions work
application.secret_key = os.urandom(24)

# AWS Polly is set here. It requires the newest version of Boto3
polly = boto3.client('polly', region_name='us-east-1')


# bucket = boto3.client('s3', region_name='us-east-1')


@application.route('/')
def hello_world():
    return render_template('home.html')


# @application.route('/signup', methods=['GET', 'POST'])
# def sign_up():
#     form = aws_controller.SignUpForm()
#     if form.validate_on_submit():
#         print(
#             form.name.data,
#             form.email.data
#         )
#         return redirect(url_for('hello_world'))
#     return render_template('signup.html', form=form)


@application.route('/get-items')
def get_items():
    return render_template('get-items.html')


# @application.route('/get-items')
# def get_items():
#     return jsonify(aws_controller.get_items())


@application.route('/about')
def about():
    return render_template('about.html')


@application.route('/auktion')
def auktion():
    return render_template('auktion.html')


@application.route("/testS3")
def storage():
    contents = list_files("imgbucketebay2")
    return render_template('testS3.html', contents=contents)


@application.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        upload_file(f"additionalFiles/{f.filename}", BUCKET)

        return redirect("/testS3")


@application.route("/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = download_file(filename, BUCKET)

        return send_file(output, as_attachment=True)


# @application.route('/testS3')
# def tests3():
#     return render_template('testS3.html')

# @application.route('/inserttext')
# def inserttext():
#     return render_template('inserttext.html')

# This generates the primary site used where text is inputted


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
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response


def download_file(file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3')
    output = f"downloads/{file_name}"
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


if __name__ == '__main__':
    application.run()
