#!/usr/bin/env python3.2
import argparse
import os
import re
import sys

class Complaint:
	def __init__(self, header, insteadof=None):
		self.header = header
		self.insteadof = insteadof
	def alt(self):
		return bool(self.insteadof)

def check(job, prefix, include_path, quiet=False, reverse=False):
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

	def redundant_include(include):
		parts = include.split('::')
		first_parts = include[0:include.rfind('::')]
		for name in nameset:
			if name.startswith(include):
				return False
			if len(parts) > 2 and parts[-1] == parts[-2] and name.startswith(
				first_parts): #smart!
				return False
		return True

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
				return Complaint(header=base, insteadof=combining_header(base))
		else: #there might be a combining header somewhere up the file tree...
			result = check_recursively(base)
			if not result: #none found, still missing!
				ret = base
			else: #found what seems to be a combining header
				return Complaint(header=base, insteadof=result)

		ret = base #header must be missing, so report this

		if not header_exists(ret): #give up
			return False

		return Complaint(header=ret)

	#"absolute" C++ includes of the form: #include <foo/bar.hpp>, _NOT_ "foo/bar.hpp"!
	include_pattern = re.compile(r'^\s*#include\s+<(?P<file>.+)>$', re.M)
	name_pattern = re.compile('(' + prefix + '(?:::\\w+)+)', re.M)
	source_lines = job.readlines()

	includes = set()
	nameset = set()
	names = []

	line_no = 1
	for line in source_lines:
		for match in re.finditer(pattern = name_pattern, string = line):
			if not match.group() in nameset:
				nameset.add(match.group())
				names.append(
					{"row":line_no, "col":match.start(), "text":match.group()})
		m = re.match(pattern = include_pattern, string = line)
		if m:
			header = m.group('file')
			if header in includes:
				print("Duplicate header file detected! ({}.hpp)".format(header), file=sys.stderr)
			if header.startswith(prefix + '/'):
				includes.add(header)
		line_no += 1
	
	if not quiet:
		print('checking source file {}.'.format(job.name))

	base_format = '{filename}:{row}:{col} warning: '
	message_format = base_format + 'expected {header}.hpp to be included because of {name}'
	alt_message_format = base_format + 'including {header}.hpp instead of {alt} would be more specific for {name}'
	redundant_format = base_format + '{include} appears to be unused'
	quiet_format = '#include <{}.hpp>'

	messages = []
	if reverse:
		for include in includes:
			include = include.rstrip('.hpp')
			rep = include.replace('/', '::')
			complaint = redundant_include(rep)
			if complaint:
				if quiet:
					messages.append(quiet_format.format(include))
				else:
					messages.append(
						redundant_format.format(
							filename=job.name,
							row=0,
							col=0,
							include=include))
	else:
		for occur in names:
			rep = occur['text'].replace('::', '/') 
			complaint = missing_include(rep)
			if complaint:
				if quiet:
					messages.append(
						quiet_format.format(
							complaint.header))
				else:
					if complaint.alt():
						messages.append(
							alt_message_format.format(
								filename=job.name,
								row=occur['row'],
								col=occur['col'],
								alt=complaint.insteadof,
								header=complaint.header,
								name=occur['text']))
					else:
						messages.append(
							message_format.format(
								filename=job.name,
								row=occur['row'],
								col=occur['col'],
								header=complaint.header,
								name=occur['text']))

	if quiet:
		messages.sort()
	for msg in messages:
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
		nargs='+',
		help='target file(s) you want checked')
	parser.add_argument(
		'-q', '--quiet',
		action='store_true',
		help='only output missing include statementes to be used directly in the header/source file')
	parser.add_argument(
		'-r', '--reverse',
		action='store_true',
		help='instead of checking for missing headers, check if any existing ones can be removed')
	args = parser.parse_args()

	for target in args.file:
		try:
			with open(target) as f:
				check(f, prefix=args.prefix[0], include_path=args.include_path[0], quiet=args.quiet, reverse=args.reverse)
		except IOError as e:
			print(e)

if __name__ == '__main__':
	main()
