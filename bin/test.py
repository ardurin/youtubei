import asyncio
import json
import sys
import youtubei


def main():
	success = False
	match sys.argv[1]:
		case 'audio':
			success = audio(sys.argv[1:])
		case 'search':
			success = search(sys.argv[1:])
		case 'suggestions':
			success = suggestions(sys.argv[1:])
	if not success:
		print('Usage:')
		print('  test.py {audio|search|suggestions} [options] <value>')
		print('')
		print('Options:')
		print('  -n <number>  Limit the number of items in the results')


def parse(arguments):
	size = None
	value = 1
	if len(arguments) == 4 and arguments[1] == '-n':
		try:
			size = int(arguments[2])
			value = 3
		except ValueError:
			return None
	elif len(arguments) != 2:
		return None
	return size, arguments[value]


def audio(arguments):
	options = parse(arguments)
	if options is None:
		return False
	size, value = options
	try:
		response = asyncio.run(youtubei.audio(value, size=size))
		print(json.dumps(response, default=vars))
	except youtubei.Error as error:
		print(error, file=sys.stderr)
	return True


def search(arguments):
	options = parse(arguments)
	if options is None:
		return False
	size, value = options
	try:
		response = asyncio.run(youtubei.search(value, size=size))
		print(json.dumps(response, default=vars))
	except youtubei.Error as error:
		print(error, file=sys.stderr)
	return True


def suggestions(arguments):
	options = parse(arguments)
	if options is None:
		return False
	size, value = options
	try:
		response = asyncio.run(youtubei.suggestions(value, size=size))
		print(json.dumps(response, default=vars))
	except youtubei.Error as error:
		print(error, file=sys.stderr)
	return True


main()
