mkdir -p /tmp/example-out

docker compose build
docker compose up --detach example
docker logs --follow example-project-example-1 > /tmp/example-out/example.log 2>&1 &
docker compose run tests
docker compose down
