from sqlalchemy.orm import Session

from controllers import rules_controller
from auth import auth
from core.models import schema

# from rules_controller import Rules
rules = rules_controller.Rules()


# Code for creating group category
def create_scope(db: Session, scope: str, token: str):
    user = auth.get_user_from_token(db, token)
    db_scope = schema.Scope(
        user_id=user.id,
        scope=scope
    )
    db.add(db_scope)
    db.commit()
    db.refresh(db_scope)
    rules.set_rules()
    return db_scope


# Get all scopes
def get_scopes(db: Session, token: str):
    user = auth.get_user_from_token(db, token)
    return db.query(schema.Scope) \
        .filter(schema.Scope.user_id == user.id) \
        .all()


# Get a particular scope
def get_scope(db: Session, token: str, scope_id: int):
    user = auth.get_user_from_token(db, token)
    return db.query(schema.Scope) \
        .filter(schema.Scope.id == scope_id,
                schema.Scope.user_id == user.id) \
        .first()


# Update a scope
def update_scope(db: Session, scope_id: int, scope: str):
    bad_chars = [';', '"', "'", "*"]
    scope_list = scope.split(",")
    sanitized_list = []

    for stripped_string in scope_list:
        for i in bad_chars:
            stripped_string = stripped_string.replace(i, '')

        stripped_string = stripped_string.strip()
        if ' ' in stripped_string:
            stripped_string = '"' + stripped_string + '"'
        sanitized_list.append(stripped_string)

    # print(sanitized_list)
    scopes = ",".join(sanitized_list)

    result = db.query(schema.Scope) \
        .filter(schema.Scope.id == scope_id) \
        .update({"scope": scopes})
    db.commit()
    rules.set_rules()
    return result


# Delete a scope
def delete_scope(db: Session, scope_id: int):
    # crud.get_user_token(db, token)
    result = db.query(schema.Scope) \
        .filter(schema.Scope.id == scope_id) \
        .delete()
    db.commit()
    rules.set_rules()
    return result
