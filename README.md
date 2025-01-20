# Football Results Predictor

This was initially built to (attempt) to win a 'Last Man Standing' fantasy league.

The rules:
- Choose any team from the top 4 football leagues for the Saturday 3pm fixtures
- If your team looses you are out
- You must not choose the same team twice

The algorithm works as follows:
1. Enter the date of the fixures you wish to process.
2. The program will gather all the fixtures for the predefined leagues of that date.
3. For each game, various odds are imported via API. These are processed and averaged.
4. The top 10 teams most likely to win are returned to the user.
5. The previously selected teams that have been saved to csv are filtered out of this list.
6. The user will select which out of the remaining teams to choose. This is saved to the existing csv of selected teams.

## Author

**Ben Hunt**  
[GitHub Profile](https://github.com/benhunt19)  
[LinkedIn](https://www.linkedin.com/in/benjaminrjhunt)

If you have any questions, feedback, or suggestions, feel free to reach out or open an issue in the repository.