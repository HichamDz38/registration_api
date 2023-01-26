from pydantic import EmailStr
from fastapi import FastAPI, Depends, status,\
                    Response, Request
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal, engine, raw_database
from app.funcs import send_email, generate_key
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from asyncpg import exceptions

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/")
async def get_user(email: EmailStr, request: Request,
                   db: Session = Depends(get_db)):
    client_host = request.client.host
    user = await crud.get_user(email, client_host, raw_database, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/users/{email}")
async def del_user(email: EmailStr, request: Request,
                   db: Session = Depends(get_db)):
    client_host = request.client.host
    user = await crud.get_user(email, client_host, raw_database, db)
    if user:
        await crud.del_user(email, client_host, raw_database, db)
        return user
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/users/")
async def register_user(user_data: schemas.User,
                        request: Request,
                        db: Session = Depends(get_db)):
    client_host = request.client.host
    pin_code = generate_key()
    try:
        user = await crud.add_user(user_data, client_host, pin_code,
                                   raw_database, db)
    except exceptions.UniqueViolationError:
        return Response(status_code=status.HTTP_409_CONFLICT)
    if user:
        result = send_email(client_host,
                            user_data.email,
                            pin_code,
                            user_data.first_name,
                            user_data.last_name
                            )
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/users/{user_id}")
async def put_users(user_data: schemas.User_update,
                    db: Session = Depends(get_db)):
    user = await crud.put_user(user_data, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.patch("/users/{user_id}")
async def patch_user(user_data: schemas.User_update,
                     db: Session = Depends(get_db)):
    user = await crud.patch_user(user_data, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/users/validation/")
async def validate_user(pin_code: str,
                        request: Request,
                        db: Session = Depends(get_db),
                        credentials: HTTPBasicCredentials
                        = Depends(security)):
    client_host = request.client.host
    response = await crud.validate_user(credentials.username,
                                        credentials.password,
                                        client_host,
                                        pin_code,
                                        db,
                                        raw_database)
    if response:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
