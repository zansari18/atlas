from flask import Flask, request, session, jsonify
from flask_cors import CORS
import os
from math import radians, sin, cos, sqrt, atan2
import models.db as db

app = Flask(__name__)
#key from Railway
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

CORS(app, supports_credentials=True)
 

#Haversine Distance Function

def haversine(lat1, lon1, lat2, lon2):
    R=3958.8 #for miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lat1

    a= sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2 )**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c

# routes 
@app.route("/")
def home(): 
    return "Backend is running!" 

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    pw = data.get("password")

    user = db.get_user_by_username(username)
    if user is None:
        return jsonify({"error": "Invalid username or password"}), 400

    from werkzeug.security import check_password_hash
    if not check_password_hash(user["password_hash"], pw):
        return jsonify({"error": "Invalid username or password"}), 400

    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return jsonify({"message": "Logged in successfully"})

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/updateLocation", methods="POST")
def update_location():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    lat = data.get("latitude")
    lon = data.get("longitude")

    if lat is None or lon is None:
        return jsonify({"error": "Missing latitude or longitude"}), 400

    db.update_location(session["user_id"], lat, lon)

    return jsonify({"message": "Location updated"})

@app.route("/distance", methods=["GET"])
def distance():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    rows = db.get_locations()

    if len(rows) < 2:
        return jsonify({"error": "Not enough users"}), 400

    # Expect exactly 2 users
    user1 = rows[0]
    user2 = rows[1]

    if user1["latitude"] is None or user2["latitude"] is None:
        return jsonify({"message": "Waiting for locations", "milesApart": None})

    d = haversine(
        user1["latitude"], user1["longitude"],
        user2["latitude"], user2["longitude"]
    )

    return jsonify({"milesApart": round(d, 2)})


# App Startup


if __name__ == "__main__":
    db.init_db()

    #only run once! make 2 users
    db.create_user("Zuha", "ZA73853!")
    db.create_user("Suwaiba", "SM73757!")

    port =  int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)