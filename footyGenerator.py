import requests
import pprint
import json
from datetime import datetime
from datetime import timedelta
import pandas as pd

# gets the date next Saturday
def dateNextSat():
    currentDay = datetime.weekday(datetime.now())
    daysUntilSat = 5 - currentDay
    dateOnSatObj = datetime.now() + timedelta(days=daysUntilSat)
    dateOnSat = str(dateOnSatObj.date())

    return dateOnSat

dateInput = input(f"What date would you like to run this for? press enter for {dateNextSat()}...")

if dateInput == "":
    runForDate = dateNextSat()
else:
    runForDate = dateInput


params = {"fromDate": runForDate,
          "toDate": runForDate,
          "leagueIDArr": [39,40,41,42], # prem, champ., league one, league 2
          "season": "2024"}


# gets detail of all fixture json given the required paramaters, result is an array of json blobs, one per league

def getFixtures(fromDate, toDate, season, leagues):

    print("Retrieving Fixture Data...")

    leagueFixtureArr = []

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    for leagueID in leagues:

        querystring = {"league": leagueID, "season": season, "from": fromDate, "to": toDate}

        headers = {
            "X-RapidAPI-Key": "864600b7dbmshebfba37bd0b19dfp1802a4jsnf85c0a07a34b",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        leagueFixtureArr.append(response.json()["response"])

    return leagueFixtureArr


#get odds of home win, draw or away win for all book makers for all leages on a certain date
def getOdds(date, leagues, season):

	print("Retrieving Odds Data...")

	oddsArr = []

	url = "https://api-football-v1.p.rapidapi.com/v3/odds"

	for leagueID in leagues:
		querystring = {"date": date,
					   "league": leagueID,
					   "season": season,
					   "bet": 1}

		headers = {
			"X-RapidAPI-Key": "864600b7dbmshebfba37bd0b19dfp1802a4jsnf85c0a07a34b",
			"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
		}

		response = requests.get(url, headers=headers, params=querystring)

		oddsArr.append(response.json()["response"])


	return oddsArr


# compares a string of time to a time in a timestamp
def tsStringValidator(ts, string):

    tsTimeObj = datetime.fromtimestamp(ts).time()
    stringTimeObj = datetime.strptime(string, "%H:%M:%S").time()

    return tsTimeObj == stringTimeObj



fixturesJSONArr = getFixtures(fromDate=params["fromDate"], toDate=params["toDate"], season=params["season"], leagues=params["leagueIDArr"])


# getting all the fixture ids out of the fixturesJSONArr
cleanFixturesJSONArr = []
for arr in fixturesJSONArr:
    for i in arr:
        #print(i)
        cleanFixturesJSONArr.append(i)

#print("cleanArr: ",cleanFixturesJSONArr)




#getting odds and cleaning it up

oddsJSONArr = getOdds(date=params["fromDate"], leagues=params["leagueIDArr"], season=params["season"])


#pprint.pprint(oddsJSONArr)
#print(len(oddsJSONArr))

cleanOddsJSONArr = []
for arr in oddsJSONArr:
    for i in arr:
        #print(i)
        cleanOddsJSONArr.append(i)



# getting combinging the fixture arr and the odds arr

combiArr = []
threeOClock = "15:00:00"

for fixtureBlob in cleanFixturesJSONArr:
    #print(fixtureBlob)
    tempCombiBlob = {
    "fixtureID":  fixtureBlob["fixture"]["id"],
    "awayTeamName": fixtureBlob["teams"]["away"]["name"],
    "awayTeamID":  fixtureBlob["teams"]["away"]["id"],
    "homeTeamName":  fixtureBlob["teams"]["home"]["name"],
    "homeTeamID":  fixtureBlob["teams"]["home"]["id"],
    "timestamp": fixtureBlob["fixture"]["timestamp"],
    "allowedStartTime": tsStringValidator(ts=fixtureBlob["fixture"]["timestamp"], string=threeOClock),
    "oddsBlob": {},
    "averageHomeOdds": 0,
    "averageAwayOdds": 0,
    "favourite": "---neither---",
    "favouriteiD": -1,
    "lowestOdds": 999
    }

    for oddsBlob in cleanOddsJSONArr:
        if oddsBlob["fixture"]["id"] == fixtureBlob["fixture"]["id"]:
            #tempCombiBlob["oddsBlob"] = oddsBlob

            tempHomeTeamSum = 0
            tempHomeTeamCount = 0
            tempAwayTeamSum = 0
            tempAwayTeamCount = 0

            for bookies in oddsBlob["bookmakers"]:
                for bet in bookies["bets"][0]["values"]:
                    if bet["value"] == 'Home':
                        tempHomeTeamSum += float(bet["odd"])
                        tempHomeTeamCount += 1
                    if bet["value"] == 'Away':
                        tempAwayTeamSum += float(bet["odd"])
                        tempAwayTeamCount += 1

            if tempHomeTeamCount > 0:
                homeAverageOdds = tempHomeTeamSum / tempHomeTeamCount
                tempCombiBlob["averageHomeOdds"] = homeAverageOdds
            else:
                print("Divide by zero error 1")

            if tempAwayTeamCount > 0:
                awayAverageOdds = tempAwayTeamSum / tempAwayTeamCount
                tempCombiBlob["averageAwayOdds"] = awayAverageOdds
            else:
                print("Divide by zero error 2")

            if homeAverageOdds > 0 and awayAverageOdds > 0:
                if awayAverageOdds > homeAverageOdds:
                    tempCombiBlob["favourite"] = fixtureBlob["teams"]["home"]["name"]
                    tempCombiBlob["favouriteID"] = fixtureBlob["teams"]["home"]["id"]
                    tempCombiBlob["lowestOdds"] = homeAverageOdds
                if homeAverageOdds > awayAverageOdds:
                    tempCombiBlob["favourite"] = fixtureBlob["teams"]["away"]["name"]
                    tempCombiBlob["favouriteID"] = fixtureBlob["teams"]["away"]["id"]
                    tempCombiBlob["lowestOdds"] = awayAverageOdds


    combiArr.append(tempCombiBlob)
    #print(tempCombiBlob)

combiArrCorrectTimeOnly = [i for i in combiArr if i["allowedStartTime"] == True]

sortedArr = sorted(combiArrCorrectTimeOnly, key=lambda x: x["lowestOdds"])

print(f"For the {threeOClock} games on {params['fromDate']}")
print(f"\nTop {min(len(sortedArr), 10)} Lowest Average Odds: ")

for i in range(min(len(sortedArr), 10)):
    print(i + 1, ": ", sortedArr[i]["favourite"], "@",sortedArr[i]["lowestOdds"], "in", sortedArr[i]["homeTeamName"], "vs.", sortedArr[i]["awayTeamName"])



usedTeamsDF = pd.read_csv("usedteams.csv")


sortedArrExcludeUsed = [teamBlob for teamBlob in sortedArr if (teamBlob["favourite"] not in usedTeamsDF["teamName"].to_numpy())]


print("\nBased on your previous selections of... ")


for team in usedTeamsDF["teamName"].to_numpy():
    print(team)

print("\nYou should select one of: ")

suggestionLength = min(5, len(sortedArrExcludeUsed))

for i in range(suggestionLength):
    print(sortedArrExcludeUsed[i]["favourite"], "@",sortedArrExcludeUsed[i]["lowestOdds"])


#buiding question string
optionString = "To select a team, enter "
for i in range(suggestionLength):
    optionString += str(i + 1) + ' for ' + sortedArrExcludeUsed[i]["favourite"] + '...'

optionString += ' or anything else to cancel'
print(optionString)

answer = input("Selection: ")



#try:
if (int(answer) -1) in [*range(suggestionLength)]:
    print("got here1")
    newWeekData = pd.DataFrame({
        "week": [max(usedTeamsDF["week"].to_numpy()) + 1],
        "teamName": [sortedArrExcludeUsed[int(answer) - 1]["favourite"]],
        "teamID": [sortedArrExcludeUsed[int(answer) - 1]["favouriteID"]]
    })
    print("got here2")
    newWeekData.to_csv('usedteams3.csv', mode='a', index=False, header=False)
    print("got here3")
    dfUpdated = pd.read_csv("./usedteams3.csv")
    print("got here4")
    print(f'{sortedArrExcludeUsed[int(answer) - 1]["favourite"]} added to list')
    print(dfUpdated)
else:
    print("Input not valid, team list not updated")

#except:
#    print("Non Valid argument, team list not updated")
