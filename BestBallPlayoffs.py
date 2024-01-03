from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from datetime import datetime
import csv
from itertools import islice
from tk import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import sys

# conda activate bestballplayoffs

def requestWeek(stat): 
    
    s = Service('/usr/local/bin/chromedriver') 

    driver = webdriver.Chrome(service=s)  



    if(stat == 'passing'):
        page = driver.get("https://www.espn.com/nfl/stats/player")
        page_final = driver.page_source   
    if(stat == 'receiving'):
        driver.get("https://www.espn.com/nfl/stats/player/_/stat/receiving")
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT,'Show More')))
        a = driver.find_element(By.LINK_TEXT,'Show More').click()
        time.sleep(2)
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT,'Show More')))
        a = driver.find_element(By.LINK_TEXT,'Show More').click()
        time.sleep(2)
        driver.implicitly_wait(10) #find_element_by_link_text
        page_final = driver.page_source  
        driver.close()

    if(stat == 'rushing'):
        page = driver.get("https://www.espn.com/nfl/stats/player/_/stat/rushing")
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT,'Show More')))
        a = driver.find_element(By.LINK_TEXT,'Show More').click()
        time.sleep(2)
        page_final = driver.page_source 
        driver.close()  

    
    return BeautifulSoup(page_final, 'html.parser')


def getWeek(soup):
    return soup.find_all('tr'), soup.find_all('th')


def filterWeek(data, headers, POS):

    data_final = [[t.get_text() for t in data[game].find_all('td')] for game in range(0, len(data))]
    headers_final = [game.get_text() for game in headers]
    headers_final.pop(0)
    
    data_null = [data for data in data_final if data]
    final_data = []
    
    for i in range(0,int((len(data_null)/2))):
        temp = ((data_null[i])+(data_null[i+int((len(data_null)/2))]))
        final_data.append(temp)

    for data in final_data:
        temp_1 = data[1]
        temp = temp_1[-3:]
        count = 0 
        for ch in temp:
            if ch.isupper():
                count += 1
        data[1] = temp_1[:-count]
        data.pop(0)
            

    final = []
    columns = []


    if (POS == "QB"):

        df = pd.DataFrame(final_data)
        df.columns = headers_final  # d
        
    if (POS == "WR" or POS == "RB"):

        df = pd.DataFrame(final_data)
        df.columns = headers_final  # d


    return df,final_data


data,headers = getWeek(requestWeek("passing"))
QBs,qb_fd = filterWeek(data,headers,"QB")
data,headers = getWeek(requestWeek("rushing"))
RUSH,rush_fd = filterWeek(data,headers,"RB")
data,headers = getWeek(requestWeek("receiving"))
REC,rec_fd = filterWeek(data,headers,"WR")


draft_df = pd.read_excel (r'p.xlsx', usecols = 'A:F')
draft_df.columns = ["pick num","Chase","David","Jack","Ty","Dustin"]
chase = draft_df["Chase"].tolist()
Dave_Aaron = draft_df["David"].tolist()
Jack = draft_df["Jack"].tolist()
Ty = draft_df["Ty"].tolist()
dustin = draft_df["Dustin"].tolist()




def getLists(QBs,REC,RUSH):
    
    QB_list = QBs["Name"].tolist()
    RUSH_list = RUSH["Name"].tolist()
    REC_list = REC["Name"].tolist()
    
    return QB_list,RUSH_list, REC_list

def getStats(team):
    team_dict = dict.fromkeys(team, "0")
    for player in team:
        rec_pts,rush_pts,pts = 0,0,0
        
        if player in QB_list:
            # if(player == 'Patrick Mahomes'):
            #     # print(player)
            #     # temp_PYDS = str(QBs.loc[QBs["Name"] == player]['YDS'])
            #     # print(temp_PYDS)
            #     # y = temp_PYDS[5:]
            #     # x = y.replace(',','')
            #     # print(x)
            #     PYDS = 1057
            # elif(player == 'Joe Burrow'):
            #     PYDS = 1105
            # elif(player == 'Matthew Stafford'):
            #     PYDS = 1188
            # else:
            PYDS = int(QBs.loc[QBs["Name"] == player]['YDS'])
            PTD = int(QBs.loc[QBs["Name"] == player]['TD'])
            INT = int(QBs.loc[QBs["Name"] == player]['INT'])
            pts = (PYDS/25)+(PTD*4)-(INT*2)
        if player in RUSH_list:
            RYDS = int(RUSH.loc[RUSH["Name"] == player]['YDS'])
            RTD = int(RUSH.loc[RUSH["Name"] == player]['TD'])
            FUML = int(RUSH.loc[RUSH["Name"] == player]['FUM'])
            rush_pts = (RYDS/10)+(RTD*6)-(FUML*2)
        if player in REC_list:
            RECYDS = int(REC.loc[REC["Name"] == player]['YDS'])
            RECTD = int(REC.loc[REC["Name"] == player]['TD'])
            RECs = int(REC.loc[REC["Name"] == player]['REC'])
            rec_pts = (RECYDS/10)+(RECTD*6)+(RECs)
        total_pts = round((rec_pts + rush_pts + pts),2)
        
        team_dict[player] = total_pts
    
    return team_dict
    

QB_list,RUSH_list, REC_list = getLists(QBs,REC,RUSH)
chase_stats = getStats(chase) # ceedee 
dustin_stats = getStats(dustin)
Jack_stats = getStats(Jack)
Ty_stats = getStats(Ty)
Dave_Aaron_stats = getStats(Dave_Aaron)



dateTimeObj = datetime.now()
date = (str(dateTimeObj.year)+str(dateTimeObj.month)+str(dateTimeObj.day))



with open(''+date+'.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    for key, value in chase_stats.items():
        writer.writerow([key, value])
    for key, value in dustin_stats.items():
        writer.writerow([key, value])
    for key, value in Jack_stats.items():
        writer.writerow([key, value])
    for key, value in Ty_stats.items():
        writer.writerow([key, value])
    for key, value in Dave_Aaron_stats.items():
        writer.writerow([key, value])

######## chnage date of previous csv date ############################

date = str(2023123)

chase_prev = pd.read_csv(''+date+'.csv', nrows=14, header = None)
david_aron_prev = pd.read_csv(''+date+'.csv', skiprows=56, nrows=14, header = None)
jack_prev = pd.read_csv(''+date+'.csv', skiprows=28, nrows=14, header = None)
ty_prev = pd.read_csv(''+date+'.csv', skiprows=42, nrows=14, header = None)
dustin_prev = pd.read_csv(''+date+'.csv', skiprows=14, nrows=14, header = None)


chase_prev_dict = {}
keys = chase_prev[0].tolist()
values = chase_prev[1].tolist()
chase_prev_dict = dict(zip(keys,values))

david_aron_prev_dict = {}
keys = david_aron_prev[0].tolist()
values = david_aron_prev[1].tolist()
david_aron_prev_dict = dict(zip(keys,values))

jack_prev_dict = {}
keys = jack_prev[0].tolist()
values = jack_prev[1].tolist()
jack_prev_dict = dict(zip(keys,values))

ty_prev_dict = {}
keys = ty_prev[0].tolist()
values = ty_prev[1].tolist()
ty_prev_dict = dict(zip(keys,values))

dustin_prev_dict = {}
keys = dustin_prev[0].tolist()
values = dustin_prev[1].tolist()
dustin_prev_dict = dict(zip(keys,values))


qb_name = QBs[['Name','POS']]
rush_names = RUSH[['Name','POS']]
rec_names = REC[['Name','POS']]
final_names = pd.concat([qb_name,rush_names,rec_names]).drop_duplicates().reset_index(drop=True)


def player_pos(team):
    
    team_list = [*team]
    pos_list = []
    pos_dict = {}
    POS = 0
    for player in team_list:
        POS = final_names.loc[final_names["Name"] == player]['POS']
        if POS.empty:
            POS = 0
        else:
            POS = final_names.loc[final_names["Name"] == player]['POS'].values.item()
        pos_list.append(POS)

    pos_dict = dict(zip(team,pos_list))
    return pos_dict
            

chase_pos = player_pos(chase_stats)
david_aron_pos = player_pos(Dave_Aaron_stats)
jack_pos = player_pos(Jack_stats)
ty_pos = player_pos(Ty_stats)
dustin_pos = player_pos(dustin_stats)

# chase_curr = get_current_pts(chase_stats,chase_prev_dict,"chase") 
# dustin_curr = get_current_pts(dustin_stats,dustin_prev_dict,"dustin") 
# Jack_curr = get_current_pts(Jack_stats,jack_prev_dict,"jack") 
# ty_curr = get_current_pts(Ty_stats,ty_prev_dict,"ty") 
# dave_aaron_curr = get_current_pts(Dave_Aaron_stats,david_aron_prev_dict,"dave") 

def get_current_pts(current_stats,prev_stats,team):
        names = current_stats.keys()
        #print(team)
        for player in names:
            curr = current_stats.get(player)
            prev = prev_stats.get(player)
            if(prev == None):
                prev = 0
            if((curr - prev) != 0 ):
                current_stats[player] = round((curr - prev),1)
            else:
                current_stats[player] = "NA"
            # CHANGE BACK 
            #current_stats[player] = curr
        return current_stats
chase_curr = get_current_pts(chase_stats,chase_prev_dict,"chase") 
dustin_curr = get_current_pts(dustin_stats,dustin_prev_dict,"dustin") 
Jack_curr = get_current_pts(Jack_stats,jack_prev_dict,"jack") 
ty_curr = get_current_pts(Ty_stats,ty_prev_dict,"ty") 
dave_aaron_curr = get_current_pts(Dave_Aaron_stats,david_aron_prev_dict,"dave") 





def get_points(team,pos):
    
    final_dict = {'QB':0,'WR1':0,'WR2':0,'RB1':0,'RB2':0,'FLEX1':0,'FLEX2':0}
    bench_dict = {}
    QB = {"NONE": 0}
    WR = {"NONE": 0,"NONE": 0,"NONE": 0}
    RB = {"NONE": 0,"NONE": 0,"NONE": 0}
    TE = {"NONE": 0,"NONE": 0}

    print(final_dict)
    print("team///////////",team)
    print(pos)
    for player in list(team):
        if (team.get(player) == 'NA'):
            del team[player]


    names = team.keys()

    for player in list(pos):
        if not player in names:
            del pos[player]



    for player in pos:
        if (pos.get(player)) == 'QB':
            pts = team.get(player)
            QB[player] = pts
        if (pos.get(player)) == 'WR':
            pts = team.get(player)
            WR[player] = pts
        if (pos.get(player)) == 'RB':
            pts = team.get(player)
            RB[player] = pts
        if (pos.get(player)) == 'TE':
            pts = team.get(player)
            TE[player] = pts

            
    max_key = max(QB, key=QB.get)

    max_value = max(QB.values())
    final_dict['QB'] = max_value
    
    final_dict[max_key] = final_dict['QB']
    del final_dict['QB']
    
    print(RB)
    max_key = max(RB, key=RB.get)

    max_value = max(RB.values())
    final_dict['RB1'] = max_value
    
    final_dict[max_key] = final_dict['RB1']
    del final_dict['RB1']
    del RB[max_key]
    if(RB == {}):
        del final_dict['RB2']
        pass
    else:
        max_key = max(RB, key=RB.get)

        max_value = max(RB.values())
        final_dict['RB2'] = max_value
        
        final_dict[max_key] = final_dict['RB2']
        del final_dict['RB2']
        del RB[max_key]


    max_key = max(WR, key=WR.get)

    max_value = max(WR.values())
    final_dict['WR1'] = max_value
    
    final_dict[max_key] = final_dict['WR1']
    del final_dict['WR1']
    del WR[max_key]
    
    max_key = max(WR, key=WR.get)

    max_value = max(WR.values())
    final_dict['WR2'] = max_value
    
    final_dict[max_key] = final_dict['WR2']
    del final_dict['WR2']
    del WR[max_key]

    # try:
    #     merge = z = {**RB, **WR, **TE}
    # except:
    #     pass
    #     try: 
    #         merge = z = {**WR, **TE}
    #     except:
    #         pass
    #         try:
    #             merge = z = {**RB, **WR}
    #         except:
    #             pass
    #             try: 
    #                 merge = z = {**RB, **TE}
    #             except:
    #                 pass
    #                 try:
    #                     merge = z = {**RB}
    #                 except:


    #     pass
    #     try: 
    #         merge = z = {**RB, **WR, **TE}
    #     except:
    #         pass

    # if not (RB and WR and TE):
    #     final_dict['FLEX1'] = 0
    #     final_dict['FLEX2'] = 0

    # else:
    #     print("in")
    
    merge =  {**RB, **WR, **TE}

    max_key = max(merge, key=merge.get)

    max_value = max(merge.values())
    final_dict['FLEX1'] = max_value
    
    final_dict[max_key] = final_dict['FLEX1']
    del final_dict['FLEX1']
    del merge[max_key]

    
    max_key = max(merge, key=merge.get)

    max_value = max(merge.values())
    final_dict['FLEX2'] = max_value
    
    final_dict[max_key] = final_dict['FLEX2']
    del final_dict['FLEX2']
    del merge[max_key]
        
    
    return final_dict 
    

def df_final(team,t_sum,t_sum_total):

    print(team)

    sum_df = {'POS': "SUM_Week", 'NAME': "-----", 'POINTS': t_sum}
    sum_df_total = {'POS': "SUM_Toatl", 'NAME': "-----", 'POINTS': t_sum_total}
    display = pd.DataFrame(team.items(), columns=["NAME","POINTS"])
    print(display)
    if ((display.shape[0]) < 7):
        temp = {'NAME': 'NONE', 'POINTS': 0}
        for i in range(0,(7 - (display.shape[0]))):
            display = display.append(temp, ignore_index = True)
    value = ["QB","RB1","RB2","WR1","WR2","FLEX1","FLEX2"]
    print("/////////////",value)
    display.insert(loc=0, column='POS', value=value)
    display = display.append(sum_df, ignore_index = True)
    display = display.append(sum_df_total, ignore_index = True)


    return display


chase = get_points(chase_curr,chase_pos)
david_aron = get_points(dave_aaron_curr,david_aron_pos)
jack = get_points(Jack_curr,jack_pos)
ty = get_points(ty_curr,ty_pos)
dustin = get_points(dustin_curr,dustin_pos)




chase_wk_sum = round((sum(chase.values())),2)
david_aron_wk_sum = round((sum(david_aron.values())),2)
jack_wk_sum = round((sum(jack.values())),2)
ty_wk_sum = round((sum(ty.values())),2)
dustin_wk_sum = round((sum(dustin.values())),2)

dateTimeObj = datetime.now()
date = (str(dateTimeObj.year)+str(dateTimeObj.month)+str(dateTimeObj.day))

prev_date = str(2022131)

# with open('totals-'+prev_date+'.csv', 'r', newline='') as csvDataFile:
#     csvReader = csv.reader(csvDataFile)
#     print(csvReader)
#     rows = list(csvReader)
#     chase_prev_total = rows[0]
#     david_aron_prev_total = rows[1]
#     jack_prev_total = rows[2]
#     ty_prev_total = rows[3]
#     dustin_prev_total = rows[4]

# workbook = xlrd.open_workbook('totals-'+prev_date+'.xls')
# chase_prev_total = worksheet.cell(0, 0)
# david_aron_prev_total = worksheet.cell(1, 0)
# jack_prev_total = worksheet.cell(2, 0)
# ty_prev_total = worksheet.cell(3, 0)
# dustin_prev_total = worksheet.cell(4, 0)
# chase_prev_total = pd.read_csv('totals-'+prev_date+'.csv', nrows=1, header = None)
# david_aron_prev_total = pd.read_csv('totals-'+prev_date+'.csv', skiprows=1, nrows=1, header = None)
# jack_prev_total = pd.read_csv('totals-'+prev_date+'.csv', skiprows=2, nrows=1, header = None)
# ty_prev_total = pd.read_csv('totals-'+prev_date+'.csv', skiprows=3, nrows=1, header = None)
# dustin_prev_total = pd.read_csv('totals-'+prev_date+'.csv', skiprows=4, nrows=1, header = None)

#prev_list = [chase_prev_total,david_aron_prev_total,jack_prev_total,ty_prev_total,dustin_prev_total]

#print(prev_list)

#def chunks(lst, n):
    # for i in range(0, len(lst), n):
    #     yield lst[i:i + n]

# with open('totals-'+date+'.xls', 'w') as csv_file:  
#     writer = csv.writer(csv_file)
#     for chunk in chunks(prev_list, 5):
#         writer.writerow(chunk)
#     # writer.writerow(chase_wk_sum)
#     # writer.writerow(david_aron_wk_sum)
#     # writer.writerow(jack_wk_sum)
#     # writer.writerow(ty_wk_sum)
#     # writer.writerow(dustin_wk_sum)


# chase_fin_total = chase_wk_sum + float(chase_prev_total)
# david_aron_fin_total = david_aron_wk_sum + float(david_aron_prev_total)
# jack_fin_total = jack_wk_sum + float(jack_prev_total)
# ty_fin_total = ty_wk_sum + float(ty_prev_total)
# dustin_fin_total = dustin_wk_sum + float(dustin_prev_total)

# chase_fin_total = chase_wk_sum + 323.88
# david_aron_fin_total = david_aron_wk_sum + 371.98
# jack_fin_total = jack_wk_sum + 326.40
# ty_fin_total = ty_wk_sum + 250.9
# dustin_fin_total = dustin_wk_sum + 246.08

chase_fin_total = chase_wk_sum + 260.12
david_aron_fin_total = david_aron_wk_sum + 227.98
jack_fin_total = jack_wk_sum + 227.6
ty_fin_total = ty_wk_sum + 179.14
dustin_fin_total = dustin_wk_sum  + 239.04

teams = [chase,david_aron,jack,ty,dustin]
t_sums = [chase_fin_total,david_aron_fin_total,jack_fin_total,ty_fin_total,dustin_fin_total]

c_dis = df_final(chase,chase_wk_sum,chase_fin_total)
da_dis = df_final(david_aron,david_aron_wk_sum,david_aron_fin_total)
j_dis = df_final(jack,jack_wk_sum,jack_fin_total)
t_dis = df_final(ty,ty_wk_sum,ty_fin_total)
d_dis = df_final(dustin,dustin_wk_sum,dustin_fin_total)

print(("CHASE"))
print(c_dis)
print("DAVID")
print(da_dis)
print("JACK")
print(j_dis)
print("TY")
print(t_dis)
print("DUSTIN")
print(d_dis)
print('\n')



