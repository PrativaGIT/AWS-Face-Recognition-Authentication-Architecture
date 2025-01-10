import os
import uuid
import requests
from flask import Flask, request, render_template,make_response
import boto3
import base64

app = Flask(__name__)

# Set the upload directory (make sure this exists)
Upload_Folder = './uploads'
aws_access_key = 'YOUR_ACCESS_KEY'
aws_secret_key = "YOUR_SECRET_KEY"
region_name = 'YOUR_REGION_NAME'
S3_Bucket = 'YOUR_VALIDATION_BUCKETNAME'
s3_client = boto3.client('s3', region_name=region_name, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
API_Gateway_Endpoint = 'YOUR_ENDPOINT_URL'  # API Gateway URL for Lambda function
isBase64Encoded: True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/authenticate', methods=['POST'])
def upload_image():
    image = request.files.get('image')
    if image:
        print("Uploaded image:", image.filename, image.content_type)
        # Generate unique name for the image
        image_name = f"{uuid.uuid4()}.jpeg"
        image_path = os.path.join(Upload_Folder, image_name)
        os.makedirs(Upload_Folder, exist_ok=True)
        print(image_path)
        # Save the uploaded image
        image.save(image_path)

        # Upload file to S3 from local
        image.seek(0)
        s3_client.upload_fileobj(image, S3_Bucket, image_name)
        print(f"File {image_name} uploaded to S3 bucket {S3_Bucket}.")
        
        # Read the binary image
        with open(image_path, "rb") as file:
            binary_data = file.read()
        # Base64 encode the binary data
        base64_data = base64.b64encode(binary_data).decode("utf-8")
        # Send the request
        # Payload
        payload = {
            "body": base64_data,
            "isBase64Encoded": True,
            "bucket_name": S3_Bucket,
            "object_key": image_name
            }
        
        headers = {
             "Content-Type": "application/json",
             }
        try:
            response = requests.post(API_Gateway_Endpoint, json=payload, headers=headers)
            print("API Gateway Status Code::", response.status_code)
            print("API Gateway Response:", response.text)
       
                      
            # Check if the upload was successful
            if response.status_code == 200:
                # Authenticate the image
                auth_response = img_authenticate(image_name)
                print("Authentication Response:", auth_response)
                if auth_response.get('message') == "Processing complete":
                    response_data = {
                        'status': 'success',
                        'message': f"Hi {auth_response['firstname']} {auth_response['lastname']}, welcome to work."
                        }
                    
                    response = make_response(response_data, 200)  # 200 is the status code
                    
                else:
                     response_data = {
                        'status': 'failure',
                        'message': 'Authentication failed. Please try again.'
                        }
                     response = make_response(response_data, 401)  # 401 for unauthorized

            elif response.status_code == 500:
                 response_data = {
                'status': 'failure',
                'message': 'Person not available in dynamodb. Please try again.'
                }
                 response = make_response(response_data, 500)  

            else:
                 response_data = {
                'status': 'failure',
                'message': 'Person not recognized. Please try again.'
                }
                 response = make_response(response_data, 404)
               
        except Exception as e:
            response_data = {
            'status': 'failure',
            'message': 'An error occurred during the authentication process.',
            'error': str(e)
            }
        response.headers['Content-Type'] = 'application/json'
        return response
   

def img_authenticate(image_name):
    payload = {
        "object_key": image_name,
        "bucket_name": S3_Bucket
        }

    
    headers = {'Accept': 'application/json', 
               'Content-Type': 'application/json'}
    
    try:
        response = requests.post(API_Gateway_Endpoint, json=payload, headers=headers)
        print("Authentication API response:", response.json())  # Log the response
        return response.json()
    except Exception as e:
        return {'Message': 'Failure', 'error': str(e)}


if __name__ == '__main__':
    app.run(debug=True)
