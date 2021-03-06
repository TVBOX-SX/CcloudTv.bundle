######################################################################################
#
#	CcloudTv
#
######################################################################################
import common, common_fnc, updater, time, transcoder, share, myxmltvparser, guide_online, playback
import re, urllib2, sys, os, json
import datetime as DT
from datetime import datetime
from DumbTools import DumbKeyboard

# Set global variables
TITLE = common.TITLE
PREFIX = common.PREFIX
ART = "art-default.jpg"
ICON_DISPLAY = "icon-ccloudtv-main.png"
ICON = "icon-ccloudtv.png"
ICON_VIDEO = "icon-video.png"
ICON_AUDIO = "icon-audio.png"
ICON_SERIES = "icon-series.png"
ICON_SERIES_UNAV = "icon-series-unav.png"
ICON_GENRES = "icon-genres.png"
ICON_GENRE = "icon-genre.png"
ICON_LANGUAGES = "icon-languages.png"
ICON_COUNTRIES = "icon-countries.png"
ICON_LISTVIEW = "icon-listview.png"
ICON_PAGE = "icon-paged.png"
ICON_PAGELIST = "icon-pagelist.png"
ICON_NEXT = "icon-next.png"
ICON_SEARCH = "icon-search.png"
ICON_SEARCH_QUEUE = "icon-search-queue.png"
ICON_PIN = "icon-pin.png"
ICON_BOOKMARK = "icon-bookmark.png"
ICON_LOCK = "icon-lock.png"
ICON_UNLOCK = "icon-unlock.png"
ICON_PREFS = "icon-prefs.png"
ICON_UPDATE = "icon-update.png"
ICON_UPDATE_NEW = "icon-update-new.png"
ICON_RECENT = "icon-recent.png"
ICON_SHARE = "icon-share.png"
ICON_UNKNOWN = "icon-unknown.png"
ICON_GUIDE = "icon-guide.png"
ICON_IMPORTED = "icon-imported.png"
ICON_OK = "icon-ok.png"
ICON_WARNING = "icon-warning.png"
ICON_CANCEL = "icon-error.png"
ICON_CLEAR = "icon-clear.png"
ICON_UPLOAD = "icon-upload.png"
ICON_DISCOVER = "icon-discover.png"
ICON_DK_ENABLE = "icon-dumbKeyboardE.png"
ICON_DK_DISABLE = "icon-dumbKeyboardD.png"

# using dictionary for temp. storing channel listing
# Dict['items_dict'] = {}
Dict['PlexShareThreadAlive'] = 'False'

# set clients thats should display content as list
LIST_VIEW_CLIENTS = ['Android','iOS']

# set clients that dont update menu as expected
NONUPDATE_VIEW_CLIENTS = ['Android']

# genre listing
GENRE_ARRAY = []

# language listing
LANGUAGE_ARRAY = []
LANGUAGE_ARRAY_POP = ['English','Spanish','Hindi','Russian']

# country listing
COUNTRY_ARRAY = []
COUNTRY_ARRAY_POP = ['US','UK','IN','RU']

# page data for verifying sharability
CCLOUD_PAGE_DATA = []
del CCLOUD_PAGE_DATA[:]

# cache discovered links to reduce load on Google API
CACHE_DISCOVER = []
del CACHE_DISCOVER[:]

# cache links
CACHE_LINKS = []
del CACHE_LINKS[:]

CCLOUDTV_BOOL = []
IMPORT_BOOL = []
TIMEOUT_BOOL = []

BASE_URL = ""
CCLOUDTV_DB_URL = [common_fnc.decode(common_fnc.decode("YUhSMGNEb3ZMM0JzWlhndVkyTnNaQzVwYnc9PQ==")) , common_fnc.decode(common_fnc.decode("YUhSMGNEb3ZMM1JwYm5rdVkyTXZVR3hsZUE9PQ==")) ,  common_fnc.decode(common_fnc.decode("YUhSMGNEb3ZMM2d1WTI4dlpHSmphREF5"))]

PLEXSHARE_URL = common_fnc.decode(common_fnc.decode("YUhSMGNEb3ZMM1JwYm5rdVkyTXZVR3hsZUZOb1lYSmw="))

US_EST_UTC_SHIFT = 5
NO_OF_THREADS = 2



######################################################################################

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_SERIES)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_SERIES)
	VideoClipObject.art = R(ART)
	
	HTTP.ClearCache()
	#HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'
	if Prefs['use_transcoder']:
		del transcoder.VLC_INSTANCES[:]
		transcoder.GetAllExtVlcInstances()
		
	if Prefs['debug']:
		Log(common.TITLE + ' v.' + common.VERSION)
	
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON_DISPLAY)
def MainMenu():
		
	if Prefs['debug']:
		Log('Plex-Identifier: ' + common_fnc.getSession())
		Log('Plex-Product: ' + common_fnc.getProduct())
		Log('Plex-Platform: ' + common_fnc.getPlatform())
		Log('Plex-Device: ' + common_fnc.getDevice())
		Log('Plex-DeviceName: ' + common_fnc.getDeviceName())
		
	oc = ObjectContainer(title2=TITLE)
	ChHelper = ' (Refresh List)'
	ChHelper2 = ' (Initialize this Channel List once before Search, Search Queue and Bookmark menu are made available)'

	if len(CACHE_LINKS) > 0 and len(CCLOUDTV_BOOL) > 0:
		ChHelper = ''
		ChHelper2 = ' - Listing retrieved. ' + CCLOUDTV_BOOL[0] + ' cCloud TV Channels.'
	oc.add(DirectoryObject(
		key = Callback(ShowMenu, title = 'Main Menu'), 
		title = 'Channels' + ChHelper, 
		summary = 'Channels' + ChHelper2,
		thumb = R(ICON)))
			
	oc.add(DirectoryObject(key = Callback(Pins, title='My Channel Pins'), title = 'My Channel Pins', summary = 'Shows Pinned Channels. Pins are based on Channel Name, Category, Language and Country including channel url. This is NOT useful when a Channel url is token based or is updated frequently. It also does not require the cCloud TV server listing to be retrieved.', thumb = R(ICON_PIN)))
	
	oc.add(DirectoryObject(key = Callback(Options, title='Device Options'), title = 'Device Options', summary = 'Device Specific Options like Access Control, Preferences Menu and Enabling DumbKeyboard', thumb = R(ICON_PREFS)))
	
	if updater.update_available()[0]:
		oc.add(DirectoryObject(
			key = Callback(updater.menu, title='Update Plugin'), 
			title = 'Update (New Available)', 
			summary = 'A New Update is Available',
			thumb = R(ICON_UPDATE_NEW)))
	else:
		oc.add(DirectoryObject(
			key = Callback(updater.menu, title='Update Plugin'), 
			title = 'Update (Running Latest)', 
			summary = 'No Update Available',
			thumb = R(ICON_UPDATE)))
	
	return oc

@route(PREFIX + "/options")
def Options(title):

	oc = ObjectContainer(title2=title)
	session = common_fnc.getSession()
	
	if Prefs['glob_prefs']:
		oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
		
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		oc.add(DirectoryObject(key = Callback(ToggleDumbKeyboard), title = 'Enable DumbKeyboard', summary='Click here to Enable DumbKeyboard for this Device', thumb = R(ICON_DK_ENABLE)))
	else:
		oc.add(DirectoryObject(key = Callback(ToggleDumbKeyboard), title = 'Disable DumbKeyboard', summary='Click here to Disable DumbKeyboard for this Device', thumb = R(ICON_DK_DISABLE)))
		
	oc.add(DirectoryObject(key = Callback(DefineAccessControl, title='Access Control'), title = 'Access Control', summary='Set/Remove Device Specific Temporary Access', thumb = R(ICON_LOCK)))
	
	return oc
	
@route(PREFIX + "/UseDumbKeyboard")
def UseDumbKeyboard():
	session = common_fnc.getSession()
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		return False
	else:
		return True

@route(PREFIX + "/ToggleDumbKeyboard")
def ToggleDumbKeyboard():
	# CACHE_LINKS = {}
	session = common_fnc.getSession()
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		Dict['ToggleDumbKeyboard'+session] = 'enabled'
	else:
		Dict['ToggleDumbKeyboard'+session] = 'disabled'

	Dict.Save()
	return ObjectContainer(header='DumbKeyboard', message='DumbKeyboard has been ' + Dict['ToggleDumbKeyboard'+session] + ' for this device.', title1='DumbKeyboard')

	
@route(PREFIX + "/verifyaccess")
def VerifyAccess():
	session = common_fnc.getSession()
	if not Prefs['show_adult'] and Dict['AccessPin'+session] != Prefs['access_pin']:
		return False
	else:
		return True
	
@route(PREFIX + "/defineaccesscontrol")
def DefineAccessControl(title):
	oc = ObjectContainer(title2=title)
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, SetTempKey,
				dktitle = 'Set Access Key',
				dkthumb = R(ICON_UNLOCK)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(SetTempKey), thumb = R(ICON_UNLOCK), title='Set Access Key', summary='Set Temporary Access Key', prompt='Set Access..'))
	oc.add(DirectoryObject(key = Callback(ClearAccessKey), thumb = R(ICON_LOCK), title='Clear Access Key', summary='Clear Temporary Access Key'))
	return oc
	
@route(PREFIX + "/settempkey")
def SetTempKey(query):
	# CACHE_LINKS = {}
	session = common_fnc.getSession()
	Dict['AccessPin'+session] = query;
	Dict.Save()
	return ObjectContainer(header='Access Key', message='Your Temporary Access Key ' + query + ' has been saved.', title1='Acess Key Saved')

@route(PREFIX + "/noaccess")
def NoAccess():
	return ObjectContainer(header='Update Plugin', message='Requires Parental Access Control. Enable via Channel Preferences or set under Access Control Menu first.')
	
@route(PREFIX + "/clearaccesskey")
def ClearAccessKey():
	# CACHE_LINKS = {}
	session = common_fnc.getSession()
	Dict['AccessPin'+session] = '-';
	Dict.Save()
	return ObjectContainer(header='Access Key', message='Your Temporary Access Key has been cleared.', title1='Access Cleared')
	
@route(PREFIX + "/showMenu")
def ShowMenu(title, additionalURL=None):

	oc = ObjectContainer(title2=title)
	
	abortBool = RefreshListing(False, additionalURL)

	if abortBool:
		return ObjectContainer(header=title, message='No cCloud TV Channels Available. Server seems down !', title1='Server Down')

	oc.add(DirectoryObject(key = Callback(DisplayList, title='List View'), title = 'List View', summary = 'Displays the full channel list as a single listing', thumb = R(ICON_LISTVIEW)))
	oc.add(DirectoryObject(key = Callback(DisplayPage, title='Page View', iRange=0), title = 'Page View', summary = 'Displays the full channel list as 10 items per page', thumb = R(ICON_PAGE)))
	oc.add(DirectoryObject(key = Callback(DisplayPageList, title='Page List'), title = 'Page List', summary = 'Displays the full channel list as numbered pages with 10 items each', thumb = R(ICON_PAGELIST)))
	oc.add(DirectoryObject(key = Callback(DisplayGenreMenu, title='Category'), title = 'Category', summary = 'Displays the full channel list organized by Category', thumb = R(ICON_GENRES)))
	oc.add(DirectoryObject(key = Callback(DisplayLanguageMenu, title='Language'), title = 'Language', summary = 'Displays the full channel list organized by Language', thumb = R(ICON_LANGUAGES)))
	oc.add(DirectoryObject(key = Callback(DisplayCountryMenu, title='Country'), title = 'Country', summary = 'Displays the full channel list organized by Country', thumb = R(ICON_COUNTRIES)))
	oc.add(DirectoryObject(key = Callback(ShowRecentMenu, title='Recent'), title = 'Recent', summary = 'Displays the channel list based on date when channel was added/updated using selectable date-filters', thumb = R(ICON_RECENT)))
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue'), title = 'Search Queue', summary='Search using previously used search terms', thumb = R(ICON_SEARCH_QUEUE)))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title='My Channel Bookmarks'), title = 'My Channel Bookmarks', summary = 'Shows Bookmarked Channels. Bookmarks are based on Channel Name, Category, Language and Country and does not store channel url. This is useful when a Channel url is token based or is updated frequently.', thumb = R(ICON_BOOKMARK)))
	if VerifyAccess():
		if len(IMPORT_BOOL) > 0 and Dict['ParsingPrivThreadAlive'] == 'False':
			oc.add(DirectoryObject(key = Callback(ShowMenu2, title='Imported ('+IMPORT_BOOL[0]+') Channels'), title = IMPORT_BOOL[0]+' Imported Channels', summary = IMPORT_BOOL[0] + ' Channels were Imported using your Private List(s)', thumb = R(ICON_IMPORTED)))
		elif Dict['ParsingPrivThreadAlive'] <> None and Dict['ParsingPrivThreadAlive'] == 'True':
			oc.add(DirectoryObject(key = Callback(ShowMenu2, title='Imported Channels'), title = 'Imported Channels', summary = 'Imported Channels from Private List(s) will show up here', thumb = R(ICON_IMPORTED)))
		oc.add(DirectoryObject(
			key = Callback(Discover), 
			title = 'Discover Channels', 
			summary = 'Discover Channels from online Pastebin.com listings',
			thumb = R(ICON_DISCOVER)))
	oc.add(DirectoryObject(key = Callback(RefreshListing, doRefresh=True, additionalURL=additionalURL), title = 'Refresh Channels', summary='Refreh Channel downloads the latest listing from the cCloud TV server and also any changes made to your Private List(s)', thumb = R(ICON)))
	
	return oc
	
@route(PREFIX + "/showMenu2")
def ShowMenu2(title):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.', title1='Please wait')
		
	if len(IMPORT_BOOL) > 0:
		oc = ObjectContainer(title2='Imported ('+IMPORT_BOOL[0]+') Channels')
	else:
		oc = ObjectContainer(title2='Imported Channels')
	oc.add(DirectoryObject(key = Callback(DisplayList, title='List View', showimported='True'), title = 'List View', thumb = R(ICON_LISTVIEW)))
	oc.add(DirectoryObject(key = Callback(DisplayPage, title='Page View', iRange=0, showimported='True'), title = 'Page View', thumb = R(ICON_PAGE)))
	oc.add(DirectoryObject(key = Callback(DisplayPageList, title='Page List', showimported='True'), title = 'Page List', thumb = R(ICON_PAGELIST)))
	
	return oc
	
@route(PREFIX + "/discover")
def Discover(query=''):

	oc = ObjectContainer(title2='Discover')
	
	if query != '':
		del CACHE_DISCOVER[:]
		searchfor = query
		serachTerms = ' : Discover using: '
		if (searchfor <> None and searchfor != ''):
			serachTerms = ' : Discover (' + searchfor + ') using: '
		searchfor = re.sub(r'[^0-9a-zA-Z \-.+#!]', ' ', searchfor)
		searchfor = searchfor + ' EXTINF m3u8'
		searchfor = 'site:pastebin.com ' + searchfor

		query = urllib2.quote(searchfor, safe='+')
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	   'Accept-Encoding': 'none',
	   'Accept-Language': 'en-US,en;q=0.8',
	   'Connection': 'keep-alive'}
		count = 0
		for x in range(5):
			url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=8&start=%s&tbs=%s&q=%s' % (str(x*8), 'sbd:1%2Cqdr:d', query)
			#search_response = HTTP.Request(url).content
			req = urllib2.Request(url, headers=hdr)
			response = urllib2.urlopen(req, timeout=common_fnc.global_request_timeout)
			search_response = response.read()
			
			if count==0 and '"responseStatus": 403' in search_response:
				return ObjectContainer(header='Google API Limit', message='Google\'s API Limit for free search has been reached. Please try after some time.', title1 = 'Google API Limit')
			#Log(search_response)
			search_results = search_response.decode("utf8")
			#Log(search_response)
			results = json.loads(search_results)
			data = results['responseData']
			#print('Total results: %s' % data['cursor']['estimatedResultCount'])
			if data == None:
				break
			hits = data['results']
			#print('Top %d hits:' % len(hits))
					
			for h in hits:
				if h['url'][len(h['url'])-1] != '/':
				
					#print('For more results, see %s' % data['cursor']['moreResultsUrl'])
					rawLink = common_fnc.getRawPastebinLink(h['url'])
					dateStr = common_fnc.getDatePastebinLink(h['content'])

					if rawLink <> None and ('hour' in dateStr or 'day' in dateStr):
						if 'hour' in dateStr:
							count = count + 1
						CACHE_DISCOVER.append({'rawLink': rawLink, 'dateStr': dateStr, 'url': h['url'], 'serachTerms': serachTerms})

						oc.add(DirectoryObject(
							key = Callback(ShowMenu, title = 'Main Menu', additionalURL = rawLink), 
							title = dateStr + serachTerms + h['url'],
							tagline = dateStr,
							summary = 'Import Channels from ' + h['url'] + ' & Initialize Menu',
							thumb = R(ICON_DISCOVER)))
				if count >= 3:
					break
			if count >= 3:
				break
	else:
		if len(CACHE_DISCOVER) > 0:
			for i in range(len(CACHE_DISCOVER)):
				oc.add(DirectoryObject(
					key = Callback(ShowMenu, title = 'Main Menu', additionalURL = CACHE_DISCOVER[i]['rawLink']), 
					title = CACHE_DISCOVER[i]['dateStr'] + CACHE_DISCOVER[i]['serachTerms'] + CACHE_DISCOVER[i]['url'],
					tagline = CACHE_DISCOVER[i]['dateStr'],
					summary = 'Import Channels from ' + CACHE_DISCOVER[i]['url'] + ' & Initialize Menu',
					thumb = R(ICON_DISCOVER)))

	if len(oc) > 0:
		oc.objects.sort(key=lambda obj: obj.tagline, reverse=False)
	
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Discover,
				dktitle = 'Discover',
				dkthumb = R(ICON_DISCOVER)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Discover), thumb = R(ICON_DISCOVER), title='Discover Channels', summary='Discover Channels from online Pastebin.com listings', prompt='Discover for...'))

	return oc
	
@route(PREFIX + "/refreshlisting")
def RefreshListing(doRefresh, additionalURL=None):

	dateToday = DT.date.today()
	datetimet = Datetime.Now()
	timezoneoffset = int((datetimet - datetimet.utcnow()).total_seconds()) + (US_EST_UTC_SHIFT*60*60)

	if ((datetimet.hour*60*60) + (datetimet.minute*60) + (datetimet.second)) < timezoneoffset:
		dateToday = dateToday - DT.timedelta(days=1) # fix timezone
	week_ago = dateToday - DT.timedelta(days=7)
	
	
	if additionalURL <> None and not doRefresh and len(CCLOUD_PAGE_DATA) > 0:
		# dont refresh cCloud Cached Links but add links from additional urls and we have page data
		del CACHE_LINKS[int(CCLOUDTV_BOOL[0])-1:len(CACHE_LINKS)]
		# Parse Private list in separate thread
		Dict['ParsingPrivThreadAlive'] = 'True'
		#Log("additionalURL : " + additionalURL)
		Thread.Create(ExtM3uParser,{},CCLOUD_PAGE_DATA[0],str(int(CCLOUDTV_BOOL[0])-1),dateToday,week_ago,additionalURL)
		return False
	elif not doRefresh and len(CACHE_LINKS) > 0:
		return False

	abortBool = True
	del CCLOUDTV_BOOL[:]
	del CACHE_LINKS[:]
		
	if CCLOUDTV_DB_URL <> None and len(CCLOUDTV_DB_URL) > 0:
		wUrls = 0
		for webUrl in common_fnc.shuffle(CCLOUDTV_DB_URL):
			if len(CACHE_LINKS) > 0 and not doRefresh:
				return False

			wUrls = wUrls+1
			if webUrl<> None and common_fnc.FollowRedirectGetHttpStatus(webUrl) in common_fnc.GOOD_RESPONSE_CODES or len(CCLOUDTV_DB_URL) == wUrls: # loop through servers
				try:
					# CACHE_LINKS = {}
					ch_count_array = []
					page_data = ""
					
					try:
						page_data = HTTP.Request(webUrl).content
						del CCLOUD_PAGE_DATA[:]
						CCLOUD_PAGE_DATA.append(page_data)
					except:
						page_data = '0;cCloud TV Server Currently Offline;Announcement;US;English;https://archive.org/download/cCloud_20151126/cCloud.mp4;http://i.imgur.com/yX8CKx3.png;Today;'
						pass
					
					count = 0
					lastchannelNum = '-1'

					

					del GENRE_ARRAY[:]
					del LANGUAGE_ARRAY[:]
					del COUNTRY_ARRAY[:]
					cCloudPageData = page_data
					
					sharable = 'False'
					
					page_data = page_data.strip()
					channels = []
					if '||' in page_data:
						channels = page_data.split('||')
					else:
						channels.append(page_data)
					
					# Parse XML Tv Guide in separate thread
					Thread.Create(xmlTvParser)

					# Parse Private list in separate thread
					Dict['ParsingPrivThreadAlive'] = 'True'
					#Log("additionalURL : " + additionalURL)
					Thread.Create(ExtM3uParser,{},cCloudPageData,len(channels)-1,dateToday,week_ago,additionalURL)
					
					# Purge Commit keys from Dict
					Thread.Create(share.ResetCommits,{},cCloudPageData)
					
					ch_count_array.append(str(len(channels)))
					for eachCh in channels:
						skip = False
						if eachCh.startswith('//'):
							pass
						else:
							chMeta = eachCh.split(';')
							channelNum = ' '
							channelUrl = ' '
							logoUrl = None
							channelDesc = ' '
							desc = 'Unknown'
							country = 'Unknown'
							lang = 'Unknown'
							genre = 'Unknown'
							views = 'Unknown'
							active = 'Unknown'
							onair = 'Unknown'
							channelID = 'Unknown'
							dateStrM = channelDesc
							epgLink = 'Unknown'
							epgInfo = ''
							
							try:
								if chMeta[0] <> None:
									channelNum = chMeta[0].strip()
									if channelNum == '!':
										channelNum = '00'
									
									if int(channelNum) <= int(lastchannelNum):
										channelNum = str(int(lastchannelNum)+1)
									
									lastchannelNum = channelNum
									channelNum = "{0:0=4d}".format(int(channelNum))
								if chMeta[1] <> None:
									channelDesc = unicode(chMeta[1])
									channelDesc = FixTitle(channelDesc, engonly=True)
								if chMeta[2] <> None:
									genre = chMeta[2].strip()
									genre = FixGenre(genre)
									if genre in GENRE_ARRAY:
										pass
									elif genre != '!':
										GENRE_ARRAY.append(genre)
								if chMeta[3] <> None:
									country = chMeta[3]
									country = FixCountry(country)
									
									if country in COUNTRY_ARRAY:
										pass
									elif country != '!':
										COUNTRY_ARRAY.append(country)
								if chMeta[4] <> None:
									lang = chMeta[4]
									lang = FixLanguage(lang)
									
									if lang in LANGUAGE_ARRAY:
										pass
									elif lang != '!':
										LANGUAGE_ARRAY.append(lang)
								if chMeta[5] <> None:
									channelUrl = chMeta[5]
								if len(chMeta) >= 7 and chMeta[6] <> None:
									logoUrl = chMeta[6]
								if len(chMeta) >= 8 and chMeta[7] <> None:
									dateStrM = chMeta[7]
								if len(chMeta) >= 9 and chMeta[8] <> None:
									epgLink = chMeta[8]
								desc = channelDesc
							except:
								pass
							
							if channelDesc == None or channelDesc == 'Loading...' or channelDesc == ' ' or channelDesc == '':
								channelDesc = unicode('Undefined Channel: ' + channelNum)
								
							#Log("channelDesc----------" + channelDesc)
							# get update date and used DirectoryObject tagline for sort feature
							dateStr = ' '
							try:
								dateStr = getDate(dateStrM,dateToday)
							except:
								pass
								
							mature = 'N'
							try:
								mature = isAdultChannel(channelDesc, genre)
							except:
								pass
							
							try:
								if not skip:
									CACHE_LINKS.append({'channelNum': channelNum, 'channelDesc': channelDesc, 'channelUrl': channelUrl, 'channelDate': dateStr, 'desc': desc, 'country': country, 'lang': lang, 'genre': genre, 'views': views, 'active': active, 'onair': onair, 'mature': mature, 'epg': epgInfo, 'logoUrl': logoUrl, 'sharable': sharable, 'epgLink': epgLink, 'imported': 'N'})
									count = count + 1
							except:
								pass
					
					CCLOUDTV_BOOL.append(str(int(ch_count_array[0])))
					abortBool = False
					if doRefresh:
						return ObjectContainer(header='Refresh Successful', message= str(int(ch_count_array[0])) + ' cCloud Channels retrieved !', title1='Refresh Successful')
				except e:
					Log(str(e))
					BASE_URL = ""
					abortBool = True
	if doRefresh:
		return ObjectContainer(header='Refresh Failed', message='Channel listing could not be retrieved !', title1='Refresh Failed')		
	return abortBool
	
def xmlTvParser():
		
	try:
		if Prefs['use_epg'] and not Prefs['epg_guide'].startswith('http://'):
			myxmltvparser.initchannels()
	except:
		pass

def ExtM3uParser(cCloudPageData, lastchannelNum, dateToday, week_ago, additionalURL):
	
	cCloudTv_chs = int(lastchannelNum)
	no_chs = 0
	webUrl2 = Prefs['web_url_priv']
	del IMPORT_BOOL[:]
	if webUrl2 == None and additionalURL == None:
		Dict['ParsingPrivThreadAlive'] = 'False'
		return no_chs
	
	ALL_PLAYLIST_FILES = []
	if webUrl2 <> None:
		if (';' or ',' or ' ') in webUrl2:
			webUrls = None
			if ';' in webUrl2:
				webUrls = webUrl2.split(';')
			elif ',' in webUrl2:
				webUrls = webUrl2.split(',')
			elif ' ' in webUrl2:
				webUrls = webUrl2.split(' ')
			if webUrls <> None and len(webUrls) > 0:
				for file in webUrls:
					ALL_PLAYLIST_FILES.append(file.strip())
		else:
			ALL_PLAYLIST_FILES.append(webUrl2)
	
	TEMP_ALL_PLAYLIST_FILES = ALL_PLAYLIST_FILES
	if additionalURL <> None:
		TEMP_ALL_PLAYLIST_FILES.insert(0,additionalURL)
	
	while len(CACHE_LINKS) < int(lastchannelNum):
		time.sleep(1)
		if Prefs['debug']:
			Log("ExtM3uParser Thread sleeping")
	
	plalistCount = 0
	for playListFile in TEMP_ALL_PLAYLIST_FILES:
		plalistCount = plalistCount+1
		if Prefs['debug']:
			Log("Private playlist: " + playListFile)
		playlist = None
		try:
			if 'http' in playListFile:
				playlist = HTTP.Request(playListFile).content
			elif len(playListFile) > 0:
				playlist = Resource.Load(playListFile, binary = True)
		except:
			pass

		if playlist <> None and ('EXTM3U' in playlist or '#EXTINF:' in playlist):
			lines = playlist.splitlines()

			for i in range(len(lines) - 1):
				Dict['ParsingPrivThreadAliveComp'] = (100*i*plalistCount)/((len(lines) - 1)*len(TEMP_ALL_PLAYLIST_FILES))
				line = lines[i].strip().replace('”','"').replace('”','"')
				#Log(line)
				if line.startswith('#EXTINF'):
					for i2 in range(1, 4):
						url = lines[i + i2].strip()
						if len(url) > 0 and '#EXTINF' not in url:
							try:
								#furl = common_fnc.GetRedirector(url)
								furl = url
								url = FixUrl(furl)
								#Log("url--------------" + url)
								
								title = line[line.rfind(',') + 1:len(line)].strip()
								
								if '[' in title:
									title = title.split('[')[0]
									
								if len(title) == 0:
									break
									
								title = unicode(title)
								title = FixTitle(title, engonly=True)
								#Log("title--------------" + title)
								
								thumb = common_fnc.GetAttribute(line, 'tvg-logo')
								if 'http' not in thumb:
									thumb = R(ICON_SERIES)

								country = common_fnc.GetAttribute(line, 'tvg-country')
								if country == '':
									country = 'Unknown'
								if country in COUNTRY_ARRAY:
									pass
								else:
									COUNTRY_ARRAY.append(country)
									
								language = common_fnc.GetAttribute(line, 'tvg-language')
								if language == '':
									language = 'Unknown'
								else:
									language = language.title()
								if language in LANGUAGE_ARRAY:
									pass
								else:
									LANGUAGE_ARRAY.append(language)
									
								date = common_fnc.GetAttribute(line, 'tvg-date')
								if date == '':
									date = str(dateToday.month) + '/' + str(dateToday.day) + '/' + str(dateToday.year)
								
								group = unicode(common_fnc.GetAttribute(line, 'group-title'))
								if group == '':
									group = 'Uncategorized'
								else:
									group = group.title()
								if group in GENRE_ARRAY:
									pass
								else:
									GENRE_ARRAY.append(group)
								
								epgLink = unicode(common_fnc.GetAttribute(line, 'epgLink'))
								if epgLink == '':
									epgLink = 'Unknown'
								
								sharable = 'True'
								if url in cCloudPageData or furl in cCloudPageData:
									sharable = 'False'
								views = 'Unknown'
								active = 'Unknown'
								onair = 'Unknown'
									
								epgInfo = ' '
									
								mature = 'N'
								try:
									mature = isAdultChannel(title + ' ' + group, genre)
								except:
									pass
									
								if mature == 'N':
									for filter in common.FILTER_WORDS:
										if filter in group.lower() or filter in title.lower():
											mature = 'Y'
											group = 'Adult'
											break
								else:
									group = 'Adult'
								
								channelNum = "{0:0=4d}".format(1 + int(lastchannelNum))
								lastchannelNum = channelNum
								#Log(channelNum + " : channelDesc----------" + title)
								
								CACHE_LINKS.append({'channelNum': channelNum, 'channelDesc': title, 'channelUrl': url, 'channelDate': date, 'desc': title, 'country': country, 'lang': language, 'genre': group, 'views': views, 'active': active, 'onair': onair, 'mature': mature, 'epg': epgInfo, 'logoUrl': thumb, 'sharable': sharable, 'epgLink': epgLink, 'imported': 'Y'})
								no_chs = no_chs + 1
								#Log("added ----------------------------- " + str(channelNum) + ' ' + title)
							except:
								pass
							break
						elif len(url) > 0 and '#EXTINF' in url:
							break
		elif playlist <> None and ';' in playlist:
			try:
				page_data = playlist.strip()
				channels = page_data.split('||')
				count = 0
				for eachCh in channels:
					if eachCh.startswith('//'):
						pass
					else:
						chMeta = eachCh.split(';')
						channelNum = ' '
						channelUrl = ' '
						logoUrl = None
						channelDesc = ' '
						desc = 'Unknown'
						country = 'Unknown'
						lang = 'Unknown'
						genre = 'Uncategorized'
						views = 'Unknown'
						active = 'Unknown'
						onair = 'Unknown'
						channelID = 'Unknown'
						dateStrM = channelDesc
						epgLink = 'Unknown'
						epgInfo = ' '
						
						try:
							channelNum = "{0:0=4d}".format(1 + int(lastchannelNum))
							lastchannelNum = channelNum
								
							if chMeta[1] <> None:
								channelDesc = unicode(chMeta[1])
								channelDesc = FixTitle(channelDesc, engonly=True)
							if chMeta[2] <> None:
								genre = chMeta[2].strip()
								genre = FixGenre(genre)
								if genre in GENRE_ARRAY:
									pass
								elif genre != '!':
									GENRE_ARRAY.append(genre)
							if chMeta[3] <> None:
								country = chMeta[3]
								country = FixCountry(country)
								Log(country)
								if country in COUNTRY_ARRAY:
									pass
								elif country != '!':
									COUNTRY_ARRAY.append(country)
							if chMeta[4] <> None:
								lang = chMeta[4]
								lang = FixLanguage(lang)
								
								if lang in LANGUAGE_ARRAY:
									pass
								elif lang != '!':
									LANGUAGE_ARRAY.append(lang)
							if chMeta[5] <> None:
								channelUrl = chMeta[5]
							if len(chMeta) >= 7 and chMeta[6] <> None:
								logoUrl = chMeta[6]
							if len(chMeta) >= 8 and chMeta[7] <> None:
								dateStrM = chMeta[7]
							if len(chMeta) >= 9 and chMeta[8] <> None:
								epgLink = chMeta[8]
							desc = channelDesc
						except:
							pass
						
						if channelDesc == None or channelDesc == ' ' or channelDesc == '':
							channelDesc = unicode('Undefined Channel: ' + channelNum)
							
						sharable = 'True'
						if channelUrl in cCloudPageData:
							sharable = 'False'
							
						#Log("channelDesc----------" + channelDesc)
						# get update date and used DirectoryObject tagline for sort feature
						dateStr = ' '
						try:
							dateStr = getDate(dateStrM,week_ago)
						except:
							pass
							
						mature = 'N'
						try:
							mature = isAdultChannel(channelDesc, genre)
						except:
							pass
						
						Dict['ParsingPrivThreadAliveComp'] = 100*count/(len(channels))
						count = count+1
						
						#Log(channelNum + " : channelDesc----------" + channelDesc)
						try:
							CACHE_LINKS.append({'channelNum': channelNum, 'channelDesc': channelDesc, 'channelUrl': channelUrl, 'channelDate': dateStr, 'desc': desc, 'country': country, 'lang': lang, 'genre': genre, 'views': views, 'active': active, 'onair': onair, 'mature': mature, 'epg': epgInfo, 'logoUrl': logoUrl, 'sharable': sharable, 'epgLink': epgLink, 'imported': 'Y'})
							no_chs = no_chs + 1
						except:
							pass
			except:
				pass
	lastchannelNum = no_chs + int(lastchannelNum)
	#Log(content)
	#Log('cCloud Channels: ' + str(cCloudTv_chs))
	#Log('Imported Channels: ' + str(no_chs))
	#Log('Total Channels: ' + str(lastchannelNum))
	
	if (lastchannelNum - cCloudTv_chs) > 0:
		IMPORT_BOOL.append(str(no_chs))
	
	Dict['ParsingPrivThreadAlive'] = 'False'
	return no_chs


@route(PREFIX + "/showRecentMenu")
def ShowRecentMenu(title):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.', title1= 'Please wait')
		
	oc = ObjectContainer(title2=title)
	
	abortBool = RefreshListing(False)
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1='Channels Unavailable')
		
	datetimet = Datetime.Now()
	timezoneoffset = int((datetimet - datetimet.utcnow()).total_seconds()) + (US_EST_UTC_SHIFT*60*60)
	#Log("timezoneoffset " + str(timezoneoffset))
	today = DT.date.today()
	if ((datetimet.hour*60*60) + (datetimet.minute*60) + (datetimet.second)) < timezoneoffset:
		today = today - DT.timedelta(days=1) # fix timezone

	oc.add(DirectoryObject(key = Callback(RecentListing, title='Today'), title = 'Today (' + str(today)+' US-EST)', summary='Shows Channels updated today based on US-EST timezone', thumb = R(ICON_RECENT)))
	oc.add(DirectoryObject(key = Callback(RecentListing, title='Since Yesterday'), title = 'Since Yesterday', summary='Shows Channels updated since Yesterday based on US-EST timezone', thumb = R(ICON_RECENT)))
	oc.add(DirectoryObject(key = Callback(RecentListing, title='Since Last 3 Days'), title = 'Since Last 3 Days', summary='Shows Channels updated in the last 3 days based on US-EST timezone', thumb = R(ICON_RECENT)))
	oc.add(DirectoryObject(key = Callback(RecentListing, title='Since Last 7 Days'), title = 'Since Last 7 Days', summary='Shows Channels updated in the last 7 days based on US-EST timezone', thumb = R(ICON_RECENT)))
	oc.add(DirectoryObject(key = Callback(RecentListing, title='Since Last 30 Days'), title = 'Since Last 30 Days', summary='Shows Channels updated in the last 30 days based on US-EST timezone', thumb = R(ICON_RECENT)))
	return oc
	
@route(PREFIX + "/RecentListing")
def RecentListing(title):
	
	datetimet = Datetime.Now()
	timezoneoffset = int((datetimet - datetimet.utcnow()).total_seconds()) + (US_EST_UTC_SHIFT*60*60)
	
	filterD = DT.date.today()
	if ((datetimet.hour*60*60) + (datetimet.minute*60) + (datetimet.second)) < timezoneoffset:
		filterD = filterD - DT.timedelta(days=1) # fix timezone
	
	if title == 'Since Yesterday':
		filterD = filterD - DT.timedelta(days=1)
	elif title == 'Since Last 3 Days':
		filterD = filterD - DT.timedelta(days=3)
	elif title == 'Since Last 7 Days':
		filterD = filterD - DT.timedelta(days=7)
	elif title == 'Since Last 30 Days':
		filterD = filterD - DT.timedelta(days=30)
	filterDate = datetime.combine(filterD, datetime.min.time())
	
	abortBool = RefreshListing(False)
	session = common_fnc.getSession()
	
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1 = 'Please wait')
		
	oc = ObjectContainer(title2=title)
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		if Client.Platform not in LIST_VIEW_CLIENTS:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
		else:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = None, title='Search', summary='Search Channel', prompt='Search for...'))
			
	try:
		#oc = MultiThreadedRecentListing(title, filterDate, oc)	
		for count in range(0,len(CACHE_LINKS)):
			
			channelNum = CACHE_LINKS[count]['channelNum']
			channelDesc = CACHE_LINKS[count]['channelDesc']
			channelUrl = CACHE_LINKS[count]['channelUrl']
			dateStr = CACHE_LINKS[count]['channelDate']
			#Log("Date===========  " + dateStr)
			dateStrA = dateStr.split('/')
			dateObj = datetime(int(dateStrA[2]), int(dateStrA[0]), int(dateStrA[1]))
			
			title = unicode(channelDesc)
			
			desc = 'Unknown'
			country = 'Unknown'
			lang = 'Unknown'
			genre = 'Unknown'
			views = 'Unknown'
			active = 'Unknown'
			onair = 'Unknown'
			mature = 'Unknown'
			logoUrl = None
			sharable = 'True'
			epgLink = 'Unknown'
			
			try:
				logoUrl = CACHE_LINKS[count]['logoUrl']
				mature = CACHE_LINKS[count]['mature']
				desc = CACHE_LINKS[count]['desc']
				country = CACHE_LINKS[count]['country']
				lang = CACHE_LINKS[count]['lang']
				genre = CACHE_LINKS[count]['genre']
				views = CACHE_LINKS[count]['views']
				active = CACHE_LINKS[count]['active']
				onair = CACHE_LINKS[count]['onair']
				epgInfo = CACHE_LINKS[count]['epg']
				sharable = CACHE_LINKS[count]['sharable']
				epgLink = CACHE_LINKS[count]['epgLink']
			except:
				pass
			
			#abortBool2 = ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session)
			
			summaryStr = '#: ' + channelNum + ' | '+ desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang + ' | ' + views + ' Views'
			if epgInfo != '':
				summaryStr = summaryStr + ' | ' + epgInfo
				
			#Log("Date===========  " + dateStr + " = " + str(dateObj) + " = " + str(filterDate))
			#Log(channelNum + " : channelDesc----------" + channelDesc)
				
			if dateObj >= filterDate and not ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session):
				if Client.Platform not in LIST_VIEW_CLIENTS:
					oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
				else:
					oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = None))
		abortBool = False	
	except:
		abortBool = True
	
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1 = 'Please wait')
		
	if Prefs['use_datesort']:
		oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
	return oc
	
@route(PREFIX + "/displaylist", allow_sync=True)
def DisplayList(title, showimported='False'):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.', title1 = 'Please wait')
		
	oc = ObjectContainer(title2=title)

	abortBool = RefreshListing(False)
	session = common_fnc.getSession()
	
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1 = 'Please wait')
	
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		if Client.Platform not in LIST_VIEW_CLIENTS:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
		else:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = None, title='Search', summary='Search Channel', prompt='Search for...'))
		
	try:
		for count in range(0,len(CACHE_LINKS)):
			
			#items_dict[count] = {'channelNum': channelNum, 'channelDesc': channelDesc, 'channelUrl': channelUrl, 'channelDate': dateStr}
			
			channelNum = CACHE_LINKS[count]['channelNum']
			channelDesc = CACHE_LINKS[count]['channelDesc']
			channelUrl = CACHE_LINKS[count]['channelUrl']
			dateStr = CACHE_LINKS[count]['channelDate']
			
			#Log("channelUrl--------------" + str(channelUrl))
			title = unicode(channelDesc)
			#Log("title----------" + title)
			
			desc = 'Unknown'
			country = 'Unknown'
			lang = 'Unknown'
			genre = 'Unknown'
			views = 'Unknown'
			active = 'Unknown'
			onair = 'Unknown'
			mature = 'Unknown'
			epgInfo = ''
			logoUrl = None
			sharable = 'True'
			epgLink = 'Unknown'
			imported = 'N'
			
			try:
				logoUrl = CACHE_LINKS[count]['logoUrl']
			except:
				pass
			try:
				sharable = CACHE_LINKS[count]['sharable']
			except:
				pass
			try:
				imported = CACHE_LINKS[count]['imported']
			except:
				pass
			try:
				mature = CACHE_LINKS[count]['mature']
				desc = CACHE_LINKS[count]['desc']
				country = CACHE_LINKS[count]['country']
				lang = CACHE_LINKS[count]['lang']
				genre = CACHE_LINKS[count]['genre']
				views = CACHE_LINKS[count]['views']
				active = CACHE_LINKS[count]['active']
				onair = CACHE_LINKS[count]['onair']
				epgInfo = CACHE_LINKS[count]['epg']
				epgLink = CACHE_LINKS[count]['epgLink']
			except:
				pass
			
			#abortBool2 = ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session)
			
			summaryStr = '#: ' + channelNum + ' | '+ desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang
			if epgInfo != '':
				summaryStr = summaryStr + ' | ' + epgInfo
				
			if not ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session):
				if Client.Platform not in LIST_VIEW_CLIENTS:
					if logoUrl <> None:
						if (showimported == 'False' or (showimported == 'True' and imported == 'Y')):
							oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
					else:
						if (showimported == 'False' or (showimported == 'True' and imported == 'Y')):
							oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = R(ICON_SERIES)))
				else:
					if (showimported == 'False' or (showimported == 'True' and imported == 'Y')):
						oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = None))
			
		abortBool = False
	except:
		abortBool = True
	
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1 = 'Error')
		
	if Prefs['use_datesort']:
		oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
		
	try:
		if Prefs['use_transcoder']:
			transcoder.CloseThisSessionPidInstance()
	except:
		pass	
	return oc

@route(PREFIX + "/displaygenremenu")
def DisplayGenreMenu(title, filter1=None, filter2=None, filter3=None):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.', title1 = 'Please wait')
		
	oc = ObjectContainer(title2=title)
	for genre in GENRE_ARRAY:
		if genre == 'Adult':
			pass
		elif genre == 'Top10':
			oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=genre, type="Category", filter1=genre, filter2=filter2, filter3=filter3), title = ' '+genre, thumb = R(ICON_GENRE)))
		else:
			oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=genre, type="Category", filter1=genre, filter2=filter2, filter3=filter3), title = genre, thumb = R(ICON_GENRE)))
	
	oc.objects.sort(key=lambda obj: obj.title)
	genre = 'Adult'
	
	session = common_fnc.getSession()
	if Prefs['show_adult'] or Dict['AccessPin'+session] == Prefs['access_pin']:
		oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=genre, type="Category", filter1=genre, filter2=filter2, filter3=filter3), title = genre, thumb = R(ICON_GENRE)))
	
	return oc

@route(PREFIX + "/displaylanguagemenu")
def DisplayLanguageMenu(title, filter1=None, filter2=None, filter3=None):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.', title1 = 'Please wait')
		
	oc = ObjectContainer(title2=title)
	
	LastSaveLanguage = ' '
	if Dict['LastUsed'+title] <> None:
		LastSaveLanguage = Dict['LastUsed'+title]
		oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=LastSaveLanguage, type="Language", filter1=filter1, filter2=LastSaveLanguage, filter3=filter3), title = LastSaveLanguage, thumb = R(ICON_GENRE)))
	for language in LANGUAGE_ARRAY_POP:
		if language != LastSaveLanguage:
			oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=language, type="Language", filter1=filter1, filter2=language, filter3=filter3), title = language, thumb = R(ICON_GENRE)))
	for language in sorted(LANGUAGE_ARRAY):
		if language not in LANGUAGE_ARRAY_POP and language != LastSaveLanguage:
			oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=language, type="Language", filter1=filter1, filter2=language, filter3=filter3), title = language, thumb = R(ICON_GENRE)))
			
	#oc.objects.sort(key=lambda obj: obj.title)
	return oc
	
@route(PREFIX + "/displaycountrymenu")
def DisplayCountryMenu(title, filter1=None, filter2=None, filter3=None):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.', title1 = 'Please wait')
		
	oc = ObjectContainer(title2=title)
	oc2 = []
	
	LastSaveCountry = ' '
	if Dict['LastUsed'+title] <> None:
		LastSaveCountry = Dict['LastUsed'+title]
		oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=LastSaveCountry, type="Country", filter1=filter1, filter2=filter2, filter3=LastSaveCountry), title = common.getCountryName(LastSaveCountry), thumb = R(ICON_GENRE)))
	for country in COUNTRY_ARRAY_POP:
		if country != LastSaveCountry:
			oc.add(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=country, type="Country", filter1=filter1, filter2=filter2, filter3=country), title = common.getCountryName(country), thumb = R(ICON_GENRE)))
	for country in sorted(COUNTRY_ARRAY):
		if country not in COUNTRY_ARRAY_POP and country != LastSaveCountry:
			oc2.append(DirectoryObject(key = Callback(DisplayGenreLangConSort, titleGen=country, type="Country", filter1=filter1, filter2=filter2, filter3=country), title = common.getCountryName(country), thumb = R(ICON_GENRE)))
	if len(oc2) > 0:
		for o in sorted(oc2, key=lambda obj: obj.title):
			oc.add(o)
			
	#oc.objects.sort(key=lambda obj: obj.title)
	return oc
	
@route(PREFIX + "/displaygenresort")
def DisplayGenreLangConSort(titleGen, type, filter1=None, filter2=None, filter3=None):

	if type == 'Country':
		oc = ObjectContainer(title2=common.getCountryName(titleGen))
		filter3=titleGen
	elif type == 'Language':
		oc = ObjectContainer(title2=titleGen)
		filter2=titleGen
	elif type == 'Country':
		oc = ObjectContainer(title2=titleGen)
		filter1=titleGen
	else:
		oc = ObjectContainer(title2=titleGen)
		
	abortBool = RefreshListing(False)
	
	if abortBool:
		return ObjectContainer(header=titleGen, message='Connection error or Server seems down !', title1 = 'Please wait')
		
	session = common_fnc.getSession()
	oc2 = []
	#Log("DisplayGenreLangConSort------------------- " + str(len(CACHE_LINKS)))
	try:
		# for count in range(0,len(CACHE_LINKS)):
			
			# #items_dict[count] = {'channelNum': channelNum, 'channelDesc': channelDesc, 'channelUrl': channelUrl, 'channelDate': dateStr}
			
			# channelNum = CACHE_LINKS[count]['channelNum']
			# channelDesc = CACHE_LINKS[count]['channelDesc']
			# channelUrl = CACHE_LINKS[count]['channelUrl']
			# dateStr = CACHE_LINKS[count]['channelDate']
			# #Log("channelNum----------" + channelNum)
			# #Log("channelUrl--------------" + str(channelUrl))
			# title = unicode(channelDesc)
			# #Log("title----------" + title)
			# tkey = 'Unknown'
			# desc = 'Unknown'
			# country = 'Unknown'
			# lang = 'Unknown'
			# genre = 'Unknown'
			# views = 'Unknown'
			# active = 'Unknown'
			# onair = 'Unknown'
			# mature = 'Unknown'
			# epgInfo = ''
			# logoUrl = None
			# sharable = 'True'
			
			# try:
				# logoUrl = CACHE_LINKS[count]['logoUrl']
			# except:
				# pass
			# try:
				# sharable = CACHE_LINKS[count]['sharable']
			# except:
				# pass
			# try:
				# mature = CACHE_LINKS[count]['mature']
				# desc = CACHE_LINKS[count]['desc']
				# country = CACHE_LINKS[count]['country']
				# lang = CACHE_LINKS[count]['lang']
				# genre = CACHE_LINKS[count]['genre']
				# views = CACHE_LINKS[count]['views']
				# active = CACHE_LINKS[count]['active']
				# onair = CACHE_LINKS[count]['onair']
				# epgInfo = CACHE_LINKS[count]['epg']
			# except:
				# pass
			
			# if type == 'Category':
				# tkey = genre
			# elif type == 'Language':
				# tkey = lang
			# elif type == 'Country':
				# tkey = country
			
			# abortBool2 = ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session)
			
			# summaryStr = '#: ' + channelNum + ' | '+ desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang
			# #Log(summaryStr)
			# if epgInfo != '':
				# summaryStr = summaryStr + ' | ' + epgInfo
				
			# if (titleGen == tkey or ('/' in tkey and titleGen in tkey.split('/'))) and not ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session):
				# if Client.Platform not in LIST_VIEW_CLIENTS:
					# if logoUrl <> None:
						# oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
					# else:
						# oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = R(ICON_SERIES)))
				# else:
					# oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = None))
					
		oc2 = MultiThreadedDisplayGenreLangConSort(titleGen, type, oc2, filter1, filter2, filter3)	
		
		abortBool = False	
	except:
		abortBool = True
	
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1 = 'Please wait')
		
	if type <> 'Category':
		oc.add(DirectoryObject(key = Callback(DisplayGenreMenu, title='Category', filter1=filter1, filter2=filter2, filter3=filter3), title = 'Sort Further by Category', summary = 'Sort Further by Category within ' + titleGen, thumb = R(ICON_GENRES)))
	if type <> 'Language':
		oc.add(DirectoryObject(key = Callback(DisplayLanguageMenu, title='Language', filter1=filter1, filter2=filter2, filter3=filter3), title = 'Sort Further by Language', summary = 'Sort Further by Language within ' + titleGen, thumb = R(ICON_LANGUAGES)))
	if type <> 'Country':
		oc.add(DirectoryObject(key = Callback(DisplayCountryMenu, title='Country', filter1=filter1, filter2=filter2, filter3=filter3), title = 'Sort Further by Country', summary = 'Sort Further by Country within ' + titleGen, thumb = R(ICON_COUNTRIES)))
		
	if Prefs['use_datesort']:
		#oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
		if len(oc2) > 0:
			for o in sorted(oc2, key=lambda obj: obj.title, reverse=True):
				oc.add(o)
	else:
		#oc.objects.sort(key=lambda obj: obj.title)
		if len(oc2) > 0:
			for o in sorted(oc2, key=lambda obj: obj.title):
				oc.add(o)
	
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		if Client.Platform not in LIST_VIEW_CLIENTS:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
		else:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = None, title='Search', summary='Search Channel', prompt='Search for...'))
		
	Dict['LastUsed'+type] = titleGen
	Dict.Save()
	
	try:
		if Prefs['use_transcoder']:
			transcoder.CloseThisSessionPidInstance()
	except:
		pass
	
	return oc
	
@route(PREFIX + "/displaypage")
def DisplayPage(title, iRange, showimported='False'):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.', title1 = 'Please wait')
		
	oc = ObjectContainer(title2=title)
	
	abortBool = RefreshListing(False)
	session = common_fnc.getSession()
	
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1='Error')
		
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		if Client.Platform not in LIST_VIEW_CLIENTS:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
		else:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = None, title='Search', summary='Search Channel', prompt='Search for...'))
		
	try:
		mCount=0
		mmCount=0
		lastCount=0
		for count in range(int(iRange),len(CACHE_LINKS)):
			
			#CACHE_LINKS[count] = {'channelNum': channelNum, 'channelDesc': channelDesc, 'channelUrl': channelUrl, 'channelDate': dateStr}
			
			channelNum = CACHE_LINKS[count]['channelNum']
			channelDesc = CACHE_LINKS[count]['channelDesc']
			channelUrl = CACHE_LINKS[count]['channelUrl']
			dateStr = CACHE_LINKS[count]['channelDate']
			
			title = unicode(channelDesc)
			
			desc = 'Unknown'
			country = 'Unknown'
			lang = 'Unknown'
			genre = 'Unknown'
			views = 'Unknown'
			active = 'Unknown'
			onair = 'Unknown'
			mature = 'Unknown'
			epgLink = 'Unknown'
			epgInfo = ''
			logoUrl = None
			sharable = 'True'
			imported = 'N'
			
			try:
				logoUrl = CACHE_LINKS[count]['logoUrl']
			except:
				pass
			try:
				sharable = CACHE_LINKS[count]['sharable']
			except:
				pass
			try:
				imported = CACHE_LINKS[count]['imported']
			except:
				pass
			try:
				mature = CACHE_LINKS[count]['mature']
				desc = CACHE_LINKS[count]['desc']
				country = CACHE_LINKS[count]['country']
				lang = CACHE_LINKS[count]['lang']
				genre = CACHE_LINKS[count]['genre']
				views = CACHE_LINKS[count]['views']
				active = CACHE_LINKS[count]['active']
				onair = CACHE_LINKS[count]['onair']
				epgInfo = CACHE_LINKS[count]['epg']
				epgLink = CACHE_LINKS[count]['epgLink']
			except:
				pass
			
			summaryStr = '#: ' + channelNum + ' | '+ desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang
			if epgInfo != '':
				summaryStr = summaryStr + ' | ' + epgInfo
			
			if not ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session):
				if Client.Platform not in LIST_VIEW_CLIENTS:
					if logoUrl <> None:
						if (showimported == 'False' or (showimported == 'True' and imported == 'Y')):
							oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
							mmCount = mmCount+1
					else:
						if (showimported == 'False' or (showimported == 'True' and imported == 'Y')):
							oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = R(ICON_SERIES)))
							mmCount = mmCount+1
				else:
					if (showimported == 'False' or (showimported == 'True' and imported == 'Y')):
						oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = None))
						mmCount = mmCount+1
				
				lastCount = count
			if ((mCount == 10 and not showimported) or (mmCount == 10 and showimported)):
				oc.add(DirectoryObject(key = Callback(DisplayPage, title='Page View', iRange=lastCount+1, showimported=showimported), title = 'More >>', thumb = R(ICON_NEXT)))
				break
			mCount = mCount+1
	except:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1='Error')
		
	try:
		if Prefs['use_transcoder']:
			transcoder.CloseThisSessionPidInstance()
	except:
		pass	
	return oc
	
@route(PREFIX + "/displaypagelist")
def DisplayPageList(title, showimported='False'):

	if Dict['ParsingPrivThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Parsing Private Channels Still Running ! Please wait... ' + str(Dict['ParsingPrivThreadAliveComp'] ) + '% done.')
		
	oc = ObjectContainer(title2=title)
	
	abortBool = RefreshListing(False)
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1='Error')
		
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		if Client.Platform not in LIST_VIEW_CLIENTS:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
		else:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = None, title='Search', summary='Search Channel', prompt='Search for...'))
		
	try:
		mCount=0
		sCh = '0'
		eCh = '9'
		pageCount=0
		for count in range(0,len(CACHE_LINKS)):
			mCount = mCount+1
			
			channelNum = CACHE_LINKS[count]['channelNum']
			if mCount == 1:
				sCh = channelNum
			
			if mCount == 10 or count == len(CACHE_LINKS)-1:
				oc.add(DirectoryObject(key = Callback(DisplayPage, title='Page View', iRange=(pageCount), showimported=showimported), title = 'Channels: ' + str(sCh) + ' - ' + str(channelNum), thumb = R(ICON_PAGE)))
				mCount = 0
				pageCount=pageCount+10
	except:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1='Error')

	return oc
	
@route(PREFIX + '/getdate')
def getDate(channelDesc,week_ago):
	
	dateStr = str(week_ago.month) + '/' + str(week_ago.day) + '/' + str(week_ago.year)
	
	dateStrS = channelDesc.split('/')
	if len(dateStrS) == 3:
		dateStr = channelDesc
		return dateStr
	
	# tricky keep in seperate try
	try:
		if 'Updated' in channelDesc:
			dateStr = str(week_ago.month) + '/' + str(week_ago.day)
			channelUpDate = channelDesc.replace('Updated:','')
			channelUpDate = channelUpDate.replace('24/7','')
			if '/' in channelUpDate and '-' in channelUpDate:
				dateStr = channelUpDate.split('-')[0]
			elif '/' in channelUpDate and ':' in channelUpDate:
				dateStr = channelUpDate.split(':')[0]
	except:
		dateStr = str(week_ago.month) + '/' + str(week_ago.day) + '/' + str(week_ago.year)
		
	try:
		if ':' in dateStr:
			dateStr = dateStr.split(':')[0]
	except:
		dateStr = str(week_ago.month) + '/' + str(week_ago.day)
		
	try:
		dateStrS = dateStr.split('/')
		dateStr = str("%02d" % int(dateStrS[0])) + '/' + str("%02d" % int(dateStrS[1]))
		if len(dateStrS) > 2:
			if len(dateStrS[2]) == 2:
				dateStr = dateStr + '/20' + str("%02d" % int(dateStrS[2]))
			elif len(dateStrS[2]) == 4:
				dateStr = dateStr + '/' + str(dateStrS[2])
		else:
			dateStr = dateStr + '/' + str(week_ago.year)
	except:
		dateStr = str(week_ago.month) + '/' + str(week_ago.day) + '/' + str(week_ago.year)
		
	#Log("dateStr----------" + dateStr)
	return dateStr



@route(PREFIX + '/channelpage', allow_sync=True)
def ChannelPage(url, title, channelDesc, channelNum, logoUrl, country, lang, genre, sharable, epgLink):

	title = unicode(title)
	oc = ObjectContainer(title2=title)
	try:
		if Prefs['use_transcoder']:
			transcoder.CloseThisSessionPidInstance()
	except:
		pass
	transcode = False
	if Prefs['use_transcoder'] and common_fnc.getProduct() not in playback.RTMP_TRANSCODE_CLIENTS:
		transcode = True
		
	thumb = ''
	try:
		url = common_fnc.GetRedirector(url)
		thumb = GetChannelThumb(url,logoUrl)
	except:
		pass
		
	listingUrl = epgLink
	
	tvGuide = ' '
	tvGuideSum = ' '
	tvGuideCurr = ''
	rtmpVid = ''
	if listingUrl != 'Unknown' and listingUrl <> None:
		try:
			tvGuide = guide_online.GetListing(title, url, listingUrl)
			l = len(tvGuide)
			if l > 0:
				tvGuideCurr = unicode(' : ' + tvGuide[0]['showtitles'])
			for x in xrange(l):
				tvGuideSum += tvGuide[x]['showtitles'] + ' : ' + tvGuide[x]['showtimes'] + ' || '
		except:
			pass
	elif Prefs['use_epg']:
		now = str(datetime.now()).replace(':','').replace('-','').replace(' ', '')[0:14]
		tvGuideSum = myxmltvparser.epgguide(title, country, lang, now)
	else:
		tvGuideSum = 'EPG Not Yet Implemented'
		
	session = common_fnc.getSession()
	
	try:
		#Log("----------- url ----------------")
		#Log(url)
		if 'rtmp:' in url or 'rtmpe:' in url:
			rtmpVid = ' (rtmp) '
		oc.add(playback.CreateVideoClipObject(
			url = url,
			title = title + rtmpVid + tvGuideCurr,
			thumb = thumb,
			summary = channelDesc + ' || ' + tvGuideSum,
			session = session,
			transcode = transcode))
	except:
		url = ""

	if listingUrl != 'Unknown' and listingUrl <> None and len(tvGuideCurr) > 0:
		oc.add(DirectoryObject(
				key = Callback(guide_online.CreateListing, title=title, videoUrl=url, listingUrl=listingUrl, transcode=transcode, session=session),
				title = "TV Guide",
				summary = 'TV Guide for ' + title,
				thumb = R(ICON_GUIDE)
			))
	
	if CheckBookmark(channelNum=channelNum, url=url, title = title, genre = genre, lang = lang, country = country):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, channelNum = channelNum, url = url, genre = genre, lang = lang, country = country),
			title = "Remove Bookmark",
			summary = 'Removes the current Channel from the Boomark queue',
			thumb = R(ICON_BOOKMARK)
		))
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, channelNum = channelNum, url = url, title = title, genre = genre, lang = lang, country = country),
			title = "Bookmark Channel",
			summary = 'Adds the current Channel to the Boomark queue',
			thumb = R(ICON_BOOKMARK)
		))
	if CheckPin(url=url):
		oc.add(DirectoryObject(
			key = Callback(RemovePin, url = url),
			title = "Remove Pin",
			summary = 'Removes the current Channel from the Pin list',
			thumb = R(ICON_PIN)
		))
	else:
		oc.add(DirectoryObject(
			key = Callback(AddPin, channelNum = channelNum, url = url, title = title, channelDesc = channelDesc, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink),
			title = "Pin Channel",
			summary = 'Adds the current Channel to the Pin list',
			thumb = R(ICON_PIN)
		))
		
	if sharable == 'True' and thumb != R(ICON_SERIES_UNAV) and not CheckPlexShare(url):
		fixedChTitle = FixTitle(title, engonly=True, sharable=True)
		
		oc.add(DirectoryObject(
			key = Callback(AddPlexShare, url = url, title = fixedChTitle, country = country, lang = lang, genre = genre, logoUrl=logoUrl, channelNum=channelNum, channelDesc=channelDesc, sharable=sharable, epgLink=epgLink),
			title = "Share Channel",
			summary = 'Interface for Adding the current Channel to the cCloudTV community listing',
			thumb = R(ICON_SHARE)
		))
	
	abortBool = RefreshListing(False)
	if not abortBool:
		if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
			DumbKeyboard(PREFIX, oc, Search,
					dktitle = 'Search',
					dkthumb = R(ICON_SEARCH)
			)
		else:
			oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))	
	return oc

####################################################################################################
# Gets the redirecting url for .m3u8 streams
@route(PREFIX + '/getchannelthumb')
def GetChannelThumb(url, logoUrl):

	#Log('Thumb1:' + logoUrl)
	thumb = R(ICON_SERIES_UNAV)
	try:
		if 'http' not in logoUrl:
			logoUrl = R(ICON_SERIES)
		if '.m3u8' in url:
			try:
				Thread.Create(TimeoutChecker)
				page = HTTP.Request(url, timeout = float(common_fnc.global_request_timeout)).content
			except:
				thumb = R(ICON_UNKNOWN)

			if Dict['Timeout'] <> None and int(Dict['Timeout']) > common_fnc.global_request_timeout:
				if Prefs['debug']:
					Log('GetChannelThumb : Timeout = ' + Dict['Timeout'])
				thumb = R(ICON_UNKNOWN)
			del TIMEOUT_BOOL[:]
			if page <> None and 'html' not in page and 'div' not in page and '#EXTM3U' in page:
				thumb = logoUrl
		elif 'rtmp:' in url:
			if Prefs['use_transcoder'] and common_fnc.getProduct() in playback.RTMP_TRANSCODE_CLIENTS:
				thumb = logoUrl
			elif (not Prefs['use_transcoder'] or len(Prefs['transcode_prog']) == 0) and common_fnc.getProduct() not in playback.RTMP_TRANSCODE_CLIENTS:
				thumb = R(ICON_UNKNOWN)
			else:
				thumb = logoUrl
		elif '.m3u' in url:
			thumb = logoUrl
		elif '.aac' in url or '.mp3' in url:
			thumb = logoUrl
		elif 'mmsh:' in url:
			thumb = R(ICON_UNKNOWN)
		elif '.mp4' in url or common_fnc.ArrayItemsInString(playback.MP4_VIDEOS, url):
			resp = common_fnc.FollowRedirectGetHttpStatus(url)
			if resp in common_fnc.GOOD_RESPONSE_CODES:
				thumb = logoUrl
		else:
			resp = common_fnc.FollowRedirectGetHttpStatus(url)
			if resp in common_fnc.GOOD_RESPONSE_CODES:
				thumb = logoUrl
	except:
		thumb = R(ICON_SERIES_UNAV)
		
	#Log('Thumb2:' + str(thumb))

	return thumb
	
####################################################################################################
# Runs a timeout timer check
@route(PREFIX + '/TimeoutChecker')
def TimeoutChecker():
	if Prefs['debug']:
		Log("Timeout timer start")
	
	t = 0
	TIMEOUT_BOOL.append(t)
	Dict['Timeout'] = '0'
	while (len(TIMEOUT_BOOL) > 0):
		time.sleep(1)
		t = t+1
		Dict['Timeout'] = str(t)

	Dict['Timeout'] = None
	if Prefs['debug']:
		Log("Timeout timer stop")

####################################################################################################
# Filter channels based on preferences
@route(PREFIX + '/channelfilters')
def ChannelFilters(active, onair, lang, country, mature, session):

	if Prefs['show_active'] and active == 'N':
		return True
	if Prefs['show_onair'] and onair == 'N':
		return True
	if Prefs['show_lang'] <> None and lang != 'Unknown' and unicode(Prefs['show_lang']).strip().lower() != unicode(lang).strip().lower():
		return True
	if Prefs['show_country'] <> None and Prefs['show_country'] != 'ALL' and country != 'Unknown' and Prefs['show_country'] != country:
		return True	
	if not Prefs['show_adult'] and mature == 'Y' and Dict['AccessPin'+session] != Prefs['access_pin']:
		return True
		
	return False
	
####################################################################################################
# is Channel Adult rated based on '18+' keyword
@route(PREFIX + '/isadultchannel')
def isAdultChannel(channelDesc, genre):
	
	adult = 'N'
	if '18+' in channelDesc or 'Adult' in genre or genre == 'Private':
		adult = 'Y'
		
	return adult
	
####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	
	if query == None or query == '':
		return ObjectContainer(header='Search Results', message='No input received !')
		
	session = common_fnc.getSession()
	if not Prefs['show_adult'] and Dict['AccessPin'+session] != Prefs['access_pin']:
		if common.isFilterWord(query):
			return ObjectContainer(header='Search Results', message='This search term is not allowed based on your access !', title1='Search Results')
	
	Dict['MyCustomSearch'+query] = query
	Dict['LastUsedSearchQuery'] = query
	
	abortBool = RefreshListing(False)
	if abortBool:
		return ObjectContainer(header='Search Results', message='No cCloud TV Channels Available or Server seems down !', title1='Search Results')
		
	dict_len = len(CACHE_LINKS)
	if dict_len == 0:
		return ObjectContainer(header='Search Results', message='No Channels loaded ! Initialize Channel list first.', title1='Search Results')
	
	start = 0
	end = 0
	if '~' in query:
		split = query.split('~')
		try:
			start = int(split[0])
			end = int(split[1])
		except:
			start = 0
			end = 0

	for count in range(0,len(CACHE_LINKS)):
		try:
			channelNum = CACHE_LINKS[count]['channelNum']
			channelDesc = CACHE_LINKS[count]['channelDesc']
			channelUrl = CACHE_LINKS[count]['channelUrl']
			dateStr = CACHE_LINKS[count]['channelDate']
			title = unicode(channelDesc)
			#Log("channelDesc--------- " + channelDesc)
			
			desc = 'Unknown'
			country = 'Unknown'
			lang = 'Unknown'
			genre = 'Unknown'
			views = 'Unknown'
			active = 'Unknown'
			onair = 'Unknown'
			mature = 'Unknown'
			epgInfo = ''
			logoUrl = None
			sharable = 'True'
			epgLink = 'Unknown'
			
			try:
				mature = CACHE_LINKS[count]['mature']
			except:
				pass
			try:
				logoUrl = CACHE_LINKS[count]['logoUrl']
				desc = CACHE_LINKS[count]['desc']
				country = CACHE_LINKS[count]['country']
				lang = CACHE_LINKS[count]['lang']
				genre = CACHE_LINKS[count]['genre']
				views = CACHE_LINKS[count]['views']
				active = CACHE_LINKS[count]['active']
				onair = CACHE_LINKS[count]['onair']
				epgInfo = CACHE_LINKS[count]['epg']
				sharable = CACHE_LINKS[count]['sharable']
				epgLink = CACHE_LINKS[count]['epgLink']
			except:
				pass
			
			
			abortBool2 = ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session)
			
			summaryStr = '#: ' + channelNum + ' | '+ desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang
			if epgInfo != '':
				summaryStr = summaryStr + ' | ' + epgInfo
			
			if not abortBool2 and (query.lower() in channelDesc.lower() or query == channelNum):
				#Log(title + ' : ' + str(abortBool2))
				#Log(mature)
				if logoUrl <> None:
					oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
				else:
					oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = R(ICON_SERIES)))
			elif '~' in query and int(channelNum) > start-1 and int(channelNum) < end+1:
				if not Prefs['show_adult'] and mature == 'Y' and Dict['AccessPin'+session] != Prefs['access_pin']:
					pass
				else:
					if logoUrl <> None:
						oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
					else:
						oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = R(ICON_SERIES)))
		except:
			pass
	
	if len(oc) == 0:
		return ObjectContainer(header='Search Results', message='No Channels Available based on Search query', title1='Search Results')
		
	if Prefs['use_datesort']:
		oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
	else:	
		oc.objects.sort(key=lambda obj: obj.title)
		
	if Client.Product in DumbKeyboard.clients or UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
		
	# CACHE_LINKS = {}
	Dict.Save()
	abortBool = RefreshListing(False)
	
	try:
		if Prefs['use_transcoder']:
			transcoder.CloseThisSessionPidInstance()
	except:
		pass
	return oc

######################################################################################
@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title):
	oc = ObjectContainer(title2='Search Using Term')
	oc2 = []
	queryLast = Dict['LastUsedSearchQuery']
	if queryLast <> None and queryLast != '' and queryLast != 'removed':
		if '~' in queryLast:
			oc.add(DirectoryObject(key = Callback(Search, query = queryLast), title = queryLast, thumb = R(ICON_PAGE)))
		else:
			oc.add(DirectoryObject(key = Callback(Search, query = queryLast), title = queryLast, thumb = R(ICON_SEARCH)))
	
	for each in Dict:
		query = Dict[each]
		#Log("each-----------" + each)
		#Log("query-----------" + query)
		if 'MyCustomSearch' in each and query != 'removed' and query <> None and query != '' and queryLast != query:
			if '~' in query:
				oc2.append(DirectoryObject(key = Callback(Search, query = query), title = query, thumb = R(ICON_PAGE)))
			else:
				oc2.append(DirectoryObject(key = Callback(Search, query = query), title = query, thumb = R(ICON_SEARCH)))
		
	if len(oc2) > 0:
		for o in sorted(oc2, key=lambda obj: obj.title):
			oc.add(o)
	
	#add a way to clear search que list
	oc.add(DirectoryObject(
		key = Callback(ClearSearches),
		title = "Clear Search Queue",
		thumb = R(ICON_SEARCH),
		summary = "CAUTION! This will clear your entire search queue list!"
		)
	)
	
	return oc
	
######################################################################################
# Clears the Dict that stores the search list
	
@route(PREFIX + "/clearsearches")
def ClearSearches():

	# CACHE_LINKS = {}
	for each in Dict:
		if 'MyCustomSearch' in each:
			Dict[each] = 'removed'
			
	Dict['LastUsedSearchQuery'] = None
	Dict.Save()
	abortBool = RefreshListing(False)
	return ObjectContainer(header="Search Queue", message='Your Search Queue list will be cleared soon.', title1='Search Queue')
	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title)
	abortBool = RefreshListing(False)
	session = common_fnc.getSession()
	
	if abortBool:
		return ObjectContainer(header=title, message='Connection error or Server seems down !', title1='Error')
		
	dict_len = len(CACHE_LINKS)
	if dict_len == 0:
		return ObjectContainer(header='Bookmarks', message='No Channels loaded ! Channel list needs to be initialized first.', title1='Bookmarks')
		
	for x in range(0,len(CACHE_LINKS)):
		try:
			#for each in Dict:
			channelNum = CACHE_LINKS[x]['channelNum']
			#Log("channelNum--------- " + str(channelNum))
			
			channelDesc = CACHE_LINKS[x]['channelDesc']
			channelUrl = CACHE_LINKS[x]['channelUrl']
			dateStr = CACHE_LINKS[x]['channelDate']
			title = channelDesc
			#Log("channelDesc--------- " + str(channelDesc))
			
			desc = 'Unknown'
			country = 'Unknown'
			lang = 'Unknown'
			genre = 'Unknown'
			views = 'Unknown'
			epgInfo = ''
			logoUrl = None
			sharable = 'True'
			epgLink = 'Unknown'
			
			try:
				desc = CACHE_LINKS[x]['desc']
				country = CACHE_LINKS[x]['country']
				lang = CACHE_LINKS[x]['lang']
				genre = CACHE_LINKS[x]['genre']
				views = CACHE_LINKS[x]['views']
				epgInfo = CACHE_LINKS[x]['epg']
				sharable = CACHE_LINKS[x]['sharable']
				epgLink = CACHE_LINKS[x]['epgLink']
			except:
				pass
			try:
				logoUrl = CACHE_LINKS[x]['logoUrl']
			except:
				pass
			
			summaryStr = '#: ' + channelNum + ' | ' + desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang
			if epgInfo != '':
				summaryStr = summaryStr + ' | ' + epgInfo
			
			mature = 'N'
			try:
				mature = isAdultChannel(channelDesc, genre)
			except:
				pass
			
			if not Prefs['show_adult'] and mature == 'Y' and Dict['AccessPin'+session] != Prefs['access_pin']:
				pass
			else:
				if (Dict[str(channelNum)] <> None and Dict[str(channelNum)] <> 'removed' and 'MyCustomSearch' not in Dict[str(channelNum)]) or (Dict[str(title+'-'+genre+'-'+lang+'-'+country)] <> None and Dict[str(title+'-'+genre+'-'+lang+'-'+country)] <> 'removed' and 'MyCustomSearch' not in Dict[str(title+'-'+genre+'-'+lang+'-'+country)]):
					#Log("channelDesc--------- " + str(channelDesc) + " " + summaryStr + " " + dateStr + " " + str(logoUrl))
					if logoUrl <> None:
						oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
					else:
						oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = R(ICON_SERIES)))
		except:
			pass
	
	if len(oc) == 0:
		return ObjectContainer(header='Bookmarks', message='No Bookmarked Channels Available.', title1='No Bookmarks')
	
	if Prefs['use_datesort']:
		oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
	else:	
		oc.objects.sort(key=lambda obj: obj.title)
		
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_BOOKMARK),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
	
	if len(oc) == 1:
		return ObjectContainer(header='Bookmarks', message='No Bookmarked Channels Available', title1='No Bookmarks')
		
	try:
		if Prefs['use_transcoder']:
			transcoder.CloseThisSessionPidInstance()
	except:
		pass
	return oc

######################################################################################
# Checks a show to the bookmarks list using the title as a key for the url
@route(PREFIX + "/checkbookmark")	
def CheckBookmark(channelNum, url, title, genre, lang, country):
	bool = False
	url = Dict[channelNum]
	url2 = Dict[str(title+'-'+genre+'-'+lang+'-'+country)]
	#Log("url check-----------" + str(url))
	if (url != None and url <> 'removed') or (url2 != None and url2 <> 'removed'):
		bool = True
	
	return bool

######################################################################################
# Adds a Channel to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/addbookmark")
def AddBookmark(channelNum, url, title, genre, lang, country):
	
	Dict[str(title+'-'+genre+'-'+lang+'-'+country)] = str(title+'-'+genre+'-'+lang+'-'+country)

	#Log("url add-----------" + str(url))
	# CACHE_LINKS = {}
	Dict.Save()
	return ObjectContainer(header= 'Channel: ' + title, message='This Channel has been added to your bookmarks.', title1='Bookmark Added')
######################################################################################
# Removes a Channel to the bookmarks list using the title as a key for the url

@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, channelNum, url, genre, lang, country):
	
	#url = Dict[title]
	#Log("url remove-----------" + str(url))
	doSave = False
	if Dict[channelNum] <> None and Dict[channelNum] != 'removed':
		Dict[channelNum] = None
		doSave = True
	
	if Dict[str(title+'-'+genre+'-'+lang+'-'+country)] <> None and Dict[str(title+'-'+genre+'-'+lang+'-'+country)] != 'removed':
		Dict[str(title+'-'+genre+'-'+lang+'-'+country)] = None
		doSave = True
		
	if doSave:
		# CACHE_LINKS = {}
		Dict.Save()
	return ObjectContainer(header='Channel: '+channelNum, message='This Channel has been removed from your bookmarks.', title1='Bookmark Removed')	
######################################################################################
# Clears the Dict that stores the bookmarks list
	
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	for channelNum in Dict:
		vals = Dict[channelNum]

		if vals <> 'removed':
			Dict[channelNum] = None
			#Log("url remove-----------" + str(url))
		vals2 = Dict[vals]
		if vals2 <> 'removed':
			Dict[vals] = None
			#Log("url remove-----------" + str(url))
	# CACHE_LINKS = {}
	Dict.Save()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.', title1='Bookmarks Cleared')
	
######### PINS #############################################################################
# Checks a show to the Pins list using the title as a key for the url
@route(PREFIX + "/checkpin")	
def CheckPin(url):

	#url = common_fnc.GetRedirector(url)
	bool = False
	url = Dict['Plex-Pin-Pin'+url]
	#Log("url check-----------" + str(url))
	if url != None and url <> 'removed':
		bool = True
	
	return bool

######################################################################################
# Adds a Channel to the Pins list using the title as a key for the url
	
@route(PREFIX + "/addpin")
def AddPin(channelNum, url, title, channelDesc, logoUrl, country, lang, genre, sharable, epgLink):
	
	#url = common_fnc.GetRedirector(url)
	Dict['Plex-Pin-Pin'+url] = channelNum + 'Key4Split' + title + 'Key4Split' + channelDesc + 'Key4Split' + url + 'Key4Split' + logoUrl + 'Key4Split' + country + 'Key4Split' + lang + 'Key4Split' + genre + 'Key4Split' + sharable + 'Key4Split' + epgLink 
	
	#Log("url add-----------" + str(url))
	# CACHE_LINKS = {}
	Dict.Save()
	return ObjectContainer(header= 'Channel: ' + channelNum, message='This Channel has been added to your Pins.', title1='Pin Added')
######################################################################################
# Removes a Channel to the Pins list using the title as a key for the url
	
@route(PREFIX + "/removepins")
def RemovePin(url):
	
	channelNum = 'Undefined'
	#url = common_fnc.GetRedirector(url)
	#url = Dict[title]
	#Log("url remove-----------" + str(url))
	keys = Dict['Plex-Pin-Pin'+url]
	if 'Key4Split' in keys:
		values = keys.split('Key4Split')
		channelNum = values[0]
		Dict['Plex-Pin-Pin'+url] = 'removed'
		# CACHE_LINKS = {}
		Dict.Save()
	return ObjectContainer(header='Channel: '+channelNum, message='This Channel has been removed from your Pins.', title1='Pin Removed')	
######################################################################################
# Clears the Dict that stores the Pins list
	
@route(PREFIX + "/clearpins")
def ClearPins():

	for each in Dict:
		keys = Dict[each]
		if 'Key4Split' in keys:
			Dict[each] = 'removed'
			#Log("url remove-----------" + str(url))
	# CACHE_LINKS = {}
	Dict.Save()
	return ObjectContainer(header="My Pins", message='Your Pins list will be cleared soon.', title1='Pins Cleared')
	
######################################################################################
# Pins
@route(PREFIX + "/pins")	
def Pins(title):

	oc = ObjectContainer(title1 = title)
	session = common_fnc.getSession()
	
	
	for each in Dict:
		try:
			keys = Dict[each]
			#Log("keys--------- " + str(keys))
			if 'Key4Split' in str(keys):
				values = keys.split('Key4Split')
				logoUrl = None
				epgLink = None
				country = 'Unknown'
				lang = 'Unknown'
				genre = 'Uncategorized'
				sharable = 'Unknown'
				epgLink = 'Unknown'
				if len(values) > 9:
					channelNum = values[0]
					title = values[1]
					channelDesc = values[2]
					channelUrl = values[3]
					logoUrl = values[4]
					country = values[5]
					lang = values[6]
					genre = values[7]
					sharable = values[8]
					epgLink = values[9]
				elif len(values) > 5:
					channelNum = values[0]
					title = values[1]
					channelDesc = values[2]
					channelUrl = values[3]
					logoUrl = values[4]
					country = values[5]
					lang = values[6]
					genre = values[7]
					sharable = values[8]
				elif len(values) == 4 or len(values) == 5:
					channelNum = values[0]
					title = values[1]
					channelDesc = values[2]
					channelUrl = values[3]
					if len(values) >= 5:
						logoUrl = values[4]
				else:
					channelNum = values[0]
					channelDesc = values[1]
					channelUrl = values[2]
					title = channelDesc
				#Log("channelDesc--------- " + str(channelDesc))
				
				desc = 'Unknown'
				views = 'Unknown'
				epgInfo = ' '
					
				summaryStr = '#: ' + channelNum + ' | '+ title + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang
				if epgInfo != '':
					summaryStr = summaryStr + ' | ' + epgInfo
				
				mature = 'N'
				try:
					mature = isAdultChannel(title, genre)
				except:
					pass
					
				abortBool2 = ChannelFilters(active='Y', onair='Y', lang=lang, country=country, mature=mature, session=session)
					
				if abortBool2:
					pass
				else:
					if 'removed' not in channelUrl:
						if logoUrl <> None:
							oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), title = title, thumb = logoUrl))
						else:
							oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), title = title, thumb = R(ICON_SERIES)))

		except:
			pass
			
	if len(oc) == 0:
		return ObjectContainer(header='Pins', message='No Pinned Channels Available', title1='Pins Unavailable')
	
	oc.objects.sort(key=lambda obj: obj.title)
	#add a way to clear pin list
	oc.add(DirectoryObject(
		key = Callback(ClearPins),
		title = "Clear All Pins",
		thumb = R(ICON_PIN),
		summary = "CAUTION! This will clear your entire Pins list!"
		)
	)

	try:
		if Prefs['use_transcoder']:
			transcoder.CloseThisSessionPidInstance()
	except:
		pass
	return oc

######### PlexShare #############################################################################
# Checks a show to the Pins list using the title as a key for the url
@route(PREFIX + "/checkplexshare")	
def CheckPlexShare(url):

	bool = False
	#url = common_fnc.GetRedirector(url)
	if len(CCLOUD_PAGE_DATA) > 0 and url in CCLOUD_PAGE_DATA[0]:
		bool = True
	url = Dict['Plex-Share-Pin'+url]
	#Log("url check-----------" + str(url))
	if url != None and url <> 'removed':
		bool = True
	
	
	return bool

########### PlexShare ###########################################################################
# Yes/No for PlexShare
@route(PREFIX + "/addplexshare")
def AddPlexShare(url, title, country, lang, genre, logoUrl, channelNum, channelDesc, sharable, epgLink):	
	
	if Dict['PlexShareThreadAlive'] == 'True':
		return ObjectContainer(header='Please wait', message='Thread Plex-Share Still Running ! Please try again in a minute.', title1='Please wait')
	
	oc = ObjectContainer(title1 = unicode('Confirm Channel Sharing ?'))
	
	oc.add(DirectoryObject(
			key = Callback(DoPlexShare, url = url, title = title, country = country, lang = lang, genre = genre, logoUrl=logoUrl),
			title = "YES",
			summary = 'Adds the current Channel to the cCloudTV community listing',
			thumb = R(ICON_OK)
		))
	oc.add(DirectoryObject(
			key = Callback(ChannelPage, url = url, title = title, channelDesc = channelDesc, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), 
			title = "CANCEL",
			summary = 'Cancel current Channel sharing',
			thumb = R(ICON_CANCEL)
		))
	return oc
	
########### PlexShare ###########################################################################
# Shares a Channel info online with cCloud Tv
@route(PREFIX + "/doplexshare")
def DoPlexShare(url, title, country, lang, genre, logoUrl, submit=False):
	
	# Make sure genre, language and country have valid cCloud values
	if submit and genre in common.CATEGORIES_LIST_SINGLETON and lang in common.LANGUAGES_LIST_SINGLETON and country in common.COUNTRY_LIST_SINGLETON:
	
		#url = common_fnc.GetRedirector(url)
		if CheckPlexShare(url=url):
			return ObjectContainer(header= 'Channel: ' + title, message='This Channel has already been shared in the cCloudTV community listing.', title1='Channel Unsharable')
		
		try:
			dateToday = DT.date.today()
			dateStr = str(dateToday.month) + '/' + str(dateToday.day) + '/' + str(dateToday.year)
			upload_str = title + ';' + genre + ';' + country + ';' + lang + ';' + url + ';' + logoUrl + ';' + dateStr
			#Log(upload_str)
			bool = share.commit(url, upload_str)
			if bool:
				## CACHE_LINKS = {}
				#Dict['Plex-Share-Pin'+url] = url
				#Log("url add-----------" + str(url))
				#Dict.Save()
				#plexShareUrl = PLEXSHARE_URL

				#plexShareUrl = common_fnc.GetRedirector(PLEXSHARE_URL)
				#Log("plexShareUrl-----------" + str(plexShareUrl))
				try:
					
					# Parse Private list in separate thread
					Dict['PlexShareThreadAlive'] = 'True'
					Thread.Create(ConfirmPlexShare,{},url)
				except:
					pass
					
				oc = ObjectContainer(title2 = 'Successfully Shared')
				oc.add(DirectoryObject(key = Callback(ShowMenu, title = 'Main Menu'), title = ' Return to Main Menu', summary = 'Return to Main Menu', thumb = R(ICON)))
				return oc
				
				#return ObjectContainer(header= 'Channel: ' + title, message='This Channel has been shared and will appear in cCloud listing soon.')
			else:
				return ObjectContainer(header= 'Channel: ' + title, message='An error occurred uploading this channel data', title1='Error')
		except:
			return ObjectContainer(header= 'Channel: ' + title, message='An error occurred sharing this channel', title1='Error')
	else:
		oc = ObjectContainer(title1 = 'Set Missing Metadata')
		
		if genre == 'Uncategorized' or genre == None or genre not in common.CATEGORIES_LIST_SINGLETON:
			oc.add(DirectoryObject(key = Callback(SetGenre, title='Category', filter2=lang, filter3=country, url=url, ctitle=title, logoUrl=logoUrl), title = 'Set Category', thumb = R(ICON_GENRES)))
		else:
			# save for next usage
			Dict['LastUsedShare'+'Category'] = genre
		
		if lang == 'Unknown' or lang == None or lang not in common.LANGUAGES_LIST_SINGLETON:
			oc.add(DirectoryObject(key = Callback(SetLanguage, title='Language', filter1=genre, filter3=country, url=url, ctitle=title, logoUrl=logoUrl), title = 'Set Language', thumb = R(ICON_LANGUAGES)))
		else:
			Dict['LastUsedShare'+'Language'] = lang

		if country == 'Unknown' or country == None or not common.isCountryCodeDefined(country):
			oc.add(DirectoryObject(key = Callback(SetCountry, title='Country', filter1=genre, filter2=lang, url=url, ctitle=title, logoUrl=logoUrl), title = 'Set Country', thumb = R(ICON_COUNTRIES)))
		else:
			Dict['LastUsedShare'+'Country'] = country
			
		if genre in common.CATEGORIES_LIST_SINGLETON and lang in common.LANGUAGES_LIST_SINGLETON and country in common.COUNTRY_LIST_SINGLETON:
			Dict.Save()
			oc.add(DirectoryObject(
				key = Callback(DoPlexShare, url = url, title = title, genre = genre, lang = lang, country = country, logoUrl=logoUrl, submit=True), 
				title = 'Submit Channel',
				summary = 'Channel: ' + title + ' | Category: ' + genre + ' | Country: ' + country + ' | Language: ' + lang,
				thumb = R(ICON_UPLOAD)))
		oc.add(DirectoryObject(
			key = Callback(DoPlexShare, url = url, title = title, genre = genre, lang = lang, country = country, logoUrl=logoUrl), 
			title = 'Clear Selections',
			summary = 'Resets the Category, Language and Country selection for this Channel to None',
			thumb = R(ICON_CLEAR)))
		return oc

@route(PREFIX + "/confirmPlexshare")
def ConfirmPlexShare(url):

	confirmBool = False
	isCommittedBool = False
	plexShareUrl = PLEXSHARE_URL
	#plexShareUrl = common_fnc.GetRedirector(PLEXSHARE_URL)
	time.sleep(10)
	expireCount = 0
	try:
		while not confirmBool or expireCount >= 10:
		
			if not isCommittedBool and share.isCommitted(url) and share.isConfirmCommitted(url):
				isCommittedBool = True
			
			if not CheckPlexShare(url):
				if isCommittedBool:
					resp = HTTP.Request(url=plexShareUrl, sleep=10.0).content
					if len(resp) > 0:
						confirmBool = True
						if Prefs['debug']:
							Log('Channel Shared ! ' + url)
							
						# CACHE_LINKS = {}
						Dict['PlexShareThreadAlive'] = 'False'
						Dict['Plex-Share-Pin'+url] = url
						return
			else:
				confirmBool = True
				break
			time.sleep(20)
			expireCount = expireCount + 1
	except:
		pass

	# CACHE_LINKS = {}
	Dict['PlexShareThreadAlive'] = 'False'
	
	Dict.Save()
	return
	
		
@route(PREFIX + "/setgenre")
def SetGenre(title, url, ctitle, logoUrl, filter1=None, filter2=None, filter3=None):

	oc = ObjectContainer(title2=title)
	oc2 = []
	LastSaveCategory = ' '
	if Dict['LastUsedShare'+title] <> None and Dict['LastUsedShare'+title] != 'Uncategorized':
		LastSaveCategory = Dict['LastUsedShare'+title]
		oc.add(DirectoryObject(
				key = Callback(DoPlexShare, url = url, title = ctitle, genre = LastSaveCategory, lang = filter2, country = filter3, logoUrl=logoUrl),
				title = LastSaveCategory,
				summary = 'Set this Channel\'s Category as: ' + LastSaveCategory,
				thumb = R(ICON_GENRE)
			))
	for genre in common.CATEGORIES_LIST_SINGLETON:
		if genre == 'Top10':
			pass
		elif genre != LastSaveCategory:
			oc2.append(DirectoryObject(
				key = Callback(DoPlexShare, url = url, title = ctitle, genre = genre, lang = filter2, country = filter3, logoUrl=logoUrl),
				title = genre,
				summary = 'Set this Channel\'s Category as: ' + genre,
				thumb = R(ICON_GENRE)
			))
	
	if len(oc2) > 0:
		for o in sorted(oc2, key=lambda obj: obj.title):
			oc.add(o)
	
	return oc

@route(PREFIX + "/setlanguage")
def SetLanguage(title, url, ctitle, logoUrl, filter1=None, filter2=None, filter3=None):

	oc = ObjectContainer(title2=title)
	
	LastSaveLanguage = ' '
	if Dict['LastUsedShare'+title] <> None and Dict['LastUsedShare'+title] != 'Unknown':
		LastSaveLanguage = Dict['LastUsedShare'+title]
		oc.add(DirectoryObject(
			key = Callback(DoPlexShare, url = url, title = ctitle, genre = filter1, lang = LastSaveLanguage, country = filter3,  logoUrl=logoUrl), title = LastSaveLanguage, 
			summary = 'Set this Channel\'s Language as: ' + LastSaveLanguage,
			thumb = R(ICON_GENRE)))
	for language in sorted(common.LANGUAGES_LIST_SINGLETON):
		if language != LastSaveLanguage:
			oc.add(DirectoryObject(
				key = Callback(DoPlexShare, url = url, title = ctitle, genre = filter1, lang = language, country = filter3,  logoUrl=logoUrl), title = language,
				summary = 'Set this Channel\'s Language as: ' + language,
				thumb = R(ICON_GENRE)))
			
	#oc.objects.sort(key=lambda obj: obj.title)
	return oc
	
@route(PREFIX + "/setcountry")
def SetCountry(title, url, ctitle, logoUrl, filter1=None, filter2=None, filter3=None):
	
	oc = ObjectContainer(title2='Set Country')
	oc2 = []
	
	LastSaveCountry = ' '
	if Dict['LastUsedShare'+title] <> None and Dict['LastUsedShare'+title] != 'Unknown':
		LastSaveCountry = Dict['LastUsedShare'+title]
		oc.add(DirectoryObject(
			key = Callback(DoPlexShare, url = url, title = ctitle, genre = filter1, lang = filter2, country = common.getCountryCode(LastSaveCountry),  logoUrl=logoUrl), title = common.getCountryName(LastSaveCountry),
			summary = 'Set this Channel\'s Country as: ' + common.getCountryName(LastSaveCountry),
			thumb = R(ICON_GENRE)))
	for country in sorted(common.COUNTRY_ARRAY_LIST_SINGLETON):
		if country.lower() != LastSaveCountry.lower():
			oc2.append(DirectoryObject(
				key = Callback(DoPlexShare, url = url, title = ctitle, genre = filter1, lang = filter2, country = common.getCountryCode(country), logoUrl=logoUrl), 
				title = country.title(), 
				summary = 'Set this Channel\'s Country as: ' + country.title(),
				thumb = R(ICON_GENRE)))
	if len(oc2) > 0:
		for o in sorted(oc2, key=lambda obj: obj.title):
			oc.add(o)

	return oc
	
######################################################################################
# Fix Title
@route(PREFIX + "/fixtitle")	
def FixTitle(title, engonly=False, sharable=False):

	if '_' in title:
		title = title.replace('_',' ')
	if title.lower() == title:
		title = title.title()
	if engonly:
		title = re.sub(r'[^0-9a-zA-Z \-/.:+&!()]', '?', title)
	if sharable:
		title = re.sub(r'[^0-9a-zA-Z \-.+&!()]', '?', title)
	
	return title
	
######################################################################################	
# Fix Url
@route(PREFIX + "/fixurl")	
def FixUrl(url):

	if '?' in url:
		n = url.index('?')+1
		par = urllib2.quote(url[n:], safe='/=&')
		#par = url[n:].replace('/','%2F')
		url = url[0:n] + par
		#Log(url)
	url = url.replace('.ts','.m3u8')
	return url
######################################################################################
# Fix Genre
@route(PREFIX + "/fixgenre")	
def FixGenre(genre):

	if Prefs['merge_cats'] and 'Public-' in genre:
		genre = genre.replace('Public-','')
	
	return genre
	
####################################################################################################
# Fix Language
@route(PREFIX + "/fixlanguage")	
def FixLanguage(lang):

	if lang.lower() == 'indian':
		lang = 'Hindi'
	elif lang.lower() == 'unk':
		lang = 'Unknown'
		
	#Log("lang ----- " + str(lang))
	return lang
	
####################################################################################################
# Fix Country
@route(PREFIX + "/fixcountry")	
def FixCountry(country):

	if country.lower() == 'gb':
		country = 'UK'
	elif country.lower() == 'usa':
		country = 'US'
		
	if len(country) > 2 and '/' not in country:
		#Log("country1 ----- " + str(country))
		country = common.COUNTRY_ARRAY_LIST.get(country.lower(),"UNK").upper()
		#Log("country2 ----- " + str(country))
		
	return country
			
####################################################################################################
# Multi Threading
####################################################################################################
@route(PREFIX + "/IsMultiThreadRunning")
def IsMultiThreadRunning(nthreads):
	for threadn in range(0,nthreads):
		if Dict['ListingThreadAlive'+str(threadn)] == 'True':
			return True
	return False
	
@route(PREFIX + "/MultiThreadedRecentListing")
def MultiThreadedRecentListing(title, filterDate, oc):
	
	nthreads = NO_OF_THREADS
	session = common_fnc.getSession()
	
	for threadn in range(0,nthreads):
		n1 = threadn + threadn*len(CACHE_LINKS)/nthreads
		n2 = n1 + (len(CACHE_LINKS)/nthreads)
		#Log(str(n1) + ' : ' + str(n2))
		Dict['ListingThreadAlive'+str(threadn)] = 'True'
		Thread.Create(MultiThreadedRecentListing2, {}, filterDate, n1, n2, oc, threadn, session)
		#Log("Thread " + str(threadn) + " started")
	
	
	while IsMultiThreadRunning(nthreads):
		#Log("Sleeping ---------- ")
		time.sleep(1)
		
	return oc

@route(PREFIX + "/MultiThreadedRecentListing2")
def MultiThreadedRecentListing2(filterDate, n1, n2, oc, threadn):
	try:
		for count in range(n1,n2):
			
			channelNum = CACHE_LINKS[count]['channelNum']
			channelDesc = CACHE_LINKS[count]['channelDesc']
			channelUrl = CACHE_LINKS[count]['channelUrl']
			dateStr = CACHE_LINKS[count]['channelDate']
			#Log("Date===========  " + dateStr)
			dateStrA = dateStr.split('/')
			dateObj = datetime(int(dateStrA[2]), int(dateStrA[0]), int(dateStrA[1]))
			
			title = unicode(channelDesc)
			
			desc = 'Unknown'
			country = 'Unknown'
			lang = 'Unknown'
			genre = 'Unknown'
			views = 'Unknown'
			active = 'Unknown'
			onair = 'Unknown'
			mature = 'Unknown'
			epgLink = 'Unknown'
			logoUrl = None
			sharable = 'True'
			try:
				logoUrl = CACHE_LINKS[count]['logoUrl']
				mature = CACHE_LINKS[count]['mature']
				desc = CACHE_LINKS[count]['desc']
				country = CACHE_LINKS[count]['country']
				lang = CACHE_LINKS[count]['lang']
				genre = CACHE_LINKS[count]['genre']
				views = CACHE_LINKS[count]['views']
				active = CACHE_LINKS[count]['active']
				onair = CACHE_LINKS[count]['onair']
				epgInfo = CACHE_LINKS[count]['epg']
				sharable = CACHE_LINKS[count]['sharable']
				epgLink = CACHE_LINKS[count]['epgLink']
			except:
				pass
			
			#abortBool2 = ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session)
			
			summaryStr = '#: ' + channelNum + ' | '+ desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang + ' | ' + views + ' Views'
			if epgInfo != '':
				summaryStr = summaryStr + ' | ' + epgInfo
				
			#Log("Date===========  " + dateStr + " = " + str(dateObj) + " = " + str(filterDate))
			#Log(channelNum + " : channelDesc----------" + channelDesc)
				
			if dateObj >= filterDate and not ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session):
				if Client.Platform not in LIST_VIEW_CLIENTS:
					oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = Resource.ContentsOfURLWithFallback(url = logoUrl, fallback= R(ICON_SERIES))))
				else:
					oc.add(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = None))
	except:
		pass

	Dict['ListingThreadAlive'+str(threadn)] = 'False'
	#Log("Thread " + str(threadn) + " ended")
	return
	
@route(PREFIX + "/MultiThreadedDisplayGenreLangConSort")
def MultiThreadedDisplayGenreLangConSort(titleGen, type, oc, filter1, filter2, filter3, startN=0):
	
	nthreads = NO_OF_THREADS
	session = common_fnc.getSession()
	
	for threadn in range(0,nthreads):
		n1 = int(startN) + (threadn + threadn*len(CACHE_LINKS)/nthreads)
		n2 = min(n1 + (len(CACHE_LINKS)/nthreads), len(CACHE_LINKS))
		#Log(str(n1) + ' : ' + str(n2))
		Dict['ListingThreadAlive'+str(threadn)] = 'True'
		Thread.Create(MultiThreadedDisplayGenreLangConSort2,{},titleGen, type, n1, n2, oc, threadn, session, filter1, filter2, filter3)
		#Log("Thread " + str(threadn) + " started")
	
	count = 0
	while IsMultiThreadRunning(nthreads):
		#Log("Sleeping ---------- ")
		time.sleep(1)
		count += 1
		if count >=10:
			return oc
		
	return oc
	
@route(PREFIX + "/MultiThreadedDisplayGenreLangConSort2")
def MultiThreadedDisplayGenreLangConSort2(titleGen, type, n1, n2, oc, threadn, session, filter1, filter2, filter3):

	#Log("DisplayGenreLangConSort------------------- " + str(len(CACHE_LINKS)))
	
	buildFilter = ''
	if filter1 <> None:
		buildFilter += filter1
	if filter2 <> None:
		buildFilter += filter2
	if filter3 <> None:
		buildFilter += filter3
	
	#try:
	for count in range(n1,n2):
		
		#items_dict[count] = {'channelNum': channelNum, 'channelDesc': channelDesc, 'channelUrl': channelUrl, 'channelDate': dateStr}
		
		channelNum = CACHE_LINKS[count]['channelNum']
		channelDesc = CACHE_LINKS[count]['channelDesc']
		channelUrl = CACHE_LINKS[count]['channelUrl']
		dateStr = CACHE_LINKS[count]['channelDate']
		
		title = unicode(channelDesc)
		tkey = 'Unknown'
		desc = 'Unknown'
		country = 'Unknown'
		lang = 'Unknown'
		genre = 'Unknown'
		views = 'Unknown'
		active = 'Unknown'
		onair = 'Unknown'
		mature = 'Unknown'
		epgInfo = ''
		logoUrl = None
		sharable = 'True'
		epgLink = 'Unknown'
		
		try:
			logoUrl = CACHE_LINKS[count]['logoUrl']
		except:
			pass
		try:
			sharable = CACHE_LINKS[count]['sharable']
		except:
			pass
		try:
			mature = CACHE_LINKS[count]['mature']
			desc = CACHE_LINKS[count]['desc']
			country = CACHE_LINKS[count]['country']
			lang = CACHE_LINKS[count]['lang']
			genre = CACHE_LINKS[count]['genre']
			views = CACHE_LINKS[count]['views']
			active = CACHE_LINKS[count]['active']
			onair = CACHE_LINKS[count]['onair']
			epgInfo = CACHE_LINKS[count]['epg']
			epgLink = CACHE_LINKS[count]['epgLink']
		except:
			pass
		
		if type == 'Category':
			tkey = genre
		elif type == 'Language':
			tkey = lang
		elif type == 'Country':
			tkey = country
			
		buildFilterM = ''
		if filter1 <> None:
			buildFilterM += genre
		if filter2 <> None:
			if ('/' in tkey and titleGen in tkey.split('/')):
				buildFilterM += titleGen
			else:
				buildFilterM += lang
		if filter3 <> None:
			buildFilterM += country
		
		summaryStr = '#: ' + channelNum + ' | '+ desc + ' | Category:' + genre + ' | Country:' + country + ' | Language:' + lang
		
		if epgInfo != '':
			summaryStr = summaryStr + ' | ' + epgInfo

		#Log("title----------" + title)
			
		if ((buildFilter == buildFilterM) and not ChannelFilters(active=active, onair=onair, lang=lang, country=country, mature=mature, session=session)):
			if Client.Platform not in LIST_VIEW_CLIENTS:
				if logoUrl <> None:
					oc.append(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = logoUrl))
				else:
					oc.append(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = R(ICON_SERIES)))
			else:
				oc.append(DirectoryObject(key = Callback(ChannelPage, url = channelUrl, title = title, channelDesc = summaryStr, channelNum=channelNum, logoUrl=logoUrl, country=country, lang=lang, genre=genre, sharable=sharable, epgLink=epgLink), tagline=dateStr, summary = summaryStr, title = title, thumb = None))
		# if (count - n1) >= 500:
			# Log("---------------------------" + str(len(oc)))
			# oc2 = ObjectContainer(title2=titleGen)
			##oc2 = MultiThreadedDisplayGenreLangConSort(titleGen, type, oc2, count)
			##oc.add(oc2)
			# oc.add(DirectoryObject(key = Callback(MultiThreadedDisplayGenreLangConSort, titleGen=titleGen, type=type, oc=oc2, startN=count), title = 'More >>', summary = 'More Channels >>', thumb = R(ICON_NEXT)))
			# Log("---------------------------" + str(len(oc)))
			# Dict['ListingThreadAlive'+str(threadn)] = 'False'
			# return
	#except:
	#	pass
	
	Dict['ListingThreadAlive'+str(threadn)] = 'False'
	#Log("Thread " + str(threadn) + " ended")
	return
	