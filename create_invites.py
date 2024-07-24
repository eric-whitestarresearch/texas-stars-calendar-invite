#     Texas Stars Calendar Invite - Automatically create google calendar invites for Texas Stars games.
#     Copyright (C) 2024  Whitestar Research LLC
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing, software
#      distributed under the License is distributed on an "AS IS" BASIS,
#      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#      See the License for the specific language governing permissions and
#      limitations under the License.


from modules.texasstarsparser import TexasStarsParser
import requests
import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class FetchExecutionError(Exception):
    pass

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def fetch_games():
    """
    Fetch the html page with all the game data

    Parameters:
        none

    Returns:
        string: A string with the HTML doc
    """
    url = 'https://www.texasstars.com/games'
    html_doument = requests.get(url)

    if not (html_doument.status_code>=200 and html_doument.status_code < 300):
        raise FetchExecutionError(f"Got a {html_doument.status_code} when trying to fecth the games listing")
    
    return html_doument.text

def get_attendees():
    """
    Get the list of people to invite from the config file. The file is just a plain text file with 1 emaill address per line

    Parameters:
        none

    Return:
        list: A list of dictonaries. 
            Dictonary schema:
                email (String): The emaill address of the invitee
    """
    
    attendees_list = open('attendees.txt','r')
    attendees = []
    for line in attendees_list:
        invitee =  {'email': line.strip()}
        attendees.append(invitee)
    
    return attendees

def build_game_invite(game, attendees):
    """
    Builds a dict with the game invite information

    Parameters:
        game (Dict): A dictonary with the game info. 
            It has the schema: 
                date (String): The date time of the start of the game in the format YYYY/MM/DD HH:MM, 
                location(String): Home or Away,
                playing(String): The name of the team we are playing
        attendees (List): A list of dictonaries of the people to invite. 
            The dictonary has the schemas:
                email: The email address to invite

    Returns:
        dict: A dictonary with the schema expected by the GCP calandar API

    """

    game_time = datetime.datetime.strptime(game['date'],"%Y/%m/%d %H:%M")
    start_time = game_time.strftime("%Y-%m-%dT%H:%M:00")
    end_time = (game_time + datetime.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:00")
    if game['location'] == 'Home':
        summary = f"Texas Stars Home Game"
        location = '2100 Ave of the Stars, Cedar Park, TX 78613'
        reminders = [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 120},
        ]
    else:
        summary = f"Away Texas Stars Game"
        location = 'AHL TV'
        reminders = [
          {'method': 'popup', 'minutes': 20}
        ]
    event = {
      'summary': summary,
      'location': location,
      'description': f"Texas Stars vs {game['playing']}",
      'start': {
        'dateTime': start_time,
        'timeZone': 'America/Chicago',
      },
      'end': {
        'dateTime': end_time,
        'timeZone': 'America/Chicago',
      },
      'attendees': attendees,
      'reminders': {
        'useDefault': False,
        'overrides': reminders,
      },
    }

    return event

def main():
    """
        The main method. This will create the invites from the info on the web page
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('/tmp/wsr/stars/token.json'):
        creds = Credentials.from_authorized_user_file('/tmp/wsr/stars/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/tmp/wsr/stars/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('/tmp/wsr/stars/token.json', 'w') as token:
            token.write(creds.to_json())

    game_html = fetch_games()
    parser = TexasStarsParser()
    game_data = parser.parse_game_data(game_html)
    attendees = get_attendees()

    try: 
        service = build('calendar', 'v3', credentials=creds)

        for game in game_data:
            event_body = build_game_invite(game, attendees)
            new_event = service.events().insert(calendarId='primary', body=event_body).execute()
            print(f"Event created: {new_event.get('htmlLink')} ")

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()
