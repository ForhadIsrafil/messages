import io
from PIL import Image
import hashlib
import tempfile
import shutil
from django.conf import settings
from os.path import join as pathjoin
import uuid
from boto.s3.key import Key
from urllib.parse import urljoin
from boto.s3.connection import S3Connection, S3ResponseError
import os
import boto3
from boto3.s3.transfer import S3Transfer

THUMBNAIL_SIDE_LIMIT = settings.THUMBNAIL_SIDE_LIMIT


# Here We were uploading a thumnail file (img)  and a ios file (model)

# def upload_byte_file(file=None, model=None):
#     filename = ''
#
#     # Process the uploaded model
#     _, ext = os.path.splitext(file.name)
#     type = ext[1:].lower() if len(ext) > 0 else None
#
#     with tempfile.NamedTemporaryFile(delete=False) as fp:
#         tmppath = fp.name
#
#         for chunk in file.chunks():
#             fp.write(chunk)
#
#         # Save the model in the static path
#         hash = str(uuid.uuid4())
#         filename = hash + '.' + type
#         path = pathjoin(settings.FILE_ROOT, filename, )
#         shutil.move(tmppath, path)
#
#     return filename, hash


def upload_file_s3(file=None):
    bucket_name = settings.MESSAGE_BUCKET_NAME
    aws_access_key_id = settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY_ID

    transfer = S3Transfer(boto3.client('s3', 'us-east-2',
                                       aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key))

    _, ext = os.path.splitext(file.name)
    type = ext[1:].lower() if len(ext) > 0 else None

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        tmppath = fp.name

        for chunk in file.chunks():
            fp.write(chunk)

        # Save the model in the static path
        hash = str(uuid.uuid4())
        filename = hash + '.' + type
        path = pathjoin(settings.FILE_ROOT, filename)
        shutil.move(tmppath, path)

        key = hash+ext

        transfer.upload_file(path, bucket_name, key=key, extra_args={'ACL': 'public-read'})
        os.remove(path)

        return key
