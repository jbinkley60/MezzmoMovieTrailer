v2.0.7 11/11/2024

-  Improved exception handling reporting to make troubleshooting easier
-  Fixed bug where TMDB trailer titles with nonprintable characters could
   cause an exception error and trailer fetching to end prematurely.

v2.0.6 10/19/2024

-  Fixed new fetch counter limit bug where limit could be reached incorrectly
-  Updated client code to support Windows 64 exe format
-  Added Windoww x64 release format for client along with native Python  

v2.0.5 8/18/2024

- Updated yt-dlp.exe to eliminate warning messages
- Added automatic yt-dlp.exe update checking/updating to the latest version
- Added automatic deletion of artwork, along with trailer files, when maximum
  number of trailers to keep is reached.  Previously just the trailer files
  were automatically deleted.
- Added automatic logfile pruning to keep it from growing beyond 16,000 lines.
- Fixed bug where trailers were being deleted when they were below the maximum
  amount to keep per category
- Added setting to limit the maximum number of new trailers per category to 
  fetch per run

v2.0.4  3/28/2024

- Fixed API key issue causing 401 errors from TMDB
- Updated yt-dlp.exe to a new version to fix other You Tube errors
- Updated format parsing to handle newer You Tube formats

v2.0.3  12/14/2023

- Added feature to trim database history table to 1000 lines and the
  logfile to 15000 lines automatically getting to 100% completely
  maintenance free running when running as a scheduled task. 
- Modified the total fetch counter to be for the last 30 days to 
  align to the automatic pruning of the history table.

v2.0.2  12/1/2023
- Improved speed and significant reduction in TMDB API calls by
  changing the method / order for determining existing trailers 
  in the database
- Fixed a bug which was causing some trailers to be incorrectly 
  deleted when checking the trailer limits and then rediscovered
- Improved statistics shown at the end of a trailer check run
- Increased configuration option for trailers to keep from 50 to 100 per category
- Fixed bug where trailer artwork files were not being deleted during limit check trailer removals

v2.0.1  11/22/2023
- Additional code cleanup - client and server
- Fixed issue where the last 2 characters were being chopped off for the last actor, genre and director
- Bug fix for no trailers being displayed when logging is enabled due to path change for v2.0.0 
- Added producers and writers to trailer information - client and server
- Added check for movie titles which have unprintable / stdout characters in Python
- Added video as default value for category if improper setting value entered - server
- Added setting to fetch up to 40 trailers per category per run vs. 20 previously - client

v2.0.0  11/17/2023
- Initial production release
- Added clean files feature to find / delete orphaned trailer files and database records
- Final code cleanup
- Improved logging clarity
- Local artwork feature added - client and server
- Added movie trailer year information - server only
- Added movie series / collection information - client and server
- Fixed duplicate Mezzmo plugin ids with old movie trailers channel - server only
- Added \ movies to paths for future TMDB TV series channel and more - client and server
- Fixed trailers table CSV export not working
- Replaced CSV ## delimiter with standard ", " for genres, directors etc.. 

v0.0.3  11/12/2023
- Added all option to trailers for fetching all categories in a single command
- Enabled movie trailer keep limits from config file setting
- Added stats option to display trailer statistics
- Added support for Mezzmo Kodi addon integration
- Removed 5 trailer download limit for each category

v0.0.2  11/11/2023
- Added trailer clean feature
- Continued code cleanup and bug fixes

v0.0.1  11/9/2023

- Initial client test release