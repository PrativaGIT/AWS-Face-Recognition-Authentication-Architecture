# AWS Face Recognition Authentication Architecture

This project demonstrates a facial recognition-based authentication system using AWS services and Python. It enables secure employee authentication by leveraging Amazon Rekognition, DynamoDB, API Gateway, and Lambda functions.

![Architecture](https://github.com/user-attachments/assets/4149690e-88d1-4c65-b7f8-c44640a3e88e)

---

## **Architecture Overview**

The system architecture includes the following components:

1. **Employee Pictures**:
   - Employees upload their pictures for authentication.

2. **Amazon S3**:
   - **Storage Bucket**: Stores employee images for initial setup.
   - **Validation Bucket**: Stores user images for authentication.

3. **AWS Lambda**:
   - **Storage Lambda Function**: Processes uploaded images and pushes them to Rekognition and DynamoDB.
   - **Authentication Lambda Function**: Authenticates user images by invoking Rekognition and fetching data from DynamoDB.

4. **Amazon Rekognition**:
   - Compares uploaded images with stored images in the collection.

5. **Amazon DynamoDB**:
   - Stores employee data, including Rekognition ID, first name, and last name.

6. **Amazon API Gateway**:
   - Exposes REST endpoints for user image authentication.

7. **Web Interface**:
   - Allows users to upload images for authentication via a simple UI.

---

## **Features**

- **Image Upload**: Employees can upload their images for authentication.
- **AWS Rekognition Integration**: Facial recognition for secure and accurate authentication.
- **DynamoDB Integration**: Stores and retrieves employee details.
- **Serverless Architecture**: Fully serverless using AWS Lambda and API Gateway.

---

## **Technologies Used**

- **Frontend**: HTML, CSS, Flask
- **Backend**: Python, AWS Lambda
- **Database**: Amazon DynamoDB
- **Image Processing**: Amazon Rekognition
- **Storage**: Amazon S3

---

## **Deployment**

1. Upload images to the S3 storage bucket.
2. Deploy Lambda functions for image processing and authentication.
3. Configure API Gateway to route requests to Lambda functions.
4. Test the system by uploading an image via the web interface.

---

## **How It Works**

1. **Employee Setup**:
   - Employees upload their images to the storage bucket.
   - Lambda function processes the images, extracts facial features using Rekognition, and stores metadata in DynamoDB.

2. **Authentication**:
   - User uploads an image via the web interface.
   - The image is processed by the authentication Lambda function, which compares it with stored data in Rekognition.
   - If a match is found, the user's details are retrieved from DynamoDB and displayed.

## **Future Enhancements**

- Add support for multi-factor authentication.
- Integrate with AWS CloudFront for faster image delivery.
- Implement role-based access control.


