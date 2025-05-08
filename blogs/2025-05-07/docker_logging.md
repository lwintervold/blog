# Accessing Docker container logs from another Docker container

When developing software that uses containers, it's often the case that you'll run tests locally by running the actual service in a container, and run tests which interact with the service in another container. At times, there can be a need to observe the service's logging output - which for this example, we will assume is simply sent to stdout/stdrr and thus visible via `docker logs`. Observing logging output is a much weaker basis for asserting the correctness of a program, but for cases where there is no observable state change from the "public interface" of the service (RESTful APIs, etc), observing side effects like logging can be helpful.


A script like so to run the tests with a docker compose setup:
```
docker compose build
docker compose up --detach  # Service is running
docker logs --follow <service> > /tmp/<service>-out/<service>.log 2>&1 &  # dump the service logs to the host
docker compose run <tests>
docker compose down
```

Combined with a docker compose file structured like so:
```
services:
    <service>:
        ...

    <service-tests>:
        volumes:
            - /tmp/<service>-out:/tmp/<service>-out
```

Allows for the service tests container to directly access logs.