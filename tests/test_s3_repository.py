import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from botocore.exceptions import ClientError

from scripts.s3_repository import download_metadata, s3_client, upload_repository


class RepositoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "S3_TEST_ENDPOINT" not in os.environ:
            raise unittest.SkipTest("S3_TEST_ENDPOINT is not set")

        os.environ["S3_ENDPOINT"] = os.environ["S3_TEST_ENDPOINT"]
        os.environ["S3_ACCESS_KEY"] = os.environ.get("S3_TEST_ACCESS_KEY", "admin")
        os.environ["S3_SECRET_KEY"] = os.environ.get("S3_TEST_SECRET_KEY", "secret")
        cls.bucket = os.environ.get("S3_TEST_BUCKET", "mindustry")
        cls.client = s3_client()
        try:
            cls.client.create_bucket(Bucket=cls.bucket)
        except ClientError as error:
            if error.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                raise

    def setUp(self):
        response = self.client.list_objects_v2(Bucket=self.bucket)
        for item in response.get("Contents", []):
            self.client.delete_object(Bucket=self.bucket, Key=item["Key"])

    def test_upload_and_restore_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            artifact = (
                repository / "com/github/Anuken/Mindustry/core/v160.2/core-v160.2.jar"
            )
            metadata = artifact.parent.parent / "maven-metadata.xml"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"artifact")
            metadata.write_text("<metadata />", encoding="utf-8")

            uploaded = upload_repository(self.client, self.bucket, repository)
            self.assertEqual(uploaded, 10)

            checksum = hashlib.sha256(b"artifact").hexdigest()
            response = self.client.get_object(
                Bucket=self.bucket,
                Key="com/github/Anuken/Mindustry/core/v160.2/core-v160.2.jar.sha256",
            )
            self.assertEqual(response["Body"].read().decode(), checksum)

            restored = Path(directory) / "restored"
            downloaded = download_metadata(
                self.client,
                self.bucket,
                restored,
                ["com/github/Anuken/Mindustry", "com/github/Anuken/Arc"],
            )
            self.assertEqual(downloaded, 1)
            restored_metadata = (
                restored / "com/github/Anuken/Mindustry/core/maven-metadata-local.xml"
            )
            self.assertEqual(restored_metadata.read_text(), "<metadata />")


if __name__ == "__main__":
    unittest.main()
