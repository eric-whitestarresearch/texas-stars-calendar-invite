# texas-stars-calendar-invite
Parses the games scheldule listed on texasstars.com/games and creates a calendar invite for each game. 

For home games it lists the location as HEB Center and will send reminders 1 day before and 2 hours before the game. 
For away games it will set a reminder 20 minutes before the game. 

# Requirements 
- A Google Cloud Platform account
- A Google email account (gmail or Google Apps will work just fine)
- This script was developed on Python 3.11. It may work on other versions, but I haven't tested it.

# How to use. 
1. You need to create a GCP project with the Calendar API and enable OAuth for the API. This [page](https://developers.google.com/calendar/api/quickstart/python) describes how to do that.
2. After you setup the GCP project you will be provided with a credentials.json file. This file contains the key that allows access to the GCP project. Safeguard this file and do not check it into git. For this script to run you need to save a copy of it in /tmp/wsr/stars/credentials.json. 
3. Create a list of invitees in the file attendees.txt. This is a falt text file with one emaill address per line. You can see a sample in attendees-sample.txt
4. Restore the python module requirements
    ```
    pip install -f requirements.txt
    ```
4. Execute the script
    ```
    python3 create_invities.py
    ```
    
# FAQ
- Q: Will this work for teams other than the Texas Stars?
  A: The script was designed to be modular. You would need to write a new parser class as every team has a different website format. Once you do that the rest of the logic will work to create the invites.
- Q: Will this work with email accounts other that Google?
  A: The invitee to the events can be any email provider. They will just receive an email from Google asking them to accept the invite. However for the person creating the invite they need to have a Google email account. 
- Q: Will it cost me money to run this script?
  A: Google charges to use their APIs. However this will only make 1 API call per game, so 72 calls for the whole season. This should be within the free teir. However if you have API usage for other stuff, there would be small charge. See the [GCP Pricing Calculator](https://cloud.google.com/products/calculator) to estimate your costs 
