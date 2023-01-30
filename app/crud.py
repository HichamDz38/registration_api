from sqlalchemy.orm import Session
from pydantic import EmailStr
from app import models, schemas
from datetime import datetime, timezone
from psycopg2.sql import Identifier, SQL
from sqlalchemy import text

NoneType = type(None)


async def get_user_by_email(email: EmailStr, client_host: str, db: Session):
    """select user from email and server"""
    query = """SELECT * FROM "user" WHERE \
        email=:email AND server=:client_host"""
    values = {"email": email, "client_host": client_host}
    user = db.execute(query, values)
    # return the selected user
    user = user.mappings().all()
    if user:
        return user[0]
    return False


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
        return False


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
                        (:email,:password,:first_name,:last_name,:birth_date,:server,FALSE)"""
    values = {"email": user_data.email,
              "password": user_data.password,
              "first_name": user_data.first_name,
              "last_name": user_data.last_name,
              "birth_date": user_data.birth_date,
              "server": client_host}
    db.execute(query, values)
    # the insert statement return None,  this is why we have to do select
    # in order to return the the user data
    return await get_user_by_email(user_data.email, client_host, db)


async def add_validation(user_id: int, pin_code: str, url: str, db: Session):
    """add a Validation routine"""
    query = """INSERT INTO "validation" (user_id,pin_code,url) values(:user_id,:pin_code,:url)"""
    values = {"user_id": user_id, "pin_code": pin_code, "url": url}
    db.execute(query, values)
    # as we said before insert return nothing, this is why i am returning the
    # crud.get_validation
    return get_validation(url, db)


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
    """select validation based on the url without ORM"""
    query = """DELETE FROM "validation" WHERE url=:url"""
    values = {"url": url}
    result = db.execute(query, values)
    # return the selected user
    return result


async def del_validation_by_id(user_id: int, db: Session):
    """select validation based on the url without ORM"""
    query = """DELETE FROM "validation" WHERE user_id=:user_id"""
    values = {"user_id": user_id}
    result = db.execute(query, values)
    # return the selected user
    return result


async def validate_user_by_url(username: str, password: str, url: str, db: Session):
    validation = get_validation(url, db)
    if validation:
        sent_time = validation["time_email_sent"]
        actual_time = datetime.now(timezone.utc)
        timing = actual_time - sent_time
        if timing.total_seconds() > 60:
            del_validation(url, db)
            raise TimeoutError
        user_id = validation["user_id"]
        user = get_user_by_id(user_id, db)
        if user:
            if password == user["password"] and username == user["email"]:
                query = """UPDATE "user" SET is_activated=True where id=:user_id"""
                values = {"user_id": user}
                result = db.execute(query, values)
                del_validation(url, db)
                return user
            else:
                raise AttributeError
        else:
            return False
    else:
        raise ValueError
