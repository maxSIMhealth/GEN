from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import clean_name

from django.conf import settings


class CustomS3Storage(S3Boto3Storage):
    def copy(self, from_path, to_path):
        from_path = self._normalize_name(clean_name(from_path))
        to_path = self._normalize_name(clean_name(to_path))

        result = self.connection.meta.client.copy_object(
            Bucket=self.bucket_name,
            CopySource=self.bucket_name + "/" + from_path,
            Key=to_path,
        )

        if result["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True
        else:
            return False

    def delete_directory(self, directory_path):
        objects_to_delete_list = self.connection.meta.client.list_objects(
            Bucket=self.bucket_name,
            Prefix=self._normalize_name(clean_name(directory_path)),
        )
        objects_to_delete_temp = dict(Objects=[])
        result = False

        for item in objects_to_delete_list["Contents"]:
            objects_to_delete_temp["Objects"].append(dict(Key=item["Key"]))
            if len(objects_to_delete_temp["Objects"]) >= 1000:
                result = self.connection.meta.client.delete_objects(
                    Bucket=self.bucket_name, Delete=objects_to_delete_temp
                )
                objects_to_delete_temp = dict(Objects=[])
        if len(objects_to_delete_temp["Objects"]) > 0:
            result = self.connection.meta.client.delete_objects(
                Bucket=self.bucket_name, Delete=objects_to_delete_temp
            )

        if result["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True
        else:
            return False

    def directory_exists(self, path: str) -> bool:
        """
        Check if a directory exists (either empty or with content).
        """
        s3 = self.connection.meta.client
        exists = False
        path = self._normalize_name(clean_name(path)).rstrip("/")
        resp = s3.list_objects(
            Bucket=self.bucket_name, Prefix=path, Delimiter="/", MaxKeys=1
        )

        # check if directory exists but it is empty
        if "CommonPrefixes" in resp:
            exists = True

        # check if directory exists and it has content
        if "Contents" in resp:
            exists = True

        return exists


class StaticStorage(CustomS3Storage):
    location = settings.AWS_STATIC_LOCATION


class MediaStorage(CustomS3Storage):
    location = settings.AWS_MEDIA_LOCATION
    file_overwrite = False


class PrivateMediaStorage(CustomS3Storage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = "private"
    file_overwrite = False
    custom_domain = False
    querystring_auth = True  # Overriding default value
    querystring_expire = 600  # 10 minutes
