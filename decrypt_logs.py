"""解密日志文件。用法: python decrypt_logs.py data/logs/push.log --key \"密钥\""""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from log_crypto import decrypt_line


def print_decrypted(path: Path, secret: str) -> None:
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                print(decrypt_line(raw, secret))
            except Exception as exc:
                print(f"[无法解密] {raw[:40]}... ({exc})", file=sys.stderr)


def follow_decrypted(path: Path, secret: str) -> None:
    with path.open(encoding="utf-8") as handle:
        handle.seek(0, 2)
        while True:
            line = handle.readline()
            if not line:
                time.sleep(0.5)
                continue
            line = line.strip()
            if not line:
                continue
            try:
                print(decrypt_line(line, secret))
            except Exception as exc:
                print(f"[无法解密] ({exc})", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="解密 push.log")
    parser.add_argument("log_file", type=Path, help="加密日志路径")
    parser.add_argument("--key", required=True, help="与 app.log_encrypt.key 相同")
    parser.add_argument("-f", "--follow", action="store_true", help="类似 tail -f")
    args = parser.parse_args()

    if not args.log_file.is_file():
        print(f"文件不存在: {args.log_file}", file=sys.stderr)
        sys.exit(1)

    if args.follow:
        follow_decrypted(args.log_file, args.key)
    else:
        print_decrypted(args.log_file, args.key)


if __name__ == "__main__":
    main()
