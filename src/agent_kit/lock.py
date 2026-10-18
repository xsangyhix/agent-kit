"""Read and write the kit lock (design §7)."""

import hashlib
import json
from pathlib import Path

LOCK_NAME = ".agents/kit.lock"
REQUIRED_KEYS = ("agents_block", "files", "harness", "kit_version")


def file_hash(path):
    """Return the SHA-256 hex of a file's bytes with CRLF normalised to LF."""
    return _hash_bytes(Path(path).read_bytes())


def text_hash(text):
    """Return the SHA-256 hex of text with CRLF normalised to LF."""
    return _hash_bytes(text.encode("utf-8"))


def _hash_bytes(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def lock_path(root):
    return Path(root) / LOCK_NAME


def read_lock(root):
    """Return the lock as a dict, or None when the file is missing."""
    path = lock_path(root)
    if not path.is_file():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{path}: not valid JSON ({error})") from error

    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")

    for key in REQUIRED_KEYS:
        if key not in data:
            raise ValueError(f"{path}: missing key {key!r}")

    return data


def write_lock(root, kit_version, harness, files, agents_block_hash):
    """Write the kit lock in the documented format."""
    data = {
        "agents_block": agents_block_hash,
        "files": {
            Path(name).as_posix(): digest
            for name, digest in files.items()
        },
        "harness": harness,
        "kit_version": kit_version,
    }
    path = lock_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
