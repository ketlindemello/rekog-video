import boto3
import os
import logging
from botocore.exceptions import BotoCoreError, ClientError


class AwsResources:
    def __init__(self, bucket_name, key_name):
        self.bucket_name = bucket_name
        self.key_name = key_name
        self.region = os.getenv("AWS_REGION", "us-east-1")

        self.s3_client = boto3.client("s3", region_name=self.region)
        self.rek_client = boto3.client("rekognition", region_name=self.region)

    def list_s3_buckets(self):
        response = self.s3_client.list_buckets()
        for bucket in response.get("Buckets", []):
            print(bucket["Name"])

    def detect_faces_in_image(self):
        try:
            response = self.rek_client.detect_faces(
                Image={
                    "S3Object": {
                        "Bucket": self.bucket_name,
                        "Name": self.key_name
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

                print("Checking against image database...")
                self.compare_faces({
                    "S3Object": {
                        "Bucket": self.bucket_name,
                        "Name": self.key_name
                    }
                })

        except ClientError as e:
            print(f"Rekognition error: {e}")

    def list_s3_files(self, prefix="image_source/"):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", []) if obj["Key"] != prefix]
        except ClientError as e:
            print(f"Error listing S3 objects: {e}")
            return []

    def compare_faces(self, source_image):
        try:
            target_images = self.list_s3_files()
            for target_key in target_images:
                try:
                    target_image = {
                        "S3Object": {
                            "Bucket": self.bucket_name,
                            "Name": target_key.strip()
                        }
                    }
                    response = self.rek_client.compare_faces(
                        SourceImage=source_image,
                        TargetImage=target_image,
                        SimilarityThreshold=70
                    )
                    matches = response.get("FaceMatches", [])
                    for match in matches:
                        confidence = match["Face"]["Confidence"]
                        bbox = match["Face"]["BoundingBox"]
                        print(f"Match found in {target_key} with {confidence:.2f}% confidence at position {bbox}")

                        if confidence > 60:
                            print(f"⚠️ Strong match in image: {target_key}")
                except ClientError as e:
                    print(f"Error comparing to image {target_key}: {e}")
        except ClientError as e:
            print(f"Compare faces failed: {e}")
