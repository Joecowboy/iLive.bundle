####################################################################################################
#
# File:		__init__.py
# Author:	joe
# Date:		02/16/2013
# Version:	0.1
# About:	This plugin will enable applicable iLive 
#		(www.ilive.to) customers to view the iLive IPTV 
#		Channels through Plex Media Server. Note: Some 
#		channels require authentication, as such they may not
#		work through this plugin - unless you authenticate 
#		through the iLive IPTV Website first.
#
####################################################################################################

PREFIX  = "/video/ilive"
TITLE   = "iLive - Live Streaming TV"
ART     = "art-default.jpg"
ICON    = "icon-default.png"
CHANNEL = "icon-channels.png"
SHOWS   = "http://www.ilive.to/channels/?p="

import time

####################################################################################################
def Start():

	# Initialize the plug-in
	Plugin.AddPrefixHandler(PREFIX, MainMenu, TITLE, ICON, ART)
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = TITLE
	ObjectContainer.view_group = "InfoList"

	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)

	HTTP.CacheTime = 0
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:15.0) Gecko/20100101 Firefox/15.0.1"


####################################################################################################
#@handler(PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():

	oc = ObjectContainer()

	i = 1	
	NUMPAGES = len(HTML.ElementFromURL(SHOWS + str(i)).xpath('//p[@class="pages"]/span/a'))

	while i <= NUMPAGES:
		do = DirectoryObject()
		do.title = "List of Channels - Page "+str(i)
		do.key = Callback(LiveShowPageAdd, title=do.title, page=str(i))
		do.summary = "Select to show Page "+str(i)+" of the line up of live channels streaming from iLive."
		do.thumb = R(CHANNEL)
		oc.add(do)

		i += 1

	return oc


####################################################################################################
#@route(PREFIX + '/page')
def LiveShowPageAdd(title, page):

	oc = ObjectContainer(title2=title)

	for channels in HTML.ElementFromURL(SHOWS + page).xpath('//ul[@class="clist clearfix"]/li'):
		url = channels.xpath('./a')[0].get('href')
		thumb = channels.xpath('./a/img')[0].get('data-lazy-src')
		cname = String.Unquote(channels.xpath('./a/strong')[0].text, usePlus=True).replace("_"," ")
		title = "Watch Live " + cname
		show = "Check out the TV guide to find out"
		duration = None
		summary = "You are watching " + cname + " part of live stream channel line up on iLive."
		streamId = thumb.rpartition('/')[2].split('_')[0]
		url = url+"/?streamId="+streamId
		localtime = time.asctime(time.localtime(time.time()))
		airdate = Datetime.ParseDate(localtime)

		oc.add(EpisodeObject(
				url = url,
				title = title,
				summary = summary,
				duration = duration,
				show = show,
				source_title = 'iLive',
				originally_available_at = airdate,
				thumb = Callback(GetThumb, url=thumb)))

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

	return oc


####################################################################################################
def GetThumb(url):

	try:
		data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))
