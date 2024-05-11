from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud, database, utils
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Constants for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI app
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create access token function
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user function
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Token generation route
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Create user route
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# Additional routes (recipes, search, suggestions, etc.)
@app.post("/recipes/", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_recipe(db=db, recipe=recipe, user_id=current_user.id)

@app.get("/recipes/", response_model=List[schemas.Recipe])
def read_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    recipes = crud.get_recipes(db, skip=skip, limit=limit)
    return recipes

@app.get("/recipes/search/", response_model=List[schemas.Recipe])
def search_recipes(query: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    recipes = crud.search_recipes(db, query=query, skip=skip, limit=limit)
    return recipes

@app.get("/recipes/suggestions/", response_model=List[schemas.Recipe])
def suggest_recipes(ingredients: List[str], skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    recipes = crud.suggest_recipes(db, ingredients=ingredients, skip=skip, limit=limit)
    return recipes

@app.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe

@app.put("/recipes/{recipe_id}", response_model=schemas.Recipe)
def update_recipe(recipe_id: int, recipe: schemas.RecipeUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None or db_recipe.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Recipe not found or not authorized")
    return crud.update_recipe(db=db, db_recipe=db_recipe, recipe=recipe)

@app.delete("/recipes/{recipe_id}", response_model=schemas.Recipe)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None or db_recipe.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Recipe not found or not authorized")
    return crud.delete_recipe(db=db, db_recipe=db_recipe)

@app.post("/recipes/{recipe_id}/ratings/", response_model=schemas.Rating)
def rate_recipe(recipe_id: int, rating: schemas.RatingCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_rating(db=db, rating=rating, recipe_id=recipe_id, user_id=current_user.id)

@app.post("/recipes/{recipe_id}/comments/", response_model=schemas.Comment)
def comment_recipe(recipe_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_comment(db=db, comment=comment, recipe_id=recipe_id, user_id=current_user.id)

@app.get("/recipes/{recipe_id}/comments/", response_model=List[schemas.Comment])
def read_comments(recipe_id: int, db: Session = Depends(get_db)):
    return crud.get_comments(db, recipe_id=recipe_id)
