from google.cloud import storage

from todayi.remote.base import Remote
from todayi.util.fs import path


class GcsRemote(Remote):
    """
    Manages pushing and pulling application resources
    with Google Cloud Storage.

    :param local_file_path: path to file to upload
    :type local_file_path: str
    :param remote_path: blob path to upload file to
    :type remote_path: str
    :param bucket_name: name of gcs bucket
    :type bucket_name: str
    """

    _bucket_prefix = "gs://"

    _bucket_suffix = "/"

    def __init__(self, local_file_path: str, remote_path: str, bucket_name: str):
        self._local_file_path = local_file_path
        self._remote_path = remote_path
        self._bucket_name = self._clean_bucket_name(bucket_name)
        self._bucket = None

    @property
    def bucket(self):
        if self._bucket is None:
            self._bucket = storage.Client().bucket(self._bucket_name)
        return self._bucket

    def push(self, backup: bool = False):
        """
        Pushes up current state to GCS remote. Optionally write
        backup file to remote.

        :param backup: whether or not to backup remote backend file
        :type backup: bool
        """
        if backup is True:
            self.bucket.rename_blob(
                self._blob(), self._backup_file_name(self._remote_path)
            )
        blob = self._blob()
        blob.upload_from_filename(self._local_file_path)

    def pull(self, backup: bool = False):
        """
        Updates current state from remote. Optionally write
        local backup file.

        :param backup: whether or not to backup local backend file
        :type backup: bool
        """
        if backup is True:
            path(self._local_file_path).rename(
                path(self._backup_file_name(self._local_file_path))
            )
        blob = self._blob()
        blob.download_to_filename(self._local_file_path)

    def _blob(self):
        return self.bucket.blob(self._remote_path)

    def _clean_bucket_name(self, bucket_name: str) -> str:
        if self._bucket_prefix in bucket_name:
            bucket_name = bucket_name.replace(self._bucket_prefix, "")
        if bucket_name[-1] == self._bucket_suffix:
            bucket_name = bucket_name[0 : len(bucket_name) - 1]
        return bucket_name
