from typing import List
from urllib import response
from pydantic import EmailStr
from fastapi import FastAPI, Depends, HTTPException, status,\
                    APIRouter, Response
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import crud
import models
import schemas
from database import SessionLocal, engine, raw_database
from funcs import send_email, generate_key
models.Base.metadata.create_all(bind=engine)
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI()
security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/{user.id}", response_model=schemas.User)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = await crud.get_user(id, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/users/{emp_id}")
async def del_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_employee(user_id, db)
    if user:
        crud.del_user(user_id, db)
        return user
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/users/")
async def register_user(user_data: schemas.User, db: Session = Depends(get_db)):
    pin_code = generate_key()
    user = await crud.add_user(user_data, db, raw_database, pin_code)
    if user:
        result = send_email(user_data.server,
                            user_data.email,
                            pin_code,
                            user_data.first_name,
                            user_data.last_name
                            )
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/users/{user_id}" )
async def put_employee(user_data: schemas.User_update,
                 db: Session = Depends(get_db)):
    user = await crud.put_employee(user_data, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/users/{user_id}" )
async def patch_user(user_data: schemas.User_update,
                 db: Session = Depends(get_db)):
    user = await crud.patch_user(user_data, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/users/validation/{key}")
async def validate_user(key:str,
                        raw_database,
                        db: Session = Depends(get_db),
                        credentials: HTTPBasicCredentials\
                        = Depends(security)):
    stat = crud.validate_user(credentials.username, 
                        credentials.password,
                        key,
                        db,
                        raw_database)
    if status:
        return Response(status_code=status.HTTP_200_OK) 
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
