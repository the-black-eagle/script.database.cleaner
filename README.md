# script.database.cleaner

A program add-on for Kodi to help clean out all the streams and other 
unwanted junk that accumulates over time in the video database.

This script will connect to your video database (either MySQL or SQLite),
read the sources you have defined in your sources.xml (all the paths you
have added to Kodi containing your movies/tv-shows) and delete anything
in the 'files' table of the database that isn't in your sources.

The script can optionally back-up your SQLite database (highly recommended)
with a date and time stamp appended.  MySQL users need to manually back-up
their database.

Users can also choose (via the add-on settings) to retain or remove old 
PVR information and to retain or remove bookmarks.

When run, the script will prompt with a pop-up box containing a (long) line
of SQL.  This is the actual SQL command that will be executed and users are
encouraged to check that all their defined sources are indeed listed. 
Clicking on 'yes' will execute the SQL, clicking on 'no' will abort the script
with no changes made to the database.

Once users are happy that the script is working correctly, this prompt can
be turned off in the add-on settings.

When the SQL command has been run the script calls Kodi's built in 'clean
library' routine to clean the other tables in the database.  This can also
be turned off in the settings but this is not recommended.

If Kodi's debugging is enabled, the script will write a few things in there.
If the script's debugging is also enabled in the settings, it will be quite
verbose as to what it is doing.

DISCLAIMER
==========

Whilst every effor has been made to ensure this script works correctly, the
authors take absolutely no responsibility for any damage caused to your database
by it's use in any way.  ALWAYS back up your database before running this script.
