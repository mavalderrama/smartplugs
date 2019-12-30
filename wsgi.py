import os

from server import create_app

config_name = os.environ["FLASK_ENV"]
app = create_app(config_name)


if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=5555)
