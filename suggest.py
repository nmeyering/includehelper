#!/usr/bin/python3
import argparse
import os
import re
import sys

def check(job, prefix, include_path):
	def missing_include(name):
		tmp = os.path.join(
			include_path,
			name + '.hpp')

		base = ''
		if os.path.exists(tmp):
			base = name
		else:
			base = os.path.normpath(
				name + '/' + os.path.pardir)

		if not os.path.exists(
				os.path.join(
					include_path,
					base + '.hpp')):
			raise Warning('possibly missing: ' + base + '.hpp')

		for suffix in ['.hpp', '_fwd.hpp','_decl.hpp','_impl.hpp']:
			if base + suffix in includes:
				return False

		return base + '.hpp'


	#C++ includes of the form: #include <foo/bar.hpp>, _NOT_ "foo/bar.hpp"!
	include_pattern = re.compile(r'^\s*#include\s+<(?P<file>.+)>$', re.M)
	name_pattern = re.compile('(' + prefix + '(?:::\\w+)+)', re.M)
	source = job.read()

	includes = re.findall(pattern = include_pattern, string = source)
	names = re.findall(pattern = name_pattern, string = source)
	names = set(names)

	print('[' + 25 * '-')
	print('checking source file {}.'.format(job.name))
	print()

	"""
	for name in names:
		print(name)
	print()

	print('Found {} names.'.format(
		len(names)))
	"""
	print('The following includes might be missing:\n')

	#print(includes)
	for name in names:
		rep = name.replace('::', '/') 

		try:
			rep = missing_include(rep)
		except Warning as w:
			print('Warning: {}.'.format(w))

		if rep:
			print(rep)

	print(25 * '-' + ']\n')

def main():
	parser = argparse.ArgumentParser(
		description='Try to find missing or superfluous include statements in a given header or source file.')
	parser.add_argument(
		'prefix',
		type=str,
		nargs=1,
		help='the first part of symbols/names to look for (a.k.a. the "foo" in foo::bar::baz)')
	parser.add_argument(
		'include_path', 
		type=str, 
		nargs=1,
		help='the path below which to look for header files ("/tmp/include" if your header paths are of the form "/tmp/include/foo/bar/baz.hpp")')
	parser.add_argument(
		'file',
		type=str,
		nargs='+',
		help='target file(s) you want checked')
	args = parser.parse_args()

	for target in args.file:
		try:
			with open(target) as f:
				check(f, prefix=args.prefix[0], include_path=args.include_path[0])
		except IOError as e:
			print(e)

if __name__ == '__main__':
	main()
