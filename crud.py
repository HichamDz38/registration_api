NoneType = type(None)
from urllib import response
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import UUID
import json
from sqlalchemy.sql import text
from models import User
import models, schemas

async def get_user(email: int, db: Session):
    user = db.query(User).from_statement(
        text("""SELECT * FROM "user" WHERE email=:email order by id DESC limit 1""")
    ).params(email=email).first()
    # return the inserted record
    return user


async def del_user(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id==user_id).first()
    db.delete(user)
    db.commit()
    return user

async def add_user(user_data : schemas.User, db: Session,
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
    # this is the imp without using ORM
    #raw_database.connect()
    await raw_database.connect()
    results =  await raw_database.execute("""INSERT INTO "user" (email,password,\
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

    user = db.query(User).from_statement(
        text("""SELECT * FROM "user" WHERE email=:email order by id DESC limit 1""")
    ).params(email=user_data.email).first()
    await raw_database.disconnect()
    # return the inserted record
    return user


def put_user(user_id: int, user_data : schemas.User, db: Session):
    update_data = user_data.dict(exclude_unset=True)
    user = db.query(models.User).filter(models.User.user_id==user_id).first()
    if type(user)==NoneType: return None
    user_dept = db.query(models.DeptEmp).filter(models.DeptEmp.user_id==user_id).first()
    if user_dept == None and "dept_id" in update_data:
        user_dept = models.DeptEmp(user_id=user_id,
                               dept_id=user_data.dept_id,
                               from_date=user_data.from_date,
                               to_date=user_data.to_date,
                               )
        db.add(user_dept)
        db.commit()
        db.refresh(user_dept)
    
    for field in update_data:
        if field in {"first_name","last_name","birth_date","gender","hire_date"}:
            setattr(user, field, update_data[field])
        if field in {"dept_id","from_date","to_date"}:
            setattr(user_dept, field, update_data[field])
                
    db.commit()
    db.refresh(user)
    if user_dept != None:
        db.refresh(user_dept)
    user_dept = db.query(models.User.user_id, models.User.first_name, models.User.last_name, 
                        models.User.hire_date, models.User.birth_date, models.User.birth_date,
                        models.DeptEmp.from_date, models.DeptEmp.to_date, models.Department.dept_name
    ).outerjoin(models.DeptEmp,models.User.user_id == models.DeptEmp.user_id
    ).outerjoin(models.Department,models.DeptEmp.dept_id == models.Department.dept_id
    ).filter(models.User.user_id==user_id
    ).first()
    return user_dept


    users = db.query(models.User.user_id, models.User.first_name, models.User.last_name, 
                        models.User.hire_date, models.User.birth_date, models.User.birth_date,
                        models.DeptEmp.from_date, models.DeptEmp.to_date, models.Department.dept_name
    ).outerjoin(models.DeptEmp,models.User.user_id == models.DeptEmp.user_id
    ).outerjoin(models.Department,models.DeptEmp.dept_id == models.Department.dept_id
    ).all()
    responce = {'data' : users}
    return responce


async def validate_user(username, password, key, raw_database, db:Session):
    user = db.query(User).from_statement(
        text("""SELECT * FROM "user" WHERE email=:email and \
            password:=password\
            order by id DESC limit 1""")
    ).params(email=username,
             password=password,
             ).first()
        
    if user:
        if key == user.key:
            result =  await raw_database.execute("""UPDATE user SET,\
                        validated=True)""")
            await raw_database.disconnect()
            return True
    else:
        await raw_database.disconnect()
        return False
    