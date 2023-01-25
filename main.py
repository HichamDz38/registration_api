from typing import List
from urllib import response
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status,\
                    APIRouter, Response
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import crud
import models
import schemas
from database import SessionLocal, engine, raw_database
from mailjet_api import send_email
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/{emp_id}", response_model=schemas.User)
async def get_user(emp_id: int, db: Session = Depends(get_db)):
    user = await crud.get_employee(emp_id, db)
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
    user = await crud.add_user(user_data, db, raw_database)
    if user:
        result = send_email(user_data.server,
                            user_data.email,
                            user_data.first_name,
                            user_data.last_name)
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
    user = await crud.patch_employee(user_data, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
