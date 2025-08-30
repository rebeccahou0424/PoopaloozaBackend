from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

# 修正 URI 前綴
uri = os.getenv("SQLALCHEMY_DATABASE_URI")  
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- Models ----------------

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    consecutive_login_days = db.Column(db.Integer)
    last_login_date = db.Column(db.Date)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    achievement_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    achievement_name = db.Column(db.String(100))
    achievement_description = db.Column(db.Text)
    achieved_at = db.Column(db.DateTime)

class Checkin(db.Model):
    __tablename__ = 'checkin'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50))  # 這邊不是 ForeignKey（以你的資料來看是文字）
    location = db.Column(db.String(120))
    emoji = db.Column(db.String(10))
    note = db.Column(db.Text)

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    analysis_id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    analysis_time = db.Column(db.DateTime)
    ai_diagnosis = db.Column(db.Text)
    health_score = db.Column(db.Integer)
    recommendations = db.Column(db.Text)

class PoopLocation(db.Model):
    __tablename__ = 'poop_locations'
    location_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    record_id = db.Column(db.Integer, nullable=True)
    record_time = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    expression_text = db.Column(db.Text)

class PoopRecord(db.Model):
    __tablename__ = 'poop_records'
    record_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    record_time = db.Column(db.DateTime)
    bristol_scale = db.Column(db.String(10))
    color = db.Column(db.String(20))
    consistency = db.Column(db.String(20))
    volume = db.Column(db.String(20))
    odor = db.Column(db.String(20))
    has_blood = db.Column(db.Boolean)
    has_mucus = db.Column(db.Boolean)
    image_url = db.Column(db.String(255))
    ai_poop_type = db.Column(db.String(20))
    ai_poop_color = db.Column(db.String(20))
    ai_poop_volume = db.Column(db.String(20))
    ai_diagnosis_summary = db.Column(db.Text)
    health_recommendations = db.Column(db.Text)
    health_indicators = db.Column(db.Text)

class PublicToilet(db.Model):
    __tablename__ = 'public_toilets'

    toilet_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    country = db.Column(db.String)
    city = db.Column(db.String)
    village = db.Column(db.String)
    administration = db.Column(db.String)
    grade = db.Column(db.String)
    type2 = db.Column(db.String)
    toilet_type = db.Column(db.String)
    exec = db.Column(db.String)
    diaper = db.Column(db.String)

class ToiletCheckin(db.Model):
    __tablename__ = 'toilet_checkins'
    toilet_checkin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    checkin_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    toilet_name = db.Column(db.String)
    toilet_rating_cleanliness = db.Column(db.Integer)
    toilet_rating_privacy = db.Column(db.Integer)
    toilet_rating_amenities = db.Column(db.Integer)
    toilet_review_text = db.Column(db.Text)
    public_toilet_id = db.Column(db.String)

class PublicCheckin(db.Model):
    __tablename__ = 'public_checkins'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String)
    bathroom_id = db.Column(db.String)
    bathroom_name = db.Column(db.String)
    bathroom_address = db.Column(db.String)
    bathroom_type = db.Column(db.String)
    bathroom_source = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)
    mood_emoji = db.Column(db.String)
    bristol_type = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    note = db.Column(db.Text)
    custom_message = db.Column(db.String)
    quick_tag = db.Column(db.String)
    image_url = db.Column(db.String)
    audio_url = db.Column(db.String)
    is_anonymous = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PrivateCheckin(db.Model):
    __tablename__ = 'private_checkins'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String)
    bathroom_id = db.Column(db.String)
    bathroom_name = db.Column(db.String)
    bathroom_address = db.Column(db.String)
    bathroom_type = db.Column(db.String)
    bathroom_source = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)
    mood_emoji = db.Column(db.String)
    bristol_type = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    note = db.Column(db.Text)
    custom_message = db.Column(db.String)
    quick_tag = db.Column(db.String)
    image_url = db.Column(db.String)
    audio_url = db.Column(db.String)
    personal_notes = db.Column(db.Text)
    health_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
# ---------------- Routes ----------------

@app.route('/')
def home():
    return "👋 Welcome to PooPalooza API!"

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

# ========== REGISTER ==========
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email') 

    if not username or not password:
        return jsonify({'message': 'All fields are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password_hash=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'username': new_user.username}), 201

# ========== LOGIN ==========
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email
        }), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# ========== USERS ==========
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = []
    for u in users:
        result.append({
            "user_id": u.user_id,
            "username": u.username,
            "email": u.email,
            "password_hash": u.password_hash,
            "created_at": u.created_at,
            "last_login": u.last_login,
            "consecutive_login_days": u.consecutive_login_days,
            "last_login_date": u.last_login_date
        })
    return jsonify(result)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    # 加密密碼（避免使用 scrypt，避免某些系統出錯）
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        created_at=datetime.now()
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "使用者不存在"}), 404

    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password_hash = data.get('password_hash', user.password_hash)
    user.last_login = datetime.utcnow()
    user.consecutive_login_days = data.get('consecutive_login_days', user.consecutive_login_days)
    user.last_login_date = datetime.utcnow().date()

    db.session.commit()
    return jsonify({"success": True, "msg": "使用者更新成功"})

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "使用者不存在"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True, "msg": "使用者已刪除"})

# ========== ACHIEVEMENTS ==========

@app.route('/achievements', methods=['GET'])
def get_achievements():
    achievements = Achievement.query.all()
    result = []
    for a in achievements:
        result.append({
            "achievement_id": a.achievement_id,
            "user_id": a.user_id,
            "achievement_name": a.achievement_name,
            "achievement_description": a.achievement_description,
            "achieved_at": a.achieved_at
        })
    return jsonify(result)

@app.route('/achievements/<int:user_id>', methods=['GET'])
def get_achievements_by_user(user_id):
    achievements = Achievement.query.filter_by(user_id=user_id).all()
    result = []
    for a in achievements:
        result.append({
            "achievement_id": a.achievement_id,
            "user_id": a.user_id,
            "achievement_name": a.achievement_name,
            "achievement_description": a.achievement_description,
            "achieved_at": a.achieved_at
        })
    return jsonify(result)

@app.route('/achievements', methods=['POST'])
def create_achievement():
    data = request.json
    achievement = Achievement(
        user_id=data.get('user_id'),
        achievement_name=data.get('achievement_name'),
        achievement_description=data.get('achievement_description'),
        achieved_at=datetime.utcnow()
    )
    db.session.add(achievement)
    db.session.commit()
    return jsonify({"success": True, "msg": "成就建立成功"})

@app.route('/achievements/<int:id>', methods=['PUT'])
def update_achievement(id):
    achievement = Achievement.query.get(id)
    if not achievement:
        return jsonify({"error": "成就不存在"}), 404

    data = request.json
    achievement.achievement_name = data.get('achievement_name', achievement.achievement_name)
    achievement.achievement_description = data.get('achievement_description', achievement.achievement_description)
    achievement.achieved_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"success": True, "msg": "成就更新成功"})

@app.route('/achievements/<int:id>', methods=['DELETE'])
def delete_achievement(id):
    achievement = Achievement.query.get(id)
    if not achievement:
        return jsonify({"error": "成就不存在"}), 404

    db.session.delete(achievement)
    db.session.commit()
    return jsonify({"success": True, "msg": "成就已刪除"})

# ========== CHECKIN ==========

# ✅ GET /checkin
@app.route('/checkin', methods=['GET'])
def get_checkin():
    checkin = Checkin.query.all()
    result = []
    for c in checkin:
        result.append({
            "id": c.id,
            "user": c.user,
            "location": c.location,
            "emoji": c.emoji,
            "note": c.note
        })
    return jsonify(result)

# ✅ PUT /checkin/<id>
@app.route('/checkin/<int:id>', methods=['PUT'])
def update_checkin(id):
    checkin = Checkin.query.get(id)
    if not checkin:
        return jsonify({"error": "找不到此打卡"}), 404

    data = request.json
    checkin.user = data.get('user', checkin.user)
    checkin.location = data.get('location', checkin.location)
    checkin.emoji = data.get('emoji', checkin.emoji)
    checkin.note = data.get('note', checkin.note)

    db.session.commit()
    return jsonify({"success": True, "msg": "打卡已更新"})

# ✅ POST /checkin
@app.route('/checkin', methods=['POST'])
def create_checkin():
    data = request.json
    checkin = Checkin(
        user=data.get('user'),
        location=data.get('location'),
        emoji=data.get('emoji'),
        note=data.get('note')
    )
    db.session.add(checkin)
    db.session.commit()
    return jsonify({"success": True, "msg": "打卡成功"})

# ✅ DELETE /checkin/<id>
@app.route('/checkin/<int:id>', methods=['DELETE'])
def delete_checkin(id):
    checkin = Checkin.query.get(id)
    if not checkin:
        return jsonify({"error": "找不到此打卡"}), 404

    db.session.delete(checkin)
    db.session.commit()
    return jsonify({"success": True, "msg": "打卡已刪除"})

# ========== ANALYSIS RESULTS ==========

@app.route('/analysis_results', methods=['GET'])
def get_all_analysis_results():
    results = AnalysisResult.query.all()
    return jsonify([
        {
            "analysis_id": r.analysis_id,
            "record_id": r.record_id,
            "user_id": r.user_id,
            "analysis_time": r.analysis_time,
            "ai_diagnosis": r.ai_diagnosis,
            "health_score": r.health_score,
            "recommendations": r.recommendations
        } for r in results
    ])

@app.route('/analysis_results/<int:id>', methods=['GET'])
def get_analysis_result(id):
    r = AnalysisResult.query.get(id)
    if not r:
        return jsonify({"error": "分析結果不存在"}), 404
    return jsonify({
        "analysis_id": r.analysis_id,
        "record_id": r.record_id,
        "user_id": r.user_id,
        "analysis_time": r.analysis_time,
        "ai_diagnosis": r.ai_diagnosis,
        "health_score": r.health_score,
        "recommendations": r.recommendations
    })

@app.route('/analysis_results', methods=['POST'])
def create_analysis_result():
    data = request.json
    new_result = AnalysisResult(
        record_id=data.get('record_id'),
        user_id=data.get('user_id'),
        analysis_time=datetime.utcnow(),
        ai_diagnosis=data.get('ai_diagnosis'),
        health_score=data.get('health_score'),
        recommendations=data.get('recommendations')
    )
    db.session.add(new_result)
    db.session.commit()
    return jsonify({"success": True, "msg": "分析結果建立成功"})

@app.route('/analysis_results/<int:id>', methods=['PUT'])
def update_analysis_result(id):
    r = AnalysisResult.query.get(id)
    if not r:
        return jsonify({"error": "分析結果不存在"}), 404

    data = request.json
    r.record_id = data.get('record_id', r.record_id)
    r.user_id = data.get('user_id', r.user_id)
    r.analysis_time = datetime.utcnow()
    r.ai_diagnosis = data.get('ai_diagnosis', r.ai_diagnosis)
    r.health_score = data.get('health_score', r.health_score)
    r.recommendations = data.get('recommendations', r.recommendations)

    db.session.commit()
    return jsonify({"success": True, "msg": "分析結果更新成功"})

@app.route('/analysis_results/<int:id>', methods=['DELETE'])
def delete_analysis_result(id):
    r = AnalysisResult.query.get(id)
    if not r:
        return jsonify({"error": "分析結果不存在"}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({"success": True, "msg": "分析結果已刪除"})

# ========== POOP LOCATIONS ==========

@app.route('/poop_locations', methods=['GET'])
def get_poop_locations():
    locations = PoopLocation.query.all()
    return jsonify([
        {
            "location_id": l.location_id,
            "user_id": l.user_id,
            "record_id": l.record_id,
            "record_time": l.record_time,
            "latitude": l.latitude,
            "longitude": l.longitude,
            "location_name": l.location_name,
            "notes": l.notes,
            "expression_text": l.expression_text
        } for l in locations
    ])

@app.route('/poop_locations/<int:id>', methods=['GET'])
def get_poop_location(id):
    l = PoopLocation.query.get(id)
    if not l:
        return jsonify({"error": "紀錄不存在"}), 404
    return jsonify({
        "location_id": l.location_id,
        "user_id": l.user_id,
        "record_id": l.record_id,
        "record_time": l.record_time,
        "latitude": l.latitude,
        "longitude": l.longitude,
        "location_name": l.location_name,
        "notes": l.notes,
        "expression_text": l.expression_text
    })

@app.route('/poop_locations', methods=['POST'])
def create_poop_location():
    data = request.json
    location = PoopLocation(
        user_id=data.get('user_id'),
        record_id=data.get('record_id'),
        record_time=datetime.utcnow(),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        location_name=data.get('location_name'),
        notes=data.get('notes'),
        expression_text=data.get('expression_text')
    )
    db.session.add(location)
    db.session.commit()
    return jsonify({"success": True, "msg": "地點紀錄新增成功"})

@app.route('/poop_locations/<int:id>', methods=['PUT'])
def update_poop_location(id):
    location = PoopLocation.query.get(id)
    if not location:
        return jsonify({"error": "地點紀錄不存在"}), 404

    data = request.json
    location.user_id = data.get('user_id', location.user_id)
    location.record_id = data.get('record_id', location.record_id)
    location.latitude = data.get('latitude', location.latitude)
    location.longitude = data.get('longitude', location.longitude)
    location.location_name = data.get('location_name', location.location_name)
    location.notes = data.get('notes', location.notes)
    location.expression_text = data.get('expression_text', location.expression_text)
    location.record_time = datetime.utcnow()

    db.session.commit()
    return jsonify({"success": True, "msg": "地點紀錄更新成功"})

@app.route('/poop_locations/<int:id>', methods=['DELETE'])
def delete_poop_location(id):
    location = PoopLocation.query.get(id)
    if not location:
        return jsonify({"error": "地點紀錄不存在"}), 404

    db.session.delete(location)
    db.session.commit()
    return jsonify({"success": True, "msg": "地點紀錄已刪除"})

# ========== POOP RECORDS ==========
@app.route('/poop-records', methods=['GET'])
def get_poop_records():
    records = PoopRecord.query.all()
    result = []
    for r in records:
        result.append({
            "record_id": r.record_id,
            "user_id": r.user_id,
            "record_time": r.record_time,
            "bristol_scale": r.bristol_scale,
            "color": r.color,
            "consistency": r.consistency,
            "volume": r.volume,
            "odor": r.odor,
            "has_blood": r.has_blood,
            "has_mucus": r.has_mucus,
            "image_url": r.image_url,
            "ai_poop_type": r.ai_poop_type,
            "ai_poop_color": r.ai_poop_color,
            "ai_poop_volume": r.ai_poop_volume,
            "ai_diagnosis_summary": r.ai_diagnosis_summary,
            "health_recommendations": r.health_recommendations,
            "health_indicators": r.health_indicators
        })
    return jsonify(result)

@app.route('/poop-records', methods=['POST'])
def create_poop_record():
    data = request.json
    record = PoopRecord(
        user_id=data['user_id'],
        record_time=datetime.utcnow(),
        bristol_scale=data.get('bristol_scale'),
        color=data.get('color'),
        consistency=data.get('consistency'),
        volume=data.get('volume'),
        odor=data.get('odor'),
        has_blood=data.get('has_blood', False),
        has_mucus=data.get('has_mucus', False),
        image_url=data.get('image_url'),
        ai_poop_type=data.get('ai_poop_type'),
        ai_poop_color=data.get('ai_poop_color'),
        ai_poop_volume=data.get('ai_poop_volume'),
        ai_diagnosis_summary=data.get('ai_diagnosis_summary'),
        health_recommendations=data.get('health_recommendations'),
        health_indicators=data.get('health_indicators')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"success": True, "msg": "糞便紀錄建立成功"})

@app.route('/poop-records/<int:record_id>', methods=['PUT'])
def update_poop_record(record_id):
    record = PoopRecord.query.get(record_id)
    if not record:
        return jsonify({"error": "紀錄不存在"}), 404

    data = request.json
    record.bristol_scale = data.get('bristol_scale', record.bristol_scale)
    record.color = data.get('color', record.color)
    record.consistency = data.get('consistency', record.consistency)
    record.volume = data.get('volume', record.volume)
    record.odor = data.get('odor', record.odor)
    record.has_blood = data.get('has_blood', record.has_blood)
    record.has_mucus = data.get('has_mucus', record.has_mucus)
    record.image_url = data.get('image_url', record.image_url)
    record.ai_poop_type = data.get('ai_poop_type', record.ai_poop_type)
    record.ai_poop_color = data.get('ai_poop_color', record.ai_poop_color)
    record.ai_poop_volume = data.get('ai_poop_volume', record.ai_poop_volume)
    record.ai_diagnosis_summary = data.get('ai_diagnosis_summary', record.ai_diagnosis_summary)
    record.health_recommendations = data.get('health_recommendations', record.health_recommendations)
    record.health_indicators = data.get('health_indicators', record.health_indicators)

    db.session.commit()
    return jsonify({"success": True, "msg": "糞便紀錄更新成功"})

@app.route('/poop-records/<int:record_id>', methods=['DELETE'])
def delete_poop_record(record_id):
    record = PoopRecord.query.get(record_id)
    if not record:
        return jsonify({"error": "紀錄不存在"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"success": True, "msg": "糞便紀錄已刪除"})

# ========== PUBLIC_TOILETS ==========
@app.route('/toilets', methods=['GET'])
def get_all_toilets():
    toilets = PublicToilet.query.all()
    return jsonify([t.__dict__ for t in toilets if '_sa_instance_state' not in t.__dict__])

@app.route('/toilets/<string:toilet_id>', methods=['GET'])
def get_toilet(toilet_id):
    toilet = PublicToilet.query.get(toilet_id)
    if not toilet:
        return jsonify({'error': 'Toilet not found'}), 404
    return jsonify(toilet.__dict__)

@app.route('/toilets', methods=['POST'])
def create_toilet():
    data = request.json
    new_toilet = PublicToilet(**data)
    db.session.add(new_toilet)
    db.session.commit()
    return jsonify({'message': 'Toilet created'}), 201

@app.route('/toilets/<string:toilet_id>', methods=['PUT'])
def update_toilet(toilet_id):
    toilet = PublicToilet.query.get(toilet_id)
    if not toilet:
        return jsonify({'error': 'Toilet not found'}), 404
    for key, value in request.json.items():
        setattr(toilet, key, value)
    db.session.commit()
    return jsonify({'message': 'Toilet updated'})

@app.route('/toilets/<string:toilet_id>', methods=['DELETE'])
def delete_toilet(toilet_id):
    toilet = PublicToilet.query.get(toilet_id)
    if not toilet:
        return jsonify({'error': 'Toilet not found'}), 404
    db.session.delete(toilet)
    db.session.commit()
    return jsonify({'message': 'Toilet deleted'})

# ========== TOILET_CHECKINS ==========
# 🔍 GET 全部資料
@app.route('/toilet_checkins', methods=['GET'])
def get_toilet_checkins():
    all_checkins = ToiletCheckin.query.all()
    result = []
    for c in all_checkins:
        result.append({
            'toilet_checkin_id': c.toilet_checkin_id,
            'user_id': c.user_id,
            'checkin_time': c.checkin_time,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'toilet_name': c.toilet_name,
            'toilet_rating_cleanliness': c.toilet_rating_cleanliness,
            'toilet_rating_privacy': c.toilet_rating_privacy,
            'toilet_rating_amenities': c.toilet_rating_amenities,
            'toilet_review_text': c.toilet_review_text,
            'public_toilet_id': c.public_toilet_id,
        })
    return jsonify(result)

# 🔍 GET 單筆
@app.route('/toilet_checkins/<int:checkin_id>', methods=['GET'])
def get_toilet_checkin(checkin_id):
    c = ToiletCheckin.query.get_or_404(checkin_id)
    return jsonify({
        'toilet_checkin_id': c.toilet_checkin_id,
        'user_id': c.user_id,
        'checkin_time': c.checkin_time,
        'latitude': c.latitude,
        'longitude': c.longitude,
        'toilet_name': c.toilet_name,
        'toilet_rating_cleanliness': c.toilet_rating_cleanliness,
        'toilet_rating_privacy': c.toilet_rating_privacy,
        'toilet_rating_amenities': c.toilet_rating_amenities,
        'toilet_review_text': c.toilet_review_text,
        'public_toilet_id': c.public_toilet_id,
    })

# ➕ POST 新增
@app.route('/toilet_checkins', methods=['POST'])
def create_toilet_checkin():
    data = request.get_json()
    new_checkin = ToiletCheckin(
        user_id=data['user_id'],
        checkin_time=datetime.strptime(data['checkin_time'], '%Y-%m-%d %H:%M:%S'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        toilet_name=data.get('toilet_name'),
        toilet_rating_cleanliness=data.get('toilet_rating_cleanliness'),
        toilet_rating_privacy=data.get('toilet_rating_privacy'),
        toilet_rating_amenities=data.get('toilet_rating_amenities'),
        toilet_review_text=data.get('toilet_review_text'),
        public_toilet_id=data.get('public_toilet_id')
    )
    db.session.add(new_checkin)
    db.session.commit()
    return jsonify({'message': 'Checkin created successfully'}), 201

# 📝 PUT 更新
@app.route('/toilet_checkins/<int:checkin_id>', methods=['PUT'])
def update_toilet_checkin(checkin_id):
    c = ToiletCheckin.query.get_or_404(checkin_id)
    data = request.get_json()
    c.latitude = data.get('latitude', c.latitude)
    c.longitude = data.get('longitude', c.longitude)
    c.toilet_name = data.get('toilet_name', c.toilet_name)
    c.toilet_rating_cleanliness = data.get('toilet_rating_cleanliness', c.toilet_rating_cleanliness)
    c.toilet_rating_privacy = data.get('toilet_rating_privacy', c.toilet_rating_privacy)
    c.toilet_rating_amenities = data.get('toilet_rating_amenities', c.toilet_rating_amenities)
    c.toilet_review_text = data.get('toilet_review_text', c.toilet_review_text)
    c.public_toilet_id = data.get('public_toilet_id', c.public_toilet_id)
    db.session.commit()
    return jsonify({'message': 'Checkin updated successfully'})

# ❌ DELETE 刪除
@app.route('/toilet_checkins/<int:checkin_id>', methods=['DELETE'])
def delete_toilet_checkin(checkin_id):
    c = ToiletCheckin.query.get_or_404(checkin_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Checkin deleted successfully'})

# ========== PUBLIC_CHECKINS ==========
# ✅ Get all public checkins
@app.route('/public-checkins', methods=['GET'])
def get_all_public_checkins():
    checkins = PublicCheckin.query.all()
    result = []
    for checkin in checkins:
        result.append({
            'id': checkin.id,
            'user_id': checkin.user_id,
            'bathroom_id': checkin.bathroom_id,
            'bathroom_name': checkin.bathroom_name,
            'bathroom_address': checkin.bathroom_address,
            'bathroom_type': checkin.bathroom_type,
            'bathroom_source': checkin.bathroom_source,
            'latitude': checkin.latitude,
            'longitude': checkin.longitude,
            'location_name': checkin.location_name,
            'mood_emoji': checkin.mood_emoji,
            'bristol_type': checkin.bristol_type,
            'rating': checkin.rating,
            'note': checkin.note,
            'custom_message': checkin.custom_message,
            'quick_tag': checkin.quick_tag,
            'image_url': checkin.image_url,
            'audio_url': checkin.audio_url,
            'is_anonymous': checkin.is_anonymous,
            'created_at': checkin.created_at,
            'updated_at': checkin.updated_at
        })
    return jsonify(result)

# ✅ Create a new public checkin
@app.route('/public-checkins', methods=['POST'])
def create_public_checkin():
    data = request.get_json()
    new_checkin = PublicCheckin(
        id=str(uuid.uuid4()),
        user_id=data.get('user_id'),
        bathroom_id=data.get('bathroom_id'),
        bathroom_name=data.get('bathroom_name'),
        bathroom_address=data.get('bathroom_address'),
        bathroom_type=data.get('bathroom_type'),
        bathroom_source=data.get('bathroom_source'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        location_name=data.get('location_name'),
        mood_emoji=data.get('mood_emoji'),
        bristol_type=data.get('bristol_type'),
        rating=data.get('rating'),
        note=data.get('note'),
        custom_message=data.get('custom_message'),
        quick_tag=data.get('quick_tag'),
        image_url=data.get('image_url'),
        audio_url=data.get('audio_url'),
        is_anonymous=data.get('is_anonymous', False),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(new_checkin)
    db.session.commit()
    return jsonify({'message': 'Check-in created successfully', 'id': new_checkin.id}), 201

# ✅ Get a single public checkin by ID
@app.route('/public-checkins/<string:checkin_id>', methods=['GET'])
def get_public_checkin(checkin_id):
    checkin = PublicCheckin.query.get(checkin_id)
    if not checkin:
        return jsonify({'message': 'Check-in not found'}), 404
    return jsonify({
        'id': checkin.id,
        'user_id': checkin.user_id,
        'bathroom_name': checkin.bathroom_name,
        'location_name': checkin.location_name,
        'custom_message': checkin.custom_message
    })

# ✅ Update a public checkin
@app.route('/public-checkins/<string:checkin_id>', methods=['PUT'])
def update_public_checkin(checkin_id):
    checkin = PublicCheckin.query.get(checkin_id)
    if not checkin:
        return jsonify({'message': 'Check-in not found'}), 404

    data = request.get_json()
    for field in data:
        if hasattr(checkin, field):
            setattr(checkin, field, data[field])
    checkin.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'Check-in updated successfully'})

# ✅ Delete a public checkin
@app.route('/public-checkins/<string:checkin_id>', methods=['DELETE'])
def delete_public_checkin(checkin_id):
    checkin = PublicCheckin.query.get(checkin_id)
    if not checkin:
        return jsonify({'message': 'Check-in not found'}), 404
    db.session.delete(checkin)
    db.session.commit()
    return jsonify({'message': 'Check-in deleted successfully'})

# ========== PRIVATE_CHECKINS ==========
# GET all private_checkins
@app.route('/private-checkins', methods=['GET'])
def get_all_private_checkins():
    checkins = PrivateCheckin.query.all()
    return jsonify([{
        'id': c.id,
        'user_id': c.user_id,
        'bathroom_id': c.bathroom_id,
        'bathroom_name': c.bathroom_name,
        'bathroom_address': c.bathroom_address,
        'bathroom_type': c.bathroom_type,
        'bathroom_source': c.bathroom_source,
        'latitude': c.latitude,
        'longitude': c.longitude,
        'location_name': c.location_name,
        'mood_emoji': c.mood_emoji,
        'bristol_type': c.bristol_type,
        'rating': c.rating,
        'note': c.note,
        'custom_message': c.custom_message,
        'quick_tag': c.quick_tag,
        'image_url': c.image_url,
        'audio_url': c.audio_url,
        'personal_notes': c.personal_notes,
        'health_notes': c.health_notes,
        'created_at': c.created_at,
        'updated_at': c.updated_at
    } for c in checkins])

# GET single private_checkin
@app.route('/private-checkins/<string:checkin_id>', methods=['GET'])
def get_private_checkin(checkin_id):
    checkin = PrivateCheckin.query.get_or_404(checkin_id)
    return jsonify({
        'id': checkin.id,
        'user_id': checkin.user_id,
        'bathroom_id': checkin.bathroom_id,
        'bathroom_name': checkin.bathroom_name,
        'bathroom_address': checkin.bathroom_address,
        'bathroom_type': checkin.bathroom_type,
        'bathroom_source': checkin.bathroom_source,
        'latitude': checkin.latitude,
        'longitude': checkin.longitude,
        'location_name': checkin.location_name,
        'mood_emoji': checkin.mood_emoji,
        'bristol_type': checkin.bristol_type,
        'rating': checkin.rating,
        'note': checkin.note,
        'custom_message': checkin.custom_message,
        'quick_tag': checkin.quick_tag,
        'image_url': checkin.image_url,
        'audio_url': checkin.audio_url,
        'personal_notes': checkin.personal_notes,
        'health_notes': checkin.health_notes,
        'created_at': checkin.created_at,
        'updated_at': checkin.updated_at
    })

# POST create new private_checkin
@app.route('/private-checkins', methods=['POST'])
def create_private_checkin():
    data = request.get_json()
    new_checkin = PrivateCheckin(
        id=str(uuid4()),
        user_id=data['user_id'],
        bathroom_id=data.get('bathroom_id'),
        bathroom_name=data.get('bathroom_name'),
        bathroom_address=data.get('bathroom_address'),
        bathroom_type=data.get('bathroom_type'),
        bathroom_source=data.get('bathroom_source'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        location_name=data.get('location_name'),
        mood_emoji=data.get('mood_emoji'),
        bristol_type=data.get('bristol_type'),
        rating=data.get('rating'),
        note=data.get('note'),
        custom_message=data.get('custom_message'),
        quick_tag=data.get('quick_tag'),
        image_url=data.get('image_url'),
        audio_url=data.get('audio_url'),
        personal_notes=data.get('personal_notes'),
        health_notes=data.get('health_notes'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(new_checkin)
    db.session.commit()
    return jsonify({'message': 'Private checkin created', 'id': new_checkin.id}), 201

# PUT update private_checkin
@app.route('/private-checkins/<string:checkin_id>', methods=['PUT'])
def update_private_checkin(checkin_id):
    data = request.get_json()
    checkin = PrivateCheckin.query.get_or_404(checkin_id)

    for key in data:
        if hasattr(checkin, key):
            setattr(checkin, key, data[key])
    checkin.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'Private checkin updated'})

# DELETE private_checkin
@app.route('/private-checkins/<string:checkin_id>', methods=['DELETE'])
def delete_private_checkin(checkin_id):
    checkin = PrivateCheckin.query.get_or_404(checkin_id)
    db.session.delete(checkin)
    db.session.commit()
    return jsonify({'message': 'Private checkin deleted'})


# ---------------- 啟動 ----------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)