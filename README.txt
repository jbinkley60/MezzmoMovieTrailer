v0.0.1  11/9/2023

- Initial client test release

v0.0.2  11/11/2023
- Added trailer clean feature
- Continued code cleanup and bug fixes

v0.0.3  11/12/2023
- Added all option to trailers for fetching all categories in a single command
- Enabled movie trailer keep limits from config file setting
- Added stats option to display trailer statistics
- Added support for Mezzmo Kodi addon integration
- Removed 5 trailer download limit for each category

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

v2.0.1  11/22/2023
- Additional code cleanup - client and server
- Fixed issue where the last 2 characters were being chopped off for the last actor, genre and director
- Bug fix for no trailers being displayed when logging is enabled due to path change for v2.0.0 
- Added producers and writers to trailer information - client and server
- Added check for movie titles which have unprintable / stdout characters in Python
- Added video as default value for category if improper setting value entered - server
- Added setting to fetch up to 40 trailers per category per run vs. 20 previously - client

