from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
options=webdriver.ChromeOptions()
options.add_argument("--no-headless")
options.add_argument("--disable-gpu")
source="BLR"
dest="DEL"
url=f"https://flight.easemytrip.com/FlightList/Index?srch=BLR-Bengaluru-India|DEL-NewDelhi-%20India|05/04/2025&px=1-0-0&cbn=0&ar=undefined&isow=true&isdm=true&lang=en-us&curr=INR&apptype=B2C"
driver=webdriver.Chrome(options=options)
driver.get(url=url)
try:
    sleep(10)
    WebDriverWait(driver,20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR,'[og="BLR"]'))
    )
    cards=driver.find_elements(By.CSS_SELECTOR,'[og="BLR"]')
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
    print(mlist)
finally:
    driver.close()