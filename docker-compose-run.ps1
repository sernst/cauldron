docker-compose.exe run -d --name=cauldron_app_win --entrypoint=/commands/bin/loop-forever app

echo "[RUN]: Starting container"
docker exec -it cauldron_app_win /bin/bash

echo "[STOP]: Shutting down container 'cauldron_app_win'"
docker stop cauldron_app_win

echo "[REMOVE]: Removing container 'cauldron_app_win'"
docker rm cauldron_app_win

echo "[DONE]: Container cleanup complete"
