from sqlalchemy.orm import Session
from pydantic import EmailStr
from app import models, schemas
from datetime import datetime, timezone
from psycopg2.sql import Identifier, SQL
from sqlalchemy import text

NoneType = type(None)


async def get_user_by_email(email: EmailStr, client_host: str, db: Session):
    """select user from the email and server url"""
    query = """SELECT * FROM "user" WHERE \
        email=:email AND server=:client_host"""
    values = {"email": email, "client_host": client_host}
    user = db.execute(query, values)
    # return the selected user
    user = user.mappings().all()
    if user:
        return user[0]
    else:
        raise ValueError


async def get_user_by_id(user_id: int, db: Session):
    """select user by using the id only"""
    query = """SELECT * FROM "user" WHERE id=:user_id"""
    values = {"user_id": user_id}
    user = db.execute(query, values)
    # return the selected user
    user = user.mappings().all()
    if user:
        return user[0]
    else:
        raise ValueError


async def del_user(email: EmailStr, client_host: str, db: Session):
    """delete user based on  email and server """
    query = """DELETE FROM "user" WHERE email=:email and server=:server"""
    values = {"email": email, "server": client_host}
    result = db.execute(query, values)
    # return True after doing the delete
    return result


async def add_user(user_data: schemas.User,
                   client_host: str,
                   db: Session):
    """
    # register/add user
    # this is the implementation using orm
    user = models.User(birth_date=user_data.birth_date,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    email=user_data.email,
                    password=user_data.password,
                    server=user_data.server)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
    """

    # the imp without using ORM
    query = """INSERT INTO "user" (email,\
                        password,\
                        first_name,\
                        last_name,\
                        birth_date,\
                        server,\
                        is_activated) values \
                        (:email,
                        :password,
                        :first_name,
                        :last_name,
                        :birth_date,
                        :server,
                        FALSE)"""
    values = {"email": user_data.email,
              "password": user_data.password,
              "first_name": user_data.first_name,
              "last_name": user_data.last_name,
              "birth_date": user_data.birth_date,
              "server": client_host}
    db.execute(query, values)
    return True


async def add_validation(user_id: int, pin_code: str, url: str, db: Session):
    """add a Validation routine"""
    query = """INSERT INTO "validation" (user_id,pin_code,url)\
               values(:user_id,:pin_code,:url)"""
    values = {"user_id": user_id, "pin_code": pin_code, "url": url}
    db.execute(query, values)
    return True


async def get_validation(url: str, db: Session):
    """select validation based on the url"""
    query = """SELECT * FROM "validation" WHERE url=:url"""
    values = {"url": url}
    validation = db.execute(query, values)
    # return the selected user
    validation = validation.mappings().all()
    if validation:
        return validation[0]
    else:
        raise ValueError


async def del_validation_by_url(url: str, db: Session):
    """delete a validation based on the url"""
    query = """DELETE FROM "validation" WHERE url=:url"""
    values = {"url": url}
    result = db.execute(query, values)
    # return the selected user
    return result


async def del_validation_by_id(user_id: int, db: Session):
    """delete a validation based on the user_id
        this func will be used as a coded cascade delete"""
    query = """DELETE FROM "validation" WHERE user_id=:user_id"""
    values = {"user_id": user_id}
    result = db.execute(query, values)
    # return the selected user
    return result


async def validate_user_by_url(username: str,
                               password: str,
                               validation: schemas.Validation,
                               user: schemas.User,
                               db: Session):
    sent_time = validation["time_email_sent"]
    actual_time = datetime.now(timezone.utc)
    timing = actual_time - sent_time
    if timing.total_seconds() > 60:
        raise TimeoutError
    if password == user["password"] and username == user["email"]:
        query = """UPDATE "user" SET is_activated=True\
                   where id=:user_id"""
        values = {"user_id": user}
        result = db.execute(query, values)
        return True
    else:
        raise AttributeError
