import boto3
#
dynamo_client = boto3.client('dynamodb', region_name='us-east-1')
# table = dynamo_client.Table('YourTestTable')
#
db = boto3.resource('dynamodb', region_name='us-east-1')
table = db.Table('YourTestTable')
#
# allItems = dynamo_client.scan(TableName='YourTestTable')
#
# for key, value in allItems:
#     if key != 'Marcel Viehmaier':
#         response = table.put_item(
#             Item={
#                 'Artist': 'Marcel Viehmaier',
#                 'Song': 'Student'
#             }
#         )
#     else:
#         print("WTF")
#
#
def get_items():
    return dynamo_client.scan(TableName='YourTestTable')
