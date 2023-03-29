import json
import os
import subprocess
import shlex
import boto3

S3_DESTINATION_BUCKET = os.environ['S3_DESTINATION_BUCKET']
SIGNED_URL_TIMEOUT = 60

def lambda_handler(event, context):
    
    # アップロードされたオブジェクトのバケット名/キーを取得
    s3_source_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_source_key = event['Records'][0]['s3']['object']['key']

    # 出力ファイル名を生成
    s3_source_basename = os.path.splitext(os.path.basename(s3_source_key))[0]
    s3_source_dirname = os.path.dirname(s3_source_key)
    s3_destination_filename = os.path.join(s3_source_dirname, s3_source_basename + "_thumbnail.jpeg")
    
    # ffmpeg に食わせる署名付きURLを発行
    s3_client = boto3.client('s3')
    s3_source_signed_url = s3_client.generate_presigned_url('get_object',
        Params={'Bucket': s3_source_bucket, 'Key': s3_source_key},
        ExpiresIn=SIGNED_URL_TIMEOUT)
    
    # 動画の1フレーム目を画像として切り出し
    ffmpeg_cmd = "/opt/bin/ffmpeg -i \"" + s3_source_signed_url + "\" -f image2 -vframes 1 -vf scale=720:-1 -"
    command1 = shlex.split(ffmpeg_cmd)
    p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # S3 へ Put
    resp = s3_client.put_object(Body=p1.stdout, Bucket=S3_DESTINATION_BUCKET, Key=s3_destination_filename)

    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete successfully')
    }