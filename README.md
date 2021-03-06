# [hello_friend](http://hello-frrriend.herokuapp.com/)

Code.Fun.Do 2016 Hackathon project by team ./ [dot slash]

A Q&A service through SMS.

Number: +1 360-900-1701

## Features
* Call for help using the SOS module
* Find the best route to your destination
* Catch up on the latest news
* Find out meaning for a new word
* Find your nearest ATM
* In a foreign country? Use Translate to speak the native language
* Keep up with the stock market
* Check out information on all the movies
* Prepare for sun or rain with weather updates

And the best part? No need to have Internet, or even a smartphone.


## APIs used
* [Twilio](https://www.twilio.com)
* [Heroku](https://www.heroku.com)
* [Wit.ai](https://wit.ai)
* [Bing Maps API](https://www.microsoft.com/maps/choose-your-bing-maps-API.aspx)
* [Google Places API](https://developers.google.com/places/)
* [Bing Translate API](https://www.microsoft.com/en-us/translator/translatorapi.aspx)
* [Open Weather Map API](https://openweathermap.org/api)
* [Bing News API](http://www.bing.com/developers/s/APIBasics.html)
* [OMDB API](https://www.omdbapi.com)
* [Duck Duck Go Instant Answer API](https://duckduckgo.com/api)
* [Yahoo Finance](https://pypi.python.org/pypi/yahoo-finance/1.1.4)


## Developed by

[Avikant Saini](https://github.com/avikantz)

[Yash Kumar Lal](https://github.com/ykl7)

[Jitesh Kumar Jha](https://github.com/jiteshjha)


### Templates

To test the functionalities provided by **hello_friend**, use these test cases:
* ```navigate from locality, city to locality, city```. To and from locations can be interchanged as well. The correct interpretation is autodetected.
* ```whats the weather in city today```
* ```help locality, city``` OR ```sos locality, city```
* ```how do you say word in language```
* ```imdb movie-name```
* ```stocks stock-name```
* ```atm near locality, city```
* ```define word/phrase```
* ```show me sports news```

### Languages

The languages currently supported by our Translate feature are:

* German
* French
* Spanish
* Chinese

### Running Locally

It's possible; Send a `GET` request to `localhost:5000/sms` with the query string in a parameter "`Body`"