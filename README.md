#Repeatr
Clone of [listenonrepeat.com](http://listenonrepeat.com/?v=ojvTSRA-O-Y#Corgi_Snow_Belly_Flop). Replace youtube.com in any YouTube video URL with localhost:5000 to watch your video loop on and on forever. A database tracks of the most looped videos across the site, and a local loop counter will gently shame you for listening to the same video for hours on end. 

Name inspired by Flaskr, the Flask tutorial site.

### To-do with more time:
* Find clever and beautiful way to incorporate video descriptions in top 10 list
* Numbering on top 10 list...
* Keep rolling tab of duration of looping thus far (i.e. `play_count * duration + time_elapsed`)
* Allow for YouTube search from form at the top right
* Regularly poll server for changes in the top 10 
  * Would love to animate these changes
* Custom error pages