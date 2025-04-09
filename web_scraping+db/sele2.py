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
start_date = datetime(2025, 4, 3)
end_date = datetime(2025, 4, 30)
output_dir = f"easemytrip/{source}-{dest}/"
os.makedirs(output_dir, exist_ok=True)

driver = webdriver.Chrome(options=options)

try:
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%Y")
        url=f"https://flight.easemytrip.com/FlightList/Index?srch=BOM-Mumbai-India|DEL-Delhi-India|{date_str}&px=1-0-0&cbn=0&ar=undefined&isow=true&isdm=true&lang=en-us&curr=INR&apptype=B2C"
        driver.get(url)
        sleep(20)
        WebDriverWait(driver,20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR,f'[og="{source}"]'))
        )
        cards=driver.find_elements(By.CSS_SELECTOR,f'[og="{source}"]')
        mlist=[]
        print(cards)
        for card in cards:
            pp=card.text.split('\n')
            x=pp[0].strip()
            if x=="Enjoy Free Meals":
                j=1
            else:
                j=0
            airline = pp[0+j].strip()
            id=pp[1+j].strip()
            dept = pp[2+j].strip()
            te = pp[3+j].strip()
            fro = te
            from_code = source
            dur = pp[4+j].strip()
            stop = pp[5+j].strip()
            arriv = pp[6+j]
            te1 = pp[7+j].strip()
            to = te1
            to_code = dest
            price = pp[9+j]
            
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
            # print(mlist)
        #     break
        # break
        date_str1 = current_date.strftime("%Y-%m-%d")

        file_path = os.path.join(output_dir, f"{date_str1}.json")
        with open(file_path, "w") as json_file:
            json.dump(mlist, json_file, indent=4)
        
        print(f"Saved data for {date_str} in {file_path}")
        current_date += timedelta(days=1)
        
finally:
    driver.quit()
