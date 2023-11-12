# -*- coding: utf-8 -*-
# #!/usr/bin/python

# Important: Plugins cannot be developed standalone outside of Mezzmo enviroment.  You will need to
# create plugins and load them into Mezzmo to get them to compile and run correctly, since
# Mezzmo injects paths & objects into python interpreter at runtime.  Use logging to debug your
# python script.

# See 'Plugins\MezzmoBaseClasses' folder for definition of Mezzmo classes that are to used
# for creating MezzmoPlugin, MezzmoDirectory, MezzmoItem and MezzmoSetting objects
from mezzmo import *

import logging
import time
import json
from functools import partial
from datetime import datetime, timedelta

import urllib
import urllib2

import pickle
from time import gmtime, strftime

# movie trailer feed URLs
MOVIETRAILERS_URL_CONFIG    = 'http://api.themoviedb.org/3/configuration?api_key=dee64c83bd0310bc227948c9d4bc5aab'
MOVIETRAILERS_URL_LIST      = 'http://api.themoviedb.org/3/movie/{}?api_key=dee64c83bd0310bc227948c9d4bc5aab'
MOVIETRAILERS_URL_DETAILS   = 'http://api.themoviedb.org/3/movie/{}?api_key=dee64c83bd0310bc227948c9d4bc5aab&append_to_response=videos,releases,casts'
MOVIETRAILERS_URL_YOUTUBE   = 'https://www.youtube.com/watch?v={}'
MOVIETRAILERS_URL_BASE      = ''
MOVIETRAILERS_POSTER_SIZE   = 'w500'
MOVIETRAILERS_BACKDROP_SIZE = 'original'


# global dictionary of user preferences for this plugin (see def get_prefs() & def mezzmo_set_settings()
MovieTrailerSettings = {}

########################################################################################################################
def getTrailerDetails(db, tmdb_id):

    global MOVIETRAILERS_URL_BASE

    if MOVIETRAILERS_URL_BASE == '':
        # retrieve JSON content about themoviedb.org configuration so we can get its base URL
        file = urllib2.urlopen(MOVIETRAILERS_URL_CONFIG)
        json_obj = json.load(file)
        file.close()
        if json_obj.get('images'):
            MOVIETRAILERS_URL_BASE = json_obj['images']['base_url']

    if MOVIETRAILERS_URL_BASE == '':
        # error - could not get base url
        return None

    trcurr = db.execute('select tmdb_id, mezzmoTrURL, trType, trTitle, trOverview, trTagline, trRelease_date, trImdb_id, trWebsite, \
    trPoster_path, trBackdrop_path, trUser_rating, trGenres, trProd_company, trContent_rating, trArtist_actor, trComposer from      \
    mTrailers where tmdb_id = ?', (tmdb_id,))
    trtuple = trcurr.fetchone()
    #genLog(str(trtuple))
    
    if trtuple:
        # has a trailer video, so create new MezzmoItem object & fill in details
        if 'n' not in MovieTrailerSettings['detlogging'].lower():
            genLog(str(trtuple))
        item = MezzmoItem()
        item.title = trtuple[3]
        if item.title[:4] == 'The ':
            item.sort_title = item.title[4:]
        elif item.title[:3] == 'An ':
            item.sort_title = item.title[3:]
        elif item.title[:2] == 'A ':
            item.sort_title = item.title[2:]
        else:
            item.sort_title = item.title
        item.type = "video"
        if MovieTrailerSettings['trcategory'].lower() in ['video', 'movie', 'trailer']:
            item.category = MovieTrailerSettings['trcategory']
        item.themoviedb_id = trtuple[0]
        item.uri = trtuple[1]
        item.description = trtuple[4]
        item.tagline = trtuple[5]
        item.release_date = trtuple[6]
        if len(MovieTrailerSettings['trkeyword']) > 2:
            item.keywords = MovieTrailerSettings['trkeyword']
        item.imdb_id = trtuple[7]
        item.website = trtuple[8]
        item.poster_uri = trtuple[9]
        item.backdrop_uri = trtuple[10]
        item.user_rating = trtuple[11]
        if trtuple[12]:
            genre_text = ''
            genre_text = trtuple[12].split('##')
            genres = []
            for g in genre_text:
                genres.append(g) 
            item.genre = genres
        if trtuple[13]:
            production_company_text = ''
            production_company_text = trtuple[13].split('##')
            production_companies = []
            for p in production_company_text:
                production_companies.append(p) 
            item.production_company = production_companies
        item.content_rating = trtuple[14]
        if trtuple[15]:
            artist_actor_text = ''
            artist_actor_text = trtuple[15].split('##')
            artist_actors = []
            for g in artist_actor_text:
                artist_actors.append(g) 
            item.artist_actor = artist_actors
        if trtuple[16]:
            composer_director_creator_text = ''
            composer_director_creator_text = trtuple[16].split('##')
            composer_director_creators = []
            for c in composer_director_creator_text:
                composer_director_creators.append(c) 
            item.composer_director_creator = composer_director_creators
        return item
    return None


########################################################################################################################
def trailerDirectoryCallback(type):

    # function to get list of trailers for a given type
    content = []
    
    # themoviedb.org has server-side rate limiting (max. 40 requests in a 10 second span), so wait a little to try to keep within this limit
    #time.sleep(0.15)

    db = openTrailerDB()     

    dbcurr = db.execute('select count (tmdb_id) from mTrailers where trType = ?', (type,))
    dbtuple = dbcurr.fetchone()

    if dbtuple:
        if 'n' not in MovieTrailerSettings['detlogging'].lower():
            genLog('Number of movies found for ' + type + ': ' + str(dbtuple[0]))
        dbcurr = db.execute('select tmdb_id from mTrailers where trType = ? ORDER BY trRelease_date DESC', (type,))
        dbtuple = dbcurr.fetchall()
        for trailer in range(len(dbtuple)):
             item = getTrailerDetails(db, dbtuple[trailer][0])
             if item != None:
                 content.append(item)
    else:
        content = None

    db.close()
        
    return content


########################################################################################################################

def openTrailerDB():

    global MovieTrailerSettings

    trailerdb = MovieTrailerSettings['mezchannelpath'].rstrip('\\') + '\\trailers\\mezzmo_trailers.db'

    if 'n' not in MovieTrailerSettings['detlogging'].lower():
        genLog(trailerdb)
    
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                      
    db = sqlite.connect(trailerdb)

    return db


########################################################################################################################
def get_prefs(language):

    # partial callback that define the preferences that user can set to change the behaviour of movie trailers plugin
    prefs = []
    
    pref_1 = MezzmoSetting()
    pref_1.id = "mezchannelpath"
    pref_1.type = "text"
    pref_1.label = "Local path to Mezzmo channels folder. (i.e. e:\mezzmo_channels ) "
    pref_1.description = "Enter local path to Mezzmo Channels folder "
    pref_1.text_hide_value = 0
    pref_1.default_value = "  "
    prefs.append(pref_1)

    pref_3 = MezzmoSetting()
    pref_3.id = "trcategory"
    pref_3.type = "text"
    pref_3.label = "Trailer media category type Video, Movie, or Trailer.  Default is Video ?  "
    pref_3.description = "Enable trailer media category type "
    pref_3.text_hide_value = 0
    pref_3.default_value = "Video"
    prefs.append(pref_3)

    pref_4 = MezzmoSetting()
    pref_4.id = "trkeyword"
    pref_4.type = "text"
    pref_4.label = "Enable default keyword(s) for all trailers.  Default is blank.  "
    pref_4.description = "Enter a default keyword "
    pref_4.text_hide_value = 0
    pref_4.default_value = ""
    prefs.append(pref_4)


    pref_2 = MezzmoSetting()
    pref_2.id = "detlogging"
    pref_2.type = "text"
    pref_2.label = "Enable detailed logging (Y/N) ?  "
    pref_2.description = "Enable detailed logging "
    pref_2.text_hide_value = 0
    pref_2.default_value = "N"
    prefs.append(pref_2)

    return prefs


########################################################################################################################
def mezzmo_set_settings(settings_path):

    # callback function that is called by Mezzmo on plugin startup and after user changes preference settings;
    # 'settings_path' contains the full path to the pickled settings file

    # reload preference settings
    global MovieTrailerSettings
    with open(settings_path, "rb") as f:
        MovieTrailerSettings = pickle.load(f)


########################################################################################################################
def mezzmo_get_plugins(language):

    # entry point callback function that is called by Mezzmo to get the list of plugins that this module defines;
    # this module defines 1 plugin - a Movie Trailers plugin
    # 'language' contains the Mezzmo user-set language (e.g. 'en', 'fr', 'de', etc.)

    # define Movie Trailers plugin details
    plugins = []
    plugin = MezzmoPluginContentProvider()
    plugin.id = "mezzmo.plugin.MovieTrailers"
    plugin.title = "Movie Trailers 2"
    plugin.version = "0.0.3"
    plugin.author = "Conceiva Pty. Ltd., jbinkley60"
    plugin.web_link = "https://www.themoviedb.org/"
    plugin.description = 'View movie trailers for current and upcoming movie releases.\n\nTrailer information provided by www.themoviedb.org.'
    plugin.media_type = ["video"]
    plugin.category = ["Video"]
    plugin.poster_uri = "MovieTrailers.jpg"
    plugin.backdrop_uri = "MovieTrailersBackdrop.jpg"
    plugin.settings = partial(get_prefs, language=language)

    # add the top-level directories for the Trailer plugin

    # view trailers for now playing movies
    nowplayingDirectory = MezzmoDirectory()
    nowplayingDirectory.title = "Movies Now Showing"
    nowplayingDirectory.description = "View movie trailers for movies that are currently playing."
    nowplayingDirectory.children = partial(trailerDirectoryCallback, "now_playing")
    nowplayingDirectory.ttl = 0
    nowplayingDirectory.backdrop_uri = "MovieTrailersBackdrop.jpg"
    nowplayingDirectory.sort_by = "Release date (Ascending)"
    plugin.children.append(nowplayingDirectory)
    
    # view trailers for upcoming movies
    upcomingDirectory = MezzmoDirectory()
    upcomingDirectory.title = "New Movies Coming Soon"
    upcomingDirectory.description = "View movie trailers for upcoming movie releases."
    upcomingDirectory.children = partial(trailerDirectoryCallback, "upcoming")
    upcomingDirectory.ttl = 0
    upcomingDirectory.backdrop_uri = "MovieTrailersBackdrop.jpg"
    upcomingDirectory.sort_by = "Release date (Ascending)"
    plugin.children.append(upcomingDirectory)
    
    # view trailers for popular movies
    popularDirectory = MezzmoDirectory()
    popularDirectory.title = "Popular Movies"
    popularDirectory.description = "View movie trailers for popular movies."
    popularDirectory.children = partial(trailerDirectoryCallback, "popular")
    popularDirectory.ttl = 0
    popularDirectory.backdrop_uri = "MovieTrailersBackdrop.jpg"
    popularDirectory.sort_by = "Sort Title (Ascending)"
    plugin.children.append(popularDirectory)
    
    # view trailers for top-rated movies
    topratedDirectory = MezzmoDirectory()
    topratedDirectory.title = "Top Rated Movies"
    topratedDirectory.description = "View movie trailers for top rated movies."
    topratedDirectory.children = partial(trailerDirectoryCallback, "top_rated")
    topratedDirectory.ttl = 0
    topratedDirectory.backdrop_uri = "MovieTrailersBackdrop.jpg"
    topratedDirectory.sort_by = "Sort Title (Ascending)"
    plugin.children.append(topratedDirectory)
    
    # add Trailer plugin to list of plugin that this module defines
    plugins.append(plugin)

    # return list of plugins
    return plugins


########################################################################################################################
def mezzmo_set_logging(status, logging_path):

    # callback function that is called by Mezzmo on plugin startup and when user Mezzmo user turns on/off logging;
    # 'logging_path' contains the path where logs can be stored
    if status == 1:
        # turn logging on
        file_name = logging_path + time.strftime("%Y-%m-%d-%H-%M-%S.txt")
        fmt_line = "%(asctime)s: %(filename)s: %(funcName)s (%(lineno)d): %(message)s"
        fmt_date = "%Y-%m-%d %H:%M:%S"
        logging.basicConfig(filename = file_name, filemode = "w", level = logging.DEBUG, format=fmt_line, datefmt=fmt_date)
        logging.disable(logging.NOTSET)
        logging.info("Logging turned on")
    else:
        #turn logging off
        logging.info("Logging turned off")
        logging.disable(logging.CRITICAL)


########################################################################################################################
def genLog(mgenlog):                                        #  Write to logfile

        logoutfile = MovieTrailerSettings['mezchannelpath'].rstrip('\\') + '\\trailers\\logfile.txt'

        fileh = open(logoutfile, "a")                       #  open logf file
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        data = fileh.write(currTime + ' - ' + mgenlog + '\n')
        fileh.close()