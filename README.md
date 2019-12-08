# health_bot
Telegram bot that helps to keep track of what hurts you and displays interesting statistics, for example, a histogram in time and an estimate by the Bayes theorem.
All data is stored in sqlite.

Instruction:
        git clone <path>
        cd health_bot
        touch records.db
        python3 create_db.py
        tmux new
        python3 hbot.py
