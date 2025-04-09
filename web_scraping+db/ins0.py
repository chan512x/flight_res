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
        with open(f'air-irctc_scrape/{src}-{dest}/{date_str}.json','r') as jsonf:
            data=json.load(jsonf)
            # print(data)
            for row in data:
                airline= row["airline"]
                if airline=="SpiceJet Ltd":
                     airline="SpiceJet"
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
                price=row["price"][2:]
                if stop=="0":
                    fl=0
                    fid=""
                    sid=""
                    for c in id:
                        if c=='/':
                            fl=1
                            continue
                        if fl==0:
                            fid+=c
                        else:
                            sid+=c
                    if fl==1:
                            temp=cur.execute('''SELECT * FROM FSCHEDULE WHERE flight_id=%s AND whe=%s AND dept=%s''',(fid,date_str,dept)).fetchone()
                            if temp:
                                 cur.execute('''UPDATE FSCHEDULE SET ai_price=%s WHERE flight_id=%s AND whe=%s AND dept=%s''',(price, fid, date_str, dept))
                            else:
                                cur.execute('''INSERT INTO FSCHEDULE (flight_id,airline,whe,dept,fro,from_code,arrival,toooo,to_code,duration,stops,ai_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(fid,airline,whe,dept,fro,from_code,arriv,to,to_code,dur,stop,price,))
                            temp=cur.execute('''SELECT * FROM FSCHEDULE WHERE flight_id=%s AND whe=%s AND dept=%s''',(sid,date_str,dept)).fetchone()
                            if temp:
                                 cur.execute('''UPDATE FSCHEDULE SET ai_price=%s WHERE flight_id=%s AND whe=%s AND dept=%s''',(price, sid, date_str, dept))
                            else:
                                cur.execute('''INSERT INTO FSCHEDULE (flight_id,airline,whe,dept,fro,from_code,arrival,toooo,to_code,duration,stops,ai_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(sid,airline,whe,dept,fro,from_code,arriv,to,to_code,dur,stop,price,))
                            
                    else:
                            print("ye")
                            temp=cur.execute('''SELECT * FROM FSCHEDULE WHERE flight_id=%s AND whe=%s AND dept=%s''',(id,date_str,dept)).fetchone()
                            if temp:
                                 cur.execute('''UPDATE FSCHEDULE SET ai_price=%s WHERE flight_id=%s AND whe=%s AND dept=%s''',(price, id, date_str, dept))
                            else:
                                cur.execute('''INSERT INTO FSCHEDULE (flight_id,airline,whe,dept,fro,from_code,arrival,toooo,to_code,duration,stops,ai_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(id,airline,whe,dept,fro,from_code,arriv,to,to_code,dur,stop,price,))
                    conn.commit()
        print(f"Saved data for {date_str}")
        current_date += timedelta(days=1)

except Exception as E:
    conn.rollback()
    raise E
finally:
    conn.close()