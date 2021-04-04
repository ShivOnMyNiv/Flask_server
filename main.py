# Getting watcher stuff ready functions n all
import os
import json as jsons
from riotwatcher import LolWatcher, ApiError

server = "na1"
api_key = open("riot-api-key.env", "r").readline().rstrip()
headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": api_key,
    "Accept-Language": "en-us",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
}

# Loading data dragon
watcher = LolWatcher(api_key)
my_region = 'na1'

current = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
champ = watcher.data_dragon.champions(current, False, 'en_US')["data"]
summoner = watcher.data_dragon.summoner_spells(current, 'en_US')["data"]
items = watcher.data_dragon.items(current, 'en_US')["data"]


exceptionMessage = "There was something wrong with the input"
gameLim = 25    

# Some useful ass methods
def initPlayer(name):
    data = watcher.summoner.by_name(my_region, name)
    playerInfo = {"name": name, "ids": [data['id'], data['accountId']],"20 matches": [], "analysis": {}}
    playerInfo = jsons.dumps(playerInfo)
    
    with open("./Player_Info/" + name + ".json", 'w', encoding="utf-8") as player:
        player.write(playerInfo)

def playerRecorded(filepath: str):
    return os.path.isfile(filepath)

def championId_to_name(id: int):
    global champ
    champions = {}
    for champion in champ:
        key = int(champ[champion]["key"])
        champions[key] = champion
    return champions[id]

def championName_to_Id(name: str):
    global champ
    return champ[name]["key"]

def sumonerSpellID_to_name(id: int):
    global summoner
    summonerSpells = {}
    for summonerSpell in summoner:
        key = int(summoner[summonerSpell]["key"])
        summonerSpells[key] = summoner[summonerSpell]["name"]
    return summonerSpells[id]

def itemID_to_name(id: int):
    global items
    for item in items:
        key = int(item)
        if (key == id):
            return items[item]["name"]
    return ""


def getRole(role: str, lane: str):
    roleDict = {
      "MIDDLE, SOLO": "Mid Laner",
      "TOP, SOLO": "Top Laner",
      "JUNGLE, NONE": "Jungle",
      "BOTTOM, DUO_CARRY": "ADC",
      "BOTTOM, DUO_SUPPORT": "Support"
    }
    return roleDict[lane + ", " + role]


def displayWinrates(matches: dict, userName:str):
    win = 0
    participantId = 0
    for match in matches:
        for player in match['participantIdentities']:
            if player['player']['summonerName'].lower() == userName.lower():
                participantId = player['participantId']

        if participantId <= 5:
            participantId = 0
        else:
            participantId = 1

        if match['teams'][participantId]['win'] == 'Win':
            win += 1

    win_rate = win / len(matches)
    return win_rate

def processMatch(match_detail):
    participants = []
    for row in match_detail['participants']:
        participants_row = {}
        participantId = row['participantId']

        for player in match_detail['participantIdentities']:
            if player['participantId'] == participantId:
                participants_row['summonerName'] = player['player']['summonerName']
                participants_row['summonerId'] = player['player']['summonerId']
                participants_row['profileIcon'] = player['player']['profileIcon']

        participants_row['champion'] = championId_to_name(row['championId'])
        participants_row['champLevel'] = row['stats']['champLevel']
        participants_row['spell1'] = sumonerSpellID_to_name(row['spell1Id'])
        participants_row['spell2'] = sumonerSpellID_to_name(row['spell2Id'])
        participants_row['win'] = row['stats']['win']

        participants_row['kills'] = row['stats']['kills']
        participants_row['deaths'] = row['stats']['deaths']
        participants_row['assists'] = row['stats']['assists']

        # role = row['timeline']['role']
        # lane = row['timeline']['lane']
        # participants_row['role'] = getRole(role, lane)

        participants_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
        participants_row['goldEarned'] = row['stats']['goldEarned']
        participants_row['visionScore'] = row['stats']['visionScore']
        participants_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']

        participants_row['item0'] = itemID_to_name(row['stats']['item0'])
        participants_row['item1'] = itemID_to_name(row['stats']['item1'])
        participants_row['item2'] = itemID_to_name(row['stats']['item2'])
        participants_row['item3'] = itemID_to_name(row['stats']['item3'])
        participants_row['item4'] = itemID_to_name(row['stats']['item4'])
        participants_row['item5'] = itemID_to_name(row['stats']['item5'])
        participants_row['item6'] = itemID_to_name(row['stats']['item6'])
        participants.append(participants_row)
    return participants

# Function to generate tags on player's champion peformance
def generateTags(champPerf, staticChamp, name):
    tags = []
    stats = ["Kills", "Deaths", "Assists", "CS/min", "DMG/min", "KDA"]
    timeRatio = champPerf["Average Game Length"]/staticChamp["averageTime"]
    ratios = []
    
    for stat in stats:
        if champPerf[stat] == "Perfect KDA":
            ratios.append("Perfect KDA")
            continue
        if stat not in "CS/min DMG/min":
            staticChamp[stat] *= timeRatio
        diff = champPerf[stat] - staticChamp[stat]
        ratios.append(diff/staticChamp[stat])
    
    # Kill stats
    if ratios[0] > 0.50:
        tags.append("Gets a LOT of kills")
    elif ratios[0] > 0.10:
        tags.append("Slightly above average killer")
    elif ratios[0] < -0.50:
        tags.append("Pacifist on " + name)
    elif ratios[0] < -0.10:
        tags.append("Slightly below average killer")
    
    # Death stats
    if ratios[1] > 0.50:
        tags.append("Ints on " + name)
    elif ratios[1] > 0.10:
        tags.append("Dies slightly more than average")
    elif ratios[1] < -0.50:
        tags.append("Very good at surviving")
    elif ratios[1] < -0.10:
        tags.append("Dies slightly less than average")
        
    # Assist stats
    if ratios[2] > 0.50:
        tags.append("Incredible assister")
    elif ratios[2] > 0.10:
        tags.append("Gets slightly more assists than average")
    elif ratios[2] < -0.50:
        tags.append("Bad assister")
    elif ratios[2] < -0.10:
        tags.append("Gets slightly less assists than average")
    
    # CS/min stats
    if ratios[3] > 0.50:
        tags.append("Strong farmer")
    elif ratios[3] > 0.10:
        tags.append("Slightly above average CS")
    elif ratios[3] < -0.50:
        tags.append("Hunter Gatherer(doesn't know what farming is)")
    elif ratios[3] < -0.10:
        tags.append("Slightly below average CS")
    
    # DMG/min stats
    if ratios[4] > 0.50:
        tags.append("Incredibly High Damage")
    elif ratios[4] > 0.10:
        tags.append("Slightly above average damage")
    elif ratios[4] < -0.50:
        tags.append("Incredibly Low Damage")
    elif ratios[4] < -0.10:
        tags.append("Slightly less damage than average")
        
    # KDA stats
    if ratios[5] == "Perfect KDA" or ratios[5] > 0.50:
        tags.append("Incredibly High KDA")
    elif ratios[5] > 0.10:
        tags.append("Slightly Higher Average KDA")
    elif ratios[5] < -0.50:
        tags.append("Incredibly Low KDA")
    elif ratios[5] < -0.10:
        tags.append("Slightly lower Average KDA")
        
    return tags

# importing necessary stuff to get riot Data_Dragon
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

# Updating Datadragon jsons
champIndex = 0
def updateJSON():
    global champ, summoner, items, current, champIndex
    # updates json if difference in version
    if current != watcher.data_dragon.versions_for_region(my_region)['n']['champion']:
        print("updating datadragon")
        current = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
        champ = watcher.data_dragon.champions(current, False, 'en_US')["data"]
        summoner = watcher.data_dragon.summoner_spells(current, 'en_US')
        items = watcher.data_dragon.items(current, 'en_US')["data"]
        print("finished updating")
    else:
        print("no update needed")
            
scheduler = BackgroundScheduler()
scheduler.add_job(func=updateJSON, trigger="interval", seconds=60)

scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Readying the pantheon class
def requestsLog(url, status, headers):
    print(url)
    print(status)
    print(headers)

from flask import Flask, jsonify, request
app = Flask("Tridev_League")

@app.route("/")
def helpFunction():
    try:
        helpDict = {}
        helpDict["analyzePlayer"] = "analyzes players and the champs they play"
        helpDict["getRecentMatches"] = "gets the recent matches"
        return jsonify(helpDict)
    except Exception as e:
        return jsonify(str(e))

@app.route("/analyzePlayer")
def analyzePlayer():   
    try:
        name = request.args.get('name').lower()       
        # Check if summoner is already recorded
        report = {}
        matches = []
        if playerRecorded("./Player_Info/" + name + ".json"):
            with open("./Player_Info/" + name + ".json", 'r+', encoding="utf-8") as player:            
                playerInfo = player.read()
                data = jsons.loads(playerInfo)
                matchlist = watcher.match.matchlist_by_account(my_region, data["ids"][1], begin_index=0, end_index=gameLim)
                # retrieving old matches and checking recency
                oldMatches = data["20 matches"]
                # If no games in matchlist then just retrieve the last 20 games
                if len(oldMatches) == 0:    
                    playerIDs = watcher.summoner.by_name(my_region, name)
                    summonerId, accountId = playerIDs["id"], playerIDs["accountId"]
                    matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist['matches']]
                else:            
                    firstMatch = oldMatches[0]
                    # finding number of games played
                    gameLag = -1
                    for i, match in enumerate(matchlist["matches"]):
                        if match["gameId"] == firstMatch["gameId"]:
                            gameLag = i
                    # if more than 20 games are found then just retrieves last 20
                    #print("NUM_RECORDED:", len(oldMatches), gameLag)
                    if gameLag == -1:
                        playerIDs = watcher.summoner.by_name(my_region, name)
                        summonerId, accountId = playerIDs["id"], playerIDs["accountId"]
                        matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist['matches']]
                    elif gameLag == 0 and data["analysis"] != {}:
                        # reusing analysis if no new games were played and analysis exists
                        return jsonify(data["analysis"])
                    else:
                        # otherwise updates games 
                        oldMatches = oldMatches[:len(oldMatches)-gameLag]
                        matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist["matches"][:gameLag]]
                        matches.extend(oldMatches)
        else:
            initPlayer(name)
            playerIDs = watcher.summoner.by_name(my_region, name)
            summonerId, accountId = playerIDs["id"], playerIDs["accountId"]
            matchlist = watcher.match.matchlist_by_account(my_region, accountId, begin_index=0, end_index=gameLim)
            matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist['matches']]
        print("analyzing games:", len(matches))
        champsPlayed = {}
        playerIDs = []
        
        # finding all of my participantIdentities and storing my role
        numGames = len(matches)
        newMatches = []
        for i in range(0, len(matches)):
            if matches[i]["gameMode"] in "ARAM URF ONEFORALL":
                numGames -= 1
                continue
            newMatches.append(matches[i])
            participantIdentities = matches[i]["participantIdentities"]    
            nameID = None
            for j in range(0, len(participantIdentities)):
                if participantIdentities[j]["player"]["summonerName"].lower() == name.lower():
                    nameID = participantIdentities[j]["participantId"]
            playerIDs.append(nameID)
            for participant in matches[i]["participants"]:
                if participant["participantId"] == nameID:
                    champ = championId_to_name(participant["championId"])
                    if champ in champsPlayed:
                        champsPlayed[champ]["amtPlayed"] += 1
                    else:
                        champsPlayed[champ] = {"amtPlayed": 1, "Kills": 0, "Deaths": 0, "Assists": 0, "CS/min": 0, "DMG/min": 0, "Average Game Length": 0}
                    champsPlayed[champ]["Kills"] += int(participant["stats"]["kills"])
                    champsPlayed[champ]["Deaths"] += int(participant["stats"]["deaths"])
                    champsPlayed[champ]["Assists"] += int(participant["stats"]["assists"])
                    champsPlayed[champ]["CS/min"] += round((int(participant["stats"]["neutralMinionsKilled"]) + int(participant["stats"]["totalMinionsKilled"])) / (int(matches[i]["gameDuration"])/60), 1)
                    champsPlayed[champ]["DMG/min"] += round(int(participant["stats"]["totalDamageDealtToChampions"]) / (int(matches[i]["gameDuration"])/60), 1)
                    champsPlayed[champ]["Average Game Length"] += round(float(matches[i]["gameDuration"])/60, 1)
                    if champsPlayed[champ]["Deaths"] > 0:
                        champsPlayed[champ]["KDA"] = round((champsPlayed[champ]["Kills"]+champsPlayed[champ]["Assists"])/champsPlayed[champ]["Deaths"], 2)
                    else:
                        champsPlayed[champ]["KDA"] = "Perfect KDA"
        champList = list(champsPlayed.keys())
        for i in range(0, len(champList)):
            champsPlayed[champList[i]]["Kills"] = champsPlayed[champList[i]]["Kills"]/champsPlayed[champList[i]]["amtPlayed"]
            champsPlayed[champList[i]]["Deaths"] = champsPlayed[champList[i]]["Deaths"]/champsPlayed[champList[i]]["amtPlayed"]
            champsPlayed[champList[i]]["Assists"] = champsPlayed[champList[i]]["Assists"]/champsPlayed[champList[i]]["amtPlayed"]
            champsPlayed[champList[i]]["CS/min"] = champsPlayed[champList[i]]["CS/min"]/champsPlayed[champList[i]]["amtPlayed"]
            champsPlayed[champList[i]]["DMG/min"] = champsPlayed[champList[i]]["DMG/min"]/champsPlayed[champList[i]]["amtPlayed"]
            champsPlayed[champList[i]]["Average Game Length"] = champsPlayed[champList[i]]["Average Game Length"]/champsPlayed[champList[i]]["amtPlayed"]
            staticChamp = None
            with open("./ChampGG/" + champList[i] + ".json", 'r') as JS:
                tags = generateTags(champsPlayed[champList[i]], jsons.loads(JS.read()), champList[i])
                champsPlayed[champList[i]]["tags"] = tags
        
        report["Winrate Last " + str(numGames) + " Games"] = round(displayWinrates(newMatches, name), 2)
        report["Champs Played"] = champsPlayed
        
        # updating player cache
        data = {}
        with open("./Player_Info/" + name + ".json", 'r', encoding="utf-8") as player:
            playerInfo = player.read()
            data = jsons.loads(playerInfo)
            data["20 matches"] = matches
            data["analysis"] = report
            #print("BUTTTTTT:", data)
        with open("./Player_Info/" + name + ".json", 'w', encoding="utf-8") as player:
            data = jsons.dumps(data)
            player.write(data)
        
        return jsonify(report)
    except Exception as e:
        return jsonify(str(e))

@app.route("/getRecentMatches")
def getRecentMatches():
    try:
        name = request.args.get('name') 
        number = request.args.get('number', type=int)
        dataframes = {}
        gameInformationList = []
        gameInformation = {}
        
        # Retrieving and processing matches from json or through requests
        matches = []
        summonerId = ""
        accountId = ''
        if number > gameLim:
            return jsonify("Input limit of " + str(gameLim) + " games")
        
        if playerRecorded("./Player_Info/" + name + ".json"):
            with open("./Player_Info/" + name + ".json", 'r+', encoding="utf-8") as player:            
                playerInfo = player.read()
                data = jsons.loads(playerInfo)
                matchlist = watcher.match.matchlist_by_account(my_region, data["ids"][1], begin_index=0, end_index=number)
                # retrieving old matches and checking recency
                oldMatches = data["20 matches"]
                # If no games in matchlist then just retrieve the last number games
                if len(oldMatches) == 0:    
                    playerIDs = watcher.summoner.by_name(my_region, name)
                    summonerId, accountId = playerIDs["id"], playerIDs["accountId"]
                    matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist['matches']]
                else:            
                    firstMatch = oldMatches[0]
                    # finding number of games played
                    gameLag = -1
                    for i, match in enumerate(matchlist["matches"]):
                        if match["gameId"] == firstMatch["gameId"]:
                            gameLag = i
                    # if more than 20 games are found then just retrieves last 20
                    #print("NUM_RECORDED:", len(oldMatches), gameLag)
                    playerIDs = watcher.summoner.by_name(my_region, name)
                    summonerId, accountId = playerIDs["id"], playerIDs["accountId"]
                    if gameLag == -1:
                        matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist['matches']]
                    elif gameLag == 0:
                        # reusing analysis if no new games were played
                        matches = oldMatches
                    else:
                        # otherwise updates games 
                        oldMatches = oldMatches[:len(oldMatches)-gameLag]
                        matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist["matches"][:gameLag]]
                        matches.extend(oldMatches)
        else:
            initPlayer(name)
            data = watcher.summoner.by_name(my_region, name)
            summonerId, accountId = data["id"], data["accountId"]
            matchlist = watcher.match.matchlist_by_account(my_region, accountId, begin_index=0, end_index=number)
            matches = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist['matches']]
        
        # Adding matches
        gameInformation['summonerId'] = summonerId
        gameInformation['accountId'] = accountId
        gameInformation['winrate'] = displayWinrates(matches, name)
        gameInformation['summonerLevel'] = watcher.summoner.by_name(my_region, name)
        gameInformation['summonerLevel'] = gameInformation['summonerLevel']['summonerLevel']
        try:
            gameInformation['playerStatus'] = watcher.spectator.by_summoner(my_region, summonerId)
        except:
            gameInformation['playerStatus'] = "Not in Game"
        league = watcher.league.by_summoner(my_region, summonerId)
        if len(league) == 0:
            gameInformation['playerLeague'] = 'Unranked'
        else:
            gameInformation['playerLeague'] = league[0]['tier'] + " " + league[0]['rank']
        for i in range(0, number):
            processedMatch = processMatch(matches[i])
            dataframes['match' + str(i + 1)] = processedMatch
        gameInformationList.append(gameInformation)
    
        dataframes['generalInfo'] = gameInformationList
        
        # updating player cache
        data = {}
        with open("./Player_Info/" + name + ".json", 'r', encoding="utf-8") as player:
            playerInfo = player.read()
            data = jsons.loads(playerInfo)
            data["20 matches"] = matches
        with open("./Player_Info/" + name + ".json", 'w', encoding="utf-8") as player:
            data = jsons.dumps(data)
            player.write(data)
        
        return jsonify(dataframes)
    except Exception as e:
        return jsonify(str(e))
    
@app.route("/getSummonerName")
def getSummonerId():
    try:
        name = request.args.get('name') 
        if playerRecorded("./Player_Info/" + name + ".json"):
            with open("./Player_Info/" + name + ".json", 'r') as player:
                data = jsons.load(player)
                return jsonify(data["ids"])
        else:        
            initPlayer(name)     
            with open("./Player_Info/" + name + ".json", 'r') as player:
                data = jsons.load(player)
                return jsonify(data["ids"])
    except Exception as e:
        return jsonify(str(e))

@app.route("/getRecentMatchList")
def getRecentMatchList():
    try:
        name = request.args.get('name') 
        number = request.args.get('number', type=int)
        accountId = watcher.summoner.by_name(my_region, name)
        accountId = accountId["accountId"]
        data = watcher.match.matchlist_by_account(my_region, accountId, begin_index=0, end_index=number)
        return jsonify(data)
    except Exception as e:
        return jsonify(str(e))

@app.route("/getRecentMatchesRaw")
def getRecentMatchesRaw():
    try:
        name = request.args.get('name') 
        number = request.args.get('number', type=int)
        accountId = watcher.summoner.by_name(my_region, name)
        accountId = accountId["accountId"]
        matchlist = watcher.match.matchlist_by_account(my_region, accountId, begin_index=0, end_index=number)
        tasks = [watcher.match.by_id(my_region, match["gameId"]) for match in matchlist['matches']]
        return jsonify(tasks)
    except Exception as e:
        return jsonify(str(e))

@app.route("/getChampionMasteries")
def getChampionMasteries():
    try:
        name = request.args.get('name') 
        summonerId = watcher.summoner.by_name(my_region, name)
        summonerId = summonerId["id"]
        masteries = watcher.champion_mastery.by_summoner(my_region, summonerId)
        for i in range(0, len(masteries)):
            masteries[i]["champName"] = championId_to_name(masteries[i]["championId"])
        def masteryLevel(champ):
            return champ["championLevel"]
        masteries.sort(key=masteryLevel, reverse=True)
        return jsonify(masteries)
    except Exception as e:
        return jsonify(str(e))
    
@app.route("/getSummonerLevel")
def getSummonerLevel():
    try:
        name = request.args.get('name') 
        summoner = watcher.summoner.by_name(my_region, name)
        return jsonify(summoner["summonerLevel"])
    except Exception as e:
        return jsonify(str(e))

@app.route("/getPlayerStatus")
def getPlayerStatus():
    try:
        name = request.args.get('name') 
        summonerId = watcher.summoner.by_name(my_region, name)
        summonerId = summonerId["id"]
        status = watcher.spectator.by_summoner(my_region, summonerId)
        gameInfo = []
        gameInfo.append(status['gameId'])
        gameInfo.append(status['mapId'])
        gameInfo.append(status['gameMode'])
        gameInfo.append(status['gameType'])
        return jsonify(gameInfo)
    except Exception as e:
        print(e)
        return jsonify("Not in game")

@app.route("/getPlayerLeague")
def getPlayerLeague():
    try:
        name = request.args.get('name') 
        summonerId = watcher.summoner.by_name(my_region, name)
        summonerId = summonerId["id"]
        league = watcher.league.by_summoner(my_region, summonerId)
        if len(league) == 0:
            return jsonify('Unranked')
        return jsonify(league[0]['tier'] + " " + league[0]['rank'])
    except Exception as e:
        return jsonify(str(e))

@app.route("/getSummoner")
def getSummoner():
    try:
        name = request.args.get('name') 
        summoner = watcher.summoner.by_name(my_region, name)
        return jsonify(summoner)
    except Exception as e:
        return jsonify(str(e))

if __name__ == "__main__":
    #app.run()
    app.run("0.0.0.0", port=8080)