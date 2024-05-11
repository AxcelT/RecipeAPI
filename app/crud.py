from typing import List, Optional
from sqlalchemy.orm import Session
from . import models, schemas, utils

# User CRUD operations
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not utils.verify_password(password, user.hashed_password):
        return None
    return user

# Recipe CRUD operations
def create_recipe(db: Session, recipe: schemas.RecipeCreate, user_id: int) -> models.Recipe:
    db_recipe = models.Recipe(**recipe.dict(), owner_id=user_id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def get_recipes(db: Session, skip: int = 0, limit: int = 10) -> List[models.Recipe]:
    return db.query(models.Recipe).order_by(models.Recipe.id.desc()).offset(skip).limit(limit).all()

def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[models.Recipe]:
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def update_recipe(db: Session, recipe_id: int, recipe: schemas.RecipeCreate) -> Optional[models.Recipe]:
    db_recipe = get_recipe_by_id(db, recipe_id)
    if db_recipe:
        for key, value in recipe.dict().items():
            setattr(db_recipe, key, value)
        db.commit()
        db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, recipe_id: int) -> Optional[models.Recipe]:
    db_recipe = get_recipe_by_id(db, recipe_id)
    if db_recipe:
        db.delete(db_recipe)
        db.commit()
    return db_recipe

# Rating CRUD operations
def create_rating(db: Session, rating: schemas.RatingCreate, user_id: int, recipe_id: int) -> models.Rating:
    db_rating = models.Rating(**rating.dict(), user_id=user_id, recipe_id=recipe_id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

# Comment CRUD operations
def create_comment(db: Session, comment: schemas.CommentCreate, user_id: int, recipe_id: int) -> models.Comment:
    db_comment = models.Comment(**comment.dict(), user_id=user_id, recipe_id=recipe_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_by_recipe_id(db: Session, recipe_id: int) -> List[models.Comment]:
    return db.query(models.Comment).filter(models.Comment.recipe_id == recipe_id).all()

# Search and suggestion operations
def search_recipes(db: Session, query: str, skip: int = 0, limit: int = 10) -> List[models.Recipe]:
    return db.query(models.Recipe).filter(models.Recipe.name.contains(query)).offset(skip).limit(limit).all()

def suggest_recipes(db: Session, ingredients: List[str], skip: int = 0, limit: int = 10) -> List[models.Recipe]:
    query = db.query(models.Recipe)
    for ingredient in ingredients:
        query = query.filter(models.Recipe.ingredients.contains(ingredient))
    return query.offset(skip).limit(limit).all()
