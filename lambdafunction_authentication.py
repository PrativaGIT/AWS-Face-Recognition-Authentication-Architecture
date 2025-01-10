import boto3
import json
import base64

rekognition = boto3.client('rekognition', region_name='YOUR_REGION')
dynamodb = boto3.client('dynamodb', region_name='YOUR_REGION')
dynamodbTablename='YOUR_DYNAMODB_TABLENAME'
s3 = boto3.client('s3', region_name='YOUR_REGION')

def lambda_handler(event, context):
    print("Event received:", json.dumps(event, indent=2))
    try:
        bucket_name = None
        object_key = None
        image_in_bytes = None

        # Check for API Gateway invocation
        if 'body' in event and event['body']:
            if event.get('isBase64Encoded', False):
                print("Decoding base64-encoded image.")
                image_in_bytes = base64.b64decode(event['body'])
                print(f"Decoded image size: {len(image_in_bytes)} bytes")
            else:
                data = json.loads(event['body'])
                bucket_name = data.get('bucket_name')
                object_key = data.get('object_key')

                if not bucket_name or not object_key:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Missing 'bucket_name' or 'object_key' in request body"})
                    }
        elif 'Records' in event:
            for record in event['Records']:
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Unsupported event format"})
            }

        # Retrieve the image from S3 if not provided directly
        if not image_in_bytes:
            print(f"Fetching file '{object_key}' from bucket '{bucket_name}'.")
            obj = s3.get_object(Bucket=bucket_name, Key=object_key)
            image_in_bytes = obj['Body'].read()
            print(f"Image retrieved from S3. Size: {len(image_in_bytes)} bytes")

        # Ensure the image is not empty
        if not image_in_bytes or len(image_in_bytes) == 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Image bytes are empty"})
            }

        # Perform face search using Rekognition
        response = rekognition.search_faces_by_image(
            CollectionId='employee',
            Image={'Bytes': image_in_bytes}
        )
        #Logic to get items from dynamodb
        firstname = None
        lastname = None

        for match in response.get('FaceMatches', []):
            FaceId = match['Face']['FaceId']
            Confidence = match['Face']['Confidence']
            print(f"FaceId: {FaceId}, Confidence: {Confidence}")

            face = dynamodb.get_item(
                TableName = dynamodbTablename,
                Key={'RecognitionId': {'S': FaceId}}
            )

            if 'Item' in face:
                firstname = face['Item']['FirstName']['S']
                lastname = face['Item']['LastName']['S']
                print("Found Person in dynamodb:", face['Item'])
                break                                 # Stop after finding the first match

        if firstname and lastname:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Processing complete",
                    "firstname": firstname,
                    "lastname": lastname
                })
            }
        else:
            print("Person cannot be recognized for the provided image.")
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "Person not recognized"})
            }
    except Exception as e:
        print(f"Error processing request: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
