import requests
from urllib.parse import urlencode
import urllib.error
import settings
import time
import os

info_dump = {'hello:': 'this is your info dump :3', 'gameName': 0, 'tagLine': 0, 'puuid': 0, 'API_KEY': settings.API_KEY}
params = {'api_key': settings.API_KEY, 'startTime': 0, 'endTime': 0, 'start': 0}
programOn= True
menuState = 0 ##0 = main menu, 1 = settings
display_width = 0

title = []
choices = []
schoices = []

def get_summoner_info( region=settings.DEFAULT_REGION_CODE):

    """"
    Multifunctional reconnaissance tool for League of Legends/Riot API.
    """
    choice = 0
    global title
    global choices
    global schoices
    global menuState
    global display_width
    while programOn == True:
        columns, lines = os.get_terminal_size()
        display_width = columns - 1
        print("Display size: ", display_width)
    
        title = [
            'LEAGUE OF LEGENDS TRACKER',
            'MAIN MENU',
            'github.com/alliums'
        ]

        choices = [
            {'num': '1', 'desc': 'Find target summoner by name', 'func': get_puuid_by_name},
            {'num': '2', 'desc': 'Find target summoner by summoner ID', 'func': get_summoner_info_by_summonerid},
            {'num': '3', 'desc': 'Get player match history', 'func': get_match_list_by_puuid},
            {'num': '4', 'desc': 'Get information on a match by its ID', 'func': get_match_info_by_id},
            {'num': '5', 'desc': 'Info dump', 'func': show_info_dump},
            #{'num': '6', 'desc': 'Change API key', 'func': set_api_key},

            {'num': '6', 'desc': 'Options', 'func': display_options_menu},
            {'num': '7', 'desc': 'Quit', 'func': progoff}
        ]

        schoices = [
            {'num': '1', 'desc': 'Change API key', 'func': set_api_key},
            {'num': '2', 'desc': 'Go back to main menu', 'func': display_main_menu}
        ]
        
       
        print_title()

        if menuState == 0:
            display_main_menu()
        if menuState == 1:
            display_options_menu()

        if params['api_key'] == "00":
            newApiKey = input("\nPlease enter your API key: ")

            #open settings file to save API key
            with open('settings.py', 'r') as file:
                filedata = file.read()

            #replace API key placeholder with real key
            filedata = filedata.replace("00", newApiKey)   

            #write file out
            with open('settings.py', 'w') as file:
                file.write(filedata)
            params['api_key'] = newApiKey
            print("you wrote", newApiKey)
            print("New API key set: ", params['api_key'])


        #match int(choice):
        #    case 1: get_puuid_by_name(info_dump)
        #    case 2: get_summoner_info_by_summonerid()
        #    case 3: get_match_list_by_puuid()
        #    case 4: get_match_info_by_id()
        #    case 5: show_info_dump(info_dump)
        #    case 6: set_api_key()
        #    case 7: programOn = False
                
def get_puuid_by_name():

    print("Set new summoner name: ")
    gameName = input("Summoner Name (No Tagline): ")
    tagLine = input("Summoner Tagline (Without the # symbol): ")

    print("Connecting to Riot API...")
    
    api_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{info_dump['gameName']}/{info_dump['tagLine']}?api_key={settings.API_KEY}"
    
    print("Getting puuid from data... \n")
    try:
        response_data = hit_api(api_url)
        try:
            if 'puuid' in response_data:
                print("Player puuid successfully found.")
                info_dump['puuid'] = response_data['puuid']
                print(info_dump['puuid'])
                info_dump['gameName'] = gameName
                info_dump['tagLine'] = tagLine
        except: print("Error - can't set puuid!\n")
    except urllib.error.HTTPError as err: 
        print("Failed to connect to Riot API. See reason below. Check API key.")
        print(err.reason, "\n")
        raise SystemExit(err)
        #if response_data.code == 403:
        #    print("API key invalid - no authorization to access Riot API!")
        #else: print("Invalid name or summoner not found. Try retyping the name or check if the summoner has changed their name.")
        print(response_data, "\n")
        return None
    


def show_info_dump():
    for i in info_dump:
        print(i, info_dump[i])
    return None

def get_match_list_by_puuid():
    if not info_dump['puuid']:
        print("No player selected! Use option 1!")
        return None
        
    
    api_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{info_dump['puuid']}/ids?api_key={settings.API_KEY}"
    
    response_data = hit_api(api_url)

    params['startTime'] = 1623816920
    params['startTime'] = int(input("Enter start time (Epoch timestamp) (enter to skip): ") or 1623816920)
    params['endTime'] = int(input("Enter end time (Epoch timestamp) (enter to use right now's timestamp): ") or time.time())

    newCount = int(input("Enter the number of matches to find: ") or 20)
    startNum = int(input("Enter start offset - 100 means you start 100 matches ago, etc.") or 0)

    full_result = []

    #max matches is 100
    #if more than 100, then start at 0, find 100, start at 100, find 100, until number of matches remaining is 0
    while newCount > 0:
        params['start'] = startNum
        if newCount <= 100 and newCount > 0:
            params['count'] = newCount
            response_data = hit_api(api_url)
            startNum += newCount
            for i in response_data:
                print("Match: ", i)
                full_result.append(i)
            newCount -= newCount

        if newCount > 100:
            
            if newCount % 100 != 0:
                params['count'] = newCount % 100
                newCount -= params['count']
                startNum += params['count']
                response_data = hit_api(api_url)
                for i in response_data:
                    print("Match: ", i)
                    full_result.append(i)
                    break

            if newCount % 100 == 0:
                params['count'] = 100
                newCount -= 100
                startNum += 100
                print(" ZERO start num: ", startNum)

                response_data = hit_api(api_url)
                for i in response_data:
                    print("Match: ", i)
                    full_result.append(i)
    print(len(response_data))
    
#use match id to get match details - just displays summoner names for now
def get_match_info_by_id():

    matchID = input("Please enter match ID: ")
    print(settings.API_KEY)
    api_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchID}?api_key={settings.API_KEY}"
    response_data = hit_api(api_url)
    for i in response_data:
        
        for j in response_data[i]:
            if j == "participants":
                for k in response_data[i][j]:
                    for l in k:
                        if l == "summonerName":
                            print(l,  "\n")
                            if k["summonerName"] == "":
                                print("summoner name blank - name changed or account deleted. ID still works.")
                            print("name: ", k["summonerName"])
                            print("summoner ID: ", k["summonerId"])
    return None

#if you have a summonerid, you can get the puuid with this, then you can get the information you need
def get_summoner_info_by_summonerid():
    print("This tool can be used to find summoners who have changed their names.")
    summonerId = input("Please enter summoner ID: ")
    api_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={settings.API_KEY}"
    response_data = hit_api(api_url)
    for i in response_data:
        print(i, ": ", response_data[i])
        if i == "puuid":
            info_dump['puuid'] = response_data[i]


    print("\nThis player has been set as target!")

    return None

def set_api_key():
    print("Current API key: ", settings.API_KEY)
    newKey = input("Enter new API key: ")
    settings.API_KEY = newKey
    return None

##UTILITY FUNCTIONS

def hit_api(url):
    try: 
        response = requests.get(url, params=urlencode(params))
        response.raise_for_status()
        response_data = response.json()
        
        return response_data
    except requests.exceptions.RequestException as e:
        #print(f'Issue getting summoner data from API: {e}')
        return e
    
def progoff():
    if programOn: programOn = False

##UI MGMT

def print_title():
    global display_width
    for title_item in title:
        print(f"{title_item:-^{display_width}}\n")
    return None

def change_menu_state():
    global menuState
    if menuState == 1: menuState = 0
    if menuState == 0: menuState = 1

def display_main_menu():
    global menuState
    menuState = 0
    for thischoice in choices:
                #spchr = ' '
                if display_width < 100:
                    if ord(thischoice['num']) % 2 == 0: spchr = '~'
                    #dl = int(display_width / 1.2 - len(thischoice['desc']))
                    print(f"  {thischoice['num']:<}  {thischoice['desc']:.^}")

                else: 
                    #dl = display_width / 2 - len(thischoice['desc'])
                    print(f"  {thischoice['num']:>30}  {thischoice['desc']: ^}")
    
    choice = input(f"{'Please pick an option: ': ^30}")
    print("Choice: ", choice, "\n")
    choiceNums = [str(1), str(2), str(3), str(4), str(5), str(6), str(7)]
    while choice not in choiceNums:
        choice = input("Invalid input- please pick an option: ")
        #print("Choice: ", choice, "\n")
            
    if choice in choiceNums:
        print("Choice is: ", choices[int(choice)-1]['desc'])
        ##exception for options menu which needs a parameter
        if int(choice) == 6:
            choices[5]['func']()
            menuState = 1
            return None
        else: choices[int(choice)-1]['func']()

def display_options_menu():
    print_title()
    global menuState
    menuState = 1
    for schoice in schoices:
        #spchr = ' '
        if display_width < 100:
            if ord(schoice['num']) % 2 == 0: spchr = '~'
            #dl = int(display_width / 1.2 - len(schoice['desc']))
            print(f"  {schoice['num']:<}  {schoice['desc']:.^}")

        else: 
            #dl = display_width / 2 - len(schoice['desc'])
            print(f"  {schoice['num']:>30}  {schoice['desc']: ^}")
    
    schoice = input(f"{'Please pick an option: ': ^30}")
    
    print("Choice: ", schoice, "\n")
    schoiceNums = [str(1), str(2)]
    while schoice not in schoiceNums:
        schoice = input("Invalid input- please pick an option: ")
        #print("Choice: ", choice, "\n")
            
    if schoice in schoiceNums:
        print("Choice is: ", schoices[int(schoice)-1]['desc'])
        ##exception for options menu which needs a parameter    
        schoices[int(schoice)-1]['func']()
    

        


