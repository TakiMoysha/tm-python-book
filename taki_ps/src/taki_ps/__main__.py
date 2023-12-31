from .asgi import app

if __name__ == "__main__":
    import daphne

    daphne.run(app, host="0.0.0.0", port=8000)
