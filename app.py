from flask import Flask, render_template, request
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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

        return "<h3 style='text-align:center;'>✅ Entry recorded successfully</h3>"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
