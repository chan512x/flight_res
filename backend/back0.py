#om
import os
import snowflake.connector
from flask import Flask,jsonify
from dotenv import load_dotenv
from flask import request,Response
from flask_cors import CORS
import json
from datetime import datetime,timedelta
load_dotenv()
import psycopg2
from flask_jwt_extended import JWTManager, decode_token,create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_jwt_extended.exceptions import JWTDecodeError
app=Flask(__name__)
bcrypt = Bcrypt(app)

conn = snowflake.connector.connect(
    user=os.environ['user'],
    password=os.environ['password'],
    account=os.environ['acc'],
    autocommit=False,
    database="FLIGHTS",
    schema="MAIN0"
)
app.config["JWT_SECRET_KEY"] = "chan" 
jwt = JWTManager(app)
CORS(app)

conn1 = psycopg2.connect(
        host="localhost",
        database="flights",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])
    
cur = conn.cursor()
cur1=conn1.cursor()
source="BLR"
dest="DEL"
def predictor(source,dest,cf_date):
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
        cur1.execute('''SELECT * FROM  DPRICE WHERE FRO=%s AND TOOOO=%s AND WHE=%s''',(source,dest,cf_date,))
        hres=cur1.fetchone()
        hcft=0
        if hres is None:
            cur1.execute('''INSERT INTO DPRICE (FRO, TOOOO, WHE, CTR, INC_VAL, ACT_VAL) VALUES(%s,%s,%s,%s,%s,%s)''',(source,dest,cf_date,1,500,0,))
            conn1.commit()
        else:
            ctr=hres[3]
            nval=hres[4]+hres[5]
            if ctr==4:
                cur1.execute('''UPDATE DPRICE SET ctr=%s, act_val=%s WHERE FRO=%s AND TOOOO=%s AND WHE=%s''',(0,nval,source,dest,cf_date,))
                hcft=nval
            else:
                cur1.execute('''UPDATE DPRICE SET ctr=%s WHERE FRO=%s AND TOOOO=%s AND WHE=%s''',(ctr+1,source,dest,cf_date,))
                hcft=hres[5]
            conn1.commit()
            PP=20

        sprice0+=hcft
        sprice1+=hcft
        sprice2+=hcft
        extra=0
        if delta<=5:
            extra=1
        temp=[]
        sprice0=round(sprice0,2)
        sprice1=round(sprice1,2)
        sprice2=round(sprice2,2)
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
    cur1.execute("SELECT uid FROM user_cred WHERE email_id = %s", (email,))
    if cur1.fetchone():
        return jsonify({"msg": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cur1.execute(
        "INSERT INTO user_cred (email_id, hpassword) VALUES (%s, %s) RETURNING uid",
        (email, hashed_password)
    )
    new_uid = cur1.fetchone()[0]
    conn1.commit()
    access_token = create_access_token(identity=str(new_uid))

    return jsonify({
        "msg": "User created successfully",
        "uid": new_uid, 
        "access_token": access_token
    }), 201

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
        access_token = create_access_token(identity=str(user[0]))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401
@jwt_required
@app.route("/fetch",methods=['POST'])
def gettodos():
    try:
        fro=request.get_json()['from']
        to=request.get_json()['to']
        source=fro
        dest=to
        date=request.get_json()['date']
        print(fro,to,date)
        query1='''SELECT F.*,
                A.url
                FROM FSCHEDULE F, AIRLINE_IMG A WHERE F.from_code=%s AND F.to_code=%s AND F.whe=%s AND A.nam=F.airline'''

        cur.execute(query1,(fro,to,date))
        res=cur.fetchall()
        ppxx=predictor(fro,to,date)

        print(res)
        tlist=[]
        for row in res:
            air=row[3]
            imgg=row[14]
            pp=row[2]
            ac=pp.strftime('%d %b')
            if ac[0]=="0":
                ac=ac[1:]
            pp1=row[3]
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

            if row[11] is not None:
                mi=min(mi,mp[0])
            if row[12] is not None:
                mi=min(mi,mp[1])
            if row[13] is not None:
                mi=min(mi,mp[2])
            be=""
            if mi==row[11] or mi==mp[0]:
                be="Air_Irctc"
            if mi==row[12] or mi==mp[1]:
                be="Easemytrip"
            if mi==row[13] or mi==mp[2]:
                be="MagicFares"
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
                'airline':row[1],
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
    print(ap)
    cur1.execute('''SELECT BID FROM FBOOKINGS WHERE FLIGHT_ID=%s AND DEPT_DATE=%s AND DEPT_TIME=%s AND PRICE=%s''',(sf['id'],sf['dept_date'],sf['dept_time'],ap))
    temp=cur1.fetchone()
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if temp is not None:
        bid=temp[0]
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
            sf['price'], ap, sf['best'], sf['flex'], timestamp_str
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
    print(bookings)
    dt=datetime.now()
    for row in bookings:
        fl=False
        fl1=False
        at_date=row[3]+" 2025"
        adate=datetime.strptime(at_date,"%d %b %Y")
        pp=adate.day-dt.day+1
        if pp>=1:
            fl=True
            fl1=True
        temp = {
            'FLIGHT_ID': row[1],
            'DEPT_TIME': row[2],
            'DEPT_DATE': row[3],
            'FRO': row[4],
            'TOOOO': row[5],
            'TYPE': row[6],
            'DURATION': row[7],
            'ARRIV_TIME': row[8],
            'ARRIV_DATE': row[9],
            'AIRLINE': row[10],
            'BAG': row[11],
            'AI_PRICE': row[12],
            'EMT_PRICE': row[13],
            'MF_PRICE': row[14],
            'PRICE': row[15],
            'PPRICE': row[16],
            'BEST': row[17],
            'FLEX': row[18],
            'TSTAMP': str(row[19]) if row[18] else None,
            'CANCELLABLE':str(fl),
            'UPCOMING':str(fl1),
            'BID':str(row[0]) 
        }
        
        formatted_bookings.append(temp)
    
    print(formatted_bookings)
    return jsonify(formatted_bookings), 201

@app.route("/cancel",methods=['POST'])
@jwt_required()
def cancel():
    data=request.get_json()
    bid=data['bid']
    user=get_jwt_identity()
    cur1.execute('''DELETE FROM UBOOKINGS WHERE BID=%s AND UID=%s''',(bid,user,))
    return jsonify("success"),201

@app.route("/graph",methods=['GET'])
def graph():
    
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
    dx1=datetime.now()
    dx=datetime.strftime(dx1,"%Y-%m-%d")
    air_irctc=cur.execute('''SELECT WHE, MIN(AI_PRICE) AS MINIMUM FROM FSCHEDULE WHERE WHE>=%s GROUP BY WHE
     ORDER BY WHE''',(dx)).fetchall() 
    emt=cur.execute('''
        SELECT WHE, MIN(EMT_PRICE) AS MINIMUM FROM FSCHEDULE WHERE WHE>=%s GROUP BY WHE
    ORDER BY WHE''',(dx)).fetchall()
    mf=cur.execute('''SELECT WHE, MIN(MF_PRICE) AS MINIMUM FROM FSCHEDULE WHERE WHE>=%s GROUP BY WHE
    ORDER BY WHE''',(dx)).fetchall()
    cday=datetime.now()
    mairtc=[]
    memt=[]
    mmf=[]
    pp=4
    delta=1
    for i in range(len(air_irctc)):
        cf_date1=mf[i][0]
        sprice0=0
        sprice1=0
        sprice2=0
        ccft=0
        close=10000
        wcft=1000   
        if delta<=5 and delta>=0:
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
        else:
            sprice0=air_irctc[i][1]
            sprice1=emt[i][1]
            sprice2=mf[i][1]
        print(sprice0,delta) 
        delta+=1
        try:
            day=cf_date1.strftime('%a')
            if day=='Fri' or day=='Sat' or day=='Sun':
                sprice0+=wcft
                sprice1+=wcft
                sprice2+=wcft
            #handle hits
            hcft=0
            cur1.execute('''SELECT * FROM  DPRICE WHERE FRO=%s AND TOOOO=%s AND WHE=%s''',(source,dest,cf_date1,))
            hres=cur1.fetchone()
            hcft=0
            if hres is None:
                print("ye")
            else:
                hcft=hres[5]
            sprice0+=hcft
            sprice1+=hcft
            sprice2+=hcft
            if delta<=0:
                sprice0+=air_irctc[i][1]
                sprice1+=emt[i][1]
                sprice2+=mf[i][1]
            act=[]
            act.append(air_irctc[i][0])
            act.append(sprice0)
            mct=[]
            mct.append(emt[i][0])
            mct.append(sprice1)
            mft=[]
            mft.append(mf[i][0])
            mft.append(sprice2)
            mairtc.append(act)
            memt.append(mct)
            mmf.append(mft)
        except Exception as e:
            temp=[]
            print("ye")
            print(e)
            return temp
    print(air_irctc)
    print(mairtc)
    return jsonify({"aictc":mairtc,"emt":memt,"mf":mmf}),201
if __name__ == "__main__":
    app.run(debug=True)
