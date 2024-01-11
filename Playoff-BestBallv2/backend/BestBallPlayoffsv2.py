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
import os


# Gets cumalative stats for playoffs
def requestWeek(stat):
    driver = webdriver.Chrome()
    if stat == "passing":
        page = driver.get(
            "https://www.espn.com/nfl/stats/player/_/season/2021/seasontype/3"
        )
        page_final = driver.page_source
    elif stat == "receiving":
        driver.get(
            "https://www.espn.com/nfl/stats/player/_/stat/receiving/season/2021/seasontype/3"
        )
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Show More"))
        )
        a = driver.find_element(By.LINK_TEXT, "Show More").click()
        time.sleep(2)
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Show More"))
        )
        a = driver.find_element(By.LINK_TEXT, "Show More").click()
        time.sleep(2)
        driver.implicitly_wait(10)  # find_element_by_link_text
        page_final = driver.page_source
        driver.close()

    elif stat == "rushing":
        page = driver.get(
            "https://www.espn.com/nfl/stats/player/_/stat/rushing/season/2021/seasontype/3"
        )
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Show More"))
        )
        a = driver.find_element(By.LINK_TEXT, "Show More").click()
        time.sleep(2)
        page_final = driver.page_source
        driver.close()

    return BeautifulSoup(page_final, "html.parser")


def getWeek(soup):
    return soup.find_all("tr"), soup.find_all("th")


def filterWeek(data, headers, POS):
    data_final = [
        [t.get_text() for t in data[game].find_all("td")]
        for game in range(0, len(data))
    ]
    headers_final = [game.get_text() for game in headers]
    headers_final.pop(0)

    data_null = [data for data in data_final if data]
    final_data = []

    for i in range(0, int((len(data_null) / 2))):
        temp = (data_null[i]) + (data_null[i + int((len(data_null) / 2))])
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

    if POS == "QB":
        df = pd.DataFrame(final_data)
        df.columns = headers_final  # d

    if POS == "WR" or POS == "RB":
        df = pd.DataFrame(final_data)
        df.columns = headers_final  # d

    return df, final_data


def getLists(PASSING, REC, RUSH):
    PASSING_list = PASSING["Name"].tolist()
    RUSH_list = RUSH["Name"].tolist()
    REC_list = REC["Name"].tolist()

    return PASSING_list, RUSH_list, REC_list


def getStats(team, passing_stats, rushing_stats, receiving_stats):
    team_dict = dict.fromkeys(team, "0")
    for player in team:
        rec_pts, rush_pts, pass_pts = 0, 0, 0
        if player in passing_stats["Name"].values:
            # Assuming 'YDS' column contains strings like '1,717'
            PASSYDS_str = passing_stats.loc[passing_stats["Name"] == player][
                "YDS"
            ].iloc[0]
            # Remove commas from each element and convert to integer
            try:
                PASSINGYDS = int(PASSYDS_str.replace(",", ""))
            except:
                PASSINGYDS = int(PASSYDS_str)
            PTD = int(passing_stats.loc[passing_stats["Name"] == player]["TD"])
            INT = int(passing_stats.loc[passing_stats["Name"] == player]["INT"])
            pass_pts = (PASSINGYDS / 25) + (PTD * 4) - (INT * 2)

        if player in receiving_stats["Name"].values:
            # Assuming 'YDS' column contains strings like '1,717'
            RECYDS_str = receiving_stats.loc[receiving_stats["Name"] == player][
                "YDS"
            ].iloc[0]
            # Remove commas from each element and convert to integer
            try:
                RECYDS = int(RECYDS_str.replace(",", ""))
            except:
                RECYDS = int(RECYDS_str)
            RECTD = int(receiving_stats.loc[receiving_stats["Name"] == player]["TD"])
            RECs = int(receiving_stats.loc[receiving_stats["Name"] == player]["REC"])
            rec_pts = (RECYDS / 10) + (RECTD * 6) + (RECs)

        if player in rushing_stats["Name"].values:
            # Assuming 'YDS' column contains strings like '1,717'
            RUSHYDS_str = rushing_stats.loc[rushing_stats["Name"] == player][
                "YDS"
            ].iloc[0]
            # Remove commas from each element and convert to integer
            try:
                RUSHYDS = int(RUSHYDS_str.replace(",", ""))
            except:
                RUSHYDS = int(RUSHYDS_str)
            RUSHTD = int(rushing_stats.loc[rushing_stats["Name"] == player]["TD"])
            FUML = int(rushing_stats.loc[rushing_stats["Name"] == player]["FUM"])
            rush_pts = (RUSHYDS / 10) + (RUSHTD * 6) - (FUML * 2)
        formatted_number = round((rec_pts + rush_pts + pass_pts), 2)
        total_pts = f"{formatted_number:.2f}"
        team_dict[player] = total_pts

    return team_dict


def getDraftInfo():
    draft_df = pd.read_excel(r"../files/p.xlsx", usecols="A:F")
    draft_df.columns = ["pick num", "Chase", "David", "Jack", "Ty", "Dustin"]
    print("Final Draft Results: " + "\n")
    print(draft_df)
    chase = draft_df["Chase"].tolist()
    dave_aaron = draft_df["David"].tolist()
    jack = draft_df["Jack"].tolist()
    ty = draft_df["Ty"].tolist()
    dustin = draft_df["Dustin"].tolist()
    return chase, dave_aaron, jack, ty, dustin


def writeCumalitiveStats(cs, ds, js, ts, das, pass_df):
    # TODO: CHAGE FROM HARD CODE!
    # This will be the current week, the max GP of QBs
    week = pass_df["GP"].max()
    week = 1  # ASDFASDFASDFASDFSDFDS
    # Write total stats for each player drafted to a file w/ the playoffs cumalative stats
    # This will write the current weeks cumulative stats
    # E.g. Week 1, this will write everyones stats to Week1.csv
    # Week 2, this will write week1 + week2 stats to Week2.csv
    # Week 3, this will write week1 + week2 + week3 stats to Week3.csv
    # This still writes the players in order of team by draft (CHAnGE)
    with open("../files/Week" + str(week) + ".csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in cs.items():
            writer.writerow([key, value])
        for key, value in ds.items():
            writer.writerow([key, value])
        for key, value in js.items():
            writer.writerow([key, value])
        for key, value in ts.items():
            writer.writerow([key, value])
        for key, value in das.items():
            writer.writerow([key, value])


def createWeekxWeekStats(maxWeek):
    # Let's write out all the logic here.
    # Loop through all the weeks (take the max number again),
    # Get players in the week_scores dict
    week_scores = {}
    for i in range(maxWeek):
        # Get week i points
        current = pd.read_csv("../files/Week" + str(i + 1) + ".csv", header=None)
        for row in current.iterrows():
            player = row[1].iloc[0]
            points = row[1].iloc[1]
            formatted_points = f"{points:.2f}"
            if player not in week_scores:
                week_scores[player] = [0, 0, 0, 0]
            week_scores[player][i] = float(formatted_points)
    # At this point we have cumulative points for each week in a dict for each player (Depending on num of weeks it's been)
    # now let's go through and get difference for each week

    # Go back to front
    for i in range(maxWeek - 1, 0, -1):
        for player in week_scores:
            if week_scores[player][i] == 0:
                pass
            week_scores[player][i] = week_scores[player][i] - week_scores[player][i - 1]

    return week_scores


def remove_other_weeks(data, index):
    return {
        position: [(name, info[1][index]) for name, info in players]
        for position, players in data.items()
    }


def calculate_bestball(team, starting, week):
    best = {}
    # Keep track of who was used to get 2 flex players
    # Iterate through each position in the starting dictionary
    for position, count in starting.items():
        # Filter players for the current position
        position_players = {
            name: data for name, data in team.items() if data[0] == position
        }
        # Sort players by their total points (assuming the points are in index 1 of the list)
        # third x[1][1][1]
        sorted_players = sorted(
            position_players.items(), key=lambda x: x[1][1][week], reverse=True
        )

        # Take the top 'count' players for the current position
        best[position] = sorted_players[:count]

    # Go through the full team again, and take the top two by week points if NOT in best and NOT a QB
    all_sorted_players = sorted(team.items(), key=lambda x: x[1][1][week], reverse=True)
    count = 0
    temp = []
    for player in all_sorted_players:
        if count == 2:
            break
        if (
            all(player[0] not in [item[0] for item in best[key]] for key in best)
            and player[1][0] != "QB"
        ):
            temp.append(player)
            count += 1
    best["W/R/T"] = temp
    return remove_other_weeks(best, week)


def getPlayerPosition(player, passingDF, rushingDF, receivingDF):
    pos = "x"
    if player in passingDF["Name"].values:
        pos = passingDF.loc[passingDF["Name"] == player, "POS"].iloc[0]
    if player in rushingDF["Name"].values:
        pos = rushingDF.loc[rushingDF["Name"] == player, "POS"].iloc[0]
    if player in receivingDF["Name"].values:
        pos = receivingDF.loc[receivingDF["Name"] == player, "POS"].iloc[0]
    return pos.upper()


def finish_weekly_scoring_all(
    allteams, week_scores, starting, passingDF, rushingDF, receivingDF, maxweek
):
    all_player_stats = []
    for team in allteams:
        temp = {}
        for name, points in week_scores.items():
            if name in team:
                position = getPlayerPosition(name, passingDF, rushingDF, receivingDF)
                temp[name] = [position, points]
        all_player_stats.append(temp)

    # now we have players points for each week, players + positions on each team
    names = ["Chase", "Dustin", "Jack", "Ty", "Dave-Aaron"]
    team_all_weeks = []
    for i in range(len(all_player_stats)):
        team_weeks = []
        for j in range(maxweek):
            weekly_team_score = calculate_bestball(all_player_stats[i], starting, j)
            team_weeks.append(["Week" + str(j + 1), weekly_team_score])
        team_all_weeks.append([names[i], team_weeks])

    return team_all_weeks


def weekly_sum_flatten(all_teams_weekly_scoring):
    flattened_data = []
    for player, weeks in all_teams_weekly_scoring:
        for week, stats in weeks:
            weekly_sum = 0
            player_data = [player, week]
            for position, player_stats in stats.items():
                for name, values in player_stats:
                    weekly_sum += values
                    values = f"{values:.2f}"
                    flattened_data.append(player_data + [position, name, values])
            flattened_data.append([player, week, "-", "Total", round(weekly_sum, 2)])

    print(flattened_data)
    # Write to .txt
    with open("../playoff-bestball-fe/public/final.txt", "w") as f:
        for line in flattened_data:
            f.write(f"{line}\n")

    # Create a DataFrame
    df = pd.DataFrame(
        flattened_data, columns=["Player", "Week", "Position", "Name", "Points"]
    )

    # Pivot the DataFrame to get the desired structure
    df_pivot = df.pivot_table(
        index=["Position", "Name"], columns="Week", values="Points", aggfunc="sum"
    ).reset_index()

    # Reorder columns
    df_pivot = df_pivot[["Name", "Week1"]]
    # Write DataFrame to Excel file
    df.to_excel("../files/fantasy_stats.xlsx", index=False)

    return df


def main():
    # Read draft, put each team in a list, begin!
    # FORMAT: jack = ['Cooper Kupp', 'Tom Brady',...]
    chase, dave_aaron, jack, ty, dustin = getDraftInfo()

    # Do we need to fetch new data?
    # fetch = input("Should we fetch new data? (y to fetch, anything else to pass): ")
    # if fetch == "y":
    # Stats for each category
    data, headers = getWeek(requestWeek("passing"))
    PASSING, qb_fd = filterWeek(data, headers, "QB")
    data, headers = getWeek(requestWeek("rushing"))
    RUSH, rush_fd = filterWeek(data, headers, "RB")
    data, headers = getWeek(requestWeek("receiving"))
    REC, rec_fd = filterWeek(data, headers, "WR")

    # Write data so we don't need to fetch again
    PASSING.to_csv("../files/passing.csv")
    RUSH.to_csv("../files/rushing.csv")
    REC.to_csv("../files/receiving.csv")

    # If not fetching, we get from here
    PASSING = pd.read_csv("../files/passing.csv", index_col=0)
    RUSH = pd.read_csv("../files/rushing.csv", index_col=0)
    REC = pd.read_csv("../files/receiving.csv", index_col=0)

    # This is a list of names in each stat category (nice to have)
    passing_list, rushing_list, receiving_list = getLists(PASSING, REC, RUSH)

    # This gets the cumalative stats for each player on someones team
    # As we run this program each week, this will create an updated sheet
    # So this only needs to be run once per week
    # chase_stats = getStats2(chase, PASSING, RUSH, REC)
    chase_stats = getStats(chase, PASSING, RUSH, REC)
    dustin_stats = getStats(dustin, PASSING, RUSH, REC)
    jack_stats = getStats(jack, PASSING, RUSH, REC)
    ty_stats = getStats(ty, PASSING, RUSH, REC)
    dave_aaron_stats = getStats(dave_aaron, PASSING, RUSH, REC)

    # Writes to files
    writeCumalitiveStats(
        chase_stats, dustin_stats, jack_stats, ty_stats, dave_aaron_stats, PASSING
    )
    maxWeek = int(PASSING["GP"].max())
    maxWeek = 2  # ASDFJLKSDJFAKLSDFJAKLDSFJKLSDFJLASDKFJASDKLJFAKLDSFJKLASDFJKLS
    week_scores = createWeekxWeekStats(maxWeek)

    allteams = [chase_stats, dustin_stats, jack_stats, ty_stats, dave_aaron_stats]

    starting = {"QB": 1, "RB": 2, "WR": 2}
    all_teams_weekly_scoring = finish_weekly_scoring_all(
        allteams, week_scores, starting, PASSING, RUSH, REC, maxWeek
    )

    finished_df = weekly_sum_flatten(all_teams_weekly_scoring)
    print("\n")
    print(finished_df)


main()
