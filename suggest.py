#!/usr/bin/env python3.2
import argparse
import os
import re
import sys

def check(job, prefix, include_path, quiet=False):
	def parent(name):
		return os.path.normpath(
			name + '/' + os.path.pardir)

	def header_exists(name):
		return os.path.exists(
			os.path.join(
				include_path,
				name + '.hpp'))

	def combining_header(name):
		return parent(name) +	'/' +	parent(name).split('/')[-1] + '.hpp'

	def check_recursively(name):
		if name.rstrip('/') == prefix:
			return False
		if combining_header(name) in includes:
			return combining_header(name)
		else:
			return check_recursively(parent(name))

	def missing_include(name):
		base = ''
		if header_exists(name):
			base = name
		else:
			base = parent(name)

		for suffix in ['.hpp', '_fwd.hpp','_decl.hpp','_impl.hpp']:
			if base + suffix in includes:
				return False

		if base == name: #a/b/c.hpp exists (for a::b::c) but not included!
			if combining_header(base) in includes:
				raise Warning(
					'More granular include possible:\n\t{}\tinstead of\n\t{}'.format(
						base + '.hpp',
						combining_header(base)))
		else: #there might be a combining header somewhere up the file tree...
			result = check_recursively(base)
			if not result: #none found, still missing!
				return base + '.hpp'
			else: #found what seems to be a combining header
				raise Warning(
					'More granular include possible:\n\t{}\tinstead of\n\t{}'.format(
						base + '.hpp',
						result + '.hpp'))

		if not header_exists(base): #give up
			return False

		return base + '.hpp' #header must be missing, so report this

	#"absolute" C++ includes of the form: #include <foo/bar.hpp>, _NOT_ "foo/bar.hpp"!
	include_pattern = re.compile(r'^\s*#include\s+<(?P<file>.+)>$', re.M)
	name_pattern = re.compile('(' + prefix + '(?:::\\w+)+)', re.M)
	source = job.read()

	includes = re.findall(pattern = include_pattern, string = source)
	names = re.findall(pattern = name_pattern, string = source)
	names = set(names)

	if not quiet:
		print('checking source file {}.'.format(job.name))

	messages = []
	message_format = ' *\tMissing include: {}\n'
	if quiet:
		message_format = '#include <{}>'
	for name in names:
		rep = name.replace('::', '/') 
		try:
			rep = missing_include(rep)
			if rep:
				messages.append(
						message_format.format(rep))
		except Warning as w:
			if not quiet:
				messages.append(' ?\t{}\n'.format(w))
	
	for msg in set(messages):
		print(msg)

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
		nargs='*',
		help='target file(s) you want checked')
	parser.add_argument(
		'-q', '--quiet',
		action='store_true',
		help='only output missing include statementes to be used directly in the header/source file')
	args = parser.parse_args()

	for target in args.file:
		try:
			with open(target) as f:
				check(f, prefix=args.prefix[0], include_path=args.include_path[0], quiet=args.quiet)
		except IOError as e:
			print(e)

if __name__ == '__main__':
	main()
