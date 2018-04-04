# Twitter Account Checker
This script checks twitter accounts current state.

## Requirements
1. Python
2. Joblib (optional) - Install to run the script parallely.

## Usage
Check several accounts from cmd:
```
python twitter_account_checker.py twitter_username1 twitter_username1
```
Also it is possible to load a list of usernames from a file where each line conatins a username:
```
python twitter_account_checker.py --file twitter_ids.txt --save results.csv
```
