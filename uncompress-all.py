import os
import zipfile

for dirname, _, fnames in os.walk('gutenberg/aleph.gutenberg.org'):
    if len(fnames) > 0:
        fname = max(fnames, key=lambda f: os.path.getsize(os.path.join(dirname,f)))
        zipf = zipfile.ZipFile(os.path.join(dirname,fname))
        zipf.extractall(path='gutenberg')
        zipf.close()
for dirname, _, fnames in os.walk('gutenberg'):
	for fname in fnames:
		if fname.endswith('.txt'):
			os.rename(os.path.join(dirname,fname), os.path.join('gutenberg',fname))
