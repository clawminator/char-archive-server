#!/bin/bash

SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do
  DIR=$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE
done
DIR=$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)

for file in "$DIR"/*; do
  if [[ -f "$file" && ("$file" == *.service || "$file" == *.timer) ]]; then
    files+=("$(basename "$file")")
  fi
done

sudo systemctl status --no-pager "${files[@]}"
