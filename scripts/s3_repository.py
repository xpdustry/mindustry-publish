import argparse
import hashlib
import logging
import os
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath

import boto3
from botocore.config import Config

LOG = logging.getLogger(__name__)
CHECKSUMS = {
    ".md5": "md5",
    ".sha1": "sha1",
    ".sha256": "sha256",
    ".sha512": "sha512",
}


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name=os.environ.get("S3_REGION", "us-east-1"),
        config=Config(
            signature_version="s3v4",
            retries={"mode": "standard", "max_attempts": 5},
            s3={"addressing_style": "path"},
        ),
    )


def metadata_keys(client, bucket: str, prefix: str) -> Iterable[str]:
    normalized = prefix.strip("/") + "/"
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=normalized):
        for item in page.get("Contents", []):
            key = item["Key"]
            if PurePosixPath(key).name == "maven-metadata.xml":
                yield key


def download_metadata(
    client, bucket: str, repository: Path, prefixes: Iterable[str]
) -> int:
    count = 0
    for prefix in prefixes:
        for key in metadata_keys(client, bucket, prefix):
            destination = repository.joinpath(*PurePosixPath(key).parts).with_name(
                "maven-metadata-local.xml"
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            LOG.info("Downloading s3://%s/%s", bucket, key)
            client.download_file(bucket, key, str(destination))
            count += 1
    return count


def repository_files(repository: Path) -> Iterable[Path]:
    return sorted(path for path in repository.rglob("*") if path.is_file())


def is_checksum(path: Path) -> bool:
    return path.suffix in CHECKSUMS


def write_checksums(path: Path) -> None:
    digests = {suffix: hashlib.new(name) for suffix, name in CHECKSUMS.items()}
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            for digest in digests.values():
                digest.update(chunk)

    for suffix, digest in digests.items():
        path.with_name(path.name + suffix).write_text(
            digest.hexdigest(), encoding="ascii"
        )


def upload_repository(client, bucket: str, repository: Path, workers: int = 16) -> int:
    source_files = [
        path for path in repository_files(repository) if not is_checksum(path)
    ]
    for path in source_files:
        LOG.info("Checksumming %s", path.relative_to(repository))
        write_checksums(path)

    files = list(repository_files(repository))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        uploads = {
            executor.submit(
                client.upload_file,
                str(path),
                bucket,
                path.relative_to(repository).as_posix(),
            ): path
            for path in files
        }
        for upload in as_completed(uploads):
            path = uploads[upload]
            upload.result()
            LOG.info("Uploaded s3://%s/%s", bucket, path.relative_to(repository))
    return len(files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize the Maven repository with S3"
    )
    parser.add_argument("--bucket", default=os.environ.get("S3_BUCKET"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    download = subparsers.add_parser("download-metadata")
    download.add_argument("repository", type=Path)
    download.add_argument("prefix", nargs="+")

    upload = subparsers.add_parser("upload")
    upload.add_argument("repository", type=Path)
    upload.add_argument("--workers", type=int, default=16)

    args = parser.parse_args()
    if not args.bucket:
        parser.error("--bucket or S3_BUCKET is required")
    return args


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()
    client = s3_client()

    if args.command == "download-metadata":
        count = download_metadata(client, args.bucket, args.repository, args.prefix)
        LOG.info("Downloaded %d Maven metadata files", count)
    else:
        if not args.repository.is_dir():
            raise SystemExit(f"Repository does not exist: {args.repository}")
        if args.workers < 1:
            raise SystemExit("--workers must be at least 1")
        count = upload_repository(client, args.bucket, args.repository, args.workers)
        LOG.info("Uploaded %d repository files", count)


if __name__ == "__main__":
    main()
