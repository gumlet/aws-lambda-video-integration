import os
import json
import urllib.parse
import urllib.request

GUMLET_PROCESS_VIDEO_BASE_URL = "https://api.gumlet.com/v1/video/process"

def gumlet_create_asset_post(event, source_id, options=None):
    """
    This function ingests video asset for processing on create object event in S3 bucket
    when invoked withing lambda function.
    
    :doc https://docs.gumlet.com/developers/video-apis#post-create-asset
    
    :param event: dict
        event object received from lambda function handler
    :param source_id: str
        Gumlet Video soure id.
    :param options: dict
        body options for Create Asset Post request
    
    :return status: bool
        True if post request is successful else False

    :return message: bool
        Empty string if post request is successful else error message

    :return response dict
        Gumlet response object if request is successful
    """
    if "GUMLET_API_KEY" not in os.environ:
        return False, "please set 'GUMLET_API_KEY' environment variable. Refer to https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html", {}
    
    if event and "ObjectCreated" in event['Records'][0]['eventName']:
        
        if not options:
            options = {
                "input": urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8'),
                "source_id": source_id,
                "format": "HLS"
            }
        else:
            options["input"] = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
            options["source_id"] = source_id

        headers = {
            "authorization": "Bearer {}".format(os.environ['GUMLET_API_KEY']),
            "Content-Type":  "application/json"
        }

        data = json.dumps(options).encode("utf-8")

        req = urllib.request.Request(GUMLET_PROCESS_VIDEO_BASE_URL, data=data, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req) as res:
                response = json.loads(res.read())
            return True, "Asset created with id: {}".format(response["asset_id"]), response
        except Exception as req_err:
            return False, str(req_err), {}
    else:
        return False, "received event (eventName: {}) is not for create object".format(event['Records'][0]['eventName']), {}
