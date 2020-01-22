from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email


class SignUpForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email(message="not a valid email")])
    username = StringField()
    password = PasswordField(validators=[DataRequired()])
    mobile = IntegerField()
    country = StringField(validators=[DataRequired()])
    submit = SubmitField()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# import boto3
# dynamo_client = boto3.client('dynamodb', region_name='us-east-1')
# db = boto3.resource('dynamodb', region_name='us-east-1')
# table = db.Table('YourTestTable')
# def put_items():
#     return table.put_item(
#         Item={
#             'Artist': 'Peter Mueller',
#             'Song': 'Angestellter'
#         }
#     )
# def get_items():
#     return dynamo_client.scan(TableName='YourTestTable')
