import boto3
import json
import os
import subprocess
from PIL import Image

s3_client = boto3.client('s3')

# CONFIGURABLE
VIDEO_BUCKET = 'my-input-videos'
VIDEO_KEY = 'video.mp4'

OUTPUT_BUCKET = 'my-output-images'

def download_video(local_path):
    print("Downloading video...")
    s3_client.download_file(VIDEO_BUCKET, VIDEO_KEY, local_path)
    print("Video downloaded.")

def extract_frame_at_timestamp(video_path, timestamp_ms, output_frame_path):
    timestamp_seconds = timestamp_ms / 1000.0
    timestamp_str = "{:02d}:{:02d}:{:06.3f}".format(
        int(timestamp_seconds // 3600),
        int((timestamp_seconds % 3600) // 60),
        timestamp_seconds % 60
    )
    print(f"Extracting frame at {timestamp_str}...")

    command = [
        '/opt/ffmpeg/ffmpeg',  # if using Lambda layer with FFmpeg
        '-i', video_path,
        '-ss', timestamp_str,
        '-frames:v', '1',
        output_frame_path
    ]

    subprocess.run(command, check=True)
    print("Frame extracted.")

def crop_frame(frame_path, bounding_box, output_cropped_path):
    print("Cropping frame...")
    image = Image.open(frame_path)
    frame_width, frame_height = image.size

    left = int(bounding_box['Left'] * frame_width)
    top = int(bounding_box['Top'] * frame_height)
    width = int(bounding_box['Width'] * frame_width)
    height = int(bounding_box['Height'] * frame_height)

    cropped = image.crop((left, top, left + width, top + height))
    cropped.save(output_cropped_path)
    print("Frame cropped.")

def upload_to_s3(local_path, bucket, key):
    print(f"Uploading {local_path} to s3://{bucket}/{key}...")
    s3_client.upload_file(local_path, bucket, key)
    print("Upload complete.")

def lambda_handler(event, context):
    # Example event with detection results (in reality, you'll get this from Rekognition Label Detection output)
    detection_result = {
        'Timestamp': 4500,  # milliseconds
        'Label': 'Dog',
        'BoundingBox': {
            'Width': 0.25,
            'Height': 0.3,
            'Left': 0.1,
            'Top': 0.2
        }
    }

    # 1️⃣ Prepare paths
    local_video_path = '/tmp/video.mp4'
    local_frame_path = '/tmp/frame.jpg'
    local_cropped_path = '/tmp/cropped_animal.jpg'

    # 2️⃣ Download video
    download_video(local_video_path)

    # 3️⃣ Extract frame at timestamp
    extract_frame_at_timestamp(local_video_path, detection_result['Timestamp'], local_frame_path)

    # 4️⃣ Crop bounding box
    crop_frame(local_frame_path, detection_result['BoundingBox'], local_cropped_path)

    # 5️⃣ Upload cropped image
    upload_to_s3(local_cropped_path, OUTPUT_BUCKET, f"animal_{detection_result['Timestamp']}.jpg")

    return {
        'statusCode': 200,
        'body': json.dumps('Animal image extracted and saved to S3.')
    }
