## background
i made sure do the work as explained, i was going to use a local SMTP docker,
gmail(which i used before) stop allowing using SMTP, i have an SMTP project already


you can find it here: https://github.com/HichamDz38/python_mailer_smtp
but in the end i used a third party provider: Mailjet but it has a limit for 200 e-mails (Free Trial)

and because the mailing process managed with a third party server,
There is no need to use queue tasks (sending mail), with RabbitMQ for example,
Also for caching with Redis,it's not neccecary for this specific application.

for the validation process, it's done via a link, there is a pin code yes.
But i did it just using a link instead, if the user has the link he has the pin_code,
And also it's better than emailing the pin_code alone.

the api can be used with different web_application, or server in another word,
but the same email can be used with different website, so the email address is not unique.
However, the combination server/email is unique.


## composition :
    in this project there is three conrainers:
        the web application : Registration API
        postgres database
        pgadmin web interface


## how to use it?

## 1: clone the project
    git clone https://github.com/HichamDz38/registration_api
## 2: run the commands:
    cd registration_api
    docker-compose up -d --build

## 2: access the api through the browser
    use the address : http://127.0.0.1:8008/docs
    where you can test the diffrent endpoints


    GET http://127.0.0.1:8008/users/ : to get the user data using an email address
    POST http://127.0.0.1:8008/users/ : to post the data for registration the user
    DELETE http://127.0.0.1:8008/users/ : to delete the user 
    GET http://127.0.0.1:8008/validation/ : to validate the user 


## 3: access to the database using pgadmin
    pgadmin can be accecible from : http://localhost:5555/
    credentials:
        PGADMIN_DEFAULT_EMAIL=pgadmin4@pgadmin.org
        PGADMIN_DEFAULT_PASSWORD=admin

    then we need to register a Server with this configuration:
        Name: [arbitrary name]
        host: host.docker.internal
        port: 6432
        maintenance databse: REG_API
        username: postgres
        password: postgres


## 4: How to run the tests
    get the id of the registration_api-web image
    >>docker ps
    you will see somthing like that

    CONTAINER ID   IMAGE                  COMMAND                  CREATED         STATUS         PORTS                           NAMES
    b0f6497345bd   registration_api-web   "uvicorn app.main:ap…"   2 minutes ago   Up 2 minutes   0.0.0.0:8000->8000/tcp          registration_api-web-1
    385ed3a76b9c   dpage/pgadmin4         "/entrypoint.sh"         2 minutes ago   Up 2 minutes   443/tcp, 0.0.0.0:5555->80/tcp   registration_api-pgadmin-1
    75464a9f01c4   postgres               "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes   0.0.0.0:6432->5432/tcp          registration_api-db-1
    
    in this case it's b0f6497345bd

    after that we need to enter to the bash of that image by
    >>docker exec -it [CONTAINER_ID] bash
    means
    >>docker exec -it b0f6497345bd bash

    after that we just need to run the tests by
    >>pytest -v
    
    

## project architecture

for this application i used a simple Monolothic architecture + third party SMTP
<pre>
+-------------------+
|     Rest API      | 
|      docker       |
| +---------------+ |                                     
| |   end points  | |                      
| |    Getway     | |  
| +---------------+ |
|         |         |
| +---------------+ |            +----------------+ 
| | busniss logic |--------------|  SMTP Service  | 
| |               | |            |                | 
| +---------------+ |            +----------------+ 
|         |         |
| +---------------+ |
| |   data layer  | |
| |               | | 
| +---------------+ |
|         |         |
+---------|---------+
          |
 +-----------------+ 
 |   Postgres DB   | 
 |     docker      | 
 +-----------------+
</pre>