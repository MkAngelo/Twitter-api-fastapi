# Python 
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
import json

# Pydantic
from pydantic import BaseModel, EmailStr, Field

# Fast API
from fastapi import FastAPI, status, Body, HTTPException, Form, Path

app = FastAPI()

# Models

class UserBase(BaseModel): 
    user_id: UUID = Field(...)
    email: EmailStr = Field(...)


class UserLogin(UserBase):
    password: str = Field(..., min_length=8)


class User(UserBase):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    birth_date: Optional[date] = Field(default=None)


class Tweet(BaseModel):
    tweet_id: UUID = Field(...)
    content: str = Field(
        ...,
        min_length=1,
        max_length=256
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)


class UserRegister(User):
    password: str = Field(..., min_length=8)

# Path Operations

## Users

### Register a User
@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a User",
    tags=["Users"]
)
def signup(user: UserRegister = Body(...)): 
    """ 
    Signup

    This path operation registers a user in the app


    Parameters:
        - Request body parameter
            - User: UserRegister

    Returns a Json with the absic user information:
        - user_id: UUID
        - email: Emailstr
        - first_name: str
        - last_name: str
        - birth_date: str

    """
    with open("users.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return user

### Login a User
@app.post(
    path="/login",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Login a User",
    tags=["Users"]
)
def login(user: UserLogin = Body(...)):
    """
    Login

    This path operation allows access to Twitter

    Parameter:
    - Request body parameters:
        - email: str
        - password: str

    Returns to twitter's home
    """
    user_dict = user.dict()
    with open("tweets.json", "r", encoding="utf-8") as h:
        home = json.loads(h.read())
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.loads(f.read())

        for person in users:
            if person["email"] == user_dict["email"]:
                if person["password"] == user_dict["password"]:
                    return home
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong email or password"
        )

### Show all Users
@app.get(
    path="/users",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="Show all users",
    tags=["Users"]
)
def show_all_users():
    """
    This path operation shows all users in the app

    Parameters:
    - return user
    
    Returns a json list with all users in the app, with the followin keys:
    - user_id: UUID
    - email: Emailstr
    - first_name: str
    - last_name: str
    - birth_date: str
    """
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Show a User
@app.get(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Show a User",
    tags=["Users"]
)
def show_a_user(id: UUID):
    """
    Show a User

    This path operations returns the user information

    Parameters:
    - Request body parameters:
        - id: UUID
    
    Returns information about the user
    """
    id = str(id)
    
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.loads(f.read())

        for us in users:
            if us["user_id"] == id:
                return us
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user not exists"
        )

### Delete a User
@app.delete(
    path="/users/{user_id}/delete",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Delete a User",
    tags=["Users"]
)
def delete_a_user(id: UUID):
    """
    Delete a user

    This path operation delete a user using his id

    **Parameters**
    - Resquest body parameters:
        - id: UUID

    Returns information about the deleted user
    """
    id = str(id)
    with open("users.json", "r", encoding="utf-8") as f:
        users_dict = json.loads(f.read())
        
        for user in users_dict:
            if user["user_id"] == id:
                users_dict.remove(user)
                with open("users.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(users_dict))
                return user
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user not exists"
        )

### Update a User
@app.put(
    path="/users/{user_id}/update",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a User",
    tags=["Users"]
)
def update_a_user(user: User = Body(...)):
    """
    Update User

    This path operation update the information about a user

    **Parameters**
    - Request body parameters: 
        - user: User
    
    Return the user's information updated
    """
    user_dict = user.dict()
    
    user_dict["user_id"] = str(user_dict["user_id"])
    user_dict["birth_date"] = str(user_dict["birth_date"])

    with open("users.json", "r", encoding="utf-8") as f:
        users_dict = json.loads(f.read())

        for user in users_dict:
            if user['user_id'] == user_dict["user_id"]:
                users_dict[users_dict.index(user)] = user_dict
                with open("users.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(users_dict))
                    return user_dict
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user not exists"
        )

## Tweets

### Show all Tweets
@app.get(
    path="/",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets",
    tags=["Tweets"]
)
def home():
    """
    Home

    This path operation shows all Tweets in the app

    Parameters:
    -
    
    Returns a json list with all tweets in the app, with the followin keys:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - updated_at: Optional[datetime]
    - by: User
    """
    with open("tweets.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Post a Tweet
@app.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a Tweet",
    tags=["Tweets"]
)
def post(tweet: Tweet = Body(...)):
    """ 
    Post a Tweet

    This path operation post a tweet in the app


    Parameters:
    - Request body parameter
        - tweet: Tweet

    Returns a Json with the basic tweet information:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - updated_by: Optional[datetime]
    - by: User

    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])
        results.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return tweet

### Show a Tweet
@app.get(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Show a Tweet",
    tags=["Tweets"]
)
def show_a_tweet(id: UUID):
    """
    Show a Tweet

    This path parameter shows a tweet of the list

    **Parameters**
    - Request body parameters:
        - id: UUID
    """
    id = str(id)

    with open("tweets.json", "r", encoding="utf-8") as f:
        tweets = json.loads(f.read())
        
        for tweet in tweets:
            if tweet["tweet_id"] == id:
                return tweet
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found :("
        )

### Delete a Tweet
@app.delete(
    path="/tweets/{tweet_id}/delete",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a Tweet",
    tags=["Tweets"]
)
def delete_a_tweet(id: UUID):
    """
    Delete a Tweet

    This path operation delete a tweet using his id

    **Parameters**
    - Resquest body parameters:
        - id: UUID

    Returns information about the deleted tweet
    """
    id = str(id)
    with open("tweets.json", "r", encoding="utf-8") as f:
        tweets_dict = json.loads(f.read())
        
        for tweet in tweets_dict:
            if tweet["tweet_id"] == id:
                tweets_dict.remove(tweet)
                with open("tweets.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(tweets_dict))
                return tweet
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )

### Update a Tweet
@app.put(
    path="/tweets/{tweet_id}/update",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a Tweet",
    tags=["Tweets"]
)
def update_a_tweet():
    pass