#!/bin/bash
cd "$(dirname "$0")"
for i in $(seq 1 30); do
  c=$(curl -s -o /dev/null -w "%{http_code}" -m 20 -A "FootballDocBot/1.0 (educational research)" "https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch=Pochettino&srnamespace=6&srlimit=1")
  echo "$(date +%H:%M) $c"
  if [ "$c" = "200" ]; then python3 photos.py; exit; fi
  sleep 300
done
