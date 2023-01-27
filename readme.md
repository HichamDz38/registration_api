## in this project there is three conrainers:
    the web application
    postgres db
    pgadmin

## how to setup pgadmin:
    pgadmin can be accecible from : http://localhost:5555/
    then we need to register a Server with this configuration:
        Name: arbitrary name
        host: host.docker.internal
        port: 6432
        maintenance databse: REG_API
        username: postgres
        password: postgres

## how to use it?

# clone the project

# run:

    docker-compose build

    docker-compose up -d