import datetime
import json
import os
from threading import Thread

from fastapi import FastAPI

from models.available_devices import Devices

api_prefix = os.getenv("API_PREFIX", "/")

first_run = datetime.datetime.utcnow()

app = FastAPI()


@app.get("".join([api_prefix, "health_check"]))
async def health_check():
    try:
        return json.dumps(
            dict(
                status="Up and running",
                local_time="{}".format(datetime.datetime.utcnow()),
                running_since="{}".format(first_run),
            )
        )
    except Exception as error:
        return json.dumps(
            dict(
                status="something went wrong",
                local_time="{}".format(datetime.datetime.utcnow()),
                message=str(error),
            )
        )


async def start(device: Devices):
    device


@app.post("".join([api_prefix, "start"]))
async def start_server(device: Devices):
    try:
        server = Thread(target=start, args=(device,), daemon=True)
        server.start()
        return json.dumps(dict(status=200, message="daemon running"))
    except Exception as error:
        raise Exception("Something happened to the server => {}".format(error))
