Brad Allen tide server

title:  FastAPI service framework with Tides

name: Brad Allen

edX name:  Brad Allen

GitHub name: BradKentAllen

location:  Gig Harbor,  Washington

date:  February 5, 2025

video URL:  https://youtu.be/Enpe8TFH3AE



<u>Introduction:</u>  I am not new to Python and have used FastAPI to run websites but I have not done it correctly and have wanted to set up a site after fully updating my approach.  I learned a number of new approaches in cs50 so decided to start with an updated framework.

I have also wanted to set up a small application that opens on my phone and gives me critical information on the tides at our house.  One desire is to have the output be somewhat artistic, as opposed to just text.  So my project did the following:

**Created a FastAPI framework**

I used what we learned in Flask to seriously improve the FastAPI I had used in the past.  I added full use of cookies, proper encryption, protected and unprotected routes, and a general layout that I can build on in the future.  I actually have a work project to apply this to next week.

**Created a Tide App for Iphone**

My second goal was to use the FastAPI framework to serve an artistic app that showed the tides for a beach near our house.  This was a fairly complex process and involved:

1.  Getting the tidal station from the user in the URL
2. Used requests to quiry the NOAA Coops API to get tidal data.  I needed data for the entire day and possibly the previous day and next day.  The tide utility gets 7 days of data.  I did not want this to query the server for each request so it is set up to check if it has up to date data each morning at 1 AM (using a cron job) and also when it is started.  It checks the data for how current it is, loads if necessary, then puts it in a pickle file for later retrieval.
3. The tides utility also had to parse this data.  The most complex part of this was trying to determine the current tide height as the NOAA data only includes the highs and lows.  I had to create an algorithm that used a sine function to get the current tide.
4. Once I had the tide information, the presentation became important.  I wanted an artistic presentation that showed a graphic of the beach with the tide going in and out.  I did this by creating a set of graphics for the water for each tide state and overlaid it on a graphic of the beach.  The html then needed to use Jinja2 templating not only for the information coming in on the current and next tide but also for the style.  The style controlled the text position and text colors (as the next tide is white when a low is coming a black for a high).
5. Finally I needed to load this on to a Raspberry Pi set up to run FastAPI and serve it outside of my network.  Setting up on the Raspberry Pi proved easy and it quickly worked but the situation became increasingly complicated when I tried to access this through duckdns from the outside.  The primary issue was port forwarding in the router that allowed both local access and web access.  This proved to be a long process in which I primarily used ChatGPT which could never quite get the complete answer.
6. I ended up having to dive deeply on how to use NGINX as a proxy server and then configure it for my ports and local host use.

<u>**Hardware**</u>
RPi 4 model B
64 GB memory card
username/password:
hostname:  homebase.local
username:  home
password:  goose

Conclusion:  This was a bit more complex than I expected but did allow me to fully apply the various aspects of cs50 to a couple of projects that will be very useful for my work.

