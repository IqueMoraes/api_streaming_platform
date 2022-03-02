from curses.ascii import HT
from http import HTTPStatus
from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils import analyze_keys
from app.models.gender_model import GendersModel
from app.configs.database import db
from app.exc import PermissionError
from sqlalchemy.exc import IntegrityError


@jwt_required()
def post_gender():
    admin = get_jwt_identity()["administer"]
    if not admin:
        # TODO não entrou no except PermissionError
        # raise PermissionError
        # Ricardo
        return {"error": "not admin"}, HTTPStatus.BAD_REQUEST
    
    try:
        # TODO permitiu salvar duplicado, mas a model está ok
        # chequei com 'flask db migrate' e 'flask db upgrade' e não há correções pendentes
        # Ricardo
        data = request.get_json()
        keys = ["gender"]
        analyze_keys(keys, data)
        
        gender = GendersModel(**data)
        current_app.db.session.add(gender)
        current_app.db.session.commit()
        
        return jsonify(gender), HTTPStatus.CREATED

    except PermissionError:
        return {"error": "not admin"}, HTTPStatus.BAD_REQUEST
    except KeyError as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST
    except IntegrityError:
        return {"error": "gender already exists"}, HTTPStatus.CONFLICT

    except Exception:
        return {"error": "An unexpected error occurred"}, HTTPStatus.BAD_REQUEST

@jwt_required()
def get_gender(id):
    
    gender = GendersModel.query.filter_by(id=id).first()
    
    if not gender:
        return {"error": "No gender found"}, HTTPStatus.NOT_FOUND

    return jsonify(gender), HTTPStatus.OK

@jwt_required()
def delete_gender(id):
    admin = get_jwt_identity()["administer"]
    if not admin:
        return {"error": "not admin"}, HTTPStatus.BAD_REQUEST
    
    try:
        gender = GendersModel.query.filter_by(id=id).first()
        if not gender:
            return {"msg": "gender not found"}, HTTPStatus.NOT_FOUND
    
        gender.series = []
        gender.movies = []
        
        current_app.db.session.delete(gender)
        current_app.db.session.commit()
        
    except Exception:
        return {"error": "An unexpected error occurred"}, HTTPStatus.BAD_REQUEST

    return {}, HTTPStatus.NO_CONTENT

@jwt_required()
def patch_gender(id): 
    try:
        admin = get_jwt_identity()["administer"]
        if not admin:
            return {"error": "not admin"}, HTTPStatus.BAD_REQUEST
        
        data = request.get_json()
        keys = ["gender"]
        analyze_keys(keys, data)
        
        gender = GendersModel.query.filter_by(id=id).first()
        gender.gender = data["gender"]
        
        current_app.db.session.add(gender)
        current_app.db.session.commit()
    
    except KeyError as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST
    except IntegrityError:
        return {"error": "gender already exists"}, HTTPStatus.CONFLICT
    
    return {"msg": f"Patch gender ok, id {id}"}, HTTPStatus.OK