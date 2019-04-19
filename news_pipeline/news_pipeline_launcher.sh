python3 news_monitor.py &
MONITOR_PID=$!
python3 news_fetcher.py &
FETCHER_PID=$!
python3 news_deduper.py &
DEDUPER_PID=$!



echo "=================================================="
read -p "PRESS [ENTER] TO TERMINATE PROCESSES." PRESSKEY

kill $MONITOR_PID $FETCHER_PID $DEDUPER_PID