import requests
import json
import sys
from bs4 import BeautifulSoup

class Cricbuzz():
    url="http://synd.cricbuzz.com/j2me/1.0/livematches.xml"
    def __init__(self):
        pass
    def getxml(self, url):
        try:
            r=requests.get(url)
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    def matchinfo(self,match):
        d={}
        d['id']=match['id']
        d['srs']=match['srs']
        d['type']=match['type']
        try:
            d['mchDesc'] = match['mchdesc']
        except:
            pass
        d['mnum']=match['mnum']
        d['mchstate'] = match.state['mchstate']
        d['status'] = match.state['status']
        d['inngCnt']=match['inngcnt']
        return d

    def matches(self):
        xml=self.getxml(self.url)
        matches = xml.find_all('match')
        info=[]
        for match in matches:
            info.append(self.matchinfo(match))
        return info

    def livescore(self,mid):
        xml = self.getxml(self.url)
        match = xml.find(id=mid)
        if match is None:
            return 'Invalid Match id.'
        if match.state['mchstate'] == 'nextlive':
            return 'Match not yet started.'
        curl = match['datapath']+'commentary.xml'
        comm = self.getxml(curl)
        mscr = comm.find('mscr')
        batting = mscr.find('bttm')
        bowling = mscr.find('blgtm')
        batsman = mscr.find_all('btsmn')
        bowler = mscr.find_all('blrs')

        data={}
        d={}
        data['matchinfo']=self.matchinfo(match)
        d['team']=batting['sname']
        d['Score']=[]
        d['Batsman']=[]
        for player in batsman:
            d['Batsman'].append({'name':player['sname'],'runs':player['r'],'balls':player['b'],'fours':player['frs'],'six':player['sxs']})
        binngs = batting.find_all('inngs')
        for inng in binngs:
            d['Score'].append({'desc': inng['desc'], 'runs': inng['r'], 'wickets': inng['wkts'], 'overs': inng['ovrs']})
        data['Batting'] = d
        d = {}
        d['team'] = bowling['sname']
        d['Score'] = []
        d['Bowler'] = []
        for player in bowler:
            d['Bowler'].append(
                {'name': player['sname'], 'overs': player['ovrs'], 'maidens': player['mdns'], 'runs': player['r'],
                 'wickets': player['wkts']})
        bwinngs = bowling.find_all('inngs')
        for inng in bwinngs:
            d['Score'].append({'desc': inng['desc'], 'runs': inng['r'], 'wickets': inng['wkts'], 'overs': inng['ovrs']})
        data['Bowling'] = d
        return data

    def commentary(self,mid):
        xml=self.getxml(self.url)
        match = self.getxml(id=url)
        if match is None:
            return "Invalid Match id"
        elif match.state["mchstate"]=="nextlive":
            return "Match not started yet"
        curl=match['datapath']+"commentary.xml"
        comm=self.getxml(curl).find_all('c')
        d=[]
        for c in comm:
            d.append(c.text)
        data={}
        data['matchinfo']=self.matchinfo(match)
        data['commentary']=d
        return data

    def scorecard(self,mid):
        xml=self.getxml(self.url)
        match=xml.find(id=mid)
        if match is None:
            return "Invalid match id"
        elif match.state['mchstate']=="nextlive":
            return "Match not started yet"
        surl=match['datapath']+"scorecard.xml"
        scard = self.getxml(surl)
        scrs=scard.find('scrs')
        innings=scrs.find_all('inngs')
        data={}
        data['matchinfo']=self.matchinfo(match)
        squads=scard.find('squads')
        teams=scard.find_all('teams')
        sq=[]
        sqd={}
        for team in teams:
            sqd['team']=team['name']
            sqd['members']=[]
            members=team['mem'].split(", ")
            for mem in members:
                sqd['members'].append(mem)
            sq.append(sqd.copy())
        data['squad']=sq
        d=[]
        card={}
        for inng in innings:
            bat = inng.find('bttm')
            card['batteam'] = bat['sname']
            card['runs'] = inng['r']
            card['wickets'] = inng['wkts']
            card['overs'] = inng['noofovers']
            card['runrate'] = bat['rr']
            card['inngdesc'] = inng['desc']
            batplayers=bat.find_all('plyr')
            batsman=[]
            bowlers=[]
            for player in batplayers:
                status = player.find('status').text
                batsman.append({'name': player['sname'], 'runs': player['r'], 'balls': player['b'], 'fours': player['frs'],'six': player['six'],'dismissal':status})
            card['batcard'] = batsman
            bowl = inng.find('bltm')
            card['bowlteam'] = bowl['sname']
            bowlplayers = bowl.find_all('plyr')
            for player in bowlplayers:
                bowlers.append({'name': player['sname'], 'overs': player['ovrs'], 'maidens': player['mdns'],
                                   'runs': player['roff'], 'wickets': player['wkts']})
            card['bowlcard'] = bowlers
            d.append(card.copy())
            data['scorecard'] = d
            return data

c=Cricbuzz()

teams={"INDIA":"Ind","NEW ZEALAND":"NZ","AUSTRALIA":"Aus","PAKISTAN":"Pak","ENGLAND":"Eng","IRELAND":"IRE","AFGANISTAN":"Afg"}
ch=1
if(ch==1):
    team=input("Team name: ")
    matches=c.matches()
    flag="false"
    if team.upper() in teams.keys():
        team_name=teams[team.upper()]
        for match in matches:
            if team_name.upper() in match['mchDesc'].upper():
                print("Team {0} has a match live".format(team))
                flag="true"
                ans = input("Display {0}'s match details: (yes/no). ".format(team))
                if ans == 'yes':
                    mid=match['id']
                    scr=input("View complete scorecard (yes/no): ")
                    if(scr=='yes'):
                        score=c.scorecard(mid)
                        print("Match Details-------------------------")
                        print("{0}, {1}".format(score['matchinfo']['mnum'], score['matchinfo']['srs']))
                        print("{0}".format(score['matchinfo']['status']))
                        for i in reversed(score['scorecard']):
                            count=0
                            print("Innings {0} scorecard---------------------".format(count))
                            print("Batting Team: {0}".format(i["batteam"]))
                            print("Bowling Team: {0}".format(i['bowlteam']))
                            print("Runs Scored: {0}".format(i['runs']))
                            print("Runrate: {0}".format(i['runrate']))
                            print("Wickets Down: {0}".format(i['wickets']))
                            print("Overs: {0}".format(i['overs']))
                            print("Batting card------------------------------")
                            for j in i['batcard']:
                                print("************")
                                print("Name: {0}".format(j['name']))
                                print("Runs scored: {0}".format(j['runs']))
                                print("Balls played: {0}".format(j['balls']))
                                print("Fours: {0}".format(j['fours']))
                                print("Six: {0}".format(j['six']))
                                print("Dismissal: {0}".format(j['dismissal']))
                            print("Bowling card------------------------------")
                            for j in i['bowlcard']:
                                print("************")
                                print("Name: {0}".format(j['name']))
                                print("Runs given: {0}".format(j['runs']))
                                print("Overs delivered: {0}".format(j['overs']))
                                print("Wickets: {0}".format(j['wickets']))
                                print("Maiden overs: {0}".format(j['maidens']))

                    mid=match['id']
                    while(ans=="yes"):
                        live=c.livescore(mid)
                        print("Match Details-------------------------")
                        print("{0}, {1}".format(live['matchinfo']['mnum'], live['matchinfo']['srs']))
                        print("{0}".format(live['matchinfo']['status']))

                        print("Batting Details-----------------------")
                        print("Batting Team: {0}".format(live['Batting']['team']))
                        print("Overs played: {0}".format(live['Batting']['Score'][0]['overs']))
                        print("Runs scored: {0}".format(live['Batting']['Score'][0]['runs']))
                        print("Wickets down: {0}".format(live['Batting']['Score'][0]['wickets']))
                        print("Batsman details-----------------------")
                        print("Batsman: {0}".format(live['Batting']['Batsman'][0]['name']))
                        print("Runs scored: {0}".format(live['Batting']['Batsman'][0]['runs']))
                        print("Balls faced: {0}".format(live['Batting']['Batsman'][0]['balls']))
                        print("Six: {0}".format(live['Batting']['Batsman'][0]['six']))
                        print("Fours: {0}".format(live['Batting']['Batsman'][0]['fours']))
                        print("--------------------------------------")
                        print("Batsman: {0}".format(live['Batting']['Batsman'][1]['name']))
                        print("Runs scored: {0}".format(live['Batting']['Batsman'][1]['runs']))
                        print("Balls faced: {0}".format(live['Batting']['Batsman'][1]['balls']))
                        print("Six: {0}".format(live['Batting']['Batsman'][1]['six']))
                        print("Fours: {0}".format(live['Batting']['Batsman'][1]['fours']))

                        print("Bowling Details-----------------------")
                        print("Bowling Team: {0}".format(live['Bowling']['team']))
                        print("Bowler details-----------------------")
                        print("Bowler: {0}".format(live['Bowling']['Bowler'][0]['name']))
                        print("Wickets taken: {0}".format(live['Bowling']['Bowler'][0]['wickets']))
                        print("Overs delivered: {0}".format(live['Bowling']['Bowler'][0]['overs']))
                        print("Maiden overs delivered: {0}".format(live['Bowling']['Bowler'][0]['maidens']))
                        print("Runs given: {0}".format(live['Bowling']['Bowler'][0]['runs']))
                        print("--------------------------------------")
                        print("Bowler: {0}".format(live['Bowling']['Bowler'][1]['name']))
                        print("Wickets taken: {0}".format(live['Bowling']['Bowler'][1]['wickets']))
                        print("Overs delivered: {0}".format(live['Bowling']['Bowler'][1]['overs']))
                        print("Maiden overs delivered: {0}".format(live['Bowling']['Bowler'][1]['maidens']))
                        print("Runs given: {0}".format(live['Bowling']['Bowler'][1]['runs']))
                        ans=input("Refresh data (yes/no) :")
                break
        if flag=="false":
            print("Team {0} has no match live".format(team))
    else:
        print("Team doesn't exist")