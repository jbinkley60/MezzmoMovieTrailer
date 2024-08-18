# Mezzmo Movie Trailer Channel 2
Add a channel to your Mezzmo server to view movie trailers from <a href="https://www.themoviedb.org/">TMDB</a>.  


## Features:

- Get current TMDB movie trailer information for Now Playing, Upcoming, Popular and Top rated movies
- Download movie trailers for local playback through your Mezzmo server
- Full movie metadata including plot, actors, artwork, movieset and more 
- User selectable feature of 480P, 720P or 1080P quality trailers (if available, otherwise best quality available)
- Automatically move trailers to designated location (i.e. NAS, local disk etc.)
- Option for how many movies to keep for each category (1-100) with auto deletions
- Option to set output trailer output format to mp4 or mkv 
- Full detailed logfile
- Full Mezzmo Movie Trailers Channel statistics
- Check and remove orphaned movie trailer files
- Local artwork for improved quality and performance
- CSV export of trailer information and checker history 
- Command line backups of Mezzmo Movie Trailers Channel database
- User ability to clear trailer information by movie category 
<br/>

## Installation and usage:

-  Download the Mezzmo Movie Trailer Channel release zipfile
-  Ensure you have Python installed on Windows. Minimum version 3.x
-  Unzip file into an empty folder on your system
-  The zipfile contains 2 folders, client and server
-  The client folder stays on your local workstation and contains the trailer downloader
-  The server folder goes onto your Mezzmo server in the Mezzmo Channels folder
-  The Mezzmo channels folder is typically located at c:\ProgramData\Conceiva\Mezzmo\Plugins\   
-  Edit the config.text client file with the location of your trailer folder and preferred output format
-  It is <b>highly suggested</b> not to use the same trailer folder as the <a href="https://github.com/jbinkley60/MezzmoTrailerChecker/wiki">Mezzmo Trailer Checker</a>  
-  Open a command window and run movie_trailers.py trailers now<br/>
   See optional command line arguments below.
-  The client will build the database, check folder locations and download the movie trailers requested
-  Next install the <a href="http://www.mezzmo.com/wiki/doku.php?id=adding_channels">Mezzmo Movie Trailers Channel 2</a> into Mezzmo
-  Open the Mezzmo Movie Trailers Channel 2 in the Mezzmo GUI and set the trailer path location in Properties->Settings
-  You should see the trailers downloaded by the client appear in the Mezzmo GUI       

<br>
   
## Command line arguments:  (Limit 1 at a time)

- <b>trailers now</b>	-  Checks for Now Playing movies <br>
- <b>trailers up</b>    -  Checks for Upcoming movies <br>
- <b>trailers pop</b>   -  Checks for Popular movies <br>
- <b>trailers top</b>   -  Checks for Top Rated movies <br>
- <b>trailers all</b>   -  Checks for all for movie categories <br> 
- <b>clean category</b> -  Clears trailer database info for movies by category and deletes downloaded trailer file <br>
- <b>clean files</b>    -  Analyzes trailer files and database entries for missing files and entries <br> 
- <b>csv trailers</b>   -  Creates a CSV file with the trailer information <br> 
- <b>csv history</b>    -  Creates a CSV file with the history information <br>
- <b>stats</b>          -  Generates summary statistics for trailers <br>
- <b>backup</b>         -  Creates a time stamped file name backup of the Mezzmo Movie Trailers Channel database <br> 

<br>          

Visit the <a href="https://github.com/Conceiva/MovieTrailer/wiki">Mezzmo Movie Trailers Channel wiki</a> for the latest information.          

           
<br/><img src="https://github.com/Conceiva/MovieTrailer/assets/63779136/1f65376d-2a70-4337-a0c7-a4899164b0a8" width="40%" height="40%">

