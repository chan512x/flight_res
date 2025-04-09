import snowflake.connector
import json

# Connect to Snowflake
conn = snowflake.connector.connect(
    user="chan",
    password="Chandanlseg1021",
    account="WQBSYUO-PU72483",
    autocommit=False,  # Not needed for SELECT, but fine if you're doing updates later
    database="FLIGHTS",
    schema="MAIN"
)
cur = conn.cursor()

try:
    query = '''
    SELECT 
        COALESCE(a.flight_id, e.flight_id, m.flight_id) AS flight_id,
        COALESCE(a.whe, e.whe, m.whe) AS whe,
        COALESCE(a.dept, e.dept, m.dept) AS dept,
        COALESCE(a.airline, e.airline, m.airline) AS airline,
        COALESCE(a.fro, e.fro, m.fro) AS from_location,
        COALESCE(a.from_code, e.from_code, m.from_code) AS from_code,
        COALESCE(a.arrival, e.arrival, m.arrival) AS arrival,
        COALESCE(a.toooo, e.toooo, m.toooo) AS destination,
        COALESCE(a.to_code, e.to_code, m.to_code) AS to_code,
        COALESCE(a.duration, e.duration, m.duration) AS duration,
        COALESCE(a.stops, e.stops, m.stops) AS stops,
 
        a.price AS air_irctc_price,
        e.price AS easemytrip_price,
        m.price AS magic_fares_price
    FROM AIR_IRCTC a
    FULL OUTER JOIN EASEMYTRIP e 
        ON a.flight_id = e.flight_id AND a.whe = e.whe AND a.dept = e.dept
    FULL OUTER JOIN MAGICFARES m 
        ON COALESCE(a.flight_id, e.flight_id) = m.flight_id 
        AND COALESCE(a.whe, e.whe) = m.whe 
        AND COALESCE(a.dept, e.dept) = m.dept;
    '''
    
    cur.execute(query)

    # Fetch the results
    results = cur.fetchall()
    print(results)
    # Fetch column names
    # columns = [desc[0] for desc in cur.description]

    # # Convert to JSON format
    # flights_data = [dict(zip(columns, row)) for row in results]

    # # Print JSON result
    # print(json.dumps(flights_data, indent=4))

except Exception as E:  
    print("Error:", str(E))

finally:
    cur.close()
    conn.close()
