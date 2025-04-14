import snowflake.connector
import json
from datetime import datetime, timedelta

conn = snowflake.connector.connect(
    user="chan",
    password="Chandanlseg1021",
    account="VAMNLGV-QF92343",
    autocommit=False,
    database="FLIGHTS",
    schema="MAIN0"
    )

cur=conn.cursor() #https://r-xx.bstatic.com/data/airlines_logo/SG.png"
try:
    cur.execute('''INSERT INTO AIRLINE_IMG (NAM,URL) VALUES (%s,%s)''',("IndiGo","https://r-xx.bstatic.com/data/airlines_logo/6E.png",))
    cur.execute('''INSERT INTO AIRLINE_IMG (NAM,URL) VALUES (%s,%s)''',("Air India Express","https://r-xx.bstatic.com/data/airlines_logo/IX.png",))
    cur.execute('''INSERT INTO AIRLINE_IMG (NAM,URL) VALUES (%s,%s)''',("Akasa Air","https://r-xx.bstatic.com/data/airlines_logo/QP.png",))
    cur.execute('''INSERT INTO AIRLINE_IMG (NAM,URL) VALUES (%s,%s)''',("Air India","https://r-xx.bstatic.com/data/airlines_logo/AI.png",))
    cur.execute('''INSERT INTO AIRLINE_IMG (NAM,URL) VALUES (%s,%s)''',("SpiceJet","https://r-xx.bstatic.com/data/airlines_logo/SG.png",))
    conn.commit()

except Exception as E:
    conn.rollback()
    raise E
finally:
    conn.close() 