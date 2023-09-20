import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database2.db'  

db = SQLAlchemy(app)  # Initialize SQLAlchemy
migrate = Migrate(app, db)

class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    users = db.relationship('User', secondary='room_user', back_populates='rooms')
    messages = db.relationship('Message', backref='room', lazy=True)

room_user_association = db.Table('room_user',
    db.Column('room_id', db.Integer, db.ForeignKey('chat_room.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rooms = db.relationship('ChatRoom', secondary='room_user', back_populates='users')
    messages = db.relationship('Message', backref='sender', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)


# User registration endpoint
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})

# User login endpoint (authentication required)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        # Implement token-based authentication (e.g., JWT) and return a token
        # ...
        return jsonify({"message": "User logged in successfully", "token": "your_token_here"})
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# User logout endpoint (authentication required)
@app.route('/api/logout', methods=['POST'])
def logout():
    # Implement user logout logic (e.g., revoke tokens, clear session)
    # ...
    return jsonify({"message": "User logged out successfully"})

@app.route('/api/chat/rooms/create', methods=['POST'])
def create_chat_room():
    data = request.get_json()
    room_name = data.get("room_name")

    # Check if the chat room with the same name already exists
    existing_room = ChatRoom.query.filter_by(name=room_name).first()
    if existing_room:
        return jsonify({"error": "Chat room with the same name already exists"}), 400

    # Create a new chat room
    new_chat_room = ChatRoom(name=room_name)
    db.session.add(new_chat_room)
    db.session.commit()

    return jsonify({"message": "Chat room created successfully"})

# Get all chat rooms endpoint (authentication required)
@app.route('/api/chat/rooms', methods=['GET'])
def get_chat_rooms():
    chat_rooms = ChatRoom.query.all()
    return jsonify([{"id": room.id, "name": room.name, "users": [user.username for user in room.users]} for room in chat_rooms])

# Get details of a specific chat room endpoint (authentication required)
@app.route('/api/chat/rooms/<int:id>', methods=['GET'])
def get_chat_room(id):
    chat_room = ChatRoom.query.get(id)
    if chat_room:
        return jsonify({"id": chat_room.id, "name": chat_room.name, "users": [user.username for user in chat_room.users]})
    else:
        return jsonify({"error": "Chat room not found"}), 404

# Send a message to a specific chat room endpoint (authentication required)
@app.route('/api/chat/rooms/<int:id>/messages', methods=['POST'])
def send_message(id):
    data = request.get_json()
    text = data.get("text")
    sender_id = data.get("sender_id")

    chat_room = ChatRoom.query.get(id)
    if not chat_room:
        return jsonify({"error": "Chat room not found"}), 404

    message = Message(text=text, sender_id=sender_id, room_id=id)
    db.session.add(message)
    db.session.commit()

    return jsonify({"message": "Message sent successfully"})

# Get messages for a specific chat room endpoint (authentication required)
@app.route('/api/chat/rooms/<int:id>/messages', methods=['GET'])
def get_messages(id):
    chat_room = ChatRoom.query.get(id)
    if not chat_room:
        return jsonify({"error": "Chat room not found"}), 404

    messages = Message.query.filter_by(room_id=id).all()
    return jsonify([{"id": msg.id, "text": msg.text, "sender_id": msg.sender_id, "room_id": msg.room_id, "created_at": msg.created_at} for msg in messages])

if __name__ == '__main__':
    app.run(debug=True)
