import os
import re

for fname in os.listdir('gutenberg'):
	f = open(os.path.join('gutenberg',fname))
	try:
		text = f.read()
		text.index('***\n\n\n\n\n')
	except Exception as e:
		print(e)
		print('in:',fname)
	finally:
		f.close()
