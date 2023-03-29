import os
import subprocess
import shlex
import boto3
import logging

BUCKET_NAME = os.environ['S3_BUCKET_NAME']
PREFIX = os.environ['S3_BUCKET_PREFIX']
SIGNED_URL_TIMEOUT = 60

s3_client = boto3.client('s3')
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_thumbnail(s3_source_bucket, s3_source_key):
    # 出力ファイル名を生成
    s3_source_basename = os.path.splitext(os.path.basename(s3_source_key))[0]
    s3_source_dirname = os.path.dirname(s3_source_key)
    s3_destination_filename = os.path.join(s3_source_dirname, s3_source_basename + "_thumbnail.jpeg")

    # 署名付きURLを生成
    s3_source_signed_url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': s3_source_bucket,
            'Key': s3_source_key
        },
        ExpiresIn=SIGNED_URL_TIMEOUT
    )

    # ffmpeg に食わせる
    ffmpeg_cmd = "/opt/homebrew/bin/ffmpeg -i \"" + s3_source_signed_url + "\" -f image2 -vframes 1 -vf scale=720:-1 -"
    command1 = shlex.split(ffmpeg_cmd)
    p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p1.returncode != 0:
        logging.warn(f'{key} のサムネイル生成に失敗しました')
        return ''
    else:
        s3_client.put_object(Body=p1.stdout, Bucket=BUCKET_NAME, Key=s3_destination_filename)
        return f'{BUCKET_NAME}/{s3_destination_filename}'


def main():
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX)

    for page in page_iterator:
        if 'Contents' in page:
            for item in page['Contents']:
                key = item['Key']
                if not key.endswith('.mp4'):
                    continue

                logging.info(f'{key} のサムネイルを作成します')
                thumbnail_key = generate_thumbnail(BUCKET_NAME, key)
                if thumbnail_key != '':
                    logging.info(f'サムネイルを作成しました: key = {thumbnail_key}')


main()
