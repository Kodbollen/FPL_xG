import numpy as np
import pandas as pd
import time
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

FPL_url = "https://fantasy.premierleague.com/statistics"
fbref_urls = [('https://fbref.com/en/squads/18bb7c10/Arsenal-Stats', 'ARS'),
              ('https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats', 'MCI'),
              ('https://fbref.com/en/squads/b2b47a98/Newcastle-United-Stats', 'NEW'),
              ('https://fbref.com/en/squads/361ca564/Tottenham-Hotspur-Stats', 'TOT'),
              ('https://fbref.com/en/squads/19538871/Manchester-United-Stats', 'MUN'),
              ('https://fbref.com/en/squads/822bd0ba/Liverpool-Stats', 'LIV'),
              ('https://fbref.com/en/squads/d07537b9/Brighton-and-Hove-Albion-Stats', 'BHA'),
              ('https://fbref.com/en/squads/cff3d9bb/Chelsea-Stats', 'CHE'),
              ('https://fbref.com/en/squads/fd962109/Fulham-Stats', 'FUL'),
              ('https://fbref.com/en/squads/cd051869/Brentford-Stats', 'BRE'),
              ('https://fbref.com/en/squads/47c64c55/Crystal-Palace-Stats', 'CRY'),
              ('https://fbref.com/en/squads/8602292d/Aston-Villa-Stats', 'AVL'),
              ('https://fbref.com/en/squads/a2d435b3/Leicester-City-Stats', 'LEI'),
              ('https://fbref.com/en/squads/4ba7cbea/Bournemouth-Stats', 'BOU'),
              ('https://fbref.com/en/squads/5bfb9659/Leeds-United-Stats', 'LEE'),
              ('https://fbref.com/en/squads/7c21e445/West-Ham-United-Stats', 'WHU'),
              ('https://fbref.com/en/squads/d3fd31cc/Everton-Stats', 'EVE'),
              ('https://fbref.com/en/squads/e4a775cb/Nottingham-Forest-Stats', 'NFO'),
              ('https://fbref.com/en/squads/33c895d4/Southampton-Stats', 'SOU'),
              ('https://fbref.com/en/squads/8cec06e1/Wolverhampton-Wanderers-Stats', 'WOL')]


def setup_driver(site_url):
    # Setting up chromedriver
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path='/usr/bin/geckodriver', options=options)
    driver.get(site_url)

    return driver


def scrape_player_values():
    print('\nSetting up driver\n')
    driver = setup_driver(FPL_url)

    time.sleep(5)
    # Decline cookies
    driver.find_element(By.CLASS_NAME, 'js-accept-all-close').click()
    time.sleep(10)

    
    next_btn = driver.find_element(By.CLASS_NAME, 'PaginatorButton__Button-xqlaki-0.cDdTXr')

    player_list = []
    for i in range(23):
        if i > 0:
            next_btn.click()

        players = driver.find_elements(By.CLASS_NAME, 'ElementTable__ElementRow-sc-1v08od9-3.kGMjuJ')

        for i, p in enumerate(players):
            name = p.find_element(By.CLASS_NAME, 'ElementInTable__Name-y9xi40-1.heNyFi').text
            team, pos = p.find_element(By.CLASS_NAME, 'ElementInTable__Info-y9xi40-2.XzKWB').find_elements(By.TAG_NAME, 'span')
            team = team.text
            pos = pos.text
            table_data = p.find_elements(By.TAG_NAME, 'td')
            value = table_data[2].text
            pts = table_data[5].text
            print(f'{name:<14}, {team}, {pos}, {value}, {pts}')

            player_list.append([name, team, pos, value, pts])

    driver.close()
    return np.array(player_list)


def scrape_player_stats():
    player_list = []
    # for url in ["https://fbref.com/en/squads/a2d435b3/Leicester-City-Stats"]:
    for i, (url, team) in enumerate(fbref_urls):
        print(f'Scraping {i+1} of {len(fbref_urls)}\n{url.split("/")[-1]}')
        try:
            driver = setup_driver(url)
            table = driver.find_element(By.CLASS_NAME, 'stats_table')
            rows = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                if not row.get_attribute('class') == '': # Disregard repeating table headers. 
                    continue
                player = []

                data = row.find_elements(By.TAG_NAME, 'td')
                name = row.find_element(By.XPATH, './th/a').text
                try:
                    country = row.find_element(By.XPATH, './td[@data-stat="nationality"]/a/span').text.split(" ")[1]
                except:
                    continue
                stats = [] # country goals, assists, xg, xg_assist, npxg_xg_assist
                stats.append(row.find_element(By.XPATH, './td[@data-stat="games"]').text)
                stats.append(row.find_element(By.XPATH, './td[@data-stat="games_starts"]').text)
                stats.append(row.find_element(By.XPATH, './td[@data-stat="minutes"]').text)                
                stats.append(row.find_element(By.XPATH, './td[@data-stat="goals"]').text)
                stats.append(row.find_element(By.XPATH, './td[@data-stat="assists"]').text)
                stats.append(row.find_element(By.XPATH, './td[@data-stat="xg"]').text)
                stats.append(row.find_element(By.XPATH, './td[@data-stat="xg_assist"]').text)
                stats.append(row.find_element(By.XPATH, './td[@data-stat="npxg_xg_assist"]').text)

                player.append(name)
                player.append(team)
                player.append(country)


                # Replace empty strings with 0.
                for stat in stats:
                    if stat == '':
                        stat = 0
                    player.append(stat)

                player_list.append(player)
                print(player)
        finally:
            driver.close()

    return np.array(player_list)
    

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'value':
        value_info = scrape_player_values()
        df = pd.DataFrame(value_info, columns=['name', 'team', 'position', 'value', 'points'])
        df.to_csv('value_info.csv', index=False)

    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        stat_info = scrape_player_stats()
        df = pd.DataFrame(stat_info, columns=['name', 'team', 'country', 'games', 'starts', 'mins',
                                              'goals', 'assists', 'xg', 'xa', 'npxg_xa'])
        df.to_csv('stat_info.csv', index=False)

