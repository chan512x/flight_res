import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from time import sleep
options = webdriver.ChromeOptions()
options.add_argument("--no-headless")
options.add_argument("--disable-gpu")

source = "BOM"
dest = "DEL"
start_date = datetime(2025, 4, 1)
end_date = datetime(2025, 4, 30)
output_dir = f"magicfares_scrape/{source}-{dest}/"
os.makedirs(output_dir, exist_ok=True)

driver = webdriver.Chrome(options=options)

try:
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url=f"https://www.magicfares.in/flight/results?dep={source}&arr={dest}&dd={date_str}&ad=&adt=1&chd=0&inf=0&agid=10778&cha=B2C&tt=1&srctyp=flt&uid=null&nonstp=false&prefarln=&cl=ec"
        driver.get(url=url)
        sleep(20)
        WebDriverWait(driver,20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR,'[class="resultsBlock"]'))
        )
        cards=driver.find_elements(By.CSS_SELECTOR,'[class="resultsBlock"]')
        print(cards)
        mlist=[]
        for card in cards:
            pp = card.text.split('\n')
            airline = pp[0].strip()
            ide = pp[1].split(' ')
            id=ide[0]+'-'+ide[1]
            dept = pp[2]
            te = pp[4]
            fro = te[:-4].strip()
            from_code = source
            dur = pp[5]
            stop = pp[6]
            arriv = pp[7][0:6].strip()
            te1 = pp[9]
            to = te1[:-4].strip()
            to_code = dest
            price = pp[10]+pp[11]
            
            mlist.append({
                "airline": airline,
                "flight_id": id,
                "departure": dept,
                "from": fro,
                "from_code": from_code,
                "arrival": arriv,
                "to": to,
                "to_code": to_code,
                "duration": dur,
                "stops": stop,
                "price": price
            })
        file_path = os.path.join(output_dir, f"{date_str}.json")
        with open(file_path, "w") as json_file:
            json.dump(mlist, json_file, indent=4)
        
        print(f"Saved data for {date_str}")
        current_date += timedelta(days=1)
        
finally:
    driver.quit()
