#!/bin/bash

STEP=5
SINK="@DEFAULT_SINK@"
NOTIFY_ID_FILE="/tmp/volume_notify_id"

# Retrieve the old notify ID if available
if [[ -f "$NOTIFY_ID_FILE" ]]; then
    REPLACE_ID=$(cat "$NOTIFY_ID_FILE")
else
    REPLACE_ID=0
fi

case "$1" in
    up)
        pactl set-sink-volume "$SINK" +"$STEP"% 
        ;;
    down)
        pactl set-sink-volume "$SINK" -"$STEP"% 
        ;;
    mute)
        pactl set-sink-mute "$SINK" toggle
        ;;
    *)
        echo "Usage: $0 {up|down|mute}"
        exit 1
        ;;
esac

# Get the current volume
VOLUME=$(pactl get-sink-volume "$SINK" | grep -oP '\d+%' | head -1)

# Check mute
MUTED=$(pactl get-sink-mute "$SINK" | awk '{print $2}')

if [[ "$MUTED" == "yes" ]]; then
    MSG="Volume: Muted"
else
    MSG="Volume: $VOLUME"
fi

# Send notify and save id to replace next time (avoid spam)
NEW_ID=$(notify-send \
    -r "$REPLACE_ID" \
    -p \
    -u low \
    "$MSG")

echo "$NEW_ID" > "$NOTIFY_ID_FILE"
