#!/usr/bin/python3
import os
import re
import sys

def check(job):
	include_pattern = re.compile(r'^#include\s+"(?P<path>.*)"$')
	name_pattern = re.compile(r'\w*::\w+')
	source = job.read()

	includes = re.finall(pattern = include_pattern, string = source)
	names = re.findall(pattern = name_pattern, string = source)
	names.sort()
	names = set(names)
	print('Found the following includes:')
	for include in includes:
		print(include)
	print(25 * '-' + '\n')
	for name in names:
		print('found name: {}'.format(
			name))


def main():
	try:
		with open(sys.argv[1]) as f:
			check(f)
	except IndexError e:
		print_usage()
	except IOError e:
		print('Could not open "{}"!'.format(sys.argv[1]))
		print_usage()

def print_usage():
	print("""
Usage: {} <file>

file: the source code or header file to be checked
""".format(sys.argv[0]))

if __name__ == '__main__':
	main()
