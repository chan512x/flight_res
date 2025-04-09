#om
import os
import snowflake.connector
from flask import Flask,jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask import request,Response
from flask_cors import CORS
import psycopg2
import uuid
import json
from datetime import datetime,timedelta
load_dotenv()
app=Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'chan'
conn1=psycopg2.connect(
        host="localhost",
        database="flights",
        user="postgres",
        password=os.environ['DB_PASSWORD']
    )
cur1=conn1.cursor()
jwt = JWTManager(app)
bcrypt = Bcrypt(app)  
CORS(app)
conn = snowflake.connector.connect(
    user=os.environ['user'],
    password=os.environ['password'],
    account=os.environ['acc'],
    autocommit=False,
    database="FLIGHTS",
    schema="MAIN1"
)   
cur = conn.cursor()
def predictor(cf_date):
    TEMP1=cur.execute('''
         SELECT AVG(MAXIMUM) FROM (SELECT WHE, MAX(AI_PRICE) AS MAXIMUM FROM FSCHEDULE GROUP BY WHE)
     ''').fetchall() 
    print(TEMP1)
    # print(TEMP1)
    TEMP2=cur.execute('''
        SELECT AVG(MAXIMUM) FROM (SELECT WHE, MAX(EMT_PRICE) AS MAXIMUM FROM FSCHEDULE GROUP BY WHE)
    ''').fetchall()
    print(TEMP2)
    TEMP3=cur.execute('''
        SELECT AVG(MAXIMUM) FROM (SELECT WHE, MAX(MF_PRICE) AS MAXIMUM FROM FSCHEDULE GROUP BY WHE)
    ''').fetchall()
    print(TEMP3)



    cf_date1=datetime.strptime(cf_date,'%Y-%m-%d')#input

    cday=datetime.now()

    pp=cf_date1.day-cday.day

    delta=pp+1

    sprice0=0

    sprice1=0

    sprice2=0

    ccft=0

    close=10000

    wcft=1000   

    if delta<=5:

        sprice0=TEMP1[0][0]

        sprice1=TEMP2[0][0]

        sprice2=TEMP3[0][0]

        if delta==0:

            ccft=0.2

        elif delta==1:

            ccft=0.15

        elif delta==2:

            ccft=0.10

        elif delta==3:

            ccft=0.075

        else:

            ccft=0.05

            sprice0+=close*ccft

            sprice1+=close*ccft

            sprice2+=close*ccft

    try:

        day=cf_date1.strftime('%a')

        if day=='Fri' or day=='Sat' or day=='Sun':

            sprice0+=wcft

            sprice1+=wcft

            sprice2+=wcft

        #handle hits

        hcft=0

        sprice0+=hcft

        sprice1+=hcft

        sprice2+=hcft

        extra=0

        if delta<=5:

            extra=1

        temp=[]

        temp.append(sprice0)

        temp.append(sprice1)

        temp.append(sprice2)

        temp.append(extra)

        print(temp)

        return temp

    except :

        temp=[]

        print("ye")

        temp.append(0,1,2)

        return temp


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

  
    # Check if user already exists
    cur1.execute("SELECT uid FROM user_cred WHERE email_id = %s", (email,))
    if cur1.fetchone():
        return jsonify({"msg": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert user (let SERIAL uid auto-increment)
    cur1.execute(
        "INSERT INTO user_cred (email_id, hpassword) VALUES (%s, %s) RETURNING uid",
        (email, hashed_password)
    )
    new_uid = cur1.fetchone()[0]
    conn1.commit()
    access_token = create_access_token(identity=new_uid)

    return jsonify({
        "msg": "User created successfully",
        "uid": new_uid, 
        "access_token": access_token
    }), 201

# 🔑 Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    cur1.execute("SELECT uid, hpassword FROM user_cred WHERE email_id = %s", (email,))
    user = cur1.fetchone()
   

    if user and bcrypt.check_password_hash(user[1], password):
        access_token = create_access_token(identity=user[0])
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401

@app.route("/fetch",methods=['POST'])
@jwt_required()
def gettodos():

    try:

        fro=request.get_json()['from']

        to=request.get_json()['to']

        date=request.get_json()['date']

        query1='''SELECT flight_id,

                whe,

                dept,

                airline,

                fro AS from_location,

                from_code,

                arrival,

                toooo AS destination,

                to_code,

                duration,

                stops,

                ai_price AS air_irctc_price,

                emt_price AS easemytrip_price,

                mf_price AS magicfares_price

                FROM FSCHEDULE WHERE from_code=%s AND to_code=%s AND whe=%s'''



        ppxx=predictor(date)

        cur.execute(query1,(fro,to,date))

        res=cur.fetchall()

        print(res)

        tlist=[]

        print("dodo")

        for row in res:

            air=row[3]

            # cur.execute('''SELECT url FROM airline_img WHERE name=(%s)''',(air,))

            # p1=cur.fetchone()

            imgg=""

            # if (p1 is not None):

            #     imgg=p1[0]

            pp=row[1]

            ac=pp.strftime('%d %b')

            if ac[0]=="0":

                ac=ac[1:]

            pp1=row[2]

            ac1=pp1.strftime('%H:%M')

            pp2=row[6]

            ac2=pp2.strftime('%H:%M')

            if pp1>pp2:

                pp+=timedelta(days=1)

            ac3=pp.strftime('%d %b')

            if ac3[0]=='0':

                ac3=ac3[1:]

            mi=float('inf')

            mp=[]

            if ppxx[3]==1:

                if row[11] is not None:

                    mp.append(ppxx[0])

                else:

                    mp.append(0)

                if row[12] is not None:

                    mp.append(ppxx[1])

                else:

                    mp.append(0)

                if row[13] is not None:

                    mp.append(ppxx[2])

                else:

                    mp.append(0)

            else:

                if row[11] is not None:

                    mp.append(row[11]+ppxx[0])

                else:

                    mp.append(0)

                if row[12] is not None:

                    mp.append(row[12]+ppxx[1])

                else:

                    mp.append(0)

                if row[13] is not None:

                    mp.append(row[13]+ppxx[2])

                else:

                    mp.append(0)



            if row[11] is not None and mp[0]!= 0:

                mi=min(mi,mp[0])

            if row[12] is not None and mp[1] != 0:

                mi=min(mi,mp[1])

            if row[13] is not None and mp[2] != 0:

                mi=min(mi,mp[2])
            be=""
            if mi==mp[0]:
                be="air_irctc"
            if mi==mp[1]:
                be="easemytrip"
            if mi==mp[2]:
                be="magicfares"
            print(be)
            print(mi)
            print(mp)

            temp={

                'id':row[0],

                'dept_time':ac1,

                'from':row[5],

                'dept_date':ac,

                'type':"Direct",

                'duration':row[9],

                'arriv_time':ac2,

                'to':row[8],

                'arriv_date':ac3,

                'airline':row[3],

                'bag':"123",

                'ai_price':mp[0],

                'emt_price':mp[1],

                'mf_price':mp[2],

                'price':mi,

                'best':be,

                'flex':"1",

                'img':imgg

            }

            tlist.append(temp)

        return Response(json.dumps(tlist),status=200)

    except:

        return Response("error",status=400)


@app.route("/book",methods=['POST'])
@jwt_required()
def book():
    user=get_jwt_identity()
    data=request.get_json()
    sf=data['selFlight']
    ap=data['aprice']
    print(sf['id'])
    cur1.execute('''SELECT BID FROM FBOOKINGS WHERE FLIGHT_ID=%s AND DEPT_DATE=%s AND DEPT_TIME=%s''',(sf['id'],sf['dept_date'],sf['dept_time'],))
    temp=cur1.fetchone()
    if temp is not None:
        bid=cur1[0]
    else:
        cur1.execute(
        '''
        INSERT INTO FBOOKINGS (
            FLIGHT_ID, DEPT_TIME, DEPT_DATE, FRO, TOOOO, TYPE, DURATION, 
            ARRIV_TIME, ARRIV_DATE, AIRLINE, BAG, AI_PRICE, EMT_PRICE, MF_PRICE, 
            PRICE, PPRICE, BEST, FLEX, TSTAMP
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING BID
        ''',
        (
            sf['id'], sf['dept_time'], sf['dept_date'], sf['from'], sf['to'],
            sf['type'], sf['duration'], sf['arriv_time'], sf['arriv_date'],
            sf['airline'], sf['bag'], sf['ai_price'], sf['emt_price'], sf['mf_price'],
            sf['price'], ap, sf['best'], sf['flex'], datetime.now()
        )
    )
        bid = cur1.fetchone()[0]
    cur1.execute(
    '''INSERT INTO UBOOKINGS (UID, BID) VALUES (%s, %s)''',
    (user, bid)
    )
    conn1.commit()
    print(sf)
    print(ap)
    return jsonify("success",201)
@app.route("/fbook",methods=['POST'])
@jwt_required()
def fbook():
    print("hello")
    user=get_jwt_identity()
    print(user)
    cur1.execute(
    '''
    SELECT f.*
    FROM UBOOKINGS u
    JOIN FBOOKINGS f ON u.BID = f.BID
    WHERE u.UID = %s
    ORDER BY f.TSTAMP DESC
    ''',
    (user,)
    )
    bookings = cur1.fetchall()
    formatted_bookings = []
    
    # Process each booking row
    for row in bookings:
        # Extract all necessary fields
        # Assuming the column order matches your needed fields
        # Adjust indices based on your actual query results
        
        temp = {
            'FLIGHT_ID': row[0],
            'DEPT_TIME': row[1],
            'DEPT_DATE': row[2],
            'FRO': row[3],
            'TOOOO': row[4],
            'TYPE': row[5],
            'DURATION': row[6],
            'ARRIV_TIME': row[7],
            'ARRIV_DATE': row[8],
            'AIRLINE': row[9],
            'BAG': row[10],
            'AI_PRICE': row[11],
            'EMT_PRICE': row[12],
            'MF_PRICE': row[13],
            'PRICE': row[14],
            'PPRICE': row[15],
            'BEST': row[16],
            'FLEX': row[17],
            'TSTAMP': str(row[18]) if row[18] else None  # Convert datetime to string if needed
        }
        
        formatted_bookings.append(temp)
    
    print(formatted_bookings)
    return jsonify(formatted_bookings), 201
if __name__ == "__main__":

    app.run(debug=True)
