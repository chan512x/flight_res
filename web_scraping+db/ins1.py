import snowflake.connector
import json
from datetime import datetime, timedelta

conn = snowflake.connector.connect(
    user="chan",
    password="Chandanlseg1021",
    account="WQBSYUO-PU72483",
    autocommit=False,
    database="FLIGHTS",
    schema="MAIN1"
    )
start_date = datetime(2025, 4, 1)
end_date = datetime(2025, 4, 10)
cur=conn.cursor()
try:
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        src="BLR"
        dest="DEL"
        with open(f'easemytrip/{src}-{dest}/{date_str}.json','r') as jsonf:
            data=json.load(jsonf)
            # print(data)
            for row in data:
                airline= row["airline"]
                if airline=="Indigo":
                     airline="IndiGo"
                if airline=="AkasaAir":
                    airline="Akasa Air"
                id=row["flight_id"]
                dept=row["departure"]
                whe=date_str
                fro=row["from"]
                from_code= row["from_code"]
                arriv= row["arrival"]
                to=row["to"]
                to_code=row["to_code"]
                dur= row["duration"]
                stop=row["stops"][0:1]
                price=row["price"]
                mp=""
                for c in price:
                    if(c==','):
                        continue
                    mp+=c
                price=mp

                if stop=="N":
                    stop="0"
                    fid=""
                    sid=""
                    for c in id:
                        if c==' ':
                            continue
                        fid+=c
                    id=fid
                    print("ye")
                    temp=cur.execute('''SELECT * FROM FSCHEDULE WHERE flight_id=%s AND whe=%s AND dept=%s''',(id,date_str,dept)).fetchone()
                    if temp:
                        cur.execute('''UPDATE FSCHEDULE SET emt_price=%s WHERE flight_id=%s AND whe=%s AND dept=%s''',(price, id, date_str, dept))
                    else:
                        cur.execute('''INSERT INTO FSCHEDULE (flight_id,airline,whe,dept,fro,from_code,arrival,toooo,to_code,duration,stops,mf_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(id,airline,whe,dept,fro,from_code,arriv,to,to_code,dur,stop,price,))
                    
                    conn.commit()
        print(f"Saved data for {date_str}")
        current_date += timedelta(days=1)

except Exception as E:
    conn.rollback()
    raise E
finally:
    conn.close()