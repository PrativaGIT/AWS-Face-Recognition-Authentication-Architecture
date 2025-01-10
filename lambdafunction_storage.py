from __future__ import print_function
import boto3


print('Loading function')

dynamodb = boto3.client('dynamodb')
dynamodbTablename='YOUR_TABLENAME'
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

# --------------- Main handler ------------------

def lambda_handler(event, context):

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    print("Records: ",event['Records'])
    key = event['Records'][0]['s3']['object']['key']
    print("Key: ",key)
    

    try:

        # Calls Amazon Rekognition IndexFaces API to detect faces in S3 object 
        # to index faces into specified collection
        
        response = index_faces(bucket, key)
        
        # Commit faceId , first name and last name object metadata to DynamoDB
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId=response['FaceRecords'][0]['Face']['FaceId'] 
            name=key.split('.')[0].split('_')
            firstname=name[0]
            lastname=name[1]
            update_index(dynamodbTablename,faceId,firstname,lastname)
            
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise e

# --------------- Supporting Functions ------------------
def index_faces(bucket, key):

    response = rekognition.index_faces(
        Image={
            "S3Object":
            {
                "Bucket": bucket,
                "Name": key
            }
            },
            CollectionId="employee")
											 
    return response

    
def update_index(tableName,faceId, firstname,lastname):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            
            'RecognitionId': {'S': faceId},
            'FirstName': {'S': firstname},
            'LastName': {'S': lastname}
            }
        ) 
									  
	
