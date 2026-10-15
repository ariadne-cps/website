#!/usr/bin/env python3

import ftplib
import os
import posixpath
import socket
import time
from pathlib import Path

HOST = "ftp.ariadne-cps.org"
REMOTE_ROOT = "/www.ariadne-cps.org"
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


def ensure_dir(ftp, remote_dir):
    current = ""
    for part in remote_dir.strip("/").split("/"):
        if not part:
            continue
        current += "/" + part
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            # "Already exists" is server-specific. Verify that the path is
            # actually a directory instead of depending on a particular code.
            previous = ftp.pwd()
            ftp.cwd(current)
            ftp.cwd(previous)


def remote_size(ftp, remote_path):
    try:
        ftp.voidcmd("TYPE I")
        return ftp.size(remote_path)
    except ftplib.error_perm:
        return None


def close_quietly(ftp):
    if ftp is None:
        return
    try:
        ftp.quit()
    except (ftplib.all_errors, OSError, EOFError):
        try:
            ftp.close()
        except Exception:
            pass


def main():
    files = sorted(path for path in LOCAL_ROOT.rglob("*") if path.is_file())
    if not files:
        raise RuntimeError("No files found under public/")

    ftp = None
    try:
        ftp = connect()

        for local_path in files:
            rel = local_path.relative_to(LOCAL_ROOT).as_posix()
            remote_path = posixpath.join(REMOTE_ROOT, rel)
            remote_dir = posixpath.dirname(remote_path)
            local_size = local_path.stat().st_size

            # Hugo copies static binary bottles on every build, which makes an
            # mtime-based deploy think they changed. They are immutable release
            # artifacts, so equal size is sufficient to avoid re-uploading them.
            if rel.startswith("cellar/"):
                try:
                    if remote_size(ftp, remote_path) == local_size:
                        print(f"SKIP {remote_path} ({local_size} bytes, already present)")
                        continue
                except (ftplib.all_errors, OSError, EOFError, socket.timeout):
                    close_quietly(ftp)
                    ftp = connect()

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
                    break

                except (ftplib.all_errors, OSError, EOFError, socket.timeout) as exc:
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

        print(f"Deployment completed: {len(files)} local files processed.")

    finally:
        close_quietly(ftp)


if __name__ == "__main__":
    main()
