import requests


def post_model_result(model_name, result):
    # Construct the URL to which the request will be sent
    url = "http://91.138.223.127:30010/create_model"

    # Construct the JSON payload
    payload = {
        # Gauge metric type
        "type": 2,
        # Model name
        "model_name": model_name,
        # Value
        "value": str(result),
        # Labels
        "labels": {
            "model": "Demo for ICOS"
        }
    }

    # Send a POST request with the JSON payload
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        print("Success: The data was posted.")
    else:
        print("Error: Something went wrong with the post request. Status code:", response.status_code)

    return response.status_code
