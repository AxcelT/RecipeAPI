from pydantic import BaseModel
from typing import List, Optional

class RecipeBase(BaseModel):
    name: str
    ingredients: str
    steps: str
    prep_time: int

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    recipes: List[Recipe] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class RatingBase(BaseModel):
    rating: int

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    recipe_id: int
    user_id: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    recipe_id: int
    user_id: int

    class Config:
        from_attributes = True

