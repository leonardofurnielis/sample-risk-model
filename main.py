import os
from typing import Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time
import certifi

from ibm_watson_openscale import APIClient
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord
from ibm_watson_openscale.utils import IAMAuthenticator

from utils.prediction import predict

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI()

# Add FastAPI CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# FastAPI Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index() -> dict[str, str]:
    return {"status": "FastAPI is running!"}


@app.post('/api/v1/predict')
async def __predict__(request: Request):
    is_wos_request = request.headers.get('X-Wos-Request')

    try:
        request_data: dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload.",
        )
    
    input_data = request_data.get('values')

    input_fields = request_data.get("fields")

    start_time = time.time()
    if (input_data is None) or (input_fields is None):
        request_data = request_data['input_data'][0]
        input_data = request_data.get('values')
        input_fields = request_data.get('fields')

    if input_data is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid request syntax, `input_data` is required`",
        )
    else:
        wos_payload_logging_data = {"fields": input_fields, "values": input_data}
        predicted_values = predict(input_data)

        response_time = int((time.time() - start_time) * 1000)

        if not is_wos_request:  # perform payload logging if not watson openscale score request
            payload_logging(wos_payload_logging_data, predicted_values, response_time)

    return JSONResponse(
                content=predicted_values,
                status_code=200,
            )


def payload_logging(payload_scoring, scoring_response, response_time=460):
    try:
        authenticator = IAMAuthenticator(apikey="<API_KEY>",
                                         disable_ssl_verification=True)
        wos_client = APIClient(authenticator=authenticator, service_instance_id="<SERVICE_INSTANCE_ID>")

        scoring_id = str(uuid.uuid4())
        records_list = []

        pl_record = PayloadRecord(scoring_id=scoring_id, request=payload_scoring, response=scoring_response,
                                  response_time=response_time)
        records_list.append(pl_record)
        wos_client.data_sets.store_records(data_set_id="<DATA_SET_ID>", request_body=records_list)

    except Exception as e:
        print("Error performing payload logging")
