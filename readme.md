## background
i made sure do the work as explained, i was going to use a local SMTP docker,
gmail(which i used before) stop allowing using SMTP, i have an SMTP project already
you can find it here: https://github.com/HichamDz38/python_mailer_smtp
but in the end i used a third party provider: Mailjet but it has a limit for 200 mail (Free Trial)

and because the mailing process managed with a third party server,
There is no need to use queue tasks (sending mail), with RabbitMQ for example,
Also for caching with Redis,it's not neccecary for this specific application.

for the validation process, it's done via a link, there is a pin code yes.
But i did it with just using a link insead, if the user has the link he has the pin_code,
And also it's better than emailing the pin_code alone.

the api can be used with diffrent web_application, or server in another word,
but the same email can be used with diffrent website, so the email address is not unique
but the combinaison server/email is unique.


## in this project there is three conrainers:
    the web application : Registration API
    postgres database
    pgadmin web interface


## how to use it?

# 1: clone the project
# 2: run the command:
    docker-compose up -d --build

# 2: access the api through the browser
    use the address : http://127.0.0.1:8000/docs
    where you can test the diffrent endpoints
    GET http://127.0.0.1:8000/users/ : to get the user data using an email address
    POST http://127.0.0.1:8000/users/ : to post the data for registration the user
    DELETE http://127.0.0.1:8000/users/ : to delete the user 



# 3: access to the database using pgadmin:
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

## project architecture schema

for this application i used a simple Monolothic architecture + third party SMTP

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
