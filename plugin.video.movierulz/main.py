# -*- coding: UTF-8 -*-
from __future__ import division
import sys,re,os
import six
from six.moves import urllib_parse
from resolveurl.lib import helpers

#import json

import requests
from requests.compat import urlparse

import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc, xbmcvfs
from resources.lib.brotlipython import brotlidec

if six.PY3:
    basestring = str
    unicode = str
    xrange = range
    from resources.lib.cmf3 import parseDOM
else:
    from resources.lib.cmf2 import parseDOM
import resolveurl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(urllib_parse.parse_qsl(sys.argv[2][1:])) 
addon = xbmcaddon.Addon(id='plugin.video.movierulz')

PATH            = addon.getAddonInfo('path')
if six.PY2:
    DATAPATH        = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
else:
    DATAPATH        = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
RESOURCES       = PATH+'/resources/'
FANART=RESOURCES+'../fanart.jpg'
ikona =RESOURCES+'../icon.png'

exlink = params.get('url', None)
nazwa= params.get('title', None)
rys = params.get('image', None)

page = params.get('page',[1])

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
TIMEOUT=15

headers = {'User-Agent': UA,}
sess = requests.Session()

def build_url(query):
    return base_url + '?' + urllib_parse.urlencode(query)

def GetSearchQuery():
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('Search ')
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_text = keyboard.getText()

    return search_text
    
def add_item(url, name, image, mode, itemcount=1, page=1,fanart=FANART, infoLabels=False,contextmenu=None,IsPlayable=False, folder=False):
    list_item = xbmcgui.ListItem(label=name)
    if IsPlayable:
        list_item.setProperty("IsPlayable", 'True')    
    if not infoLabels:
        infoLabels={'title': name}    
    list_item.setInfo(type="video", infoLabels=infoLabels)    
    list_item.setArt({'thumb': image, 'poster': image, 'banner': image, 'fanart': fanart})
    
    if contextmenu:
        out=contextmenu
        list_item.addContextMenuItems(out, replaceItems=True)

    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url = build_url({'mode': mode, 'url' : url, 'page' : page, 'title':name,'image':image}),            
        listitem=list_item,
        isFolder=folder)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %Y, %P")

def home():

    add_item('https://movierulzhd.rocks/genre/hindi/', '[B]- Hindi[/B]', ikona, "listmovies",fanart=FANART, folder=True)
    add_item('https://movierulzhd.rocks/genre/telugu/', '[B]- Telugu[/B]', ikona, "listmovies",fanart=FANART, folder=True)
    add_item('https://movierulzhd.rocks/genre/tamil/', '[B]- Tamil[/B]', ikona, "listmovies",fanart=FANART, folder=True)
	
    add_item('https://movierulzhd.rocks/genre/hindi-web-series-download/', '[B]- Hindi shows[/B]', ikona, "listmovies",fanart=FANART, folder=True)
    add_item('https://movierulzhd.rocks/genre/telugu-web-series/', '[B]- Telugu shows[/B]', ikona, "listmovies",fanart=FANART, folder=True)
    add_item('https://movierulzhd.rocks/genre/tamil-web-series/', '[B]- Tamil shows[/B]', ikona, "listmovies",fanart=FANART, folder=True)
    
    add_item('https://movierulzhd.rocks/page/1?s=','[COLOR khaki][B]**Search**[/COLOR][/B]', ikona, "listmovies",fanart=FANART, folder=True)
	

def ListMovies(url, pg):

	if url[-2:] == 's=':
		search_text = GetSearchQuery()
		search_text = urllib_parse.quote_plus(search_text)
		url += search_text
        
	if '/page/' in url:
		url = re.sub('/page/\\d+','/page/%d'%int(pg),url)
	else:
		url = url + '/page/%d' %int(pg)
	html = sess.get(url, headers = headers, verify=False).text

	ntpage = re.findall(r'<a\s+class=\'arrow_pag\'\s+href="([^"]*)"',html,re.DOTALL)

	links = parseDOM(html,'article', attrs={'id':"post\-.*?"} )
	for link in links:
	
		href = parseDOM(link,'a', ret="href")[0]
		href = 'https://movierulzhd.rocks/tvshows/'+href if href.startswith('/') else href
	

		img = parseDOM(link,'img', ret="src")#[0]
		try:
			img = ikona if img[0] == '' else img[0]
		except:
			img = ikona

		title = parseDOM(parseDOM(link,'h3')[0],'a')[0]

		title = title.replace('&#8217;',"'").replace('&#8211;','-')
		ispla = False
		fold = True
		mod = 'listlinks'
		h2 = href+'|'+title
		if '/tvshows/' in href:
			ispla = False
			fold = True
			mod = 'listserial'
			h2 = href
            
		add_item(h2, title, img, mod,fanart=FANART, folder=fold, IsPlayable=ispla, infoLabels={'plot':title})
	
	links = parseDOM(html,'div', attrs={'class':"result\-.*?"} )
	for link in links:
	
		href = parseDOM(link,'a', ret="href")[0]
		href = 'https://movierulzhd.rocks/tvshows/'+href if href.startswith('/') else href
	

		img = parseDOM(link,'img', ret="src")#[0]
		try:
			img = ikona if img[0] == '' else img[0]
		except:
			img = ikona

		title = parseDOM(parseDOM(link,'div', attrs={'class':"title.*?"})[0],'a')[0]

		title = title.replace('&#8217;',"'").replace('&#8211;','-')
		ispla = False
		fold = True
		mod = 'listlinks'
		h2 = href+'|'+title
		
		add_item(h2, title, img, mod,fanart=FANART, folder=fold, IsPlayable=ispla, infoLabels={'plot':title})
	
	

	if ntpage:
		nextpage = unicode(int(pg)+1)
		add_item(ntpage[0], '>> next page >>' ,RESOURCES+'right.png', "listmovies",fanart=FANART, page=nextpage, folder=True)
	xbmcplugin.endOfDirectory(addon_handle) 

def ListSerial(url):
    
	html = sess.get(url, headers = headers, verify=False).text

	orig_title = re.findall(r'<img[^>]*\s+alt\s*=\s*["\']([^"\']+)["\']',parseDOM(html,'div', attrs={'class':"poster"} )[0],re.DOTALL)[0]
	
	img_main = re.findall(r'<img[^>]*\s+src\s*=\s*["\']([^"\']+)["\']',parseDOM(html,'div', attrs={'class':"poster"} )[0],re.DOTALL)[0]
	plot = parseDOM(parseDOM(html,'div', attrs={'class':"wp-content"} )[0], 'p', attrs={})[-1]
	plot = plot[0] if plot else ''
	
	result = parseDOM(html,'div', attrs={'id':"serie_contenido.*?"})[0].replace('&quot;','"')
	out=[]
	seasons = parseDOM(result,'div', attrs={'class':"se-c"} )
	for season in seasons:
		ses = re.findall(r"<span class='se-t(?:\s+se-o)?'>(.*?)</span>",season,re.DOTALL)[0]
		episodes = parseDOM(season,'li')
		
		for episode in episodes:
			epis = re.findall(r"<div class='numerando'>(.*?)</div>",episode,re.DOTALL+re.I)[0]

			imag = re.findall(r"<img\s+src=['\"]([^'\"]+)['\"]",episode,re.DOTALL+re.I)[0]
			imag = 'https:'+imag if imag.startswith('//') else imag
			info = parseDOM(episode,'div', attrs={'class':"episodiotitle"} )
			href = parseDOM(info,'a', ret="href")[0]
			epistitle =  parseDOM(info,'a')[0]
			jaki = ' - S{}E{} '.format(int(ses),str(epis))+' - [COLOR gold][B]'+epistitle+'[/B][/COLOR]'
				
			tyt = orig_title+jaki
			out.append({'title':tyt,'href':href,'img':imag, 'fnrt':FANART, 'plot':plot, 'season' : int(ses),'episode' : str(epis) })
	sezony =  splitToSeasons(out)

	for i in sorted(sezony.keys()):
		ac=urllib_parse.quote_plus(str(sezony[i]))
		add_item(ac, i, img_main, 'listepisodes',fanart=FANART, folder=True, IsPlayable=False, infoLabels={'plot':plot})
	xbmcplugin.endOfDirectory(addon_handle) 
		
		
def ListEpisodes(exlink):
	import ast

	episodes = ast.literal_eval(urllib_parse.unquote_plus(exlink))
	
	itemz=episodes
	items = len(episodes)
	
	for f in itemz:
		add_item(f.get('href')+'|'+f.get('title'), f.get('title'), f.get('img'), 'listlinks',fanart=FANART, folder=True, IsPlayable=False, infoLabels={'plot':f.get('plot')})
	xbmcplugin.endOfDirectory(addon_handle) 
def splitToSeasons(input):
	out={}
	seasons = [x.get('season') for x in input]

	xx= re.findall('^(.*?)\-',input[0].get('title', None))[0]
	for s in set(seasons):

		out[xx+ ' Season %02d'%s]=[input[i] for i, j in enumerate(seasons) if j == s]
	return out
	
def ListLinks(urlk):

	url,tyt = urlk.split('|')	
	html = sess.get(url, headers = headers, verify=False).text
	html = html.replace('&quot;','"').replace('&amp;','&')
	inf = parseDOM(html,'p', attrs={'class':"Info"} )
	duration = 0 
	year = 0

	if inf:
		dur = re.findall('access_time">([^<]+)<',inf[0],re.DOTALL)
		year = re.findall('date_range">([^<]+)<',inf[0],re.DOTALL)
		if dur:

			try:
				duration = dur[0].replace('h ','*60+').replace('m','')
				duration = int(eval(duration))*60
			except:
				duration = 0
		if year:
			year = year[0]
		else:
			year = 0 

	plot = re.findall('description"\s*\:\s*"([^"]+)"',html,re.DOTALL)
	plot = plot[0] if plot else tyt

	imag = re.findall('thumbnailUrl"\s*\:\s*"([^"]+)"',html,re.DOTALL+re.I)
	imag = imag[0] if imag else ikona
	imag = 'https:'+imag if imag.startswith('//') else imag

	ids = [(a.start(), a.end()) for a in re.finditer('<li\sid=["\']player-option[^"\']*', html)]

	ids.append( (-1,-1) )

	hosty =[]
	for i in range(len(ids[:-1])):
		subset = html[ ids[i][1]:ids[i+1][0] ]
		opt = re.findall(r"data-post=['\"](\d+)['\"]",subset,re.DOTALL)
		opt2 = re.findall(r"data-nume=['\"](\d+)['\"]",subset,re.DOTALL)
		host = re.findall(r"<span\s+class=['\"]title['\"]>(.*?)</span>",subset,re.DOTALL)
		if opt and opt2 and host:
			hosty.append({"host": host[0], "opt": (opt[0],opt2[0])})
	ok = False
	for x in hosty:
		ok = True
		ht = x.get('opt')
		src = ht
		tit = tyt+ ' [I][COLOR khaki]'+x.get('host')+'[/I][/COLOR]'
		mod = 'playvideo' 
		ispla = True
		fold = False

			
		add_item(src, tit, imag, mod,fanart=FANART, folder=fold, IsPlayable=ispla, infoLabels={'plot':plot, 'year':year, 'duration':duration})
	if ok:
		xbmcplugin.endOfDirectory(addon_handle) 
	else:
		xbmcgui.Dialog().notification('[B]Info[/B]', 'Links are not available',xbmcgui.NOTIFICATION_INFO, 6000)
        

def PlayVideo(url):	
	make_url = (url.replace('(','').replace(')','')).split(',')

	url=Resolve_Main(make_url[0],make_url[1])

	html = sess.get(url, headers = headers, verify=False).text
	sub = None
    
	link = helpers.get_media_url(
            url,
            patterns=[r'''sources:\s*\[{\s*file:\s*["'](?P<url>[^"']+)'''],
            generic_patterns=False
        )

	if link:	
		play_item = xbmcgui.ListItem(path=link)#
		play_item.setProperty('inputstream', 'inputstream.ffmpegdirect')
		#play_item.setProperty('inputstream.ffmpegdirect.mime_type', 'video/mp4')
		if sub is not None:
			# Set the subtitle URL
			play_item.setSubtitles([subtitle["file"].replace(' ', '%20') for subtitle in sub])

		play_item.setContentLookup(False)
        
		try:
			succeeded = xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
			xbmc.log("#### {}".format(succeeded))
		except Exception as e:
			xbmc.executebuiltin('Notification(404 Error, File not found, 5000)')
	else:
		xbmc.executebuiltin('Cant Resolve')
        
def Resolve_Main(post,nume)	:
	
	headers.update({'Referer': 'https://movierulzhd.rocks','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'})
	#print('action=doo_player_ajax&post={}&nume={}&type=movie'.format(post,nume))
	response = sess.post('https://movierulzhd.rocks/wp-admin/admin-ajax.php', headers = headers, data='action=doo_player_ajax&post={}&nume={}&type=movie'.format(int(post.strip().strip("'")),int(nume.strip().strip("'"))))
	html = response.json()
	link = html.get('embed_url',None)
	return link


def router(paramstring):
	params = dict(urllib_parse.parse_qsl(paramstring))
	if params:    
	
		mode = params.get('mode', None)
	
		if mode == 'listmovies':
			ListMovies(exlink, page)	
		elif mode == 'playvideo':
			PlayVideo(exlink)
		elif mode == 'listserial':
			ListSerial(exlink)
		elif mode == 'listlinks':
			ListLinks(exlink)
			
			
		elif mode == 'listepisodes':
			ListEpisodes(exlink)


	else:
		home()
		xbmcplugin.endOfDirectory(addon_handle)    
if __name__ == '__main__':
    router(sys.argv[2][1:])