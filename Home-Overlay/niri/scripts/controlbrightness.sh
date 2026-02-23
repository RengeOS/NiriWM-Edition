#!/bin/bash

STEP=5
DEVICE=""   # leave empty = auto detect main display
NOTIFY_ID_FILE="/tmp/brightness_notify_id"

# get previous notification id (avoid spam)
if [[ -f "$NOTIFY_ID_FILE" ]]; then
    REPLACE_ID="$(cat "$NOTIFY_ID_FILE")"
else
    REPLACE_ID=0
fi

# change brightness
case "$1" in
    up)
        brightnessctl ${DEVICE:+-d "$DEVICE"} set +"${STEP}%" >/dev/null
        ;;
    down)
        brightnessctl ${DEVICE:+-d "$DEVICE"} set "${STEP}%-" >/dev/null
        ;;
    *)
        echo "Usage: $0 {up|down}"
        exit 1
        ;;
esac

# get brightness percentage
BRIGHTNESS="$(brightnessctl ${DEVICE:+-d "$DEVICE"} get)"
MAX="$(brightnessctl ${DEVICE:+-d "$DEVICE"} max)"

PERCENT=$(( BRIGHTNESS * 100 / MAX ))

# send notification (replace old one)
NEW_ID="$(
    notify-send \
        -r "$REPLACE_ID" \
        -p \
        -u low \
        -h int:value:"$PERCENT" \
        "Brightness: ${PERCENT}%"
)"

echo "$NEW_ID" > "$NOTIFY_ID_FILE"
