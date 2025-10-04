#!/bin/bash

SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do
  DIR=$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE
done
DIR=$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)

for file in "$DIR"/*; do
  if [[ -f "$file" && ("$file" == *.service) ]]; then
    services+=("$(basename "$file")")
  fi
done

for file in "$DIR"/*; do
  if [[ -f "$file" && ("$file" == *.timer) ]]; then
    timers+=("$(basename "$file")")
  fi
done

sudo cp "$DIR"/*.service "$DIR"/*.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl disable --now "${services[@]}" # we don't want all services starting on boot
sudo systemctl enable --now "${timers[@]}"

systemctl enable --now archive-server.service frontend-msg.service