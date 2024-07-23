from bs4 import BeautifulSoup
import re
import datetime

#Slurp up the file with the games
game_html = open("games.html","r")

parser = BeautifulSoup(game_html, 'html.parser')

this_year = str(datetime.date.today().year)
next_year = str((datetime.date.today() + datetime.timedelta(days=366)).year)

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
    year = this_year if re.search('Oct|Nov|Dec', date) else next_year
    time = re.search('([0-9]{1,2}:[0-5][0-9][PA]M)',curr_date.contents[3].contents[0]).group(0)
    game_info['date'] = datetime.datetime.strptime((date + " " + year + " " + time ),'%a, %b %d %Y %I:%M%p').strftime('%Y/%m/%d %H:%M')
    game_info['location'] = re.search('(Home|Away)',curr_vs.contents[1].contents[0]).group(0)
    game_info['playing'] = curr_team.contents[3].contents[0].strip()
    games_data.append(game_info)

print(games_data)

