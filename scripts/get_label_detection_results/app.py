import boto3

rek_client = boto3.client('rekognition')

ANIMALS = {'Dog', 'Cat', 'Horse', 'Bird', 'Deer'}

def lambda_handler(event, context):
    job_id = event['JobId']
    response = rek_client.get_label_detection(JobId=job_id)

    job_status = response['JobStatus']
    print(f"Job status: {job_status}")

    animal_detections = []

    if job_status == 'SUCCEEDED':
        pagination_token = None
        while True:
            response = rek_client.get_label_detection(
                JobId=job_id,
                MaxResults=1000,
                NextToken=pagination_token if pagination_token else None,
                SortBy='TIMESTAMP'
            )

            for detection in response['Labels']:
                label = detection['Label']['Name']
                timestamp = detection['Timestamp']

                if label in ANIMALS:
                    animal_detections.append({
                        'Timestamp': timestamp,
                        'Label': label,
                        'BoundingBox': detection['Label']['Instances'][0]['BoundingBox'] if detection['Label']['Instances'] else {},
                        'Bucket': event['Bucket'],
                        'VideoKey': event['VideoKey']
                    })

            pagination_token = response.get('NextToken')
            if not pagination_token:
                break

    return {
        'JobStatus': job_status,
        'AnimalDetections': animal_detections
    }
