#!/usr/bin/python3
import os
import re
import sys

def main():
	include_pattern = re.compile(r'^#include\s+"(?P<path>.*)"$')
	include_path = os.getcwd()
	for roots, dirs, files in os.walk(include_path):
		for job in files:
			job = os.path.join(roots, job)
			print('--- Processing {}'.format(job))

			if re.match(r'.*\.[ch]pp$', job):
				with open(job, 'r') as f:
					lines = f.readlines()
					out_lines = []
					for line in lines:
						m = include_pattern.match(line)
						if m:
							path = m.group('path')
							newpath = os.path.relpath(
									os.path.normpath(
										os.path.join(
											os.path.dirname(os.path.abspath(job)),
											path)),
									include_path)
							line = '#include <{}>\n'.format(newpath)
							print(
							'"{}"\t=> <{}>'.format(
								path,
								newpath))
						out_lines.append(line)
				try:
					if sys.argv[1] == '-x':
						with open(job, 'w') as f:
							for line in out_lines:
								f.write(line)
				except IndexError:
					pass
			print()

if __name__ == '__main__':
	main()
