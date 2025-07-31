import json
import logging

# Setup logging (this replaces the context.getLogger().log in Java)
from awsresources import AwsResources

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            size = record['s3']['object'].get('size', 'Unknown')

            logger.info("New file uploaded:")
            logger.info(f"Bucket: {bucket}")
            logger.info(f"Key: {key}")
            logger.info(f"Size: {size} bytes")

            resource = AwsResources(bucket, key)
            resource.detect_faces_in_image()
            source_image = {
                "S3Object": {
                    "Bucket": bucket,
                    "Name": key
                }
            }
            resource.compare_faces(source_image)

    except Exception as e:
        logger.error(f"Exception occurred: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processed S3 event successfully')
    }
