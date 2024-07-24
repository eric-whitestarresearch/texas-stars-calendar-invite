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


from bs4 import BeautifulSoup
import re
import datetime



class TexasStarsParser:
    """
    This class contains the functions that parse the scheldule from the HTML document on the website.

    Attributes:
        this_year(str): The year for the first half of the season stored as a string
        next_year(str): The year for the second half of the season stored as a string
    """

    def __init__(self):
        """
        The constructor for the class. 

        Parameters:
            self (TexasStarsParser): The object itself
        """

        #On the website it does not provide the year of the game. Since the game season spans two years we need to account for this. 
        #If we run this script between July and December assume the season hasn't started yer
        #If we run this script between Janurary and June assume we are in the second half of the seasons already
        if datetime.datetime.now().date().month > 6:
            self.this_year = str(datetime.date.today().year)
            self.next_year = str((datetime.date.today() + datetime.timedelta(days=366)).year)
        else:
            self.this_year = str((datetime.date.today() + datetime.timedelta(days=-366)).year)
            self.next_year = str(datetime.date.today().year)


    def parse_game_data(self, html_document):
        """
        This method parses the game data that is stored in an html document. 

        Parameters:
            self (TexasStarsParser): The object itself
            html_document(String): The document containing the game data to be parsed

        Returns:
            List: A list of dictonaries with the game data. 
                The dictonary has the following keys:
                    date: The date and time of the game in format YYYY/MM/DD HH:MM
                    location: Home or Away
                    playing: The name of the team we are playing
        """
        parser = BeautifulSoup(html_document, 'html.parser')



        games_vs_message = parser.find_all('div', class_="game_vs_message")
        teams_info = parser.find_all('div', class_="team-info")
        date_time = parser.find_all('div', class_="date-time")

        games_data = []

        for i in range(len(games_vs_message)):
            game_info = {}
            curr_vs = games_vs_message[i]
            curr_team = teams_info[i]
            curr_date = date_time[i]
            date = re.search('([A-Z][a-z]{2}, [A-Z][a-z]{2} [0-9]{1,2})',curr_date.contents[1].contents[0]).group(0)
            year = self.this_year if re.search('Oct|Nov|Dec', date) else self.next_year
            time = re.search('([0-9]{1,2}:[0-5][0-9][PA]M)',curr_date.contents[3].contents[0]).group(0)
            game_info['date'] = datetime.datetime.strptime((date + " " + year + " " + time ),'%a, %b %d %Y %I:%M%p').strftime('%Y/%m/%d %H:%M')
            game_info['location'] = re.search('(Home|Away)',curr_vs.contents[1].contents[0]).group(0)
            game_info['playing'] = curr_team.contents[3].contents[0].strip()
            games_data.append(game_info)

        return games_data

