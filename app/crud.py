from urllib import response
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
import json
from sqlalchemy.sql import text
from app import models, schemas

NoneType = type(None)


async def get_user(email: int, db: Session):
    user = db.query(models.User).from_statement(
        text("""SELECT * FROM "user" WHERE email=:email \
            order by id DESC limit 1""")
    ).params(email=email).first()
    # return the inserted record
    return user


async def del_user(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id
                                        ).first()
    db.delete(user)
    db.commit()
    return user


async def add_user(user_data: schemas.User, db: Session,
                   raw_database, pin_code):
    print(pin_code)
    """
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

    await raw_database.connect()
    results = await raw_database.execute("""INSERT INTO "user" (email,\
                        password,\
                        first_name,\
                        last_name,\
                        birth_date,\
                        server,\
                        key,\
                        activated) values \
                        ('{}','{}','{}','{}','{}','{}','{}',FALSE)""".format(
                                        user_data.email,
                                        user_data.password,
                                        user_data.first_name,
                                        user_data.last_name,
                                        user_data.birth_date,
                                        user_data.server,
                                        pin_code
                    ))

    user = db.query(models.User).from_statement(
        text("""SELECT * FROM "user" WHERE email=:email \
            order by id DESC limit 1""")
    ).params(email=user_data.email).first()
    await raw_database.disconnect()
    # return the inserted record
    return user


async def put_user(user_id: int, user_data: schemas.User, db: Session):
    pass


async def validate_user(username, password, key, db: Session, raw_database):
    user = db.query(models.User).from_statement(
        text("""SELECT * FROM "user" WHERE email=:email AND \
            password=:secret_pass order by id DESC limit 1""")
    ).params(email=username,
             secret_pass=password,
             ).first()
    if user:
        if key == user.key:
            await raw_database.connect()
            result = await raw_database.execute("""UPDATE user SET,\
                        validated=True)""")
            await raw_database.disconnect()
            return user
        else:
            return False
    else:
        return False
