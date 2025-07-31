import boto3

rek_client = boto3.client('rekognition')

def lambda_handler(event, context):
    response = rek_client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': event['Bucket'],
                'Name': event['VideoKey']
            }
        },
        MinConfidence=70
    )
    return {
        'JobId': response['JobId'],
        'Bucket': event['Bucket'],
        'VideoKey': event['VideoKey']
    }
