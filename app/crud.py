from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app import models, schemas

NoneType = type(None)


async def get_user(email: EmailStr, client_host: str, raw_database, db: Session):
    """select user from email and server without ORM"""
    await raw_database.connect() # connect raw db
    user = await raw_database.fetch_one("""SELECT * FROM "user" WHERE email='{}' \
            AND server='{}' limit 1""".format(email, client_host))
    await raw_database.disconnect() # connect raw db
    # return the selected user
    return dict(user)


async def del_user(email: EmailStr, client_host: str, raw_database, db: Session):
    """delete user based on  email and server without ORM"""
    await raw_database.connect() # connect raw db
    await raw_database.execute("""DELETE FROM "user" WHERE email='{}' \
        AND server='{}'""".format(email, client_host))
    await raw_database.disconnect() # disconnect raw db
    # return True after doing the delete
    return True


async def add_user(user_data: schemas.User,
                   client_host: str,
                   pin_code: str,
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
                        pin_code,\
                        is_activated) values \
                        ('{}','{}','{}','{}','{}','{}','{}',FALSE)""".format(
                                        user_data.email,
                                        user_data.password,
                                        user_data.first_name,
                                        user_data.last_name,
                                        user_data.birth_date,
                                        client_host,
                                        pin_code
                    ))
    await raw_database.disconnect()
    # the insert statement return None,  this is why we have to do select
    # in order to return the the user data
    return await get_user(user_data.email, client_host, raw_database, db)
    


async def put_user(user_id: int, user_data: schemas.User, db: Session):
    pass


async def validate_user(username, password, pin_code,
                        db: Session, raw_database):
    user = db.query(models.User).from_statement(
        text("""SELECT * FROM "user" WHERE email=:email AND \
            password=:secret_pass order by id DESC limit 1""")
    ).params(email=username,
             password=password,
             ).first()
    if user:
        if pin_code == user.pin_code:
            await raw_database.connect()
            result = await raw_database.execute("""UPDATE user SET,\
                        validated=True)""")
            await raw_database.disconnect()
            return user
        else:
            return False
    else:
        return False
