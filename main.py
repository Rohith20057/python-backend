from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List
app = FastAPI()

Mongodb_url = "mongodb://localhost:27017"
client = AsyncIOMotorClient(Mongodb_url)
db = client.testdatabase
user_collection = db.users

#pydantic model validates the input data

class User(BaseModel):
    name: str
    email : EmailStr

class UserOut(BaseModel):
    id:str
    name:str
    email:str

#convertion of objectid to string , specifically is to return mongodb data and fetch the users
def convert_id(user) -> dict:
    return{
    "id" : str(user["_id"]),
    "name": user["name"],
    "email": user["email"]
    }


#api end point starts here 
@app.get("/")
def home():
    return {"message": "Welcome to FastAPI with MongoDB"}

@app.post("/users",status_code=201)
async def create_users(user:User):
    
    existing_user = await user_collection.find_one({"email":user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    await user_collection.insert_one(user.dict())
    
    return{"message": "User created successfully"}

@app.get("/users",response_model=List[UserOut])
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
    
    result = await user_collection.update_one({"_id": ObjectId(user_id)}, #updating the id
                                     {"$set": user_dict}   #setting the new data
                                     )
    if result.matched_count==0:
        raise HTTPException(status_code=404, detail="user not found to update the data")
    else:
        return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result=await user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count ==0:
        raise HTTPException(status_code=404, detail="user cant found to delete the user")
    else:
        return {"message": "User deleted successfully"}


#now we have to get a single user by using ID:
@app.get("/users/{user_id}",response_model=UserOut)
async def get_single_user(user_id: str):
    
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
     
    if not user:   
        raise HTTPException(status_code=404, detail="user not found")
    return convert_id(user)

    
