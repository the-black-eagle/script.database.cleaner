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
# Version 29b/2 - Fix incorrectly altered SQL
# Version 30/b1 - UI improvements - only allow one instance

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
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
        self.container = self.getControl(6)
        self.container2 = self.getControl(8)
        self.container3 = self.getControl(10)
        self.listitems = []
        self.excludesitems = []
        self.addonsettings = []
        
    #       List paths from sources.xml 
        if not specificpath and not replacepath:
            self.display_list = display_list
            for i in range(len(self.display_list)):
                self.listitems.append('[COLOR yellow]'+ self.display_list[i] + '[/COLOR]')
            if no_sources:
                self.listitems.append('[COLOR red][B]No sources are in use[/B][/COLOR]')
                self.listitems.append('[COLOR red][B]All streaming paths will be removed[/B][/COLOR]')
                if excluding:
					self.listitems.append('')
					self.listitems.append('[COLOR red][B]Paths from excludes.xml will be kept[/B][/COLOR]')
        if replacepath:
            self.listitems.append('[COLOR yellow]Replacing a path[/COLOR]')
            self.listitems.append('[COLOR yellow]in your database[/COLOR]')
            self.listitems.append('[COLOR yellow]Confirm details below[/COLOR]')
        if specificpath:
            self.listitems.append('[COLOR yellow]Removing a path[/COLOR]')
            self.listitems.append('[COLOR yellow]in your database[/COLOR]')
            self.listitems.append('[COLOR yellow]Confirm details below[/COLOR]')
        self.container.addItems(self.listitems)
    #       List paths in excludes.xml (if it exists)
        
        self.excludes_list = excludes_list

        if excluding:
            for i in range(len(self.excludes_list)):
                self.excludesitems.append('[COLOR yellow]' + self.excludes_list[i]+ '[/COLOR]')
        else:
            self.excludesitems.append("Not Present")
        self.container2.addItems(self.excludesitems)
            
    #       List the relevant addon settings
 
        if is_pvr and (not specificpath and not replacepath):
            self.addonsettings.append('Keep PVR information')
        if bookmarks and (not specificpath and not replacepath):
             self.addonsettings.append('Keep bookmark information')
        if autoclean:
            self.addonsettings.append('Auto call Clean Library')
        if promptdelete:
            self.addonsettings.append('Show summary window (This window !!)')
        if autobackup == 'true' and not is_mysql:
            self.addonsettings.append('Auto backing up local database')
        if no_sources or specificpath or replacepath:
            self.addonsettings.append('[COLOR red]Not[/COLOR] using info from sources.xml')
        if specificpath:
            self.addonsettings.append('[COLOR red]Cleaning a specific path[/COLOR]')
        if replacepath:
            self.addonsettings.append('[COLOR red]Replacing a path[/COLOR]')
        if enable_logging:
            self.addonsettings.append('Writing a logfile to Kodi TEMP directory')
        if debugging:
            debug_string = 'Debugging [COLOR red]enabled[/COLOR]'
        else:
            debug_string = 'Debugging [COLOR green]disabled[/COLOR]'
        self.addonsettings.append(debug_string)
        self.addonsettings.append('') #blank line
        #   Display the name of the database we are connected to
        self.addonsettings.append('Database is - [COLOR green][B]%s[/B][/COLOR]' % our_dbname)
        cursor.execute(our_select)
        data_list = cursor.fetchall()
        data_list_size = len(data_list)
        if replacepath:
            self.addonsettings.append('[COLOR red][B]There are %d paths to be changed[/B][/COLOR]' % data_list_size)
        else:
            self.addonsettings.append('[COLOR red][B]There are %d entries to be removed[/B][/COLOR]' % data_list_size)

        self.container3.addItems(self.addonsettings)
        #   Show warning about backup if using MySQL    
        if is_mysql:
            self.getControl(20).setLabel('WARNING - MySQL database [COLOR red][B]not[/B][/COLOR] backed up automatically, please do this [B]manually[/B]')
        if specificpath:
            self.getControl(20).setLabel('WARNING - Removing specific path [COLOR yellow]%s[/COLOR] ' % specific_path_to_remove)
        if replacepath:
            self.getControl(20).setLabel('WARNING - Renaming specific path from [COLOR yellow]%s[/COLOR] ' % old_path)
            self.getControl(21).setLabel('TO  [COLOR yellow]%s[/COLOR] ' % new_path)

 
    def onAction(self, action):
        global flag
        dbglog('Got an action %s' % action.getId())
        if ( action == ACTION_PREVIOUS_MENU ) or ( action == ACTION_NAV_BACK ):
            self.close()
        if (action == ACTION_SELECT_ITEM) or ( action == ACTION_MOUSE_LEFT_CLICK ):
            try:
                btn = self.getFocus()
                btn_id = btn.getId()

            except:
                btn_id = None
            if btn_id == 1:
                dbglog('you pressed abort')
                flag = 0
                self.close()
            elif btn_id == 2:
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
bp_logfile_path = xbmc.translatePath('special://temp/bp-debuglog.log').decode('utf-8')
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
        
def exit_on_error():
    WINDOW.setProperty('database-cleaner-running', 'false')
    exit(1)

        
        
def cleaner_log_file(our_select, cleaning):
    cleaner_log = xbmc.translatePath('special://temp/database-cleaner.log').decode('utf-8')
    old_cleaner_log = xbmc.translatePath('special://temp/database-cleaner.old.log').decode('utf-8')
    old_log_contents =''
    do_progress = False
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
    date_long_format = xbmc.getRegion('datelong')
    time_format = xbmc.getRegion('time')
    date_long_format = date_long_format + ' '+time_format
    logfile_header = 'Video Database Cleaner V' + addonversion+ ' - Running at ' +now.strftime(date_long_format) + '\n\n'
    logfile.write(logfile_header)
    cursor.execute(our_select)
    counting = 0
    my_data = cursor.fetchall()
    listsize = len(my_data)
    dbglog("Listsize is %d" % listsize)
    logfile.write('There are %d paths in the database that meet your criteria\n\n' % listsize)
    if listsize > 600:
        do_progress = True
        dialog  = xbmcgui.DialogProgressBG()
        dbglog('Creating progress dialog for logfile')
        dialog.create('Getting required data.  Please wait')
        dialog.update(1)
    
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
        for strPath in my_data:
            counting +=1
            mystring = u''.join(strPath) + '\n'
            outdata = mystring.encode('utf-8')
            if do_progress:
                dialog.update(percent = int((counting / float(listsize)) * 100))
            if cleaning:
                dbglog('Removing %s' % strPath)
            logfile.write(outdata)
    elif specificpath and not replacepath:
        dbglog('Removing specific path %s' % specific_path_to_remove)
        for strPath in my_data:
            counting +=1
            mystring = u''.join(strPath) + '\n'
            outdata = mystring.encode('utf-8')
            if do_progress:
                dialog.update(percent = int((counting / float(listsize)) * 100))
            if cleaning:
                dbglog('Removing unwanted path %s' % strPath)
            logfile.write(outdata)
    else:
        for strPath in my_data:
            counting +=1
            mystring = u''.join(strPath) + '\n'
            outdata = mystring.encode('utf-8')
            if do_progress:
                dialog.update(percent = int((counting / float(listsize)) * 100))
            if cleaning:
                dbglog('Changing path %s' % strPath)
            logfile.write(outdata)
        our_data = cursor
    if counting == 0:  # nothing to remove
        logfile.write('No paths have been found to remove\n')
    if do_progress:
        dialog.close()  
    logfile.write('\n\n')
    logfile.close()
    
####    Start Here !!   ####

dbglog('script version %s started' % addonversion)
#if WINDOW.getProperty('database-cleaner-running') == 'true': 
    #log('Video Database Cleaner already running')
    #exit(0)
#else:
    #WINDOW.setProperty('database-cleaner-running', 'true')
    
xbmcgui.Dialog().notification(addonname, 'Starting Up', xbmcgui.NOTIFICATION_INFO, 2000)
xbmc.sleep(2000)

if xbmcvfs.exists(advanced_file):
    dbglog('Found advancedsettings.xml')
    found = True

if found:
    msg = advanced_file.encode('utf-8')
    dbglog('looking in advancedsettings for videodatabase info')
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
                our_port = videodb.find('port').text
            except:
                log('Unable to find MySQL port')
            try:
                our_dbname = videodb.find('name').text
            except:
                our_dbname = 'MyVideos'
            dbglog('MySQL details - %s, %s, %s, %s' % (our_host, our_port, our_username, our_dbname))
            is_mysql = True
    except Exception as e:
        e =str(e)
        dbglog ('Error parsing advancedsettings file - %s' % e)
        is_mysql = False

if not is_mysql:
    our_dbname = 'MyVideos'

    for num in range(114, 35, -1):
        testname = our_dbname + str(num)
        our_test = db_path + testname + '.db'

        dbglog('Checking for local database %s' % testname)
        if xbmcvfs.exists(our_test):
            break
    if num != 35:
        our_dbname = testname

    if our_dbname == 'MyVideos':
        dbglog('No video database found - assuming MySQL database')
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
        dbglog('Error parsing local sources.xml file')
        xbmcgui.Dialog().ok(addonname, 'Error parsing local sources.xml file - script aborted')
        exit_on_error()
elif xbmcvfs.exists(sources_file):
    try:
        f = xbmcvfs.File(sources_file)
        source_file = f.read()
        f.close()
        root = ET.fromstring(source_file)
        dbglog('Got remote sources.xml')
    except:
        dbglog('Error parsing remote sources.xml')
        xbmcgui.Dialog().ok(addonname, 'Error parsing remote sources.xml file - script aborted')
        exit_on_error()
else:
    xbmcgui.Dialog().notification(addonname,
                        'Warning - no sources.xml file found - defaulting to cleaning streaming paths only',xbmcgui.NOTIFICATION_INFO,3000)
    dbglog('No local sources.xml, no remote sources file set in settings')
    xbmc.sleep(3000)
    no_sources = True
my_command = ''
first_time = True
if forcedbname:
    log('Forcing video db version to %s' % forcedname)

# Open database connection

if is_mysql and not forcedbname:
    if our_dbname == '': # no db name in advancedsettings
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
    else:       # already got db name from ad settings
        for num in range(114, 35, -1):
            testname = our_dbname + str(num)
            try:
                dbglog('Attempting MySQL connection to %s' % testname)
                db = mysql.connector.connect(user=our_username, database=testname, password=our_password, host=our_host, port=our_port)
                if db.is_connected():
                    our_dbname = testname
                    dbglog('Connected to MySQL database %s' % our_dbname)
                    break
            except:
                pass
    if not db.is_connected():
        xbmcgui.Dialog().ok(addonname, "Couldn't connect to MySQL database", s)
        log("Error - couldn't connect to MySQL database - %s " % s)
        exit_on_error()
elif is_mysql and forcedbname:
    try:
        db = mysql.connector.connect(user=our_username, database=forcedname, password=our_password, host=our_host, port=our_port)
        if db.is_connected():
            our_dbname = forcedname
            dbglog('Connected to forced MySQL database %s' % forcedname)
    except:
        log('Error connecting to forced database - %s' % forcedname)
        exit_on_error()
elif not is_mysql and not forcedbname:
    try:
        my_db_connector = db_path + our_dbname + '.db'
        db = sqlite3.connect(my_db_connector)
    except Exception,e:
        s = str(e)
        xbmcgui.Dialog().ok(addonname, 'Error connecting to SQLite database', s)
        log('Error connecting to SQLite database - %s' % s)
        exit_on_error()
else:
    testpath = db_path + forcedname + '.db'
    if not xbmcvfs.exists(testpath):
        log('Forced version of database does not exist')
        xbmcgui.Dialog().ok(addonname,'Error - Forced version of database ( %s ) not found. Script will now exit' % forcedname)
        exit_on_error()
    try:
        my_db_connector = db_path + forcedname + '.db'
        db = sqlite3.connect(my_db_connector)
        dbglog('Connected to forced video database')
    except:
        xbmcgui.Dialog().ok(addonname,'Error - Unable to connect to forced database %s. Script will now exit' % forcedname)
        log('Unable to connect to forced database s%' % forcedname)
        exit_on_error()

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
        exit_on_error()

if not no_sources:
    # start reading sources.xml and build SQL statements to exclude these sources from any cleaning
    try:
        display_list =[]
        for video in root.findall('video'):
            dbglog('Contents of sources.xml file')

            for sources in video.findall('source'):
                for path_name in sources.findall('name'):
                    the_path_name = path_name.text
                    for paths in sources.findall('path'):
                            the_path = paths.text.replace("'","''")
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
        exit_on_error()

    if is_pvr:
        my_command = my_command + " AND strPath NOT LIKE 'pvr://%'"
        our_source_list = our_source_list + 'Keeping PVR info '
    if excluding:
        my_command = my_command + exclude_command
        our_source_list = our_source_list + 'Keeping items from excludes.xml '
    if bookmarks:
        my_command = my_command + ' AND idFile NOT IN (SELECT idFile FROM bookmark)'
        our_source_list = our_source_list + 'Keeping bookmarked files '
        
        # construct the full SQL query
        
    sql = \
        """DELETE FROM files WHERE idPath IN(SELECT idPath FROM path where (""" + my_command + """));"""
if no_sources:
    my_command = ''
    our_source_list = 'NO SOURCES FOUND - REMOVING rtmp(e), plugin and http info '
    dbglog('Not using sources.xml')
    if is_pvr:
        my_command = my_command + "strPath NOT LIKE 'pvr://%'"
        our_source_list = our_source_list + 'Keeping PVR info '
    if bookmarks:
        if my_command:
            my_command = my_command + ' AND idFile NOT IN (SELECT idFile FROM bookmark)'
        else: 
            my_command = my_command + ' idFile NOT IN (SELECT idFile FROM bookmark)'
        our_source_list = our_source_list + 'Keeping bookmarked files '
    if excluding:
        if my_command:
            my_command = my_command + exclude_command
        else:
            my_command = my_command + exclude_command.replace('AND','',1)
        our_source_list = our_source_list + 'Keeping items from excludes.xml '
            
# Build SQL query

if not no_sources: # this is SQL for no sources
    sql = """DELETE FROM files WHERE idPath IN ( SELECT idPath FROM path WHERE ((""" + my_command + """)));"""
#   sql2="""DELETE FROM path WHERE idPath IN (SELECT * FROM( SELECT idPath FROM path WHERE ((strPath LIKE 'rtmp://%' OR strPath Like 'rtmpe:%' OR strPath LIKE 'plugin:%' OR strPath LIKE 'http://%') AND (""" + my_command +"""))) as pathsub);"""
else:
    sql = """DELETE FROM files WHERE idPath IN (SELECT idPath FROM path WHERE ((strPath LIKE 'rtmp://%' OR strPath LIKE 'rtmpe:%' OR strPath LIKE 'plugin:%' OR strPath LIKE 'http://%' OR strPath LIKE 'https://%') AND (""" + my_command + """)));"""
#   sql2= """DELETE FROM path WHERE idPath IN (SELECT * FROM( SELECT idPath FROM path WHERE (strPath LIKE 'rtmp://%' OR strPath Like 'rtmpe:%' OR strPath LIKE 'plugin:%' OR strPath LIKE 'http://%') as pathsub);"""   
dbglog('SQL command is %s' % sql)
if not specificpath and not replacepath:
    dbglog (our_source_list)            
    our_select = sql.replace('DELETE FROM files','SELECT strPath FROM path',1)
    if bookmarks:  # have to delete from paths table rather than files as there is a conflicting trigger on the files table
        our_select = sql.replace('DELETE FROM files', 'SELECT strPath FROM path WHERE idPath in (SELECT idPath FROM files', 1)
        our_select = our_select.replace('bookmark)', 'bookmark))',1)
        sql = sql.replace('DELETE FROM files','DELETE FROM path',1)
    dbglog('Select Command is %s' % our_select)
elif not replacepath and specificpath:      # cleaning a specific path
    if specific_path_to_remove != '':
        sql = """delete from path where idPath in(select * from (SELECT idPath FROM path WHERE (strPath LIKE '""" + specific_path_to_remove +"""%')) as temptable)"""
        our_select = "SELECT strPath FROM path WHERE idPath IN (SELECT idPath FROM path WHERE (strPath LIKE'" + specific_path_to_remove + "%'))"
        dbglog('Select Command is %s' % our_select)
    else:
        xbmcgui.Dialog().ok(addonname,'Error - Specific path selected but no path defined. Script aborted')
        dbglog("Error - Specific path selected with no path defined")
        exit_on_error()
else: # must be replacing a path at this point
    if old_path != '' and new_path != '':
        our_select = "SELECT strPath from path WHERE strPath Like '" + old_path + "%'"
    else:
        xbmcgui.Dialog().ok(addonname,'Error - Replace path selected but one or more paths are not defined. Script aborted')
        dbglog('Error - Missing path for replacement')
        exit_on_error()
xbmc.sleep(500)

if promptdelete:
    cleaner_log_file(our_select, False)
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
#           cursor.execute(sql2)
        # Commit the changes in the database

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
        cursor.execute(our_select)
        tempcount=0
        listsize = len(cursor.fetchall())
        dialog  = xbmcgui.DialogProgressBG()
        dbglog('Creating progress dialog')
        dialog.create('Replacing paths in database.  Please wait')
        dialog.update(1)
        dbglog('Cursor size is %d' % listsize)
        cursor.execute(our_select)
        renamepath_list = [] 
        for strPath in cursor:  # build a list of paths to change
            renamepath_list.append( ''.join(strPath))
            
            
        for i in range(len(renamepath_list)):
            tempcount += 1
            our_old_path = renamepath_list[i]
            our_new_path = our_old_path.replace(old_path, new_path,1)
            sql = 'UPDATE path SET strPath ="' + our_new_path + '" WHERE strPath LIKE "' +our_old_path + '"'
            dialog.update(percent = int((tempcount / float(listsize)) * 100))
            dbglog('Percentage done %d' % int((tempcount / float(listsize)) * 100))
            dbglog('SQL - %s' % sql)
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                e = str(e)
                db.rollback()
                dbglog('Error in db commit %s. Transaction rolled back' % e)

    # disconnect from server
#       xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        xbmc.sleep(1000)
        dbglog('Closing progress dialog')
        dialog.close()
    db.close()
    dbglog("Database connection closed")
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
    WINDOW.setProperty('database-cleaner-running', 'false')
    exit(1)
WINDOW.setProperty('database-cleaner-running', 'false')

