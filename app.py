from flask import Flask, render_template, request, make_response
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------- Flask app ----------------
app = Flask(__name__)

# ---------------- Firebase setup ----------------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- Route ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        vehicle = request.form["vehicle"].upper()
        contact = request.form["contact"]
        amount = int(request.form["amount"])

        today = datetime.now().strftime("%Y-%m-%d")
        doc_id = f"{vehicle}_{today}"

        db.collection("checkins").document(doc_id).set({
            "name": name,
            "vehicle": vehicle,
            "contact": contact,
            "amount": amount,
            "date": today,
            "time": datetime.now()
        })

        response = make_response("✅ Entry recorded successfully")
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

    response = make_response(render_template("index.html"))
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# ---------------- Run app ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
