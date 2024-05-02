from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# Inspired from https://github.com/mbsmebye/StravaScraper
def get_last_weeks_leaderboard(strava_url):
    user_agent = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    )
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(options=options)
    driver.get(strava_url)
    driver.find_element(By.XPATH, '//*[@class="button last-week"]').click()

    table = driver.find_element(By.XPATH, '//*[@class="dense striped sortable"]')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    leaderboard = []
    rows.pop(0)  # Skip the header row
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        leaderboard.append({
            "rank": int(cells[0].text),
            "user_name": cells[1].text.strip(),
            "total_distance": cells[2].text,
            "number_of_runs": int(cells[3].text),
            "longest_run": cells[4].text,
            "avg_pace": cells[5].text,
            "total_elevation_gain": cells[6].text
        })
    return leaderboard
