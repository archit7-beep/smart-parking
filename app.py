from flask import Flask, render_template, request, make_response, redirect, url_for
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os, json



# ---------------- Config ----------------
DAILY_CHARGE = 5          # fixed parking charge per day
LOW_BALANCE_LIMIT = 5    # low balance alert

# ---------------- Flask app ----------------
app = Flask(__name__)

# ---------------- Firebase setup ----------------
firebase_key = json.loads(os.environ.get("FIREBASE_KEY"))

cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)

db = firestore.client()


# ---------------- Main Route ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        vehicle = request.form["vehicle"].upper()
        contact = request.form["contact"]
        amount = int(request.form["amount"])  # can be 0

        today = datetime.now().strftime("%Y-%m-%d")

        # -------- Check if already checked in today --------
        existing = db.collection("checkins") \
            .where("vehicle", "==", vehicle) \
            .where("date", "==", today) \
            .limit(1) \
            .stream()

        already_checked_in = any(existing)

        # -------- Fetch previous balance --------
        user_ref = db.collection("users").document(contact)
        user_doc = user_ref.get()

        balance = 0
        if user_doc.exists:
            balance = user_doc.to_dict().get("balance", 0)

        total_available = balance + amount

        # -------- Apply deduction logic --------
        if not already_checked_in:
            # First entry today → deduct
            if total_available < DAILY_CHARGE:
                return "❌ Insufficient balance or payment"

            remaining_balance = total_available - DAILY_CHARGE
            paid_today = DAILY_CHARGE
        else:
            # Already checked in → no deduction
            remaining_balance = total_available
            paid_today = 0

        # -------- Update user balance --------
        user_ref.set({
            "balance": remaining_balance
        })

        # -------- Store check-in record --------
        db.collection("checkins").document(doc_id).set({
            "name": name,
            "vehicle": vehicle,
            "contact": contact,
            "paid_today": paid_today,
            "balance_left": remaining_balance,
            "date": today,
            "time": datetime.now(),
            "repeat_entry": already_checked_in
        })

        # -------- Redirect (FIXES reload bug) --------
        return redirect(
            url_for(
                "success",
                balance=remaining_balance,
                repeat=int(already_checked_in)
            )
        )

    return render_template("index.html")

# ---------------- Success Page (GET only) ----------------
@app.route("/success")
def success():
    balance = int(request.args.get("balance", 0))
    repeat = int(request.args.get("repeat", 0))

    if repeat:
        status_msg = "ℹ️ Already checked in today (no charge applied)"
    else:
        status_msg = "✅ Entry recorded successfully"

    warning = ""
    if balance < LOW_BALANCE_LIMIT:
        warning = "<p style='color:red;'>⚠️ Low balance, please recharge soon</p>"

    return f"""
    <h3 style='text-align:center;'>{status_msg}</h3>
    <p style='text-align:center;'>💰 Remaining Balance: ₹{balance}</p>
    <div style='text-align:center;'>{warning}</div>
    """

# ---------------- Run app ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
