"""Package only the consolidated repository, with verified file checksums."""
from pathlib import Path
import hashlib
import json
import tarfile
from .config import ROOT


def digest(stream):
    value=hashlib.sha256()
    for chunk in iter(lambda:stream.read(8*1024*1024),b''):value.update(chunk)
    return value.hexdigest()


def main():
    assert (ROOT/'results/REPORT.html').is_file(), 'Run python -m src.collect first'
    files=[ROOT/'README.md',ROOT/'.gitignore']
    for folder in ['src','results']:
        files.extend(sorted(p for p in (ROOT/folder).rglob('*') if p.is_file()
                            and '__pycache__' not in p.parts and p.suffix!='.pyc'))
    hashes={}
    for file in files:
        assert file.suffix!='.patch'
        with file.open('rb') as f:hashes[str(file.relative_to(ROOT))]=digest(f)
    manifest=ROOT/'CHECKSUMS.sha256'
    manifest.write_text(''.join(hashes[name]+'  '+name+'\n' for name in sorted(hashes)))
    archive=ROOT/'segmentation-sensitivity.tar.gz'
    temporary=archive.with_suffix('.gz.tmp')
    with tarfile.open(temporary,'w:gz',compresslevel=6) as bundle:
        for file in [*files,manifest]:bundle.add(file,arcname='segmentation-sensitivity/'+str(file.relative_to(ROOT)))
    found={}
    with tarfile.open(temporary,'r|gz') as bundle:
        for entry in bundle:
            if not entry.isfile():continue
            name=entry.name.split('/',1)[1]
            with bundle.extractfile(entry) as f:
                if name=='CHECKSUMS.sha256':assert f.read()==manifest.read_bytes()
                else:found[name]=digest(f)
    assert found==hashes,'Archive read-back checksum mismatch'
    temporary.replace(archive)
    with archive.open('rb') as f:sha=digest(f)
    (ROOT/(archive.name+'.sha256')).write_text(sha+'  '+archive.name+'\n')
    print(json.dumps(dict(archive=str(archive),MiB=archive.stat().st_size/2**20,files=len(files),sha256=sha,verification='all archived files verified'),indent=2))


if __name__=='__main__':main()
