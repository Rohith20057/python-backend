from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

Mongodb_url = "mongodb://localhost:27017"
client = AsyncIOMotorClient(Mongodb_url)
db = client.testdatabase
user_collection = db.users

#pydantic model validates the input data

class User(BaseModel):
    name: str
    email : EmailStr
        
#convertion of objectid to string , specifically is to return mongodb data and fetch the users
def convert_id(user) -> dict:
    user['_id'] = str(user['_id'])
    return user

#api end point starts here 
@app.get("/")
def home():
    return {"message": "Welcome to FastAPI with MongoDB"}

@app.post("/users")
async def create_users(user:User):
    
    user_dict = user.dict()
    
    await user_collection.insert_one(user_dict)
    
    return{"message": "User created successfully"}

@app.get("/users")
async def get_users():
    
    #CREATE AN EMPTY LIST TO STORE THE USERS 
    users = []
    
    #fetch all the users from the mongodb collection
    
    async for user_data in user_collection.find():
        users.append(convert_id(user_data)) #this function converts the objectid to string
    return users
    


@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    user_dict = user.dict()
    
    await user_collection.update_one({"_id": ObjectId(user_id)}, #updating the id
                                     {"$set": user_dict}   #setting the new data
                                     )
    return {"message": "User updated successfully"}


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    await user_collection.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted successfully"}


