#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/Users/hero/Documents/quant-harness"
PYTHON_BIN="$PROJECT_DIR/apps/api/.venv/bin/python3"
JOB_SCRIPT="$PROJECT_DIR/scripts/run_daily_job.py"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/daily_job.log"

mkdir -p "$LOG_DIR"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python venv not found at: $PYTHON_BIN"
  echo "Please run ./scripts/run_api.sh once first to create the virtualenv."
  exit 1
fi

CRON_LINE="5 16 * * 1-5 cd $PROJECT_DIR && $PYTHON_BIN $JOB_SCRIPT >> $LOG_FILE 2>&1"

( crontab -l 2>/dev/null | grep -v 'quant-harness/scripts/run_daily_job.py' ; echo "$CRON_LINE" ) | crontab -

echo "Installed cron job:"
echo "$CRON_LINE"
echo "Log file: $LOG_FILE"
