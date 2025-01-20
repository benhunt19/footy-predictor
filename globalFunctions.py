import requests
import json
from datetime import datetime
from datetime import timedelta
from keys import keys

def dateNextSat() -> str:
    """
    Description: 
    Gets the date of the upcoming Saturday in the format yyyy-mm-dd
    
    Parameters:
    None
    """
    currentDay = datetime.weekday(datetime.now())
    daysUntilSat = 5 - currentDay
    dateOnSatObj = datetime.now() + timedelta(days=daysUntilSat)
    dateOnSat = str(dateOnSatObj.date())
    return dateOnSat

def getFixtures(fromDate: str, toDate: str, season: str, leagues: list) -> list:
    """
    Description:
    Gets detail of all fixture json given the required paramaters,
    result is an array of json blobs, one per league
    
    Parameters:
    fromData (string): The start date of the fixtures
    eg. "2025-01-18"
    
    toDate (string): The end date of the fixtures
    eg. "2025-01-18"
    
    season (string): The season the fixtures belong to
    eg. "2024"
    
    leagues (list): A list of the IDs of the leagues
    eg. [39,40,41,42]
    
    """
    print("Retrieving Fixture Data...")
    leagueFixtureArr = []

    # API endpoint
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    for leagueID in leagues:

        # Params for the request
        querystring = {
            "league": leagueID,
            "season": season,
            "from": fromDate,
            "to": toDate
        }
        
        # Headers for the request
        headers = {
            "X-RapidAPI-Key": keys.RAPID_API_FOOTBALL_KEY(),
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        # Api response
        response = requests.get(url, headers=headers, params=querystring)
        leagueFixtureArr.append(response.json()["response"])

    return leagueFixtureArr

def getOdds(date: str, leagues: list, season: str) -> list:
    """
    Description:
    Gets the odds for the games on a certain date for
    various leagues
    
    Parameters:
    data (string): The date of the fixtures
    eg. "2025-01-18"
    
    leagues (list): A list of the IDs of the leagues
    eg. [39,40,41,42]
    
    season (string): The season the fixtures belong to
    eg. "2024"
    """
    print("Retrieving Odds Data...")
    oddsArr = []
    
    # API endpoint
    url = "https://api-football-v1.p.rapidapi.com/v3/odds"

    # For each league in league array
    for leagueID in leagues:
        
        # Params for the API request
        querystring = {
            "date": date,
            "league": leagueID,
            "season": season,
            "bet": 1
        }

        # Headers for the api Request
        headers = {
            "X-RapidAPI-Key": keys.RAPID_API_FOOTBALL_KEY(),
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        # API response
        response = requests.get(url, headers=headers, params=querystring)
        oddsArr.append(response.json()["response"])

    return oddsArr

def tsStringValidator(ts: datetime.timestamp, string: str) -> bool:
    """
    Description:
    Validates the time from a timestamp
    
    Parameters:
    ts (timestamp): The timestamp to extract the 
    """
    # Converts a timestamp to time
    tsTimeObj = datetime.fromtimestamp(ts).time()
    # Converts the string into a time
    stringTimeObj = datetime.strptime(string, "%H:%M:%S").time()
    # Checks for equality
    return tsTimeObj == stringTimeObj