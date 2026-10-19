"""Download original Elliptic++ address data, pinned and SHA-256 checked."""
import argparse
import hashlib
import urllib.request
from pathlib import Path

COMMIT = '08fe6aded83afb97bf5a79a71130f542ca783c2e'
FILES = {
 'wallets_classes.csv': (30421134, '4e5132c99f941666bf1fefd4100a1428d339c9252ec6987909e1adf8eac902f9'),
 'wallets_features.csv': (606463522, '317daca2810c355ddfdb8c0dab34cf11d1aa90567fe975090c7e5a901386eb77'),
}


def download(destination, name):
    size, expected = FILES[name]
    target = destination / name
    if target.exists():
        with target.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        if target.stat().st_size == size and digest == expected:
            print(name, 'already verified', flush=True)
            return
        raise ValueError(f'Existing file failed validation: {target}')
    temporary = destination / (name + '.part')
    url = f'https://media.githubusercontent.com/media/git-disl/EllipticPlusPlus/{COMMIT}/Actors%20Dataset/{name}'
    digest = hashlib.sha256()
    count = 0
    with urllib.request.urlopen(url, timeout=45) as response, temporary.open('xb') as f:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            f.write(block)
            digest.update(block)
            count += len(block)
    if count != size or digest.hexdigest() != expected:
        temporary.unlink()
        raise ValueError(f'Download failed integrity validation: {name}')
    temporary.rename(target)
    print(name, count, 'SHA-256 verified', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--labels-only', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        if args.labels_only and name != 'wallets_classes.csv':
            continue
        download(args.output, name)
