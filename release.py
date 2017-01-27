import os
import sys
import json
import time

import boto3
import cauldron

configs_path = os.path.join(
    os.path.dirname(os.path.relpath(__file__)),
    'release-settings.json'
)

settings_path = os.path.join(
    os.path.dirname(os.path.realpath(cauldron.__file__)),
    'settings.json'
)

if not os.path.exists(configs_path):
    print('MISSING SETTINGS FILE:\n{}'.format(configs_path))
    sys.exit(1)


with open(configs_path, 'r') as f:
    configs = json.load(f)

session = boto3.Session(profile_name=configs.get('profile', 'default'))

s3_client = session.client('s3')
args = {'ACL': 'public-read'}
s3_client.upload_file(
    Filename=settings_path,
    Bucket=configs['bucket'],
    Key=configs['key'],
    ExtraArgs=args
)

cloudfront_client = session.client('cloudfront')
cloudfront_client.create_invalidation(
    DistributionId=configs['distributionId'],
    InvalidationBatch=dict(
        Paths={'Quantity': 1, 'Items': ['/{}'.format(configs['key'])]},
        CallerReference='{}'.format(time.time())
    )
)


print('Operation Complete')
