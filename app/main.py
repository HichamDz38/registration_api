from pydantic import EmailStr
from fastapi import FastAPI, Depends, status,\
                    Response, Request, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal, engine, raw_database
from app.funcs import send_email, generate_key, generate_url
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
    user = await crud.get_user(email, client_host, raw_database)
    if user:
        await crud.del_user(email, client_host, raw_database)
        return user
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/users/")
async def add_user(user_data: schemas.User,
                        request: Request,
                        db: Session = Depends(get_db)):
    client_host = request.client.host
    pin_code = generate_key()
    url = generate_url()
    try:
        user = await crud.add_user(user_data, client_host,
                                   raw_database, db)
    except exceptions.UniqueViolationError:
        return Response(status_code=status.HTTP_409_CONFLICT)
    if user:
        email_status = send_email(client_host,
                            user_data.email,
                            pin_code,
                            url,
                            user_data.first_name,
                            user_data.last_name
                            )
        assert email_status.status_code == 200
        validation = await crud.add_validation(user["id"], pin_code,
                                               url, raw_database)
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


@app.get("/users/validation/{url}")
async def validate_user(url: str,
                        db: Session = Depends(get_db),
                        credentials: HTTPBasicCredentials
                        = Depends(security)):
    validation = await crud.get_validation(url, raw_database)
    try:
        response = await crud.validate_user_by_url(credentials.username,
                                        credentials.password,
                                        url,
                                        raw_database)
    except TimeoutError:
        return Response(status_code=status.HTTP_408_REQUEST_TIMEOUT)
    except AttributeError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    except ValueError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    if response:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
