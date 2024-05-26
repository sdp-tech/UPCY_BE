"""
포트폴리오, 룩북, 서비스 모두 사용할 수 있도록 공통 함수로 따로 제작.
services>services.py>ServicePhotoApi 참고해서 작성하면 됨
"""

import boto3

from datetime import datetime
import uuid
from django.conf import settings
from UpcyProject import settings
import io



def get_random_text(length):
    return str(uuid.uuid4()).replace('-', '')[:length]

def s3_file_upload_by_file_data(upload_file, region_name, bucket_name, bucket_path, content_type=None):
    bucket_name = bucket_name.replace('/', '')
    if content_type:
        content_type = content_type
    else:
        content_type = upload_file.content_type

    extension = upload_file.name.split('.')[-1]
    now = datetime.now()
    random_str = get_random_text(20)
    random_file_name = f"{now.strftime('%Y%m%d%H%M%S')}_{random_str}.{extension}"
    upload_file_path_name = f"{bucket_path}/{random_file_name}"

    s3 = boto3.resource('s3', region_name=region_name, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)  # 버킷이 존재하는지 확인
    except s3.meta.client.exceptions.NoSuchBucket:
        raise Exception(f"The specified bucket does not exist: {bucket_name}")

    file_data = io.BytesIO(upload_file.read())
    if s3.Bucket(bucket_name).put_object(Key=upload_file_path_name, Body=file_data, ContentType=content_type, ACL='public-read') is not None:
        return f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{upload_file_path_name}"

    return False