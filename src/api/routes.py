import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, url_for, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import select, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError, DataError
from api.models import db, enumGender, enumLane, enumRank, Champions, Users, Items, Builds, Stats, Favourites, Builditems

api = Blueprint('api', __name__)

#Users
@api.route('/users', methods=['GET'])
def get_users():
    stmt = select(Users)
    users = db.session.execute(stmt).scalars().all()
    response_body = [user.serialize() for user in users]
    
    return jsonify(response_body), 200

@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    
    stmt = select(Users).where(Users.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()),200

@api.route('/user/', methods=['GET'])
@jwt_required()
def get_user_logged():
    user_id = int(get_jwt_identity())
    stmt = select(Users).where(Users.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({"Error": "User not found"}), 404
    
    response_body = user.serialize()
    return jsonify({**response_body, "success": True}),200

@api.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data.get("username") or not data.get("password") or not data.get("nick"):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user = Users(
            username=data["username"],
            nick=data["nick"],
            password=generate_password_hash(data["password"]),
            gender=enumGender[data.get("gender", "NA")],
            rank=enumRank[data.get("rank", "NA")],
            mainrole=enumLane[data.get("mainrole", "NA")]
        )
        db.session.add(user)
        db.session.commit()
            
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": True, "response": e.message}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Couldn't create user"}), 500
    
    return jsonify({"success": True}), 200

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error":"Missing username or password"}), 400
    stmt = select(Users).where(Users.username == data.get("username"))
    user = db.session.execute(stmt).scalar_one_or_none()

    if not user:
        return jsonify({"error":"User not found"}), 404
    elif not check_password_hash(user.password, data["password"]):
        return jsonify({"error":"Username or password don't match"}), 401
    

    token = create_access_token(identity=user.id)

    return jsonify({**user.serialize(),"success": True,"token": token}), 200

#Champions
@api.route('/champions', methods=['GET'])
def get_champions():
    stmt = select(Champions)
    champions = db.session.execute(stmt).scalars().all()
    response_body = [champion.serialize() for champion in champions]
    
    return jsonify(response_body), 200

@api.route('/champions/<int:id>', methods=['GET'])
def get_champion(id):
    
    stmt = select(Champions).where(Champions.id == id)
    champion = db.session.execute(stmt).scalar_one_or_none()
    if champion is None:
        return jsonify({"error": "Champion not found"}), 404
    return jsonify(champion.serialize()),200

#Stats
@api.route('/stats', methods=['GET'])
def get_stats():
    stmt = select(Stats)
    stats = db.session.execute(stmt).scalars().all()
    response_body = [stat.serialize() for stat in stats]
    
    return jsonify(response_body), 200

#Items
@api.route('/items', methods=['GET'])
def get_items():
    stmt = select(Items)
    items = db.session.execute(stmt).scalars().all()
    response_body = [item.serialize() for item in items]
    
    return jsonify(response_body), 200

#Builds
@api.route('/builds', methods=['GET'])
def get_builds():
    stmt = select(Builds)
    builds = db.session.execute(stmt).scalars().all()
    response_body = [build.serialize() for build in builds]
    
    return jsonify(response_body), 200

@api.route('/builds/<int:id>', methods=['GET'])
def get_build(id):
    stmt = select(Builds).where(Builds.id == id)
    build = db.session.execute(stmt).scalar_one_or_none()
    if build is None:
        return jsonify({"error": "Build not found"}), 404
    return jsonify(build.serialize()),200

@api.route('/builds', methods=['POST'])
@jwt_required()
def create_build():
    user_id = int(get_jwt_identity())

    data = request.get_json()
    
    user = db.session.get(Users, user_id)
    if user is None:
        return jsonify({"Error": "User not found"}), 404
    
    champion = db.session.get(Champions, data["champion_id"])
    if not champion:
        return jsonify({"error": "Champion not found"}), 404
    
    if not data or "title" not in data or "description" not in data or "champion_id" not in data:
        return jsonify({"error":"Missing required fields"}), 400
    try:
        new_build = Builds(
            title=data["title"],
            description=data["description"],
            champion_id=data["champion_id"],
            user_id=user_id,
            creation_date=datetime.now(timezone.utc)
        )
        db.session.add(new_build)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not create build", "details": str(e)}), 500

    return jsonify({"success": True, "build": new_build.serialize()}), 201

@api.route('/builds/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_build(id):
    user_id = int(get_jwt_identity())

    build = db.session.get(Builds, id)
    if build is None:
        return jsonify({"error": "Build not found"}), 404

    if build.user_id != user_id:
        return jsonify({"error": "Unauthorized: You can only delete your own builds"}), 403

    try:
        db.session.delete(build)
        db.session.commit()
        return jsonify({"success": True, "message": f"Build '{build.title}' deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not delete build", "details": str(e)}), 500

#Favourites
@api.route('/favourites', methods=['GET'])
@jwt_required()
def get_favourites():
    
    user_id = int(get_jwt_identity())
    favourites = db.session.query(Favourites).filter_by(user_id=user_id).all()
    response_body = [favourite.serialize() for favourite in favourites]
    
    return jsonify(response_body), 200

@api.route('/favourites/<int:build_id>', methods=['POST'])
@jwt_required()
def add_favourite(build_id):
    user_id = int(get_jwt_identity())
    
    user = db.session.get(Users, user_id)
    if user is None:
        return jsonify({"Error": "User not found"}), 404
    
    build = db.session.get(Builds, build_id)
    if build is None:
        return jsonify({"error": "Build not found"}), 404
    
    existing_fav = db.session.get(Favourites, {"user_id": user_id, "build_id": build_id})
    if existing_fav:
        return jsonify({"error": "Build already in favourites"}), 409

    try:
        favourite = Favourites(user_id=user_id, build_id=build_id)
        db.session.add(favourite)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not add favourite", "details": str(e)}), 500

    return jsonify({"success": True, "message": "Build added to favourites"}), 201

@api.route('/favourites/<int:build_id>', methods=['DELETE'])
@jwt_required()
def delete_build(build_id):
    user_id = int(get_jwt_identity())

    favourite = db.session.get(Favourites, {"user_id": user_id, "build_id": build_id})
    if favourite is None:
        return jsonify({"error": "Build not found in favourites"}), 404
    
    try:
        db.session.delete(favourite)
        db.session.commit()
        return jsonify({"success": True, "message": "Favourite discarded successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not discard favourite", "details": str(e)}), 500
    
#Builditems
@api.route('/builditems', methods=['GET'])
@jwt_required()
def get_builditems():
    
    user_id = int(get_jwt_identity())
    builditems = (db.session.query(Builditems).join(Builds, Builditems.build_id == Builds.id).filter(Builds.user_id == user_id).all())
    response_body = [builditem.serialize() for builditem in builditems]
    
    return jsonify(response_body), 200

@api.route('/builditems/<int:build_id>/<int:item_id>', methods=['POST'])
@jwt_required()
def add_builditem(build_id,item_id):
    user_id = int(get_jwt_identity())
    
    build = db.session.get(Builds, build_id)
    if build is None:
        return jsonify({"Error": "Build not found"}), 404
    
    if build.user_id != user_id:
        return jsonify({"error": "Unauthorized: You can only edit your own builds"}), 403
    
    item = db.session.get(Items, item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    existing_items = db.session.query(Builditems).filter_by(build_id=build_id).all()
    next_position = len(existing_items) + 1

    try:
        builditem = Builditems(build_id=build_id, item_id=item_id, item_position=next_position)
        db.session.add(builditem)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not add item to build", "details": str(e)}), 500

    return jsonify({"success": True, "message": "Item added to build"}), 201

@api.route('/builditems/<int:build_id>/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_builditem(build_id, item_id):
    user_id = int(get_jwt_identity())

    build = db.session.get(Builds, build_id)
    if build is None:
        return jsonify({"error": "Build not found"}), 404
    
    builditem = db.session.query(Builditems).filter_by(build_id=build_id, item_id=item_id).first()
    if builditem is None:
        return jsonify({"error": "Item not found in this build"}), 404

    if build.user_id != user_id:
        return jsonify({"error": "Unauthorized: You can only delete your own builds"}), 403

    try:
        db.session.delete(builditem)
        db.session.commit()
        return jsonify({"success": True, "message": "Item deleted from the build"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not delete the item from the build", "details": str(e)}), 500