from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Roblox API endpoints
USERNAME_TO_ID = "https://users.roblox.com/v1/usernames/users"
PRESENCE_API = "https://presence.roblox.com/v1/presence/users"

@app.route('/getPresence', methods=['GET'])
def get_presence():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username required"}), 400

    # Βήμα 1: Username → UserId
    user_payload = {
        "usernames": [username],
        "excludeBannedUsers": True
    }
    user_resp = requests.post(USERNAME_TO_ID, json=user_payload)
    user_data = user_resp.json()

    if "data" not in user_data or len(user_data["data"]) == 0:
        return jsonify({"isOnline": False})

    user_id = user_data["data"][0]["id"]

    # Βήμα 2: UserId → Presence info
    presence_payload = {
        "userIds": [user_id]
    }
    presence_resp = requests.post(PRESENCE_API, json=presence_payload)
    presence_data = presence_resp.json()

    if "userPresences" not in presence_data or len(presence_data["userPresences"]) == 0:
        return jsonify({"isOnline": False})

    presence_info = presence_data["userPresences"][0]

    # Αν ο χρήστης είναι offline
    if presence_info["userPresenceType"] == 0:
        return jsonify({"isOnline": False})

    # Αν είναι σε παιχνίδι
    place_id = presence_info.get("placeId")
    instance_id = presence_info.get("gameId")
    is_private = presence_info.get("isPrivate", False)

    # Επιστροφή δεδομένων
    return jsonify({
        "isOnline": True,
        "placeId": place_id,
        "instanceId": instance_id,
        "isPrivate": is_private,
        "isFull": False  # Δεν δίνει API αν είναι full, το αφήνουμε false
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
