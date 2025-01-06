> [!WARNING]
> The project was created solely for educational purposes.

# What is "Any More Questions"?

This is a simple Telegram bot that uses free cloud neural networks to analyze text and images and, of course, answer and reason about questions posed.

## Build

You must have .env file with:

```console
LOGGING_LEVEL=INFO
BOT_TOKEN=<...>
CODER_TOKEN=<...>
VISION_TOKEN=<...>
MAX_CLIENT_COUNT=5
FREE_USES_COUNT=30
ALL_FREE_USES_COUNT=1000
USES_SPAN=3.0
```

You must have Python and pip suspended.

```console
git clone https://github.com/Refr900/any_more_questions.git
cd any_more_questions 
pip install -r requirements.txt
python src\main.py
```

## License

See the [LICENSE](LICENSE) file for license rights and limitations (MIT).
