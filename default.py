#!/usr/bin/python
# -*- coding: utf-8 -*-

#  script.video.cleaner
#  Written by black_eagle and BatterPudding
#
# Version 27b/7 - Batter Pudding Fix added
# Version 27b/9 - Batter Pudding tweaks the debug logging
# Version 28b/1 - New GUI, several code fixes
# Version 28b/2 - Fix the WINDOWS KODI temp path
# Version 28b/3 - Tidy up temp path code, remove some unused code
# Version 29b/1 - Add ability to rename paths inside the db
# Version 29/b2 - Fix incorrectly altered SQL


import datetime

import json as jsoninterface

import sqlite3

import xml.etree.ElementTree as ET

import mysql.connector

import platform

import os

import xbmc

import xbmcaddon

import xbmcgui

import xbmcvfs

ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_NAV_BACK = 92
ACTION_MOUSE_LEFT_CLICK = 100
flag = 0
WINDOW = xbmcgui.Window(10000)

class MyClass(xbmcgui.WindowXMLDialog):
	def __init__( self, *args, **kwargs  ): pass
	
	def onInit( self ):
		self.setCoordinateResolution(0)
		self.scaleX = self.getWidth()
		self.centre = int(self.scaleX / 2)
		self.base_offset_x = -80
		self.base_offset_y = -100		
		log('Centre is %d ' %self.centre)
		self.strActionInfo = xbmcgui.ControlLabel( 868, 10, 400, 200, '', 'font13', '0xFFFF00FF')
		self.addControl(self.strActionInfo)

		self.offset = 28
	#		List paths from sources.xml 
		if not specificpath and not replacepath:
			self.base_offset_x = 200
			self.base_offset_y = 120
			self.display_list = display_list
			self.strActionInfo = xbmcgui.ControlLabel(self.base_offset_x,self.base_offset_y, 700, 200, '', 'font18', '0xFFFF00FF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Keeping data scanned from the following paths')
			self.mylist = xbmcgui.ControlList(self.base_offset_x,self.base_offset_y+30, 600, 400)
			self.addControl(self.mylist)
			self.mylist.addItem('')
			for i in range(len(self.display_list)):
				self.mylist.addItem('[COLOR yellow]'+self.display_list[i]+'[/COLOR]')
			self.setFocus(self.mylist)
	#		List paths in excludes.xml (if it exists)
		
			self.strActionInfo = xbmcgui.ControlLabel(self.base_offset_x+860,self.base_offset_y,400,200,'', 'font18', '0xFFFF00FF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Contents of excludes.xml')
			self.excludes_list = excludes_list
			self.my_excludes = xbmcgui.ControlList(self.base_offset_x+860,self.base_offset_y+30,500,400)
			self.addControl(self.my_excludes)
			self.my_excludes.addItem('')
			if excluding:
				for i in range(len(self.excludes_list)):
					self.my_excludes.addItem('[COLOR yellow]' + self.excludes_list[i]+ '[/COLOR]')
			else:
				self.my_excludes.addItem("Not Present")
			self.setFocus(self.my_excludes)	
	#		List the relevant addon settings
		self.strActionInfo = xbmcgui.ControlLabel(self.base_offset_x+860,self.base_offset_y+255,400,200,'', 'font18', '0xFFFF00FF')
		self.addControl(self.strActionInfo)
		self.strActionInfo.setLabel('Addon Settings')
		if is_pvr and (not specificpath and not replacepath):
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Keep PVR information')
			self.offset += 28
		if bookmarks and (not specificpath and not replacepath):
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Keep bookmark information')
			self.offset += 28
		if autoclean:
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Auto call Clean Library')
			self.offset += 28
		if promptdelete:
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,700,100,'','font13','0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Show summary window (This window !!)')
			self.offset += 28
		if autobackup == 'true' and not is_mysql:
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Auto backing up local database')
			self.offset += 28
		if no_sources or specificpath or replacepath:
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFF0000')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Not using info from sources.xml')
			self.offset += 28
		if specificpath:
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFF0000')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('[COLOR red]Cleaning a specific path[/COLOR]')
			self.offset += 28
		if replacepath:
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFF0000')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('[COLOR red]Replacing a path[/COLOR]')
			self.offset += 28
		if enable_logging:
			self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260,550,100,'','font13','0xFFFF0000')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('Writing a logfile to Kodi TEMP directory')
			self.offset += 28

		if debugging:
			debug_string = 'Debugging enabled'
		else:
			debug_string = 'Debugging disabled'
		self.strActionInfo = xbmcgui.ControlLabel (self.base_offset_x+900,self.base_offset_y + self.offset+260 ,550 ,100,'','font13','0xFFFFFFFF')
		self.addControl(self.strActionInfo)
		self.strActionInfo.setLabel(debug_string)
		self.offset += 45
		#	Display the name of the database we are connected to
		self.strActionInfo = xbmcgui.ControlLabel ( self.base_offset_x+860, self.base_offset_y + self.offset+260, 550, 100, '', 'font13', '0xFFFF00FF')
		self.addControl(self.strActionInfo)
		self.strActionInfo.setLabel('Database is - [COLOR green][B]%s[/B][/COLOR]' % our_dbname)
		#	Show warning about backup if using MySQL	
		if is_mysql:
			self.strActionInfo = xbmcgui.ControlLabel (200, 800, 150, 30, '', 'font18', '0xFFFF0000')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('WARNING')
			self.strActionInfo = xbmcgui.ControlLabel (352, 800, 800, 30, '', 'font13', '0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('- MySQL database [COLOR red][B]not[/B][/COLOR] backed up automatically, please do this [B]manually[/B]')
		if specificpath:
			self.strActionInfo = xbmcgui.ControlLabel (200, 830, 150, 30, '', 'font18', '0xFFFF0000')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('WARNING')
			self.strActionInfo = xbmcgui.ControlLabel(352, 830, 800, 30, '', 'font13', '0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('- Removing specific path [COLOR yellow]%s[/COLOR] ' % specific_path_to_remove)
		if replacepath:
			self.strActionInfo = xbmcgui.ControlLabel (200, 830, 150, 30, '', 'font18', '0xFFFF0000')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('WARNING')
			self.strActionInfo = xbmcgui.ControlLabel(352, 830, 800, 30, '', 'font13', '0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('- Renaming specific path from [COLOR yellow]%s[/COLOR] ' % old_path)
			self.strActionInfo = xbmcgui.ControlLabel(352, 860, 800, 30, '', 'font13', '0xFFFFFFFF')
			self.addControl(self.strActionInfo)
			self.strActionInfo.setLabel('- to  [COLOR yellow]%s[/COLOR] ' % new_path)
		#	Create the buttons
		self.button0 = xbmcgui.ControlButton(500, 950, 180, 30, "[COLOR red]ABORT[/COLOR]", alignment=2)
		self.addControl(self.button0)
		self.button1 = xbmcgui.ControlButton(1300, 950, 180, 30, "[COLOR green]DO IT ![/COLOR]", alignment=2)
		self.addControl(self.button1)
		self.setFocus(self.button0)
		button_abort = self.button0.getId()
		dbglog('Button abort has id %d' % button_abort)
		button_clean = self.button1.getId()
		dbglog('button clean has id %d' % button_clean)
		#	Make up/down/left/right switch between buttons
		self.button0.controlRight(self.button1)
		self.button1.controlLeft(self.button0)
		self.button0.controlDown(self.button1)
		self.button1.controlUp(self.button0)
	
 
	def onAction(self, action):
		global flag
		dbglog('Got an action %s' % action.getId())
		if ( action == ACTION_PREVIOUS_MENU ) or ( action == ACTION_NAV_BACK ):
			self.close()
		if (action == ACTION_SELECT_ITEM) or ( action == ACTION_MOUSE_LEFT_CLICK ):
			try:
				btn = self.getFocus()
			except:
				btn = None
			if btn == self.button0:
				dbglog('you pressed abort')
				flag = 0
				self.close()
			elif btn == self.button1:
				dbglog('you pressed clean')
				flag = 1
				self.close()

#  Set some variables ###

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonversion = addon.getAddonInfo('version')
addonpath = addon.getAddonInfo('path').decode('utf-8')

advanced_file = xbmc.translatePath('special://profile/advancedsettings.xml').decode('utf-8')
sources_file = xbmc.translatePath('special://profile/sources.xml').decode('utf-8')
excludes_file = xbmc.translatePath('special://profile/addon_data/script.database.cleaner/excludes.xml').decode('utf-8')
db_path = xbmc.translatePath('special://database').decode('utf-8')
userdata_path = xbmc.translatePath('special://userdata').decode('utf-8')

type_of_log =''
is_pvr = addon.getSetting('pvr')
autoclean = addon.getSetting('autoclean')
bookmarks = addon.getSetting('bookmark')
promptdelete = addon.getSetting('promptdelete')
source_file_path = addon.getSetting('sourcefilepath')
debugging = addon.getSetting('debugging')
no_sources = addon.getSetting('usesources')
autobackup = addon.getSetting('autobackup')
specificpath = addon.getSetting('specificpath')
backup_filename = addon.getSetting('backupname')
forcedbname = addon.getSetting('overridedb')
replacepath = addon.getSetting('replacepath')
enable_logging = addon.getSetting('logtolog')
if enable_logging == 'true':
	enable_logging = True
	type_of_log = addon.getSetting('typeoflog')
	
else:
	enable_logging = False
if replacepath == 'true':
	replacepath = True
else:
	replacepath = False
old_path = addon.getSetting('oldpath')
new_path = addon.getSetting('newpath')
if forcedbname == 'true':
	forcedbname = True
else:
	forcedbname = False
forcedname = addon.getSetting('forceddbname')
if specificpath == 'true':
	specificpath = True
else:
	specificpath = False
specific_path_to_remove = addon.getSetting('spcpathstr')
display_list = []
excludes_list = []
renamepath_list = []
excluding = False
found = False
is_mysql = False
remote_file = False
cleaning = False
path_name = ''
the_path = ''
success = 0
our_source_list = ''
if debugging == 'true':
	debugging = True
else:
	debugging = False


def log(txt):
	if isinstance(txt, str):
		txt = txt.decode('utf-8')
	message = u'%s: %s' % (addonname, txt)
	xbmc.log(msg=message.encode('utf-8'), level=xbmc.LOGDEBUG)  
	
def dbglog(txt):
	if debugging:
		log(txt)
		
		
def cleaner_log_file(our_select, cleaning):
	cleaner_log = xbmc.translatePath('special://temp/database-cleaner.log').decode('utf-8')
	old_cleaner_log = xbmc.translatePath('special://temp/database-cleaner.old.log').decode('utf-8')
	old_log_contents =''	
	if not enable_logging:
		return
	if type_of_log == '0':
		dbglog('Writing to new log file')
		if cleaning:
			if xbmcvfs.exists(cleaner_log):
				dbglog('database-cleaner.log exists - renaming to old.log')
				xbmcvfs.delete(old_cleaner_log)
				xbmcvfs.copy(cleaner_log, old_cleaner_log)
				xbmcvfs.delete(cleaner_log)
		else:
			xbmcvfs.delete(cleaner_log)
	else:
		dbglog('Appending to existing log file')
		if cleaning:
			if xbmcvfs.exists(cleaner_log):
				dbglog('database-cleaner.log exists - backing up to old.log')
				xbmcvfs.delete(old_cleaner_log)
				xbmcvfs.copy(cleaner_log, old_cleaner_log)
		old_log= xbmcvfs.File(cleaner_log)
		old_log_contents=old_log.read()
		old_log.close()
	
	now = datetime.datetime.now()
	logfile=xbmcvfs.File(cleaner_log, 'w')
	if old_log_contents:
		logfile.write(old_log_contents)
	more_info = platform.dist()
	more_info = str(more_info).replace("'","",20)
	more_info = the_platform.replace(",","",1)
	running_platform = platform.system()
	logfile_header = 'Video Database Cleaner - Running on '+ str(running_platform) +' ' +  str(more_info) + ' at ' + now.strftime('%c') + '\n\n'
	logfile.write(logfile_header)

	cursor.execute(our_select)
	if not cleaning and not replacepath:
		logfile.write('The following file paths would be removed from your database')
		logfile.write('\n\n')
	elif cleaning and not replacepath:
		logfile.write('The following paths were removed from the database')
		logfile.write('\n\n')
	elif not cleaning and replacepath:
		logfile.write('The following paths will be changed in your database')
		logfile.write('\n\n')
	else:
		logfile.write('The following paths were changed in your database')
		logfile.write('\n\n')
	if not specificpath and not replacepath:
		for strPath in cursor:
			mystring = u''.join(strPath) + '\n'
			outdata = mystring.encode('utf-8')
			dbglog('Removing unused path %s' % strPath)
			logfile.write(outdata)
	elif specificpath and not replacepath:
		dbglog('Removing specific path %s' % specific_path_to_remove)
		for strPath in cursor:
			mystring = u''.join(strPath) + '\n'
			outdata = mystring.encode('utf-8')
			dbglog('Removing unwanted path %s' % strPath)
			logfile.write(outdata)
	else:
		for strPath in cursor:
			mystring = u''.join(strPath) + '\n'
			outdata = mystring.encode('utf-8')
			dbglog('Changing path %s' % strPath)
			logfile.write(outdata)
		our_data = cursor
	logfile.write('\n\n')
	logfile.close()
	
		
		
dbglog('script version %s started' % addonversion)

our_dbname = 'MyVideos'

for num in range(114, 35, -1):
	testname = our_dbname + str(num)
	our_test = db_path + testname + '.db'

	dbglog('Checking for database %s' % testname)
	if xbmcvfs.exists(our_test):
		break
if num != 35:
	our_dbname = testname

if our_dbname == 'MyVideos':
	dbglog('No video database found - assuming MySQL database')
log('database name is %s' % our_dbname)
dbglog('Database name is %s' % our_dbname)

if is_pvr == 'true':
	is_pvr = True
else:
	is_pvr = False

if autoclean == 'true':
	autoclean = True
else:
	autoclean = False
if bookmarks == 'true':
	bookmarks = True
else:
	bookmarks = False
if promptdelete == 'true':
	promptdelete = True
else:
	promptdelete = False
if no_sources == 'true':
	no_sources = False
else:
	no_sources = True

dbglog('Settings for file cleaning are as follows')
if is_pvr:
	dbglog('keeping PVR files')
if bookmarks:
	dbglog('Keeping bookmarks')
if autoclean:
	dbglog('autocleaning afterwards')
if promptdelete:
	dbglog('Prompting before deletion')
if no_sources:
	dbglog('Not using sources.xml')

if xbmcvfs.exists(advanced_file):
	found = True
if addon:
	if found:
		msg = advanced_file.encode('utf-8')
		advancedsettings = ET.parse(advanced_file)
		root = advancedsettings.getroot()
		try:
			for videodb in root.findall('videodatabase'):
				try:
					our_host = videodb.find('host').text
				except:
					log('Unable to find MySQL host address')
				try:
					our_username = videodb.find('user').text
				except:
					log('Unable to determine MySQL username')
				try:
					our_password = videodb.find('pass').text
				except:
					log('Unable to determine MySQL password')
				try:
					our_dbname = videodb.find('name').text
				except:
					pass
				dbglog('MySQL details - %s, %s, %s' % (our_host, our_username, our_dbname))
				is_mysql = True
		except:
			is_mysql = False

	
	if source_file_path != '':
		sources_file = source_file_path
		remote_file = True
		dbglog('Remote sources.xml file path identified')
	if xbmcvfs.exists(sources_file) and not remote_file:
		try:
			source_file = sources_file
			tree = ET.parse(source_file)
			root = tree.getroot()
			dbglog('Got local sources.xml file')
		except:
			log('Error parsing local sources.xml file')
			xbmcgui.Dialog().ok(addonname, 'Error parsing local sources.xml file - script aborted')
			exit(1)
	elif xbmcvfs.exists(sources_file):
		try:
			f = xbmcvfs.File(sources_file)
			source_file = f.read()
			f.close()
			root = ET.fromstring(source_file)
			dbglog('Got remote sources.xml')
		except:
			log('Error parsing remote sources.xml')
			xbmcgui.Dialog().ok(addonname, 'Error parsing remote sources.xml file - script aborted')
			exit(1)
	else:
		xbmcgui.Dialog().ok(addonname,
							'Error - No sources.xml file found.  Please set the path to the remote sources.xml in the addon settings')
		dbglog('No local sources.xml, no path to remote sources file set in settings')
		exit(1)
	my_command = ''
	first_time = True
	if forcedbname:
		log('Forcing video db version to %s' % forcedname)

	# Open database connection

	if is_mysql and not forcedbname:
		if our_dbname == testname: # found an sqlite database, but no db name in advancedsettings
			our_dbname = 'MyVideos'
			for num in range(114, 35, -1):
				testname = our_dbname + str(num)
				try:
					dbglog('Attempting MySQL connection to %s' % testname)
					db = mysql.connector.connect(user=our_username,
							database=testname, password=our_password,
							host=our_host)
					if db.is_connected():
						our_dbname = testname
						dbglog('Connected to MySQL database %s' % our_dbname)
						break
				except:
					pass
		else: 
			for num in range(114, 35, -1):
				testname = our_dbname + str(num)
				try:
					dbglog('Attempting MySQL connection to %s' % testname)
					db = mysql.connector.connect(user=our_username, database=testname, password=our_password, host=our_host)
					if db.is_connected():
						our_dbname = testname
						dbglog('Connected to MySQL database %s' % our_dbname)
						break
				except:
					pass
			if not db.is_connected():
				xbmcgui.Dialog().ok(addonname, "Couldn't connect to MySQL database", s)
				dbglog("Error - couldn't connect to MySQL database	- %s " % s)
				exit(1)
	elif is_mysql and forcedbname:
		try:
			db = mysql.connector.connect(user=our_username, database=forcedname, password=our_password, host=our_host)
			if db.is_connected():
				our_dbname = forcedname
				dbglog('Connected to forced MySQL database %s' % forcedname)
		except:
			dbglog('Error connecting to forced	database - %s' % forcedname)
			exit(1)
	elif not is_mysql and not forcedbname:
		try:
			my_db_connector = db_path + our_dbname + '.db'
			db = sqlite3.connect(my_db_connector)
		except Exception,e:
			s = str(e)
			xbmcgui.Dialog().ok(addonname, 'Error connecting to SQLite database', s)
			dbglog('Error connecting to SQLite database - %s' % s)
			exit(1)
	else:
		testpath = db_path + forcedname + '.db'
		if not xbmcvfs.exists(testpath):
			dbglog('Forced version of database does not exist')
			xbmcgui.Dialog().ok(addonname,'Forced version of database not found. Script will now exit')
			exit(1)
		try:
			my_db_connector = db_path + forcedname + '.db'
			db = sqlite3.connect(my_db_connector)
			dbglog('Connected to forced video database')
		except:
			dbglog('Unable to connect to forced database s%' % forcedname)
			exit(1)

	cursor = db.cursor()
	
	if xbmcvfs.exists(excludes_file):
		excludes_list =[]
		excluding = True
		exclude_command = ''
		try:
			tree = ET.parse(excludes_file)
			er = tree.getroot()
			for excludes in er.findall('exclude'):
				to_exclude = excludes.text
				excludes_list.append(to_exclude)
				dbglog('Excluding plugin path - %s' % to_exclude)
				exclude_command = exclude_command + " AND strPath NOT LIKE '" + to_exclude + "%'"
			log('Parsed excludes.xml')
		except:
			log('Error parsing excludes.xml')
			xbmcgui.Dialog().ok(addonname, 'Error parsing excludes.xml file - script aborted')
			exit(1)
	
	if not no_sources:
		try:
			display_list =[]
			for video in root.findall('video'):
				dbglog('Contents of sources.xml file')
	
				for sources in video.findall('source'):
					for path_name in sources.findall('name'):
						the_path_name = path_name.text
						for paths in sources.findall('path'):
							the_path = paths.text
							display_list.append(the_path)
							dbglog('%s - %s' % (the_path_name, the_path))
							if first_time:
								first_time = False
								my_command = "strPath NOT LIKE '" + the_path + "%'"
								our_source_list = 'Keeping files in ' + the_path
							else:
								my_command = my_command + " AND strPath NOT LIKE '" + the_path + "%'"
								our_source_list = our_source_list + ', ' + the_path
				if path_name == '':
					no_sources = True
					dbglog('******* WARNING *******')
					dbglog('local sources.xml specified in settings')
					dbglog('But no sources found in sources.xml file')
					dbglog('Defaulting to alternate method for cleaning')
		except:
			log('Error parsing sources.xml file')
			xbmcgui.Dialog().ok(addonname, 'Error parsing sources.xml file - script aborted')
			exit(1)

		if is_pvr:
			my_command = my_command + " AND strPath NOT LIKE 'pvr://%'"
			our_source_list = our_source_list + 'Keeping PVR info '
		if excluding:
			my_command = my_command + exclude_command
			our_source_list = our_source_list + 'Keeping items from excludes.xml '
		if bookmarks:
			my_command = my_command + ' AND idFile NOT IN (SELECT idFile FROM bookmark)'
			our_source_list = our_source_list + 'Keeping bookmarked files '
		sql = \
			"""DELETE FROM files WHERE idPath IN(SELECT idPath FROM path where (""" + my_command + """));"""
	if no_sources:
		my_command = ''
		our_source_list = 'NO SOURCES FOUND - REMOVING rtmp(e), plugin and http info '
		dbglog('Not using sources.xml')
		if is_pvr:
			my_command = my_command + " AND strPath NOT LIKE 'pvr://%'"
			our_source_list = our_source_list + 'Keeping PVR info '
		if bookmarks:
			my_command = my_command + ' AND idFile NOT IN (SELECT idFile FROM bookmark)'
			our_source_list = our_source_list + 'Keeping bookmarked files '
		if excluding:
			my_command = my_command + exclude_command
			our_source_list = our_source_list + 'Keeping items from excludes.xml '
				
# Build SQL query	
		if my_command:
			sql = """DELETE FROM files WHERE idPath IN ( SELECT idPath FROM path WHERE ((strPath LIKE 'rtmp://%' OR strPath Like 'rtmpe:%' OR strPath LIKE 'plugin:%' OR strPath LIKE 'http://%' OR strPath LIKE 'pvr://%') AND (""" + my_command + """)));"""
		else:
			sql = """DELETE FROM files WHERE idPath IN (SELECT idPath FROM path WHERE ((strPath LIKE 'rtmp://%' OR strPath LIKE 'rtmpe:%' OR strPath LIKE 'plugin:%' OR strPath LIKE 'http://%')));"""
			
	dbglog('SQL command is %s' % sql)
	if not specificpath and not replacepath:
		dbglog (our_source_list)			
		our_select = sql.replace('DELETE FROM files','SELECT strPath FROM path',1)
		if bookmarks:  
			our_select = sql.replace('DELETE FROM files', 'SELECT strPath FROM path WHERE idPath in (SELECT idPath FROM files', 1)
			our_select = our_select.replace('bookmark)', 'bookmark))',1)
			sql = sql.replace('DELETE FROM files','DELETE FROM path',1)
		dbglog('Select Command is %s' % our_select)
	elif not replacepath and specificpath:		# cleaning a specific path
		if specific_path_to_remove != '':
			sql = """delete from path where idPath in(select * from (SELECT idPath FROM path WHERE (strPath LIKE '""" + specific_path_to_remove +"""%')) as temptable)"""
			our_select = "SELECT strPath FROM path WHERE idPath IN (SELECT idPath FROM path WHERE (strPath LIKE'" + specific_path_to_remove + "%'))"
			dbglog('Select Command is %s' % our_select)
		else:
			dbglog("Error - Specific path selected with no path defined")
			exit(1)
	else: # must be replacing a path at this point
		if old_path != '' and new_path != '':
			our_select = "SELECT strPath from path WHERE strPath Like '" + old_path + "%'"
		else:
			dbglog('Error - Missing path for replacement')
			exit(1)
	cleaner_log_file(our_select, False)
		
	if promptdelete:
		mydisplay = MyClass('cleaner-window.xml', addonpath)
		mydisplay.doModal()
		del mydisplay
		if flag == 1:
			i = True
		else:
			i = False

	else:
		i = True
	if i:
		if autobackup == 'true' and not is_mysql:
			backup_path = xbmc.translatePath('special://database/backups/'
				).decode('utf-8')

			if not xbmcvfs.exists(backup_path):
				dbglog('Creating backup path %s' % backup_path)
				xbmcvfs.mkdir(backup_path)
			now = datetime.datetime.now()
			if forcedbname:
				our_dbname = forcedname
			current_db = db_path + our_dbname + '.db'
			if backup_filename == '':
				backup_filename = our_dbname
			backup_db = backup_path + backup_filename + '_' \
				+ now.strftime('%Y-%m-%d_%H%M') + '.db'
			backup_filename = backup_filename + '_' \
				+ now.strftime('%Y-%m-%d_%H%M')
			success = xbmcvfs.copy(current_db, backup_db)
			if success == 1:
				success = 'successful'
			else:
				success = 'failed'
			dbglog('auto backup database %s.db to %s.db - result was %s'
				% (our_dbname, backup_filename, success))
		cleaner_log_file(our_select, True)
		if not replacepath:
			try:
	
			# Execute the SQL command
				dbglog('Executing SQL command - %s' % sql)
				cursor.execute(sql)
				cursor.execute('DELETE FROM files WHERE strFilename ="";')
	
			# Commit your changes in the database
	
				db.commit()
			except Exception as e:
	
			# Rollback in case there is any error
	
				db.rollback()
				dbglog('Error in db commit. Transaction rolled back')
				dbglog('******************************************************************************')
				dbglog('**  SQL ERROR  **  SQL ERROR   **  SQL ERROR  **  SQL ERROR  **  SQL ERROR  **')
				dbglog('**   %s ' % e)
				dbglog('******************************************************************************')
				
		else:
			dbglog('Changing Paths - generating SQL statements')
			our_select = "SELECT strPath from path WHERE strPath Like '" + old_path + "%'"
			xbmc.executebuiltin( "ActivateWindow(busydialog)" )
			cursor.execute(our_select)
			tempcount=0
			renamepath_list = [] 
			for strPath in cursor:	# build a list of paths to change
				renamepath_list.append( ''.join(strPath))
				tempcount += 1
				
			for i in range(len(renamepath_list)):
				our_old_path = renamepath_list[i]
				our_new_path = our_old_path.replace(old_path, new_path,1)
				sql = 'UPDATE path SET strPath ="' + our_new_path + '" WHERE strPath LIKE "' +our_old_path + '"'
				dbglog('SQL - %s' % sql)
				try:
					cursor.execute(sql)
					db.commit()
				except Exception as e:
					db.rollback()
					dbglog('Error in db commit %s. Transaction rolled back' % e)
	
		# disconnect from server
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		db.close()
		
		# Make sure replacing or changing a path is a one-shot deal
		
		if replacepath or specificpath:
			addon.setSetting('specificpath', 'false')
			addon.setSetting('replacepath', 'false')


		if autoclean:
			xbmcgui.Dialog().notification(addonname,
								'Running cleanup', xbmcgui.NOTIFICATION_INFO,
								2000)
			xbmc.sleep(2000)

			json_query = \
				xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "VideoLibrary.Clean","id": 1 }'
									)
			json_query = unicode(json_query, 'utf-8', errors='ignore')
			json_query = jsoninterface.loads(json_query)
			if json_query.has_key('result'):
				dbglog('Clean library sucessfully called')
		else:
			xbmcgui.Dialog().ok(addonname,
								'Script finished.  You should run clean library for best results'
								)
		dbglog('Script finished')
	else:
		xbmcgui.Dialog().notification(addonname, 'Script aborted - No changes made', xbmcgui.NOTIFICATION_INFO, 3000)
		dbglog('script aborted by user - no changes made')
		exit(1)
