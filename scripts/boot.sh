#!/data/data/com.termux/files/usr/bin/bash
# Termux:Boot hook: keep JARVIS alive after a reboot.
#   mkdir -p ~/.termux/boot && cp scripts/boot.sh ~/.termux/boot/50-jarvis
#   chmod +x ~/.termux/boot/50-jarvis
set -uo pipefail
APP_DIR="${JARVIS_HOME:-$HOME/jarvis}"
LOG="$APP_DIR/logs/boot.log"
mkdir -p "$APP_DIR/logs"

# Hold a wake lock for 10 minutes while services come up.
termux-wake-lock 2>/dev/null || true
sleep 20

echo "--- $(date) boot ---" >>"$LOG"

# Start a local model server if one is installed and not already running.
if command -v ollama >/dev/null 2>&1; then
  if ! curl -s --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "starting ollama" >>"$LOG"
    nohup ollama serve >>"$APP_DIR/logs/ollama.log" 2>&1 &
  fi
fi

# Background API so JARVIS is reachable without a terminal.
if [ "${JARVIS_BOOT_SERVICE:-1}" = "1" ]; then
  if command -v sv >/dev/null 2>&1 && sv status jarvis >/dev/null 2>&1; then
    echo "runit service present; leaving supervision to runit" >>"$LOG"
  else
    cd "$APP_DIR" || exit 0
    python3 jarvis.py --start >>"$LOG" 2>&1
  fi
fi

# Optional: hands-free voice loop. Needs Termux in the foreground for the mic
# dialog, so it is off unless you ask for it.
if [ "${JARVIS_BOOT_VOICE:-0}" = "1" ]; then
  cd "$APP_DIR" || exit 0
  nohup python3 jarvis.py --voice >>"$APP_DIR/logs/voice.log" 2>&1 &
  echo "voice loop pid $!" >>"$LOG"
fi

termux-wake-unlock 2>/dev/null || true
