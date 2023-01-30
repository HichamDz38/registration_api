from pydantic import EmailStr
from fastapi import FastAPI, Depends, status, Response, Request, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import get_db, engine
from app.funcs import send_email, generate_key, generate_url
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from asyncpg import exceptions
from sqlalchemy.exc import IntegrityError

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBasic()


@app.get("/users/{email}")
async def get_user_by_email(email: EmailStr, request: Request, db: Session = Depends(get_db)):
    client_host = request.client.host
    user = await crud.get_user_by_email(email, client_host, db)
    if user:
        return user
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/users/{email}")
async def del_user(email: EmailStr, request: Request, db: Session = Depends(get_db)):
    client_host = request.client.host
    user = await crud.get_user_by_email(email, client_host, db)
    if user:
        response = await crud.del_validation_by_id(user.id, db)
        response = await crud.del_user(email, client_host, db)
        return user
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/users/")
async def add_user(
        user_data: schemas.User, request: Request, db: Session = Depends(get_db)
):
    client_host = request.client.host
    pin_code = generate_key()
    while True:
        url = generate_url()
        try:
            await crud.get_validation(url, db)
        except ValueError:
            break
    try:
        user = await crud.add_user(user_data, client_host, db)
    except IntegrityError:
        return Response(status_code=status.HTTP_409_CONFLICT)
    if user:
        email_status = send_email(
            client_host,
            user_data.email,
            pin_code,
            url,
            user_data.first_name,
            user_data.last_name,
        )
        assert email_status.status_code == 200
        validation = await crud.add_validation(user["id"], pin_code, url, db)
        return user
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/validation/{url}")
async def validate_user(
        url: str,
        db: Session = Depends(get_db),
        credentials: HTTPBasicCredentials = Depends(security),
):
    try:
        await crud.get_validation(url, db)
    except ValueError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    try:
        response = await crud.validate_user_by_url(
            credentials.username, credentials.password, url, db
        )
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
