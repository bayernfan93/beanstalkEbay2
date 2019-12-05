import boto3

dynamo_client = boto3.client('dynamodb', region_name='us-east-1')
# table = dynamo_client.Table('YourTestTable')

# response = table.put_item(
#     Item={
#         'Artist': 'Thomas Schuster',
#         'Song': 'Professor'
#     }
# )

db = boto3.resource('dynamodb', region_name='us-east-1')
table = db.Table('YourTestTable')


def get_items():
    return dynamo_client.scan(TableName='YourTestTable')
