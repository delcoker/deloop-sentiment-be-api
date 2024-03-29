from typing import List

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from starlette.requests import Request

from auth import auth
# Custom
from auth.auth import get_db
from controllers import scopes_controller
from core.schemas import scopes_dto

router = APIRouter(
    prefix="/scopes",
    tags=["Scopes"],
    dependencies=[Depends(auth.get_user_from_token)])


# Route to get scopes
@router.get("", response_model=List[scopes_dto.Scope])
def get_scopes(req: Request, db: Session = Depends(get_db)):
    all_scopes = scopes_controller.get_scopes(db, req.headers['token'])
    return all_scopes


# Route to store a scope
@router.post("/create", response_model=scopes_dto.Scope)
def scope_create(req: Request, scope: str = Form(...), db: Session = Depends(get_db)):
    db_scope = scopes_controller.create_scope(db, scope, req.headers['token'])
    if db_scope is None:
        raise HTTPException(status_code=404, detail="Scope could not be created")
    return db_scope


# Get a specified scope
@router.get("/{scope_id}", response_model=scopes_dto.Scope)
def read_scope(scope_id: int, req: Request, db: Session = Depends(get_db)):
    db_scope = scopes_controller.get_scope(
        db, req.headers['token'], scope_id=scope_id)
    if db_scope is None:
        raise HTTPException(status_code=404, detail="Scope not found")
    return db_scope


# Update specified scope
@router.post("/update/{scope_id}")  # , response_model=group_categories.GroupCategory
def update_scope(scope_id: int, scope: str = Form(...), db: Session = Depends(get_db)):
    db_scope = scopes_controller.update_scope(
        db, scope_id, scope)
    if db_scope is None:
        raise HTTPException(status_code=404, detail="Scope not found")
    return {"message": "Scope has been updated successfully"}


# Delete specified scope
@router.post("/delete/{scope_id}")
def delete_scope(scope_id: int, db: Session = Depends(get_db)):
    db_scope = scopes_controller.delete_scope(
        db, scope_id)
    if db_scope == 1:
        return {"message": "Scope has been deleted successfully"}
