import pandas as pd
from globalFunctions import *

def footyGenerator(dateInput: str, leagueIds: list, season: str, gameTime: str, fileName: str) -> None:
    """
    Description:
    Main executable function, runs full process...
    
    Parameters:
    dataInput (string): Date string in format yyyy-mm-dd, this 
    is the data to gather fixtures for
    eg. "2025-01-18"
    
    leagueIds (list): An array of the IDs of which leagues to
    evaluate
    eg. [39,40,41,42]
    
    season (string): A string of the year the season starts in,
    eg. "2024"
    
    gameTime (string): The kick off time for the games to evaluate
    eg. "15:00:00"
    
    fileName (string): The name of the file to save the selected 
    team data to
    eg. "usedTeams.csv"
    
    """

    # Initialise the date
    if dateInput == "":
        runForDate = dateNextSat()
    else:
        runForDate = dateInput
    
    # Parameters for the algorithm
    params = {
        "fromDate": runForDate,
        "toDate": runForDate,
        "leagueIDArr": leagueIds,
        "season": season
    }

    # Get the fixtures for the data selected
    fixturesJSONArr = getFixtures(
        fromDate=params["fromDate"],
        toDate=params["toDate"],
        season=params["season"],
        leagues=params["leagueIDArr"]
    )

    # getting all the fixture ids out of the fixturesJSONArr
    cleanFixturesJSONArr = []
    for arr in fixturesJSONArr:
        for i in arr:
            cleanFixturesJSONArr.append(i)

    # Getting odds and cleaning it up
    oddsJSONArr = getOdds(
        date=params["fromDate"],
        leagues=params["leagueIDArr"],
        season=params["season"]
    )
    
    # Format json response from the API
    cleanOddsJSONArr = []
    for arr in oddsJSONArr:
        for i in arr:
            cleanOddsJSONArr.append(i)

    # Combine the fixture API data and the odds API data
    combiArr = []

    for fixtureBlob in cleanFixturesJSONArr:

        # Build a fixture object for each fixture for proessing
        tempCombiBlob = {
            "fixtureID":  fixtureBlob["fixture"]["id"],
            "awayTeamName": fixtureBlob["teams"]["away"]["name"],
            "awayTeamID":  fixtureBlob["teams"]["away"]["id"],
            "homeTeamName":  fixtureBlob["teams"]["home"]["name"],
            "homeTeamID":  fixtureBlob["teams"]["home"]["id"],
            "timestamp": fixtureBlob["fixture"]["timestamp"],
            "allowedStartTime": tsStringValidator(ts=fixtureBlob["fixture"]["timestamp"], string=gameTime),
            "oddsBlob": {},
            "averageHomeOdds": 0,
            "averageAwayOdds": 0,
            "favourite": "---neither---",
            "favouriteiD": -1,
            "lowestOdds": 999
        }

        # Process odds data for each match, finding the average
        for oddsBlob in cleanOddsJSONArr:
            if oddsBlob["fixture"]["id"] == fixtureBlob["fixture"]["id"]:
                tempHomeTeamSum = 0
                tempHomeTeamCount = 0
                tempAwayTeamSum = 0
                tempAwayTeamCount = 0

                # For each book maker, for each odds...
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

                # Find the average home and away odds, used for special rule in competition
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

    # Validate the starttimes
    combiArrCorrectTimeOnly = [i for i in combiArr if i["allowedStartTime"] == True]

    # Sort the data by lowest odds
    sortedArr = sorted(combiArrCorrectTimeOnly, key=lambda x: x["lowestOdds"])

    # Print to user the details about the games with the lowest odds
    print(f"For the {gameTime} games on {params['fromDate']}")
    print(f"\nTop {min(len(sortedArr), 10)} Lowest Average Odds: ")
    for i in range(min(len(sortedArr), 10)):
        print(i + 1, ": ", sortedArr[i]["favourite"], "@",sortedArr[i]["lowestOdds"], "in", sortedArr[i]["homeTeamName"], "vs.", sortedArr[i]["awayTeamName"])

    # Get previously used teams from CSV file
    usedTeamsDF = pd.read_csv(fileName)

    # Exclude teams that have been used
    sortedArrExcludeUsed = [teamBlob for teamBlob in sortedArr if (teamBlob["favourite"] not in usedTeamsDF["teamName"].to_numpy())]

    # Print to user the previous teams and the suggestion of which team to use
    print("\nBased on your previous selections of... ")
    for team in usedTeamsDF["teamName"].to_numpy():
        print(team)
    print("\nYou should select one of: ")    
    suggestionLength = min(5, len(sortedArrExcludeUsed))
    for i in range(suggestionLength):
        print(sortedArrExcludeUsed[i]["favourite"], "@",sortedArrExcludeUsed[i]["lowestOdds"])

    # Create string to prompt user to select a team
    optionString = "To select a team, enter "
    for i in range(suggestionLength):
        optionString += str(i + 1) + ' for ' + sortedArrExcludeUsed[i]["favourite"] + '...'
    optionString += ' or anything else to cancel'
    print(optionString)

    # Ask the user to select the index of the team they wish to select
    answer = input("Selection: ")

    # Run verification and add the team to 
    if (int(answer) -1) in [*range(suggestionLength)]:
        newWeekData = pd.DataFrame({
            "week": [max(usedTeamsDF["week"].to_numpy()) + 1],
            "teamName": [sortedArrExcludeUsed[int(answer) - 1]["favourite"]],
            "teamID": [sortedArrExcludeUsed[int(answer) - 1]["favouriteID"]]
        })
        newWeekData.to_csv(fileName, mode='a', index=False, header=False)
        dfUpdated = pd.read_csv(fileName)
        print(f'{sortedArrExcludeUsed[int(answer) - 1]["favourite"]} added to list')
    else:
        print("Input not valid, team list not updated")