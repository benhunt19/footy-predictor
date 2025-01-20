from footyGenerator import footyGenerator
from globalFunctions import dateNextSat

if __name__ == "__main__":
    
    # Constants
    LEAGUE_IDS = [39,40,41,42]      # prem., champ., league 1, league 2
    SEASON = "2024"                 # 2024/25 season
    GAME_TIME = "15:00:00"          # Kickoff for fixtures
    FILE_NAME = "usedTeams.csv"     # File to store used team data
    
    # Date to run the algorithm for, if blank, defaults to upcoming Saturday
    dateInput = input(f"What date would you like to run this for? press enter for {dateNextSat()}...")
    
    # Run main process
    footyGenerator(
        dateInput= dateInput,
        gameTime=GAME_TIME,
        leagueIds=LEAGUE_IDS,
        season=SEASON,
        filename=FILE_NAME
    )