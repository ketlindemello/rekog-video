import boto3

# This will use the default profile from ~/.aws/credentials
s3_client = boto3.client('s3')

# Example call
# response = s3_client.list_buckets()
# print(response)


def detect_faces_in_image():
    rek_client = boto3.client('rekognition', "us-east-1")
    try:

        #s3://awsimageshop/image_incoming/WhatsApp Image 2025-04-15 at 17.14.25_e3c83a3c.jpg
        response = rek_client.detect_faces(
            Image={
                "S3Object": {
                    "Bucket": "awsimageshop",
                    "Name": "image_incoming/WhatsApp Image 2025-04-15 at 17.14.25_e3c83a3c.jpg"
                }
            },
            Attributes=["ALL"]
        )

        face_details = response.get("FaceDetails", [])
        if not face_details:
            print("No faces detected.")
            return

        for face in face_details:
            confidence = face.get("Confidence")
            print(f"Face confidence: {confidence}")
            age = face.get("AgeRange", {})
            print(f"Estimated age: {age.get('Low')} - {age.get('High')}")



    except Exception as e:
        print(f"Rekognition error: {e}")




detect_faces_in_image()