import firebase_admin
from firebase_admin import credentials, firestore
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------- Firebase ----------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------- Google Sheets ----------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "sheets_key.json", scope
)

client = gspread.authorize(creds)
sheet = client.open("Parking_Data").worksheet("data")

# ---------- Clear old data ----------
sheet.clear()

# ---------- Header ----------
sheet.append_row([
    "name", "vehicle", "contact", "amount", "date", "time"
])

# ---------- Fetch Firestore data ----------
docs = db.collection("checkins").stream()

for doc in docs:
    data = doc.to_dict()
    sheet.append_row([
        data.get("name", ""),
        data.get("vehicle", ""),
        data.get("contact", ""),
        data.get("amount", ""),
        data.get("date", ""),
        str(data.get("time", ""))
    ])

print("✅ Google Sheet updated successfully")
