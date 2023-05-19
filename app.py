from flask import Flask, render_template, request, session, redirect, jsonify
from pymongo import MongoClient
import bcrypt
import uuid

app = Flask(__name__)
app.secret_key = "secretkey"

# MongoDB Configuration
client = MongoClient("mongodb+srv://adityace21:<password>@cluster0.odaujen.mongodb.net/")
db = client["web_app"]
users = db["users"]
statuses = db["statuses"]
chats = db["chats"]

# Routes
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/chat")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]
        user = users.find_one({"user_id": user_id})
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user_id"] = user_id
            return redirect("/chat")
        else:
            return render_template("login.html", error="Invalid user ID or password")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_id = str(uuid.uuid4())
        password = request.form["password"]
        interests = request.form.getlist("interests")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = {"user_id": user_id, "password": hashed_password, "interests": interests}
        users.insert_one(user)
        session["user_id"] = user_id
        return redirect("/chat")
    return render_template("register.html")

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    
    # Retrieve the user's interests from the database
    user = users.find_one({"user_id": user_id})
    user_interests = user["interests"]
    
    # Find other users with matching interests
    matched_users = users.find({"user_id": {"$ne": user_id}, "interests": {"$in": user_interests}})
    
    # Fetch statuses of matched users
    matched_statuses = []
    for matched_user in matched_users:
        status = statuses.find_one({"user_id": matched_user["user_id"]})
        if status:
            matched_statuses.append(status)
    
    return render_template("chat.html", user_id=user_id, matched_statuses=matched_statuses)

@app.route("/post_status", methods=["POST"])
def post_status():
    if "user_id" not in session:
        return redirect("/login")
    
    status_text = request.form["status_text"]
    user_id = session["user_id"]
    
    # Check if the user has already posted a status, update if exists, insert otherwise
    existing_status = statuses.find_one({"user_id": user_id})
    if existing_status:
        statuses.update_one({"user_id": user_id}, {"$set": {"text": status_text}})
    else:
        status = {"user_id": user_id, "text": status_text}
        statuses.insert_one(status)
    
    return redirect("/chat")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")

@app.route("/get_chat/<other_user_id>")
def get_chat(other_user_id):
    user_id = session["user_id"]
    chat = chats.find_one({"$or": [
        {"$and": [{"user1": user_id}, {"user2": other_user_id}]},
        {"$and": [{"user1": other_user_id}, {"user2": user_id}]}
    ]})
    if chat:
        messages = chat["messages"]
    else:
        messages = []
    return jsonify(messages)

@app.route("/send_message", methods=["POST"])
def send_message():
    user_id = session["user_id"]
    other_user_id = request.form["other_user_id"]
    message = request.form["message"]
    
    chat = chats.find_one({"$or": [
        {"$and": [{"user1": user_id}, {"user2": other_user_id}]},
        {"$and": [{"user1": other_user_id}, {"user2": user_id}]}
    ]})
    
    if chat:
        chats.update_one({"_id": chat["_id"]}, {"$push": {"messages": {"sender": user_id, "message": message}}})
    else:
        chat = {"user1": user_id, "user2": other_user_id, "messages": [{"sender": user_id, "message": message}]}
        chats.insert_one(chat)
    
    return jsonify({"success": True})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
