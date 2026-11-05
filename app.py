import os
from urllib.parse import urlparse
from flask import Flask, jsonify, request
from datetime import datetime

app=Flask(__name__)
records=[]

def mysql_connection():
    """Return a MySQL connection when DATABASE_URL is configured; otherwise None."""
    url=os.getenv("DATABASE_URL", "")
    if not url.startswith("mysql"):
        return None
    try:
        import mysql.connector
        parsed=urlparse(url)
        return mysql.connector.connect(host=parsed.hostname, port=parsed.port or 3306, user=parsed.username, password=parsed.password, database=parsed.path.lstrip("/"))
    except Exception as error:
        print(f"[Database] MySQL unavailable, using memory fallback: {error}")
        return None

@app.get("/")
def index(): return jsonify(application="Waste records sample", records=len(records))

@app.post("/records")
def create_record():
    data=request.get_json(silent=True) or {}
    if not data.get("material"): return jsonify(error="material is required"),400
    record={"material":data["material"],"confidence":float(data.get("confidence",0)),"advice":data.get("advice",""),"created_at":datetime.now().isoformat()}
    connection=mysql_connection()
    if connection:
        cursor=connection.cursor(); cursor.execute("INSERT INTO waste_records (material, confidence, advice) VALUES (%s, %s, %s)", (record["material"], record["confidence"], record["advice"])); connection.commit(); cursor.close(); connection.close()
    records.append(record); return jsonify(record),201

@app.get("/records")
def list_records(): return jsonify(records)

if __name__=="__main__": app.run(debug=False)
