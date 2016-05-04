#!/usr/bin/python
# -*- coding: utf-8 -*-

#  script.video.cleaner
#  Written by black_eagle and BatterPudding
#
# Version 27b/7 - Batter Pudding Fix added
#
#

import datetime

import json as jsoninterface

import sqlite3

import xml.etree.ElementTree as ET

import mysql.connector

import xbmc

import xbmcaddon

import xbmcgui

import xbmcvfs

#  Set some variables ###

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonversion = addon.getAddonInfo('version')

advanced_file = xbmc.translatePath('special://profile/advancedsettings.xml').decode('utf-8')
sources_file = xbmc.translatePath('special://profile/sources.xml').decode('utf-8')
excludes_file = xbmc.translatePath('special://profile/addon_data/script.database.cleaner/excludes.xml').decode('utf-8')
db_path = xbmc.translatePath('special://database').decode('utf-8')
userdata_path = xbmc.translatePath('special://userdata').decode('utf-8')

is_pvr = addon.getSetting('pvr')
autoclean = addon.getSetting('autoclean')
bookmarks = addon.getSetting('bookmark')
promptdelete = addon.getSetting('promptdelete')
source_file_path = addon.getSetting('sourcefilepath')
debugging = addon.getSetting('debugging')
no_sources = addon.getSetting('usesources')
autobackup = addon.getSetting('autobackup')

backup_filename = addon.getSetting('backupname')
forcedbname = addon.getSetting('overridedb')
if forcedbname == 'true':
	forcedbname = True
else:
	forcedbname = False
forcedname = addon.getSetting('forceddbname')

excluding = False
found = False
is_mysql = False
remote_file = False
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


if debugging:
	log('script version %s started' % addonversion)

our_dbname = 'MyVideos'

for num in range(114, 35, -1):
	testname = our_dbname + str(num)
	our_test = db_path + testname + '.db'

	if debugging:
		log('Checking for database %s' % testname)
	if xbmcvfs.exists(our_test):
		break
if num != 35:
	our_dbname = testname

if our_dbname == 'MyVideos':
	if debugging:
		log('No video database found - assuming MySQL database')
log('database name is %s' % our_dbname)
if debugging:
	log('Database name is %s' % our_dbname)

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

if debugging:
	log('Settings for file cleaning are as follows')
	if is_pvr:
		log('keeping PVR files')
	if bookmarks:
		log('Keeping bookmarks')
	if autoclean:
		log('autocleaning afterwards')
	if promptdelete:
		log('Prompting before deletion')
	if no_sources:
		log('Not using sources.xml')

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
				if debugging:
					log('MySQL details - %s, %s, %s' % (our_host, our_username, our_dbname))
				is_mysql = True
		except:
			is_mysql = False

	if autobackup == 'true' and not is_mysql:
		backup_path = xbmc.translatePath('special://database/backups/'
				).decode('utf-8')

		if not xbmcvfs.exists(backup_path):
			if debugging:
				log('Creating backup path %s' % backup_path)
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
		if debugging:
			log('auto backup database %s.db to %s.db - result was %s'
				% (our_dbname, backup_filename, success))

	if source_file_path != '':
		sources_file = source_file_path
		remote_file = True
		if debugging:
			log('Remote sources.xml file path identified')
	if xbmcvfs.exists(sources_file) and not remote_file:
		try:
			source_file = sources_file
			tree = ET.parse(source_file)
			root = tree.getroot()
			if debugging:
				log('Got local sources.xml file')
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
			if debugging:
				log('Got remote sources.xml')
		except:
			log('Error parsing remote sources.xml')
			xbmcgui.Dialog().ok(addonname, 'Error parsing remote sources.xml file - script aborted')
			exit(1)
	else:
		xbmcgui.Dialog().ok(addonname,
							'Error - No sources.xml file found.  Please set the path to the remote sources.xml in the addon settings')
		if debugging:
			log('No local sources.xml, no path to remote sources file set in settings')
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
					if debugging:
						log('Attempting MySQL connection to %s' % testname)
					db = mysql.connector.connect(user=our_username,
							database=testname, password=our_password,
							host=our_host)
					if db.is_connected():
						our_dbname = testname
						if debugging:
							log('Connected to MySQL database %s' % our_dbname)
						break
				except:
					pass
		else: 
			for num in range(114, 35, -1):
				testname = our_dbname + str(num)
				try:
					if debugging:
						log('Attempting MySQL connection to %s' % testname)
					db = mysql.connector.connect(user=our_username, database=testname, password=our_password, host=our_host)
					if db.is_connected():
						our_dbname = testname
						if debugging:
							log('Connected to MySQL database %s' % our_dbname)
						break
				except:
					pass
			if not db.is_connected():
				xbmcgui.Dialog().ok(addonname, "Couldn't connect to MySQL database", s)
				if debugging:
					log("Error - couldn't connect to MySQL database	- %s " % s)
				exit(1)
	elif is_mysql and forcedbname:
		try:
			db = mysql.connector.connect(user=our_username, database=forcedname, password=our_password, host=our_host)
			if db.is_connected():
				log('Connected to forced MySQL database %s' % forcedname)
		except:
			log('Error connecting to forced	database - %s' % forcedname)
			exit(1)
	elif not is_mysql and not forcedbname:
		try:
			my_db_connector = db_path + our_dbname + '.db'
			db = sqlite3.connect(my_db_connector)
		except Exception,e:
			s = str(e)
			xbmcgui.Dialog().ok(addonname, 'Error connecting to SQLite database', s)
			if debugging:
				log('Error connecting to SQLite database - %s' % s)
			exit(1)
	else:
		testpath = db_path + forcedname + '.db'
		if not xbmcvfs.exists(testpath):
			log('Forced version of database does not exist')
			xbmcgui.Dialog().ok(addonname,'Forced version of database not found. Script will now exit')
			exit(1)
		try:
			my_db_connector = db_path + forcedname + '.db'
			db = sqlite3.connect(my_db_connector)
			log('Connected to forced video database')
		except:
			log('Unable to connect to forced database s%' % forcedname)
			exit(1)

	cursor = db.cursor()
	
	if xbmcvfs.exists(excludes_file):
		excluding = True
		exclude_command = ''
		try:
			tree = ET.parse(excludes_file)
			er = tree.getroot()
			for excludes in er.findall('exclude'):
				to_exclude = excludes.text
				if debugging:
					log('Excluding plugin path - %s' % to_exclude)
				exclude_command = exclude_command + " AND strPath NOT LIKE '" + to_exclude + "%'"
			log('Parsed excludes.xml')
		except:
			log('Error parsing excludes.xml')
			xbmcgui.Dialog().ok(addonname, 'Error parsing excludes.xml file - script aborted')
			exit(1)
	
	if not no_sources:
		try:
			for video in root.findall('video'):
				if debugging:
					log('Contents of sources.xml file')
	
				for sources in video.findall('source'):
					for path_name in sources.findall('name'):
						the_path_name = path_name.text
						for paths in sources.findall('path'):
							the_path = paths.text
							if debugging:
								log('%s - %s' % (the_path_name, the_path))
							if first_time:
								first_time = False
								my_command = "strPath NOT LIKE '" + the_path + "%'"
								our_source_list = 'Keeping files in ' + the_path
							else:
								my_command = my_command + " AND strPath NOT LIKE '" + the_path + "%'"
								our_source_list = our_source_list + ', ' + the_path
				if path_name == '':
					no_sources = True
					if debugging:
						log('******* WARNING *******')
						log('local sources.xml specified in settings')
						log('But no sources found in sources.xml file')
						log('Defaulting to alternate method for cleaning')
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
		if debugging:
			log('Not using sources.xml')
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
			sql = """DELETE FROM files WHERE idPath IN ( SELECT idPath FROM path WHERE ((strPath LIKE 'rtmp://%' OR strPath LIKE 'rtmpe:%' OR strPath LIKE 'plugin:%' OR strPath LIKE 'http://%') AND (""" + my_command + """)));"""
		else:
			sql = """DELETE FROM files WHERE idPath IN (SELECT idPath FROM path WHERE ((strPath LIKE 'rtmp://%' OR strPath LIKE 'rtmpe:%' OR strPath LIKE 'plugin:%' OR strPath LIKE 'http://%')));"""
			
	if debugging:
		log('SQL command is %s' % sql)
	line1 = 'Please review the following and confirm if correct'
	line2 = our_source_list
	line3 = 'Are you sure ?'
	if promptdelete:
		dialog = xbmcgui.Dialog()
		i = dialog.yesno(addonname, line1, line2, line3)
	else:
		i = True
	if i:
		try:

		# Execute the SQL command

			cursor.execute(sql)

		# Commit your changes in the database

			db.commit()
		except:

		# Rollback in case there is any error

			db.rollback()
			if debugging:
				log('Error in db commit. Transaction rolled back')

	# disconnect from server

		db.close()

		if autoclean:
			xbmcgui.Dialog().notification(addonname,
								'Running built in library cleanup', xbmcgui.NOTIFICATION_INFO,
								5000)
			xbmc.sleep(5000)

			json_query = \
				xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "VideoLibrary.Clean","id": 1 }'
									)
			json_query = unicode(json_query, 'utf-8', errors='ignore')
			json_query = jsoninterface.loads(json_query)
			if json_query.has_key('result'):
				if debugging:
					log('Clean library sucessfully called')
		else:
			xbmcgui.Dialog().ok(addonname,
								'Script finished.  You should run clean library for best results'
								)
		if debugging:
			log('Script finished')
	else:
		xbmcgui.Dialog().ok(addonname, 'Script aborted by user')
		if debugging:
			log('script aborted by user - no changes made')
		exit(1)
