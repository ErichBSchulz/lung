#!/bin/bash
echo "starting"
inotifywait -mr -e close_write ventos |
while read D E F; do
  # echo "----------------hello $D $E $F"
  if [[ "$F" == *py ]] # debounce events by only reacting to second
  then
    ventos/test_trace.py
  fi
done
