import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase initialization
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

print("Welcome to Parking System!")

while True:
    date = time.strftime("%Y-%m-%d")
    print("\n=== Today is:", date)
    print("1. Enter Details")
    print("2. Check balance")
    print("3. See today's checkins")
    print("4. Exit")

    choice = input("Enter your choice? (1-4): ")

    if choice == "1":
        vehicle = input("Your vehicle number? ").upper()
        checkin_id = vehicle + "_" + date

        checkin_ref = db.collection("checkins").document(checkin_id)
        checkin_doc = checkin_ref.get()

        if checkin_doc.exists:
            contact = checkin_doc.to_dict()["contact"]
            user_doc = db.collection("users").document(contact).get()
            owner_name = user_doc.to_dict().get("name", "Unknown")
            print("Already checked in!")
            print("Vehicle:", vehicle)
            print("Owner:", owner_name, "(", contact, ")")
            print("No money deducted - pass valid all day!")
            continue

        contact = input("Your phone number (10 digits)? ")

        if len(contact) != 10 or not contact.isdigit():
            print("Wrong phone number!")
            continue

        user_ref = db.collection("users").document(contact)
        user_doc = user_ref.get()

        if not user_doc.exists:
            user_name = input("Your name? ")
            user_ref.set({
                "name": user_name,
                "balance": 250
            })
            balance = 250
            print("New user! Started with 250rs")
        else:
            data = user_doc.to_dict()
            user_name = data["name"]
            balance = data["balance"]
            print("Welcome back,", user_name)

        if balance < 5:
            print("Not enough money! Your current balance is:", balance)
            continue

        balance -= 5
        user_ref.update({"balance": balance})

        checkin_ref.set({
            "vehicle": vehicle,
            "contact": contact,
            "date": date,
            "time": datetime.now()
        })

        print("Check-in successful!")
        print("Vehicle:", vehicle)
        print("Money left:", balance)

    elif choice == "2":
        contact = input("Enter your contact number: ")
        user_doc = db.collection("users").document(contact).get()

        if user_doc.exists:
            data = user_doc.to_dict()
            print(data["name"], "- Money left:", data["balance"])
        else:
            print("No record found!")

    elif choice == "3":
        checkins = db.collection("checkins").stream()
        found = False

        print("Today's parked vehicles:")
        for doc in checkins:
            data = doc.to_dict()
            if data["date"] == date:
                found = True
                contact = data["contact"]
                user_doc = db.collection("users").document(contact).get()
                owner = user_doc.to_dict().get("name", "Unknown")
                print("--> Vehicle:", data["vehicle"], "by", owner)

        if not found:
            print("No vehicles parked today.")

    elif choice == "4":
        print("Thank you, visit again!")
        break

    else:
        print("Pick 1, 2, 3 or 4 please!")
