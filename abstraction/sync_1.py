import hashlib
import os
import shutil
from pathlib import Path

BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def sync(source, dest):
    source_hashes = {}
    for folder, _, files in os.walk(source):
        for file in files:
            path = Path(folder) / file
            source_hashes[hash_file(path)] = file

    seen = set()

    for folder, _, files in os.walk(dest):
        for file in files:
            dest_path = Path(folder) / file
            dest_hash = hash_file(dest_path)
            seen.add(dest_hash)
            if hash in source_hashes:
                dest_path.remove()
            elif dest_hash in source_hashes and file != source_hashes[dest_hash]:
                shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])

    for src_hash, file in source_hashes.items():
        if src_hash not in seen:
            shutil.copy(Path(source) / file, Path(dest) / file)
