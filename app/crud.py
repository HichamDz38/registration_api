from sqlalchemy.orm import Session
from pydantic import EmailStr
from app import models, schemas
from datetime import datetime, timezone

NoneType = type(None)


async def get_user(email: EmailStr, client_host: str, raw_database):
    """select user from email and server without ORM"""
    await raw_database.connect()  # connect raw db
    user = await raw_database.fetch_one("""SELECT * FROM "user" WHERE \
        email='{}' AND server='{}' limit 1""".format(email, client_host))
    await raw_database.disconnect()  # connect raw db
    # return the selected user
    return dict(user)


async def get_user_by_id(user_id: int, raw_database):
    """select user from email and server without ORM"""
    await raw_database.connect()  # connect raw db
    user = await raw_database.fetch_one("""SELECT * FROM "user" WHERE id='{}'\
            """.format(user_id))
    await raw_database.disconnect()  # connect raw db
    # return the selected user
    return dict(user)


async def del_user(email: EmailStr, client_host: str, raw_database):
    """delete user based on  email and server without ORM"""
    await raw_database.connect()  # connect raw db
    await raw_database.execute("""DELETE FROM "user" WHERE email='{}' \
        AND server='{}'""".format(email, client_host))
    await raw_database.disconnect()  # disconnect raw db
    # return True after doing the delete
    return True


async def add_user(user_data: schemas.User,
                   client_host: str,
                   raw_database,
                   db: Session,):
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
    await raw_database.connect()
    await raw_database.execute("""INSERT INTO "user" (email,\
                        password,\
                        first_name,\
                        last_name,\
                        birth_date,\
                        server,\
                        is_activated) values \
                        ('{}','{}','{}','{}','{}','{}',FALSE)""".format(
                                        user_data.email,
                                        user_data.password,
                                        user_data.first_name,
                                        user_data.last_name,
                                        user_data.birth_date,
                                        client_host,
                    ))
    await raw_database.disconnect()
    # the insert statement return None,  this is why we have to do select
    # in order to return the the user data
    return await get_user(user_data.email, client_host, raw_database)


async def put_user(user_id: int, user_data: schemas.User):
    pass


async def add_validation(user_id: int, pin_code: str, url: str, raw_database):
    """add a Validation routine"""
    await raw_database.connect()
    await raw_database.execute("""INSERT INTO "validation" (user_id,\
                        pin_code,\
                        url) values \
                        ('{}','{}','{}')""".format(user_id,
                                                   pin_code,
                                                   url))
    await raw_database.disconnect()
    """as we said before insert return nothing, this is why i am returning the
    crud.get_validation"""
    return await get_validation(url, raw_database)


async def get_validation(url: str, raw_database):
    """select validation based on the url without ORM"""
    await raw_database.connect()  # connect raw db
    validation = await raw_database.fetch_one("""SELECT * FROM "validation"\
         WHERE url='{}' limit 1""".format(url))
    await raw_database.disconnect()  # connect raw db
    # return the selected user
    if validation:
        return dict(validation)
    else:
        raise ValueError


async def del_validation(url: str, raw_database):
    """select validation based on the url without ORM"""
    await raw_database.connect()  # connect raw db
    validation = await raw_database.fetch_one("""DELETE FROM "validation"\
         WHERE url='{}' """.format(url))
    await raw_database.disconnect()  # connect raw db
    # return the selected user
    return True


async def validate_user_by_url(username, password, url, raw_database):
    validation = await get_validation(url, raw_database)
    if validation:
        sent_time = validation["time_email_sent"]
        actual_time = datetime.now(timezone.utc)
        timing = actual_time-sent_time
        if timing.total_seconds() > 60:
            await del_validation(url, raw_database)
            raise TimeoutError
        user_id = validation["user_id"]
        user = await get_user_by_id(user_id, raw_database)
        if user:
            if password == user["password"] and username == user["email"]:
                await raw_database.connect()
                result = await raw_database.execute("""UPDATE "user" SET \
                    is_activated=True where id={}""".format(user_id))
                await raw_database.disconnect()
                await del_validation(url, raw_database)
                return user
            else:
                raise AttributeError
        else:
            return False
    else:
        raise ValueError
