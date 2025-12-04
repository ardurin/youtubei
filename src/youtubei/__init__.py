from aiohttp import ClientSession
import json

ALBUM = 0
TRACK = 1

ADDRESS = 'https://music.youtube.com/youtubei/v1{}?prettyPrint=false'


class InnertubeError(Exception):
	pass


class Track:
	def __init__(self, code: str, name: str, creator: str, image: str, duration: str):
		self.code = code
		self.name = name
		self.creator = creator
		self.image = image
		self.duration = duration


async def audio(
	code: str, size: int | None = None, session: ClientSession | None = None
) -> list[str]:
	if session is None:
		async with ClientSession() as session:
			return await _audio(code, size, 'audio/mp4', session)
	return await _audio(code, size, 'audio/mp4', session)


async def _audio(
	code: str, size: int | None, mime: str, session: ClientSession
) -> list[str]:
	body = json.dumps(
		{
			'context': {
				'client': {
					'clientName': 'ANDROID',
					'clientVersion': '20.10.38',
				}
			},
			'videoId': code,
		}
	)
	headers = {
		'Accept-language': 'en-US,en',
		'Content-type': 'application/json',
		'Host': 'music.youtube.com',
		'Origin': 'https://music.youtube.com',
		'Referer': 'https://music.youtube.com/',
		'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 11) gzip',
	}
	response = await session.post(ADDRESS.format('/player'), data=body, headers=headers)
	if response.status != 200:
		raise InnertubeError(f'{response.status} HTTP status')
	response = await response.text()
	data = json.loads(response)
	status = data['playabilityStatus']['status']
	if status != 'OK':
		raise InnertubeError(status)
	sources = []
	for source in data['streamingData']['adaptiveFormats']:
		if source['mimeType'].startswith(mime):
			sources.append(source['url'])
		if len(sources) == size:
			break
	return sources


async def search(
	value: str,
	size: int | None = None,
	session: ClientSession | None = None,
) -> list[Track]:
	if session is None:
		async with ClientSession() as session:
			return await _search(value, TRACK, size, session)
	return await _search(value, TRACK, size, session)


async def _search(
	value: str, data: int, size: int | None, session: ClientSession
) -> list[Track]:
	match data:
		case 0:
			parameters = 'EgWKAQIYAQ=='
		case _:
			parameters = 'EgWKAQIIAQ=='
	body = json.dumps(
		{
			'context': {
				'client': {
					'clientName': 'WEB_REMIX',
					'clientVersion': '1.20251006.03.00',
				}
			},
			'params': parameters,
			'query': value,
		}
	)
	headers = {
		'Accept-language': 'en-US,en',
		'Content-type': 'application/json',
		'Host': 'music.youtube.com',
		'Origin': 'https://music.youtube.com',
		'Referer': 'https://music.youtube.com/',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3',
	}
	response = await session.post(ADDRESS.format('/search'), data=body, headers=headers)
	if response.status != 200:
		raise InnertubeError(f'{response.status} HTTP status')
	response = await response.text()
	response = json.loads(response)
	if data != TRACK:
		return []
	tracks = []
	sections = response['contents']['tabbedSearchResultsRenderer']['tabs'][0]
	sections = sections['tabRenderer']['content']['sectionListRenderer']['contents']
	for section in sections:
		if 'musicShelfRenderer' not in section:
			continue
		for entry in section['musicShelfRenderer']['contents']:
			values = entry['musicResponsiveListItemRenderer']['flexColumns']
			creator = values[1]['musicResponsiveListItemFlexColumnRenderer']['text'][
				'runs'
			][0]['text']
			if creator in {
				'Album',
				'Artist',
				'Episode',
				'Playlist',
				'Podcast',
				'Profile',
				'Video',
			}:
				continue
			code = values[0]['musicResponsiveListItemFlexColumnRenderer']['text'][
				'runs'
			][0]['navigationEndpoint']['watchEndpoint']['videoId']
			name = values[0]['musicResponsiveListItemFlexColumnRenderer']['text'][
				'runs'
			][0]['text']
			image = entry['musicResponsiveListItemRenderer']['thumbnail'][
				'musicThumbnailRenderer'
			]['thumbnail']['thumbnails'][0]['url']
			duration = values[1]['musicResponsiveListItemFlexColumnRenderer']['text'][
				'runs'
			][-1]['text']
			tracks.append(Track(code, name, creator, image, duration))
			if len(tracks) == size:
				return tracks
	return tracks


async def suggestions(
	value: str, size: int | None = None, session: ClientSession | None = None
) -> list[str]:
	if session is None:
		async with ClientSession() as session:
			return await _suggestions(value, size, session)
	return await _suggestions(value, size, session)


async def _suggestions(
	value: str, size: int | None, session: ClientSession | None
) -> list[str]:
	data = json.dumps(
		{
			'context': {
				'client': {
					'clientName': 'WEB_REMIX',
					'clientVersion': '1.20251006.03.00',
				}
			},
			'input': value,
		}
	)
	headers = {
		'Accept-language': 'en-US,en',
		'Content-type': 'application/json',
		'Host': 'music.youtube.com',
		'Origin': 'https://music.youtube.com',
		'Referer': 'https://music.youtube.com/',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3',
	}
	response = await session.post(
		ADDRESS.format('/music/get_search_suggestions'), data=data, headers=headers
	)
	if response.status != 200:
		raise InnertubeError(f'{response.status} HTTP status')
	response = await response.text()
	response = json.loads(response)
	suggestions = []
	for value in response['contents'][0]['searchSuggestionsSectionRenderer'][
		'contents'
	]:
		suggestions.append(
			value['searchSuggestionRenderer']['navigationEndpoint']['searchEndpoint'][
				'query'
			]
		)
		if len(suggestions) == size:
			break
	return suggestions
