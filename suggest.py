#!/usr/bin/python3
import os
import re
import sys

def check(job, prefix, include_path=os.getcwd()):
	def missing_include(name):
		if name + '.hpp' in includes:
			return False
		tmp = name + '.hpp'
		if os.path.exists(tmp):
			return True
		tmp =	os.path.normpath(
			name + '/' + os.path.pardir)
		if tmp + '.hpp' in includes:
			return False
		for suffix in ['.hpp', '_fwd.hpp','_decl.hpp','_impl.hpp']:
			if tmp + suffix in includes:
				return False
			if os.path.exists(tmp + suffix): #(and _not_ in includes)
				return True
		"""
		if not os.path.exists(tmp + '.hpp'):
			raise Exception("Missing header file for " + name)
		"""
		return True

	#C++ includes of the form: #include <foo/bar.hpp>, _NOT_ "foo/bar.hpp"!
	include_pattern = re.compile(r'^\s*#include\s+<(?P<file>.+)>$', re.M)
	name_pattern = re.compile(r'({}(?:::\w+)+)'.format(prefix), re.M)
	source = job.read()

	includes = re.findall(pattern = include_pattern, string = source)
	names = re.findall(pattern = name_pattern, string = source)
	names = set(names)

	print(25 * '-')
	print('checking source file {}.'.format(job.name))
	print(25 * '-' + '\n')

	for name in names:
		print(name)
	print()

	print('Found {} names.'.format(
		len(names)))
	print('The following includes might be missing:\n')

	#print(includes)
	for name in names:
		rep = name.replace('::', '/') 
		if missing_include(rep):
			print("#include <{}.hpp>".format(rep))

	print(25 * '-' + '\n')

def main():
	try:
		with open(sys.argv[1]) as f:
			if len(sys.argv) <= 3:
				check(f, sys.argv[2])
			else:
				check(f, sys.argv[2], sys.argv[3])
	except IndexError:
		print_usage()
	except IOError as e:
		print('Could not open "{}"!'.format(sys.argv[1]))
		print(e)
		print_usage()

def print_usage():
	print("""
Usage: {} <file> [<include_path>]

file: the source code or header file to be checked
include_path: where to look for header files
""".format(sys.argv[0]))

if __name__ == '__main__':
	main()
