from flask import Flask, render_template, jsonify, request, session, send_file
import boto3
import http.client
import tempfile
import os
import aws_controller

application = Flask(__name__)

# Make sessions work
application.secret_key = os.urandom(24)

# AWS Polly is set here. It requires the newest version of Boto3
polly = boto3.client('polly', region_name='us-east-1')


@application.route('/')
def hello_world():
    return render_template('home.html')


@application.route('/get-items')
def get_items():
    return render_template('get-items.html')


# @application.route('/get-items')
# def get_items():
#     return jsonify(aws_controller.get_items())

@application.route('/about')
def about():
    return render_template('about.html')

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


if __name__ == '__main__':
    application.run()
