from fastapi import FastAPI
import json
from random import randint

app = FastAPI()


@app.get("/get_predictions_test")
async def get_predictions_test():
    return {"prediction": randint(-13, 13)}
