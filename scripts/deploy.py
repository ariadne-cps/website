#!/usr/bin/env python3

import ftplib
import hashlib
import io
import json
import os
import posixpath
import time
from pathlib import Path

HOST = "ftp.ariadne-cps.org"
REMOTE_ROOT = "/www.ariadne-cps.org"
REMOTE_MANIFEST = posixpath.join(REMOTE_ROOT, ".deploy-manifest.json")
LOCAL_ROOT = Path("public")
TIMEOUT = 30
RETRIES = 4
BLOCKSIZE = 128 * 1024

USER = os.environ["FTP_USER"]
PASSWORD = os.environ["FTP_PASSWORD"]


def connect():
    ftp = ftplib.FTP(timeout=TIMEOUT)
    ftp.connect(HOST, 21)
    ftp.login(USER, PASSWORD)
    ftp.set_pasv(True)
    return ftp


def close_quietly(ftp):
    if ftp is None:
        return
    try:
        ftp.quit()
    except ftplib.all_errors:
        try:
            ftp.close()
        except Exception:
            pass


def ensure_dir(ftp, remote_dir):
    current = ""
    for part in remote_dir.strip("/").split("/"):
        if not part:
            continue
        current += "/" + part
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            previous = ftp.pwd()
            ftp.cwd(current)
            ftp.cwd(previous)


def remote_size(ftp, remote_path):
    try:
        ftp.voidcmd("TYPE I")
        return ftp.size(remote_path)
    except ftplib.error_perm:
        return None


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(ftp):
    buffer = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {REMOTE_MANIFEST}", buffer.write)
    except ftplib.error_perm:
        return None

    try:
        data = json.loads(buffer.getvalue().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict) or data.get("version") != 1:
        return None
    files = data.get("files")
    return files if isinstance(files, dict) else None


def upload_file(ftp, local_path, remote_path):
    remote_dir = posixpath.dirname(remote_path)
    local_size = local_path.stat().st_size

    for attempt in range(1, RETRIES + 1):
        try:
            if ftp is None:
                ftp = connect()

            ensure_dir(ftp, remote_dir)
            print(f"PUT  {remote_path} ({local_size} bytes), attempt {attempt}/{RETRIES}")

            with local_path.open("rb") as source:
                ftp.storbinary(
                    f"STOR {remote_path}",
                    source,
                    blocksize=BLOCKSIZE,
                )

            print(f"UP   100% {remote_path}")
            return ftp

        except ftplib.all_errors as exc:
            close_quietly(ftp)
            ftp = None

            if attempt == RETRIES:
                raise RuntimeError(
                    f"Failed to upload {remote_path} after {RETRIES} attempts"
                ) from exc

            delay = attempt * 5
            print(
                f"FTP error while uploading {remote_path}: {exc}; "
                f"retrying in {delay}s"
            )
            time.sleep(delay)


def write_manifest(ftp, files_manifest):
    payload = json.dumps(
        {"version": 1, "files": files_manifest},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    temp_path = REMOTE_MANIFEST + ".tmp"

    for attempt in range(1, RETRIES + 1):
        try:
            if ftp is None:
                ftp = connect()

            print(f"PUT  {REMOTE_MANIFEST} ({len(payload)} bytes), attempt {attempt}/{RETRIES}")
            ftp.storbinary(f"STOR {temp_path}", io.BytesIO(payload), blocksize=BLOCKSIZE)
            try:
                ftp.delete(REMOTE_MANIFEST)
            except ftplib.error_perm:
                pass
            ftp.rename(temp_path, REMOTE_MANIFEST)
            print(f"UP   100% {REMOTE_MANIFEST}")
            return ftp

        except ftplib.all_errors as exc:
            close_quietly(ftp)
            ftp = None

            if attempt == RETRIES:
                raise RuntimeError(
                    f"Failed to write deployment manifest after {RETRIES} attempts"
                ) from exc

            delay = attempt * 5
            print(f"FTP error while writing manifest: {exc}; retrying in {delay}s")
            time.sleep(delay)


def main():
    files = sorted(path for path in LOCAL_ROOT.rglob("*") if path.is_file())
    if not files:
        raise RuntimeError("No files found under public/")

    local_manifest = {}
    for local_path in files:
        rel = local_path.relative_to(LOCAL_ROOT).as_posix()
        local_manifest[rel] = {
            "sha256": sha256_file(local_path),
            "size": local_path.stat().st_size,
        }

    ftp = None
    uploaded = 0
    skipped = 0

    try:
        ftp = connect()

        try:
            remote_manifest = load_manifest(ftp)
        except ftplib.all_errors:
            close_quietly(ftp)
            ftp = connect()
            remote_manifest = None

        bootstrap = remote_manifest is None
        if bootstrap:
            print("No deployment manifest found; bootstrapping from remote file sizes.")
        else:
            print(f"Loaded deployment manifest with {len(remote_manifest)} entries.")

        for local_path in files:
            rel = local_path.relative_to(LOCAL_ROOT).as_posix()
            remote_path = posixpath.join(REMOTE_ROOT, rel)
            local_info = local_manifest[rel]

            try:
                size_matches = remote_size(ftp, remote_path) == local_info["size"]
            except ftplib.all_errors:
                close_quietly(ftp)
                ftp = connect()
                size_matches = remote_size(ftp, remote_path) == local_info["size"]

            hash_matches = (
                not bootstrap
                and isinstance(remote_manifest.get(rel), dict)
                and remote_manifest[rel].get("sha256") == local_info["sha256"]
            )

            if size_matches and (bootstrap or hash_matches):
                reason = "same size (bootstrap)" if bootstrap else "unchanged"
                print(f"SKIP {remote_path} ({local_info['size']} bytes, {reason})")
                skipped += 1
                continue

            ftp = upload_file(ftp, local_path, remote_path)
            uploaded += 1

        ftp = write_manifest(ftp, local_manifest)
        print(
            f"Deployment completed: {len(files)} files processed, "
            f"{uploaded} uploaded, {skipped} skipped."
        )

    finally:
        close_quietly(ftp)


if __name__ == "__main__":
    main()
