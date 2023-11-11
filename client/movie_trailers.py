# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv, json, glob
from datetime import datetime, timedelta
import time
import urllib.request, urllib.parse, urllib.error
import http.client
import mimetypes
import subprocess
import string, random, re
from urllib.request import Request, urlopen


trailerdb = ''
tr_config = {}
totcount = bdcount = gdcount = mvcount = 0
trlcount = skipcount = longcount = 0

# movie trailer feed URLs
MOVIETRAILERS_URL_LIST  = 'http://api.themoviedb.org/3/movie/{}?{}&api_key=dee64c83bd0310bc227948c9d4bc5aab'
MOVIETRAILERS_URL_CONFIG    = 'http://api.themoviedb.org/3/configuration?api_key=dee64c83bd0310bc227948c9d4bc5aab'
MOVIETRAILERS_URL_DETAILS   = 'http://api.themoviedb.org/3/movie/{}?api_key=dee64c83bd0310bc227948c9d4bc5aab&append_to_response=videos,releases,casts'
MOVIETRAILERS_URL_YOUTUBE   = 'https://www.youtube.com/watch?v={}'
MOVIETRAILERS_URL_BASE      = ''
MOVIETRAILERS_POSTER_SIZE   = 'w500'
MOVIETRAILERS_BACKDROP_SIZE = 'original'

version = 'version 0.0.2'

sysarg1 = sysarg2 = sysarg3 = sysarg4 = ''

if len(sys.argv) == 2:
    sysarg1 = sys.argv[1]
if len(sys.argv) == 3:
    sysarg1 = sys.argv[1]   
    sysarg2 = sys.argv[2]

if len(sys.argv) == 4:
    sysarg1 = sys.argv[1]   
    sysarg2 = sys.argv[2]
    sysarg3 = sys.argv[3]
 
if len(sys.argv) == 5:
    sysarg1 = sys.argv[1]   
    sysarg2 = sys.argv[2]
    sysarg3 = sys.argv[3]
    sysarg4 = sys.argv[4]


def checkVersion():

    if sys.version_info[0] < 3:
        print('\nThe Mezzmo Movie Trailer Channel requires Python version 3 or higher')
        print('Python version: ' + str(sys.version_info[0]) + '.' + str(sys.version_info[1])   \
        + '.' + str(sys.version_info[2]) + ' found.')
        exit()  


def getConfig():

    try: 

        global tr_config, version      
        fileh = open("config.txt")                                     # open the config file

        data = fileh.readline()                                        # Get local channels location
        datab = data.split('#')                                        # Remove comments
        ltrailerloc = datab[0].strip().rstrip("\n")                    # cleanup unwanted characters

        data = fileh.readline()                                        # Get Mezzmo channels location
        dataj = data.split('#')                                        # Remove comments
        mtrailerloc = dataj[0].strip().rstrip("\n")                    # cleanup unwanted characters

        data = fileh.readline()                                        # Get number of trailers to keep
        datac = data.split('#')                                        # Remove comments
        tkeepcount = datac[0].strip().rstrip("\n")                     # cleanup unwanted characters
        if int(tkeepcount) > 50:
            tkeepcount = 50                                            # Max trailers per type is 30

        data = fileh.readline()                                        # Get trailer max resolution
        datae = data.split('#')                                        # Remove comments
        maxres = datae[0].strip().rstrip("\n")                         # cleanup unwanted characters
        if maxres not in ['1080', '720', '480'] :
            maxres = '720'                                             # Default to 720P

        data = fileh.readline()                                        # Logfile location
        if data != '':
            datai = data.split('#')                                    # Remove comments
            logoutfile = datai[0].strip().rstrip("\n")                 # cleanup unwanted characters         
        else:
            logoutfile = 'logfile.txt'                                 # Default to logfile.txt

        data = fileh.readline()                                        # Get output format option
        if data != '':
            datav = data.split('#')                                    # Remove comments
            tformat = datav[0].strip().rstrip("\n").lower()            # cleanup unwanted characters
        else:
            tformat = 'mp4'   
        fileh.close()                                                  # close the file
        
        tr_config = {
                     'ltrailerloc': ltrailerloc,
                     'mtrailerloc': mtrailerloc,
                     'mcount': tkeepcount,
                     'maxres': maxres,
                     'logoutfile': logoutfile,
                     'tformat': tformat,
                    }

        if not tformat in ['mkv', 'mp4']:
            tformat = 'mp4'
            mgenlog = 'Invalid output format in config file.  Defaulting to mp4 format'
            genLog(mgenlog)
            print(mgenlog) 

        configuration = [ltrailerloc, mtrailerloc, tkeepcount, maxres, logoutfile, tformat]
        mgenlog = ("Mezzmo Movie Trailers Channel Checker Client - " + version)
        print(mgenlog)
        genLog(mgenlog)
        genLog(str(configuration))               # Record configuration to logfile     
        mgenlog = "Finished reading config file."
        genLog(mgenlog)       
        return 
 
    except Exception as e:
        print (e)
        mgenlog = 'There was a problem parsing the config file.'
        genLog(mgenlog)
        print(mgenlog)


def checkCommands(sysarg1, sysarg2):                                   # Check for valid commands
   
    if len(sysarg1) > 1 and sysarg1.lower() not in ['trailers', 'csv', 'help', 'backup', 'clean']:
        displayHelp(sysarg1)
        exit()
    if len(sysarg1) == 0 or 'help' in sysarg1.lower():
        displayHelp(sysarg1)
        exit()


def displayHelp(sysarg1):                                 #  Command line help menu display

        print('\n=====================================================================================================')
        print('\nThe only valid commands are -  trailers, csv, backup, clean, and help  ')
        print('\nExample:  mezzmo_trailers.py trailers now')      
        print('\ntrailers now\t - Checks for Now Playing movies')
        print('trailers up\t - Checks for Upcoming movies')
        print('trailers pop\t - Checks for Popular movies')
        print('trailers top\t - Checks for Top Rated movies ')
        print('trailers all\t - Checks for all for movie categories - Future ')
        print('\nclean category\t - Clears trailer database info for movies by category and deletes downloaded trailer file')
        print('\t\t   Valid types are: now, up, pop,top, all') 
        print('\ncsv trailers\t - Creates a CSV file with the trailer information in the Mezzmo Trailer Checker')
        print('csv history\t - Creates a CSV file with the history information in the Mezzmo Trailer Checker')
        print('\nbackup\t\t - Creates a time stamped file name backup of the Mezzmo Trailer Checker database')
        print('\n=====================================================================================================')
        print('\n ')


def getMezzmoTrailers(sysarg1= '', sysarg2= ''):              #  Get Movie Channel Trailers  
    
    global tr_config
    content = []                                              # function to get list of trailers for a given type

    page = 1
    count = 0    

    try:
        if not sysarg1.lower() in ['trailers', 'sync']:
            return
        if sysarg2.lower() not in ['now', 'up', 'top', 'pop']:
            print('\nThe valid trailers options are:  now, up, pop and top\n')
            return

        if sysarg2.lower() == 'now':
            mtype = 'now_playing'
        elif sysarg2.lower() == 'up':
            mtype = 'upcoming'
        elif sysarg2.lower() == 'top':
            mtype = 'top_rated'
        elif sysarg2.lower() == 'pop':
            mtype = 'popular'


        jresponse = urllib.request.urlopen(MOVIETRAILERS_URL_LIST.format(mtype, 'page=' + str(page)))
        json_obj = json.load(jresponse)
        #print(str(json_obj))
        jresponse.close()
    
        if json_obj.get('results'):
            print('Number of movies ' + mtype + ' found: ' + str(len(json_obj['results'])))
            for trailer in json_obj['results']:
                item = getTrailerDetails(trailer['id'])
                if item != None:
                    #print(item)
                    found = checkTrailer(item, mtype)            # Check if movie already in database
                    if count <= 4 and found == 0:
                        trresults = getTrailer(item['uri'])      # Fetch trailer
                        if trresults[0] == 0:                    # New trailer fetched
                            trname = checkFormats(trresults[1])  # Check if encoding needs changed
                            if trname != 0:                      # Trailer file reencoded                              
                                moveTrailers(trname)             # Move trailer to trailer folder
                                updateTempHist(item['tmdb_id'], trname, trresults[2], trresults[3])
                        #print(str(trresults))
                        count += 1
        #print(str(content))

    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting Movie Trailer Channel listing for: ' + mtype
        print(mgenlog)
        genLog(mgenlog)           


def getTrailerDetails(id):

    global MOVIETRAILERS_URL_BASE

    try:
        if MOVIETRAILERS_URL_BASE == '':
            # retrieve JSON content about themoviedb.org configuration so we can get its base URL
            file = urllib.request.urlopen(MOVIETRAILERS_URL_CONFIG)
            json_obj = json.load(file)
            file.close()
            if json_obj.get('images'):
                MOVIETRAILERS_URL_BASE = json_obj['images']['base_url']

        if MOVIETRAILERS_URL_BASE == '':                # error - could not get base url
            return None
        
        # retrieve JSON content about this movie and parse it
        file = urllib.request.urlopen(MOVIETRAILERS_URL_DETAILS.format(id))
        json_obj = json.load(file)
        file.close()

        item = {                                        # Movie information dictionary
                 'tmdb_id': id,
                 'title': '',
                 'uri': '',
                 'type': 'video',
                 'description': '',
                 'tagline': '',
                 'release_date': '',
                 'imdb_id': '',
                 'website': '',
                 'poster_uri': '',
                 'backdrop_uri': '',
                 'user_rating': 0,
                 'genre': '',
                 'production_company': '',
                 'content_rating': '',
                 'artist_actor': '',
                 'composer_director_creator': ''
               }
        
        # make sure it has a trailer video
        if json_obj.get('videos'):
            videos = json_obj['videos']
            if videos.get('results'):
                results = videos['results']
                for video in results:
                    if video.get('type') and video['type'] == 'Trailer' and video.get('key') \
                    and (video['site'] == 'YouTube' or video['site'] == None):
                        item['title'] = json_obj['title']
                        item['uri'] = MOVIETRAILERS_URL_YOUTUBE.format(video['key'])
                        if json_obj.get('overview'):
	                        item['description'] = json_obj['overview']
                        if json_obj.get('tagline'):
	                        item['tagline'] = json_obj['tagline']
                        if json_obj.get('release_date'):
                            item['release_date'] = json_obj['release_date']
                        if json_obj.get('imdb_id'):
                            item['imdb_id'] = json_obj['imdb_id']
                        if json_obj.get('homepage'):
                            item['website'] = json_obj['homepage']
                        if json_obj.get('poster_path'):
                            item['poster_uri'] = '{}{}{}'.format(MOVIETRAILERS_URL_BASE, MOVIETRAILERS_POSTER_SIZE,     \
                            json_obj['poster_path'])
                        if json_obj.get('backdrop_path'):
                            item['backdrop_uri'] = '{}{}{}'.format(MOVIETRAILERS_URL_BASE, MOVIETRAILERS_BACKDROP_SIZE, \
                            json_obj['backdrop_path'])
                        if json_obj.get('vote_average'):
                            item['user_rating'] = int((json_obj.get('vote_average') + 0.5)/2.0)
                        if json_obj.get('genres'):
                            genres = json_obj['genres']
                            for genre in genres:
                                item['genre'] = item['genre'] + genre['name'] + '##'
                            item['genre'] = item['genre'][:len(item['genre']) - 2]
                        if json_obj.get('production_companies'):
                            companies = json_obj['production_companies']
                            for company in companies:
                                item['production_company'] = item['production_company'] + company['name'] + '##'
                            item['production_company'] = item['production_company'][:len(item['production_company']) - 2]
                        if json_obj.get('releases'):
                            releases = json_obj['releases']
                            if releases.get('countries'):
                                countries = releases['countries']
                                for country in countries:
                                    if country['iso_3166_1'] == "US":
                                        item['content_rating'] = country['certification']
                                        break
                                if item['content_rating'] == None and len(countries) > 0:
                                    item['content_rating'] = country[0]['certification']
                        if json_obj.get('casts'):
                            casts = json_obj['casts']
                            if casts.get('cast'):
                                cast = casts['cast']
                                acount = 0
                                for actor in cast:
                                    item['artist_actor'] = item['artist_actor'] + actor['name'] + '##'
                                    acount += 1
                                    if acount > 9:
                                        item['artist_actor'] = item['artist_actor'][:len(item['artist_actor']) - 2]
                                        break
                                item['artist_actor'] = item['artist_actor'][:len(item['artist_actor']) - 2]
                            if casts.get('crew'):
                                crew = casts['crew']
                                #print(crew)
                                for member in crew:
                                    if member['job'] == 'Director':
                                        #item['composer_director_creator'].append(member['name'])
                                        item['composer_director_creator'] = item['composer_director_creator'] +   \
                                        member['name'] + '##'
                                        item['composer_director_creator'] = item['composer_director_creator']\
                                        [:len(item['composer_director_creator']) - 2]
                                        break
                                item['composer_director_creator'] = item['composer_director_creator']\
                                [:len(item['composer_director_creator']) - 2]
                        return item
        return None

    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting Movie Trailer Details for: ' + str(id)
        print(mgenlog)
        genLog(mgenlog)  


def checkTrailer(item, mtype):                             # Check if trailer / movie already in database

    try:
        db = openTrailerDB()
        found = -1

        trcurr = db.execute('SELECT trTitle from mTrailers WHERE tmdb_id = ?', (item['tmdb_id'],)) 
        trtuple = trcurr.fetchone()
        del trcurr

        if trtuple:
            print('Movie already in database, skipping: ' + item['title'])
            found = 1
        else:
            print('New movie found: ' + str(item['title']))
            currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.execute('INSERT into mTemp (dateAdded, tmdb_id, trailerUri, trType, trTitle, trOverview,  \
            trTagline, trRelease_date, trImdb_id, trWebsite, trPoster_path, trBackdrop_path, trUser_rating,  \
            trGenres, trProd_company, trContent_rating, trArtist_actor, trComposer ) values                  \
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (currTime, item['tmdb_id'],             \
            item['uri'], mtype, item['title'],  item['description'], item['tagline'], item['release_date'],  \
            item['imdb_id'], item['website'], item['poster_uri'], item['backdrop_uri'], item['user_rating'], \
            str(item['genre']), str(item['production_company']), item['content_rating'],                     \
            str(item['artist_actor']), str(item['composer_director_creator']) ))
            db.commit()    
            found = 0
        db.close()
        return found

    except Exception as e:
        print (e)
        mgenlog = 'There was an error checking trailer details for: ' + str(item['itle'])
        print(mgenlog)
        genLog(mgenlog)
        return found 


def genLog(mgenlog):                                        #  Write to logfile

        global tr_config
        logoutfile = tr_config['logoutfile']
        fileh = open(logoutfile, "a")                       #  open logf file
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        data = fileh.write(currTime + ' - ' + mgenlog + '\n')
        fileh.close()


def checkDatabase():

    try:
        global trailerdb

        db = openTrailerDB()

        db.execute('CREATE table IF NOT EXISTS mTrailers (dateAdded TEXT, tmdb_id INTEGER, trailerUri TEXT,    \
        localTrURL TEXT, mezzmoTrURL TEXT, trType TEXT, trTitle TEXT, trOverview TEXT, trTagline TEXT,         \
        trRelease_date TEXT, trImdb_id TEXT, trWebsite TEXT, trPoster_path TEXT, locPoster_path TEXT,          \
        mezPoster_path TEXT, trBackdrop_path TEXT, locBackdrop_path TEXT, mezBackdrop_path TEXT, trUser_rating \
        INTEGER, trGenres TEXT, trProd_company TEXT, trContent_rating TEXT, trArtist_actor TEXT, trComposer    \
        TEXT, lastchecked TEXT, tr_resol INTEGER, tr_size INTEGER, var1 TEXT, var2 TEXT, var3 TEXT, var4 TEXT)')

        db.execute('CREATE INDEX IF NOT EXISTS trailer_1 ON mTrailers (dateAdded)')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS trailer_2 ON mTrailers (trailerUri)')
        db.execute('CREATE INDEX IF NOT EXISTS trailer_3 ON mTrailers (trRelease_date)')
        db.execute('CREATE INDEX IF NOT EXISTS trailer_4 ON mTrailers (trType)')
        db.execute('CREATE INDEX IF NOT EXISTS trailer_5 ON mTrailers (tmdb_id)')

        db.execute('CREATE table IF NOT EXISTS mHistory (dateAdded TEXT, tmdb_id INTEGER, trailerUri TEXT,     \
        localTrURL TEXT, mezzmoTrURL TEXT, trType TEXT, trTitle TEXT, trOverview TEXT, trTagline TEXT,         \
        trRelease_date TEXT, trImdb_id TEXT, trWebsite TEXT, trPoster_path TEXT, locPoster_path TEXT,          \
        mezPoster_path TEXT, trBackdrop_path TEXT, locBackdrop_path TEXT, mezBackdrop_path TEXT, trUser_rating \
        INTEGER, trGenres TEXT, trProd_company TEXT, trContent_rating TEXT, trArtist_actor TEXT, trComposer    \
        TEXT, lastchecked TEXT, tr_resol INTEGER, tr_size INTEGER, var1 TEXT, var2 TEXT, var3 TEXT, var4 TEXT)')

        db.execute('CREATE INDEX IF NOT EXISTS htrailer_1 ON mHistory (dateAdded)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_2 ON mHistory (trailerUri)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_3 ON mHistory (trRelease_date)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_4 ON mHistory (trType)')
        db.execute('CREATE INDEX IF NOT EXISTS htrailer_5 ON mHistory (tmdb_id)')

        db.execute('CREATE table IF NOT EXISTS mTemp (dateAdded TEXT, tmdb_id INTEGER, trailerUri TEXT,        \
        localTrURL TEXT, mezzmoTrURL TEXT, trType TEXT, trTitle TEXT, trOverview TEXT, trTagline TEXT,         \
        trRelease_date TEXT, trImdb_id TEXT, trWebsite TEXT, trPoster_path TEXT, locPoster_path TEXT,          \
        mezPoster_path TEXT, trBackdrop_path TEXT, locBackdrop_path TEXT, mezBackdrop_path TEXT, trUser_rating \
        INTEGER, trGenres TEXT, trProd_company TEXT, trContent_rating TEXT, trArtist_actor TEXT, trComposer    \
        TEXT, lastchecked TEXT, tr_resol INTEGER, tr_size INTEGER, var1 TEXT, var2 TEXT, var3 TEXT, var4 TEXT)')

        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_1 ON mTemp (dateAdded)')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS tetrailer_2 ON mTemp (trailerUri)')
        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_3 ON mTemp (trRelease_date)')
        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_4 ON mTemp (trType)')
        db.execute('CREATE INDEX IF NOT EXISTS tetrailer_5 ON mTemp (tmdb_id)')
        db.execute('DELETE FROM mTemp')                                    # Clear temp table on startup

        db.commit()
        db.close()
 
        mgenlog = "Mezzmo Movie Trailer Channel database check completed."
        print (mgenlog)
        genLog(mgenlog)

    except Exception as e:
        print (e)
        mgenlog = "There was a problem verifying the trailer database file: " + trailerdb
        print(mgenlog)
        exit()   


def updateTempHist(tmdb_id, trname, trsize, trres):                       # Update temp table

    try:
        global tr_config, trailerdb                                       # Get config information
        db = openTrailerDB()

        newmtrailer = tr_config['mtrailerloc'] + 'trailers\\' + trname    # Mezzmo trailer name
        newctrailer = tr_config['ltrailerloc'] + 'trailers\\' + trname    # Local trailer name 
        resolution =  int(trres.strip('p'))                               # Resolution as number 
        db.execute('UPDATE mTemp SET LocalTrURL=?, mezzmoTrURL=?, tr_resol=?, tr_size=? WHERE tmdb_id=?', \
        (newctrailer, newmtrailer, resolution, trsize, tmdb_id,)) 
        db.commit()
        db.execute('INSERT INTO mTrailers SELECT * FROM mTemp WHERE tmdb_id=?', (tmdb_id,))
        db.execute('INSERT INTO mHistory SELECT * FROM mTemp WHERE tmdb_id=?', (tmdb_id,))
        db.commit()
        db.execute('DELETE FROM mTemp WHERE tmdb_id=?', (tmdb_id,))
        db.commit()

    except Exception as e:
        print (e)
        mgenlog = "There was a problem updating the temp table: " + trailerdb
        print(mgenlog)
        genLog(mgenlog)  


def checkFormats(trailfile):                                             # Check / modify output formats

    try:

        global tr_config
        tformat = tr_config['tformat']

        if tformat in trailfile and 'mp4' in tformat:                            # No adjustment needed
            mgenlog = "Format conversion not required for: " + trailfile
            print(mgenlog)
            genLog(mgenlog)        
            return trailfile
 
        new_name = trailfile.replace('.mp4', '.mkv')                              # New trailer name

        curr_trailer = 'temp\\' + trailfile                                       # Current trailer path and file name
        new_trailer = 'temp\\' +  new_name                                        # Converted trailer path and file name
        mgenlog = "Format conversion to " + tformat + ' beginning for trailer ' + trailfile
        print(mgenlog)
        genLog(mgenlog)
        #print('Format file names: ' + trailer_name + '  ' + convert_name)
        frcommand = 'ffmpeg.exe -i ' +  curr_trailer + ' -vcodec copy -acodec copy ' + new_trailer + ' >nul 2>nul'
        #print(frcommand)
        os.system(frcommand)
        #print('Trailer file names: ' + curr_trailer + '  ' + new_trailer)
        delcommand = "del " + '"' + curr_trailer + '"'                           # Remove old trailer from disk    
        #print(delcommand)
        os.system(delcommand)
        mgenlog = "Format conversion successful to: " + new_name
        print(mgenlog)
        genLog(mgenlog)
        return new_name

    except Exception as e:
        print (e)
        mgenlog = "There was a problem adjusting the output formats."
        print(mgenlog)
        genLog(mgenlog)  
        return 0


def openTrailerDB():

    global trailerdb
    
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                       
    db = sqlite.connect(trailerdb)

    return db


def getTrailer(trailer, imdbtitle = ''):                   # Download You Tube \ IMDB trailers

    try:
        global tr_config
        maxres = int(tr_config['maxres'])                  # Get max resolution
        tr_cmd = fmt = ''
        formats = str(getFormats(trailer, imdbtitle))     # Get available trailer formats
        #print('Formats result is: ' + str(formats))
        #print('Trailer info: ' + imdbtitle + ' ' + str(maxres)) 
        if 'Error' in formats:                             # You Tube / IMDB error getting formats file
            return 'Error'
        elif 'imdb' in imdbtitle and '1080p' in formats and maxres >= 1080:         # 1080 available for IMDB   
            tr_cmd = "yt-dlp.exe -f 1080p -q --check-formats --windows-filenames " + trailer
            fmt = '1080p' 
        elif 'imdb' in imdbtitle and '720p' in formats and maxres >= 720:           # 720 available for IMDB   
            tr_cmd = "yt-dlp.exe -f 720p -q --check-formats --windows-filenames " + trailer
            fmt = '720p' 
        elif 'imdb' in imdbtitle and '480p' in formats and maxres >= 480:           # 480 available for IMDB   
            tr_cmd = "yt-dlp.exe -f 480p -q --check-formats --windows-filenames " + trailer
            fmt = '480p' 
        elif 'imdb' in imdbtitle and 'SD' in formats:                               # SD available for IMDB   
            tr_cmd = "yt-dlp.exe -f SD -q --check-formats --windows-filenames " + trailer
            fmt = '360p'        
        elif '137 mp4' in formats and '140 m4a' in formats and maxres >= 1080:      # 1080P available
            tr_cmd = "yt-dlp.exe -f 137+140 -q --check-formats --restrict-filenames " + trailer
            fmt = '1080p' 
        elif '137 mp4' in formats and '139 m4a' in formats  and maxres >= 1080:     # 1080P available
            tr_cmd = "yt-dlp.exe -f 137+139 -q --check-formats --restrict-filenames " + trailer
            fmt = '1080p' 
        elif '22  mp4' in formats and maxres >= 720:                                # 720P available
            tr_cmd = "yt-dlp.exe -f 22 -q --restrict-filenames " + trailer
            fmt = '720p' 
        elif  '135 mp4' in formats and '140 m4a' in formats and maxres >= 480:      # 480P available
            tr_cmd = "yt-dlp.exe -f 135+140 -q --check-formats --restrict-filenames " + trailer
            fmt = '480p' 
        elif  '135 mp4' in formats and '140 m4a' in formats and maxres >= 480:      # 480P available
            tr_cmd = "yt-dlp.exe -f 135+139 -q --check-formats --restrict-filenames " + trailer
            fmt = '480p' 
        elif '18  mp4' in formats:                                                  # 360P available
            tr_cmd = "yt-dlp.exe -f 18 -q --restrict-filenames " + trailer
            fmt = '360p'
        else:
            return 'Error'                                 # No acceptable format available 
        
        #print (tr_cmd)

        if 'imdb' in imdbtitle:
            tsource = 'IMDB'
        else:
            tsource = 'You Tube'
        mgenlog = 'Attempting fetch ' + tsource + ' trailer at: ' + fmt + ' - ' + trailer
        genLog(mgenlog)
        print(mgenlog)

        fetch_result = subprocess.call(tr_cmd, shell=True)
        if fetch_result == 0:
            mgenlog = 'Fetched ' + tsource + ' trailer at: ' + fmt + ' - ' + trailer
            genLog(mgenlog)
            print(mgenlog)
            trfile = renameFiles(imdbtitle)                  # Cleanup trailer name and move to temp folder
            return [fetch_result, trfile[0], trfile[1], fmt]
                                                             # Return trailer file info and status
                                                             # trfile[0] = new trailer file name
                                                             # trfile[1] = new trailer file size
        elif fetch_result == 1:
            mgenlog = "A Youtube / IMDB fetching error occured for: " + trailer
            print(mgenlog)
            genLog(mgenlog)
            return [fetch_result, '0', '0', '0']
    
    except Exception as e:
        print (e)
        mgenlog = 'There was a problem getting the formats information'
        genLog(mgenlog)
        print(mgenlog)


def getFormats(trailer,imdbtitle = ''):             # Get available You Tube Trailer formats

    try:
        global tr_config

        formats = []
        tr_cmd = "yt-dlp.exe -F " + trailer + " > output.txt"
        fetch_result = subprocess.call(tr_cmd, shell=True)

        if fetch_result == 0:
            fileh = open("output.txt")             # open formats file
            data = fileh.readlines()            
            for x in range(6, len(data)):
                if 'imdb' in imdbtitle:
                    formats.append(data[x][:5].strip())    # List of available formats
                else:
                    formats.append(data[x][:7].strip())    # List of available formats
            fileh.close()  
            return formats
        else:
            return 'Error'

    except Exception as e:
        print (e)
        mgenlog = "There was a problem getting the trailer formats: " + trailer
        print(mgenlog)
        genLog(mgenlog) 


def getDuration(trailerfile, checktr=''):         # Get trailer duration from ffmpeg

    try:

        global tr_config
        maxdur = int(tr_config['maxdur'])         # Get maximum duration to keep

        if '&' in trailerfile:                    # Invalid name for ffpmeg processing
            mgenlog = 'Trailer file name bad name: ' + trailerfile
            genLog(mgenlog)
            print(mgenlog)
            return (1,1,1)
        dur_cmd = "ffmpeg -i " + trailerfile + " > output1.txt 2>&1"
        fetch_result = subprocess.call(dur_cmd, shell=True)
        #print('Fetch result is: ' + str(fetch_result) + ' - ' + trailerfile)
        fileh = open("output1.txt", encoding='utf-8', errors='ignore') # open ffmpeg output file
        data = fileh.readlines()                   # Read file into data
        fileh.close()      
        found = 0
        trfps_text = '0'
        for x in range(len(data)): 
            fpos = data[x].find('Duration')
            rpos = data[x].find('Video')
            if fpos > 0 and found == 0:            # Found duration
                dur_text = data[x][fpos+10:fpos+19] + '00'
                #print(str(dur_text))
                found += 1
                duration = getSeconds(dur_text)    # Convert to seconds
            if rpos > 0 and found == 1:                
                dataa = data[x].split('x')
                if '.mp4' in trailerfile:
                    vres_text = dataa[2][:4].strip(',').strip()
                    hres_text = dataa[1][len(dataa[1])-4:len(dataa[1])].strip()
                elif '.mkv' in trailerfile:
                    vres_text = dataa[1][:4].strip(',').strip()
                    hres_text = dataa[0][len(dataa[0])-4:len(dataa[0])].strip()
                found += 1       
                #print(hres_text + ' ' + vres_text + ' ' + trailerfile)
                fpspos = data[x].rfind('fps')      # Find fps
                if fpspos > 0:
                    trfps_text = data[x][fpspos-6:fpspos-1].strip()
                    if 's' in trfps_text:         # Whole number frame rate
                       tempfps = trfps_text.split(' ')[1].strip()
                       trfps_text = tempfps
                    if trfps_text == '23.98':     # Adjust for You Tube format rounding
                        trfps_text = '23.976'
                    #print('The frame rate is: ' + trfps_text)
                if int(vres_text) > 720 or int(hres_text) > 1280:
                    vres_text = 1080
                elif  int(vres_text) > 480 or int(hres_text) > 720:
                    vres_text = 720
                elif  int(vres_text) > 360 or int(hres_text) > 480:
                    vres_text = 480
                else:
                    vres_text = 360
            #print('Length of file is: ' + str(len(data)) + ' ' + str(x) + ' ' + str(rpos) + ' ' + str(fpos) + ' ' + trailerfile)
        if trfps_text != '0' and maxdur > duration:    # Check for frame rate and audio adjustments
            trfps_text = convertTrailer(trailerfile, trfps_text, checktr)             

        if found == 0: 
            duration = 0
            hres_text = '0'
            vres_text = '0'
            trfps_text = '0'
        elif found == 1:
            hres_text = '0'
            vres_text = '0'
            trfps_text = '0'        
        return (int(hres_text), int(vres_text), duration, trfps_text)
        #print(str(duration))

    except Exception as e:
        print (e)
        mgenlog = 'There was a problem calculating the duration for: ' + trailerfile
        genLog(mgenlog)
        print(mgenlog)
        return (0,0,0)


def convertTrailer(trailerfile, trfps, checktr=''):  # Adjust frame rate and audio level, if needed

    try:
        if 'check' in checktr.lower() or not os.path.isfile(trailerfile): # Check or trailer deleted
            return trfps           
        global tr_config
        trfrate = tr_config['trfrate']
        trback = tr_config['trback']
        ltrailerloc = tr_config['ltrailerloc']
        audiolvl = tr_config['audiolvl']        
        hwenc = tr_config['hwenc']

        if trfrate == '0' and audiolvl == '100':                            # Frame rate and audio changes disabled
            return trfps
        elif (trfrate == trfps) and audiolvl == '100':                      # No changes needed
            mgenlog = "No adjustments needed for: " + trailerfile
            genLog(mgenlog)
            print(mgenlog)
            return trfps       
        elif (trfrate != '0' and trfrate != trfps) or audiolvl == '100':    # Adjust frame rate only
            #print('Frame rate mismatch for: ' + trfrate + ' ' + trfps + ' ' + trailerfile)
            if 'yes' in trback.lower():
                backuploc = os.path.join(ltrailerloc, "backup")
                command = "copy " + trailerfile + " " + backuploc + " >nul 2>nul"
                os.system(command)                  # Rename trailer file to trimmed newname                
                mgenlog = 'Backup trailer successful: ' + trailerfile
                genLog(mgenlog)
                print(mgenlog)
            if hwenc.lower() in ['nevc']:                                   # nVidia HW encoding
                frcommand = "ffmpeg -i " + trailerfile + " -c:v h264_nvenc -filter:v fps=" + trfrate + " converted.mp4 >nul 2>nul"
            else:
                frcommand = "ffmpeg -i " + trailerfile + " -filter:v fps=" + trfrate + " converted.mp4 >nul 2>nul"
            #print(frcommand)
            mgenlog = "Ajusting frame rate to " + trfrate + " for: " + trailerfile
        elif trfrate != '0' and trfrate != trfps and audiolvl != '100':    # Adjust frame rate and audio
            if 'yes' in trback.lower():
                backuploc = os.path.join(ltrailerloc, "backup")
                command = "copy " + trailerfile + " " + backuploc + " >nul 2>nul"
                os.system(command)                  # Rename trailer file to trimmed newname                
                mgenlog = 'Backup trailer successful: ' + trailerfile
                genLog(mgenlog)
                print(mgenlog)
            volvl = str(float(audiolvl)/100)
            if hwenc.lower() in ['nevc']:                                   # nVidia HW encoding
                frcommand = "ffmpeg -i " + trailerfile + " -c:v h264_nvenc -filter:v fps=" + trfrate +    \
                "-filter:a volume=" + volvl + " converted.mp4 >nul 2>nul"
            else:
                frcommand = "ffmpeg -i " + trailerfile + " -filter:v fps=" + trfrate + "-filter:a volume=" + volvl \
                + " converted.mp4 >nul 2>nul"
            #print(frcommand)
            mgenlog = "Ajusting frame rate and audio to " + trfrate + ":" + audiolvl + " for: " + trailerfile
        elif (trfrate == '0' or trfrate == trfps) and audiolvl != '100':    # Adjust audio only
            if 'yes' in trback.lower():
                backuploc = os.path.join(ltrailerloc, "backup")
                command = "copy " + trailerfile + " " + backuploc + " >nul 2>nul"
                os.system(command)                  # Rename trailer file to trimmed newname                
                mgenlog = 'Backup trailer successful: ' + trailerfile
                genLog(mgenlog)
                print(mgenlog)
            volvl = str(float(audiolvl)/100)
            if hwenc.lower() in ['nevc']:                                   # nVidia HW encoding
                frcommand = "ffmpeg -i " + trailerfile +  " -c:v h264_nvenc -filter:a volume=" \
                + volvl + " converted.mp4 >nul 2>nul"
            else:
                frcommand = "ffmpeg -i " + trailerfile +  " -filter:a volume=" + volvl \
                + " converted.mp4 >nul 2>nul"
            #print(frcommand)
            mgenlog = "Ajusting audio volume to " + audiolvl + " for: " + trailerfile

        genLog(mgenlog)
        print(mgenlog)
        genLog(frcommand)
        os.system(frcommand)
        if ltrailerloc not in trailerfile:
            copytrailer = os.path.join(ltrailerloc, trailerfile)
        else:
            copytrailer = trailerfile
        mvcommand =  "copy converted.mp4 " + copytrailer + " /y >nul 2>nul"  
        genLog(mvcommand)
        os.system(mvcommand)

        command = 'del *.mp4 /q >nul 2>nul'          #  Remove old converted files
        os.system(command)                           #  Clear converted files
        return trfrate

    except Exception as e:
        print (e)
        mgenlog = "There was a problem converting the trailer: " + trailerurl
        print(mgenlog)
        genLog(mgenlog) 



def getSeconds(dur_text):                          # Convert time string to secs

    try:
        x = time.strptime(dur_text.split(',')[0],'%H:%M:%S.00')
        td = timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec)
        seconds = int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)
        if seconds == None:
            seconds = 0
        return seconds

    except Exception as e:
        print (e)
        mgenlog = "There was a problem calculating seconds: " + str(dur_text)
        print(mgenlog)
        genLog(mgenlog) 


def checkFolders():                                # Check folders and files

    try:
        global tr_config, trailerdb
        trailerloc = tr_config['ltrailerloc']
        if not os.path.exists('temp'):             #  Check temp files location
            os.makedirs('temp')
        command = 'del temp\*.mp4 >nul 2>nul'      #  Delete temp files if exist 
        os.system(command)                         #  Clear temp files
        command = 'del *.mp4 >nul 2>nul'           #  Remove old converted files
        os.system(command)                         #  Clear converted files
        if not os.path.exists(trailerloc):         #  Check trailer files location
            mgenlog = 'Local trailer file location does not exist.  Mezzmo Movie Trailer Channel exiting.'  
            genLog(mgenlog)
            print(mgenlog)            
            sys.exit()
        ltrailersloc = os.path.join(trailerloc, "trailers")        
        if not os.path.exists(ltrailersloc):       #  Check trailer files location       
            os.makedirs(ltrailersloc)
            mgenlog = 'Trailers folder location did not exist.  Trailers folder created.'  
            genLog(mgenlog)
            print(mgenlog)
        trailerdb = os.path.join(trailerloc, "trailers\\mezzmo_trailers.db")                
        backuploc = os.path.join(trailerloc, "trailers\\backup")
        if not os.path.exists(backuploc):          #  Check trailers backup files location
            os.makedirs(backuploc)
            mgenlog = 'Trailer backup file location did not exist.  Backup folder created.'  
            genLog(mgenlog)
            print(mgenlog)
        ltrailersloc = os.path.join(trailerloc, "trailers\\artwork")        
        if not os.path.exists(ltrailersloc):       #  Check artwork files location       
            os.makedirs(ltrailersloc)
            mgenlog = 'Trailers artwork folder location did not exist.  Trailers artwork folder created.'  
            genLog(mgenlog)
            print(mgenlog)    
        if not os.path.isfile('./ffmpeg.exe'):
            mgenlog = 'ffmpeg.exe not found in Mezzmo Movie Channel Trailer folder.  Mezzmo Movie Trailer Channel exiting.'
            genLog(mgenlog)
            print(mgenlog)            
            sys.exit()
        if not os.path.isfile('./yt-dlp.exe'):
            mgenlog = 'ytp-dl.exe not found in Mezzmo Movie Channel Trailer folder.  Mezzmo Movie Trailer Channel exiting.'
            genLog(mgenlog)
            print(mgenlog)            
            sys.exit()
  

    except Exception as e:
        print (e)
        mgenlog = 'There was a problem checking folders'
        genLog(mgenlog)
        print(mgenlog)    


def checkFiles(sysarg1 = '', sysarg2 = '', ccount = 0): # Check size, resolution and duration for trailers

    try:
        if sysarg1.lower() not in 'check':
            return
        elif len(sysarg2.lower()) > 0 and sysarg2.lower() not in ['new']:
            print('\nThe valid media check option is:  new\n')
            return

        global tr_config
        trailerloc = tr_config['ltrailerloc']         # Get locatal path to trailer lcoation
        maxcheck = tr_config['maxcheck']              # Number of movies to check
        if ccount > 0:
            maxcheck = ccount
   
        db = openTrailerDB()

        if 'new' in sysarg2.lower():
            dbcurr = db.execute('SELECT extras_File from mTrailers WHERE extras_File NOT LIKE ?    \
            ORDER BY lastchecked ASC LIMIT ?', ('%www.youtube%', maxcheck,))
        else: 
            dbcurr = db.execute('SELECT extras_File from mTrailers WHERE extras_File NOT LIKE ?    \
            AND (trDuration=? or trDuration is NULL or tr_resol is NULL or tr_size=? OR tr_size is \
            NULL) ORDER BY extras_FileID, extras_File LIMIT ?', ('%www.youtube%', 0, 0, maxcheck,))      
        dbtuple = dbcurr.fetchall()                   # Get entries with missing info

        if len(dbtuple) == 0:                         # All files updated
            mgenlog = 'There were no trailers found which need checking.'
            genLog(mgenlog)
            print(mgenlog)
            db.close 
            return

        #print('Length of tuples is: ' + str(len(dbtuple)) + ' ' + str(maxcheck)) 
        #print(str(dbtuple)) 

        checkcount = 0
        if ccount == 0:                              # Display start message if not called by checkFinish
            mgenlog = 'Checking trailer files beginning.'
            genLog(mgenlog)
            print(mgenlog)
        for fname in range(len(dbtuple)):
            lpos = dbtuple[fname][0].rfind('\\')     # Slice file name 
            fpart = dbtuple[fname][0][lpos+1:]       # Get file name portion
            newname = trailerloc + fpart             # Local path to trailer file
            currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            target = '%' + fpart                     # Find trailer by like name 
            if os.path.isfile(newname ):             # Verify trailerfile exists
                # print('File name is: ' +  newname)
                fdur = getDuration(newname, 'check')
                filestat = os.stat(newname)
                fsize = filestat.st_size             # Get trailer size in bytes
                #print(str(fdur[1]) + ' ' + str(fdur[2]) + ' ' + str(fsize) + ' ' + newname)
                if fdur[0] == 1 and fdur[1] == 1 and fdur[2] == 1:
                    db.execute('UPDATE mTrailers SET lastchecked=?, tr_resol=?, tr_size=?, trStatus=?,     \
                    trDuration=? WHERE extras_File LIKE ?', (currTime, fdur[1], fsize, 'Invalid', fdur[2], \
                    target,))
                else:
                    db.execute('UPDATE mTrailers SET lastchecked=?, tr_resol=?, tr_size=?, trStatus=?, \
                    trDuration=?, var1=? WHERE extras_File LIKE ?', (currTime, fdur[1], fsize, 'Yes',  \
                    fdur[2], fdur[3], target,))
            else:
                db.execute('UPDATE mTrailers SET lastchecked=?, tr_resol=?, tr_size=?, trStatus=?,     \
                trDuration=? WHERE extras_File LIKE ?', (currTime, 2, 2, 'Missing', 2, target,))
                mgenlog = 'Trailer file not found for duration checking: ' + newname
                genLog(mgenlog)
            checkcount += 1
            if checkcount % 100 == 0:
                print('Files checked: ' + str(checkcount))
            if checkcount % 500 == 0:
                db.commit()             
        db.commit()
        db.close()
        if ccount == 0:                               # Display ending message if not called by checkFinish
            mgenlog = 'Checking trailer files completed. ' + str(checkcount) + ' files checked'  
            genLog(mgenlog)
            print(mgenlog)

        return

    except Exception as e:
        print (e)
        mgenlog = "There was a problem checking files: "
        print(mgenlog)
        genLog(mgenlog) 


def renameFiles(imdbtitle = ''):                    # Rename trailer file names / move to temp folder

        global tr_config

        listOfFiles = os.listdir('.')
        pattern = "*.mp4"
        for x in listOfFiles:
            if fnmatch.fnmatch(x, pattern):
                #print (x)
                filestat = os.stat(x)
                fsize = filestat.st_size            # Get trailer size in bytes
                rpos = x.find('[')
                newname = x[:rpos - 1]
                # Remove file name characters which cannot be reencoded
                newname = newname.replace(' ' ,'_')
                imdbtitle = imdbtitle.replace(' ' ,'_').replace(',' ,'_')
                newname = re.sub(r'[^\x61-\x7a,\x5f,^\x41-\x5a,^\x30-\x39]',r'', newname) 
                imdbtitle = re.sub(r'[^\x61-\x7a,\x5f,^\x41-\x5a,^\x30-\x39]',r'', imdbtitle)  
                if rpos >= 10:                    # Trim extra characters
                    newname = newname[:rpos - 1]  + ".mp4"
                elif len(newname) < 10:
                    tempname = ''.join(random.choices(string.ascii_letters, k=12))
                    newname = "trailer_" + tempname + ".mp4"
                command = "rename " + '"' + x + '" "' + newname + '"'
                os.system(command)                  # Rename trailer file to trimmed newname
                command = "move " + '"' + newname + '" temp >nul 2>nul'
                #print('The file name is: ' + newname + ' ' + str(rpos))
                os.system(command)                  # Move to temp folder till done fetching all
                return [newname, str(fsize)]        # Return new trailer name and info


def moveTrailers(trfile):                           # Move trailers to trailer location

    try:
        global tr_config                            # Get locatal path to trailer lcoation
        trailerloc = tr_config['ltrailerloc'] + 'trailers'

        command = "move temp\\" + trfile + " " + trailerloc + " >nul 2>nul"
        #print(command)
        os.system(command)
    except Exception as e:
        print (e)
        mgenlog = 'There was a problem moving trailers to the trailer folder.'
        genLog(mgenlog)
        print(mgenlog)


def checkCsv(sysarg1 = '', sysarg2 = ''):           # Generate CSV files

        if len(sysarg1) == 0 or sysarg1.lower() not in 'csv':
            return
        elif sysarg2.lower() not in ['trailers', 'history']:
            print('\nThe valid csv options are:  trailers or history\n')
            return
  
        mgenlog = 'CSV file export beginning for - ' + sysarg1
        genLog(mgenlog)
            
        db = openTrailerDB()
        fpart = datetime.now().strftime('%H%M%S')
        if sysarg2.lower() == 'trailer':
            curm = db.execute('SELECT * FROM mTrailers ORDER BY dateAdded')
            filename = 'meztrailers_' + fpart + '.csv'
        elif sysarg2.lower() == 'history':
            curm = db.execute('SELECT * FROM mHistory')
            filename = 'mezhistory_' + fpart + '.csv'          

        headers = [i[0] for i in curm.description]      
        recs = curm.fetchall()
        writeCSV(filename, headers, recs)
        del curm
        db.close()
        mgenlog = 'CSV file export completed to - ' + filename
        genLog(mgenlog)
        print(mgenlog)


def writeCSV(filename, headers, recs):

    try:
        csvFile = csv.writer(open(filename, 'w', encoding = 'utf-8'),
                         delimiter=',', lineterminator='\n',
                         quoting=csv.QUOTE_ALL)
        csvFile.writerow(headers)     # Add the headers and data to the CSV file.
        for row in recs:
            recsencode = []
            for item in range(len(row)):
                if isinstance(row[item], int) or isinstance(row[item], float):  # Convert to strings
                    recitem = str(row[item])
                else:
                    recitem = row[item]
                recsencode.append(recitem) 
            csvFile.writerow(recsencode)               

    except Exception as e:
        print (e)
        mgenlog = 'An error occurred creating the CSV file.'
        genLog(mgenlog)
        pring(mgenlog)


def checkFinish(sysarg1, sysarg2):                           # Successfully finished

    if sysarg1.lower() in ['trailer']:                       # Sync trailer db to Mezzmo
        getMezzmoTrailers('sync')
        checkFiles('check', '', gdcount)      
    mgenlog = 'Mezzmo Trailer Checker completed successfully.'
    print(mgenlog)
    genLog(mgenlog)
    if sysarg1.lower() in ['trailer', 'stats']:   
        displayStats(sysarg1, sysarg2)


def getTotals():                                             # Gets checked download totals

    try:
        db = openTrailerDB()
        currDate = datetime.now().strftime('%Y-%m-%d')
        dateMatch = currDate + '%'
        dqcurr = db.execute('SELECT count (*) from mHistory WHERE lastchecked LIKE ?', (dateMatch,))
        daytuple = dqcurr.fetchone()
        dqcurr = db.execute('SELECT count (*) from mHistory')
        htottuple = dqcurr.fetchone()
        db.close()
        return [daytuple[0], htottuple[0]]

    except Exception as e:
        print (e)
        mgenlog = 'An error occurred generating totals.'
        genLog(mgenlog)
        print(mgenlog)


def makeBackups():                                   # Make database backups

    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
    
    try:
        if len(sysarg1) == 0 or sysarg1.lower() not in 'backup':
            return

        global tr_config                            # Get locatal path to trailer lcoation
        trailerloc = tr_config['ltrailerloc']

        DB = trailerloc + 'trailers\\backup\\mezzmo_trailers_' +             \
        datetime.now().strftime('%m%d%Y-%H%M%S') + '.db'
        #print(DB)
        dbout = sqlite.connect(DB)
        dbin = openTrailerDB()

        with dbout:
            dbin.backup(dbout, pages=100)
        dbout.close()
        dbin.close()
        mgenlog = 'Mezzmo Trailer Checker backup successful: ' + str(DB)
        genLog(mgenlog)
        print(mgenlog) 

    except Exception as e:
        print (e)
        mgenlog = 'An error occurred creating a Mezzmo Trailer Checker backup.'
        genLog(mgenlog)
        print(mgenlog)      

                                  

def cleanTrailers(sysarg1 = '', sysarg2 = '', sysarg3 = ''): # Clean show movie trailers from DB


        if sysarg1.lower() not in ['clean']:
            return
        elif sysarg2.lower() not in ['now', 'up', 'top', 'pop', 'all']: 
            return

        if sysarg2.lower() == 'now':
            mtype = 'now_playing'
        elif sysarg2.lower() == 'up':
            mtype = 'upcoming'
        elif sysarg2.lower() == 'top':
            mtype = 'top_rated'
        elif sysarg2.lower() == 'pop':
            mtype = 'popular'
        elif sysarg2.lower() == 'all':
            mtype = 'all'

        global tr_config
        ltrailerloc = tr_config['ltrailerloc']       # Get local path to trailer lcoation
        mtrailerloc = tr_config['mtrailerloc']       # Get Mezzmo path to trailer lcoation

        if sysarg2.lower() not in ['files']:
            db = openTrailerDB()
            if mtype == 'all':
                dbcurr = db.execute('SELECT tmdb_id, localTrURL, trTitle from mTrailers ')            
            else:
                dbcurr = db.execute('SELECT tmdb_id, localTrURL, trTitle from mTrailers    \
                WHERE trType=? ', (mtype,))
            dbtuples = dbcurr.fetchall() 
            if len(dbtuples) == 0:
                mgenlog = 'No trailers found with movie type: ' + str(mtype)
                print('\n')
                genLog(mgenlog)
                print(mgenlog)
                db.close()
                return
            else:
                print('\nNumber of movie trailers to clean: ' + str(len(dbtuples)) + '\n')
                for n in range(len(dbtuples)):
                    print(str(dbtuples[n][2]))
                choice = input('\nDo you want to delete these movie trailers (Y/N) ?  \n')
                if 'n' in choice.lower():
                    mgenlog = 'Movie trailers will not be cleaned with status: ' + str(mtype)
                    genLog(mgenlog)
                    print(mgenlog)                
                    db.close()
                    return 
                else:
                    delcount = 0
                    for x in range(len(dbtuples)):
                        command = "del " + dbtuples[x][1] + " >nul 2>nul"
                        os.system(command)                    
                        db.execute('DELETE FROM mTrailers WHERE tmdb_id=?', (dbtuples[x][0],))
                        delcount += 1
                        mgenlog = 'Successfully cleaned movie trailer: ' + dbtuples[x][2]
                        genLog(mgenlog)
                        print(mgenlog)   
                    db.commit()
                    db.close()
                    print("\n")
                    mgenlog = 'Number of movie trailers successfully cleaned: ' + str(delcount)
                    genLog(mgenlog)
                    print(mgenlog)  


def displayStats(sysarg1, ssyarg2 = ''):              # Display statistics    

    try:
        global totcount, bdcount, gdcount, mvcount, skipcount, trlcount, longcount
        global tr_config
        trailerloc = tr_config['ltrailerloc']
        mtrailerloc = tr_config['mtrailerloc']

        print ('\n\n\t ************  Mezzmo Trailer Checker Stats  *************\n')

        daytotal, grandtotal =  getTotals()

        if sysarg1.lower() in ['trailer']:
            print ("Mezzmo movies checked: \t\t\t" + str(totcount))
            print ("Mezzmo movies skipped: \t\t\t" + str(skipcount))
            print ("Mezzmo trailers fetched: \t\t" + str(trlcount))
            print ("Mezzmo trailers bad trailer: \t\t" + str(bdcount))
            print ("Mezzmo trailers too long: \t\t" + str(longcount))
            print ("Mezzmo trailers downlaoded: \t\t" + str(gdcount))
            print ("\nTrailers fetched today: \t\t" + str(daytotal))
            print ("Trailers fetched total: \t\t" + str(grandtotal))

        elif sysarg1.lower() in ['stats'] and not sysarg2.lower() in ['frame']:
            db = openTrailerDB()
            dqcurr = db.execute('SELECT count (*) from mTrailers')
            totaltuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE extras_File NOT LIKE ?', ('%www.youtube%',))
            localtuple = dqcurr.fetchone()
            target = "%" + mtrailerloc + "imdb%"
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE extras_File LIKE ?', (target,))
            imdbtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE extras_File LIKE ?', ('%www.youtube%',))
            youtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE trstatus LIKE ?', ('%Bad%',))
            badtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE trstatus LIKE ?', ('%Long%',))
            longtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE trstatus LIKE ?', ('%Yes%',))
            chktuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE trstatus LIKE ?', ('%Invalid%',))
            invtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE trstatus LIKE ?', ('%Missing%',))
            mistuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE trstatus IS NULL')
            nulltuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (DISTINCT extras_FileID) from mTrailers')
            movtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (DISTINCT extras_FileID) from mTrailers WHERE trStatus IS NULL')
            nullmvtuple = dqcurr.fetchone()
            dqcurr = db.execute('SELECT COUNT (DISTINCT extras_FileID) from mTrailers WHERE extras_File LIKE ?',
            (mtrailerloc + "%",))
            localmovie = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE extras_File LIKE ?', ('%.mp4',))
            mp4format = dqcurr.fetchone()
            dqcurr = db.execute('SELECT count (*) from mTrailers WHERE extras_File LIKE ?', ('%.mkv',))
            mkvformat = dqcurr.fetchone()
            #noTrailer()                                # Update Temp table for no trailer analysis
            dqcurr = db.execute('select count(extras_FileID) FROM mTemp WHERE extras_FileID NOT IN     \
            (SELECT extras_FileID FROM mTrailers) ORDER BY extras_FileID')
            notrailer = dqcurr.fetchone()

            db.close()
            foldersize = filecount = bfoldersize = bstoragegb = 0
            for element in os.scandir(trailerloc):
                foldersize+=os.stat(element).st_size
                filecount += 1
            storagegb = round((float(foldersize) / 1073741824),2)
            trbackfolder = os.path.join(trailerloc, 'backup')
            if os.path.exists(trbackfolder):
                for belement in os.scandir(trbackfolder):
                    bfoldersize+=os.stat(belement).st_size            
                bstoragegb = round((float(bfoldersize) / 1073741824),2)
            avgsize = round((float(foldersize) / 1048576 / filecount),2) 
            print ("\nTrailers fetched today: \t\t" + str(daytotal))
            print ("Trailers fetched total: \t\t" + str(grandtotal))
            print ("\nTotal Movies with trailers: \t\t" + str(movtuple[0]))
            print ("Movies with local trailers: \t\t" + str(localmovie[0]))
            print ("Mezzmo movies with no trailers: \t" + str(notrailer[0]))  
            print ("Movies not yet fetched: \t\t" + str(nullmvtuple[0]))
            print ("Movies total trailers: \t\t\t" + str(totaltuple[0]))
            print ("Mezzmo local trailers:  \t\t" + str(localtuple[0]))
            print ("Mezzmo You Tube trailers: \t\t" + str(youtuple[0]))
            print ("Mezzmo IMDB trailers: \t\t\t" + str(imdbtuple[0]))
            print ("Mezzmo bad trailers: \t\t\t" + str(badtuple[0]))
            print ("Mezzmo long trailers: \t\t\t" + str(longtuple[0]))
            print ("Mezzmo invalid name trailers: \t\t" + str(invtuple[0]))
            print ("Mezzmo trailer file missing: \t\t" + str(mistuple[0]))
            print ("\nMezzmo local trailers mp4 format: \t" + str(mp4format[0]))
            print ("Mezzmo local trailers mkv format: \t" + str(mkvformat[0]))
            print ("\nLocal trailer files in folder: \t\t" + str(filecount))
            print ("Total size of local trailers: \t\t" + str(storagegb) + 'GB')
            print ("Average trailer file size: \t\t" + str(avgsize) + 'MB')
            if bstoragegb > 0:
                print ("Total size of backup trailers: \t\t" + str(bstoragegb) + 'GB')
            print ("\nMezzmo trailers fetched: \t\t" + str(chktuple[0]))
            print ("Mezzmo trailers not fetched: \t\t" + str(nulltuple[0]))
            print ("\n\n")

        elif sysarg1.lower() in ['stats'] and sysarg2.lower() in ['frame']:
            db = openTrailerDB()
            dqcurr = db.execute('SELECT var1, COUNT(*) counter FROM mTrailers WHERE NOT var1 \
            is NULL GROUP BY var1')
            frametuples = dqcurr.fetchall()
            db.close()

            if len(frametuples) == 0:
                print('There was a problem getting the frame rate statistics')
                return
            else:
                #print('The number of rows is: ' + str(len(frametuples)))
                print('\tFrame')
                print('\tRate\t\tCount\n')        
                for a in range(len(frametuples)):
                    print('\t' + str(frametuples[a][0]) + '\t\t' + str(frametuples[a][1]))


    except Exception as e:
        print (e)
        mgenlog = "There was a problem displaying statistics "
        print(mgenlog)
        genLog(mgenlog) 


checkVersion()                                               # Ensure Python version 3+
checkCommands(sysarg1, sysarg2)                              # Check for valid commands
getConfig()                                                  # Process config file
checkFolders()                                               # Check trailer and temp folder locations
checkDatabase()                                              # Check trailer database 
getMezzmoTrailers(sysarg1, sysarg2)                          # Get Movie Channel Trailers
checkCsv(sysarg1, sysarg2)
cleanTrailers(sysarg1, sysarg2, sysarg3)
makeBackups()

#checkFiles(sysarg1, sysarg2)
#checkFinish(sysarg1, sysarg2)

