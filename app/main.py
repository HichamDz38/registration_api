from pydantic import EmailStr
from fastapi import FastAPI, Depends, status, Response, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError
import logging
from app import crud, models, schemas
from app.database import get_db, engine
from app.funcs import send_email, generate_key, generate_url, get_hostname
from app.config import settings

logging.basicConfig(level=logging.DEBUG)
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBasic()


@app.get("/users/{email}")
async def get_user_by_email(email: EmailStr,
                            request: Request,
                            db: Session = Depends(get_db)):
    client_host = request.client.host
    try:
        user = await crud.get_user_by_email(email, client_host, db)
        return user
    except ValueError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/users/{email}")
async def del_user(email: EmailStr,
                   request: Request,
                   db: Session = Depends(get_db)):
    client_host = request.client.host
    try:
        user = await crud.get_user_by_email(email, client_host, db)
        response = await crud.del_validation_by_id(user.id, db)
        response = await crud.del_user(email, client_host, db)
        return user
    except ValueError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/users/")
async def add_user(user_data: schemas.User,
                   request: Request,
                   db: Session = Depends(get_db)):
    client_host = request.client.host
    pin_code = generate_key()
    while True:
        url = generate_url()
        try:
            await crud.get_validation(url, db)
        except ValueError:
            break
    try:
        result = await crud.add_user(user_data, client_host, db)
        # the insert statement return None,  this is why we have to do select
        # in order to return the the user data
        user = await crud.get_user_by_email(user_data.email, client_host, db)
    except IntegrityError:
        return Response(status_code=status.HTTP_409_CONFLICT)
    except ValueError:
        logging.CRITICAL("this is must not happen, check the code")
        return Response(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    if user:
        email_status = send_email(
            client_host,
            user_data.email,
            pin_code,
            url,
            user_data.first_name,
            user_data.last_name,
        )
        if not email_status.status_code == 200:
            logging.CRITICAL("email not send, subscription expired or no internet")
            logging.DEBUG(f"but here is the pin_code here{pin_code}")
            logging.DEBUG(f"you need to use this url to validate :")
            logging.DEBUG(f"http://{get_hostname}:{settings.WEB_APP_PORT}/validation/{url}")

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
        validation = await crud.get_validation(url, db)
    except ValueError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    try:
        user = await crud.get_user_by_id(validation["user_id"], db)
        result = await crud.validate_user_by_url(
            credentials.username, credentials.password, validation, user, db
        )
    except TimeoutError:
        return Response(status_code=status.HTTP_410_GONE)
    except AttributeError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    except ValueError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    if result:
        return Response(status_code=status.HTTP_200_OK)
    else:
        logging.CRITICAL("this will never print unless something wrong in the code")
        return Response(status_code=status.HTTP_501_NOT_IMPLEMENTED)
