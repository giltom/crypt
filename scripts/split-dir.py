import argparse
import os
import itertools

parser = argparse.ArgumentParser()
parser.add_argument('dir', help='the directory to split.')
parser.add_argument('n', type=int, help='number of directories to split to.')
args = parser.parse_args()

def pjoin(*paths):
    return os.path.join(*paths)

all_fnames = [fn for fn in os.listdir(args.dir) if os.path.isfile(pjoin(args.dir,fn))]
for i in range(1,args.n+1):
    try:
        os.mkdir(pjoin(args.dir,str(i)))
    except FileExistsError:
        pass

for _,fnames in itertools.groupby(all_fnames, key=lambda f:all_fnames.index(f)//args.n):
    for i,fname in enumerate(fnames):
        print(pjoin(args.dir,fname))
        os.rename(pjoin(args.dir,fname), pjoin(args.dir,str(i+1),fname))
