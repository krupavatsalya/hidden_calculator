import boto3
import json

class AWSStorage:
    def __init__(self):
        with open("aws.json", 'r') as json_file:
            credentials = json.load(json_file)
        self.s3 = boto3.resource(
            service_name='s3',
            region_name="us-east-1",
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"]
        )
        self.s3_client = boto3.client(
            service_name='s3',
            region_name="us-east-1",
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"]
        )
        self.bucket_name = 'calculator-hidden'
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_keys = [obj.key for obj in self.bucket.objects.all()]

    def create_folder(self, folder):
        if not folder.endswith('/'):
            folder += '/'
        self.s3_client.put_object(Bucket=self.bucket_name, Key=folder)

    def upload_file(self, file, folder):
        if not folder.endswith('/'):
            folder += '/'
        self.s3_client.upload_fileobj(
            file,
            self.bucket_name,
            folder + file.filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
        )
        return f'File successfully uploaded to {folder}{file.filename} in bucket {self.bucket_name}'

    def get_signed_url(self, key, expiration=3600):
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=expiration
        )

    def delete_file(self, key):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return f'File {key} deleted successfully from bucket {self.bucket_name}'
        except Exception as e:
            return f'Error deleting file {key}: {str(e)}'
