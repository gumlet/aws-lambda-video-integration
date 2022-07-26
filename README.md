# aws-lambda-video-integration
This repository contains utility functions for AWS Lambda function integration with Gumlet. Sometimes it requires automating direct ingestion of video into the Gumlet processing pipeline. This script helps to create a video asset in Gumlet for processing when an AWS Lambda function is set to be triggered on a create object event in an S3 bucket.

## Steps to automate processing pipeline

1. Create a lambda function (or use the existing one) to be triggered on various events in a perticular S3 bucket.

2. Generate an API key from [Gumlet Account Dashboard](https://www.gumlet.com/dashboard/organization/apikey/) and set it as environment variable `GUMLET_API_KEY` in the lambda function. Find the reference [here](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html).

3. Crate python script named `gumlet_integration_functions.py` in the lambda function and copy contents from `gumlet_integration_functions.py` in this repository to newly created file in the lambda function.

4. Import the Gumlet integration script (`gumlet_integration_functions.py`) in your lambda function python script containing the `lambda_handler` function (named `lambda_function.py` by default). 

5. Call `gumlet_create_asset_post` method from `gumlet_integration_functions` in your `lambda_handler` function with three parameters named `event`, `collection_id`, and `options`. `event` parameter takes event object received from `lambda_handler` directly, pass your Gumlet video collection id in `collection_id` parameter. And pass video processing parameters to `option` parameterm, find comeplete reference [here](https://docs.gumlet.com/reference/create-asset).

6. This function will return three values namely `status`, `message`, and `response`. `status` will be `False` in case of any error. `message` will contain an error message if any. And `response` will contain a response object from Gumlet on successfully creating a video asset.

## Code Example

An example of lambda function script is given below.

```python
import json
import boto3
import urllib.parse
import urllib.request

# import Gumlet integration function script
import gumlet_integration_functions

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        
        # Gumlet video collection id
        gumlet_collection_id = "5fc7765de648a029e1e62edf"
        
        # Video Asset Options
        options = {
            "format": "HLS",
            "image_overlay": {
                "url": "https://assets.gumlet.io/assets/logo.svg?format=png",
                "height": "10%",
                "width": "10%",
                "horizontal_align": "left",
                "horizontal_margin": "10%",
                "vertical_align": "bottom",
                "vertical_margin": "10%"
            }
        }
        
        # Gumlet integration function call
        status, message, response = gumlet_integration_functions.gumlet_create_asset_post(
            event, 
            gumlet_collection_id,
            options
        )

        print("Message: {}".format(message))
        
        print("Gumlet Response: {}".format(json.dumps(response, indent=4)))
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

```

Output

```
Message: Asset created with id: 5fd34ed6f4d8180a72c1efb2
Gumlet Response: {
    "asset_id": "5fd34ed6f4d8180a72c1efb2",
    "progress": 0,
    "created_at": 1607683798307,
    "status": "queued",
    "tag": "",
    "input": {
        "transformations": {
            "resolution": [],
            "thumbnail": [
                "auto"
            ],
            "format": "hls",
            "video_codec": "libx264",
            "audio_codec": "aac",
            "image_overlay": {
                "url": "https://assets.gumlet.io/assets/logo.svg?format=png",
                "vertical_align": "bottom",
                "horizontal_align": "left",
                "vertical_margin": "10%",
                "horizontal_margin": "10%",
                "width": "10%",
                "height": "10%"
            },
            "thumbnail_format": "png",
            "mp4_access": false
        },
        "source_url": "test/key"
    },
    "output": {
        "status_url": "https://api.gumlet.com/video/v1/status/5fd34ed6f4d8180a72c1efb2",
        "playback_url": "https://video.gumlet.io/5fc7765de648a029e1e62edf/5fd34ed6f4d8180a72c1efb2/1.m3u8",
        "thumbnail_url": [
            "https://video.gumlet.io/5fc7765de648a029e1e62edf/5fd34ed6f4d8180a72c1efb2/thumbnail-1-0.png"
        ]
    }
}
```