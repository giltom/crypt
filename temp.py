import os
import re

#search = re.compile(r'\*\*\* ?END')
#search = re.compile(r'\*\*\*\s*START[^\n*]*\*\*\*\n')
#search = re.compile(r'^Produced by[\w ]*\n')
search = re.compile(r'\nEnd of .+$')

tot = len(os.listdir('gutenberg'))
cnt = 0
for fname in os.listdir('gutenberg'):
	path = os.path.join('gutenberg',fname)
	f = open(path, encoding='iso8859-1', mode='r')
	text = f.read()
	f.close()
	f = open(path, encoding='UTF-8', mode='w')
	f.write(text)
	f.close()
	cnt += 1
	if cnt % 50 == 0:
		print('{:.02%} complete.'.format(cnt/tot))
