import os
import numpy as np
import time
import threading
from step1_querry_to_premetheus import create_prometheus_range_query_url, call_prometheus_query_url_with_timeout
from step2_intelligence_layer_call_for_prediction_model_crud import load_saved_model, load_scaler, run_model
from step3_prometheus_or_thanos_call_to_upload_predicted_metrics import post_model_result

SEQUENCE_SIZE = 5
MODEL_PARALLEL_INSTANCES_NUMBER = int(os.getenv('PARALLEL_INSTANCES_NUMBER', '50'))
BASE_URL = os.getenv('BASE_URL', 'http://91.138.223.127:30008/api/v1/query_range')
QUERY = os.getenv('QUERY', 'scaph_process_power_consumption_microwatts{container_id="a5e78c7ba4b2351f4cc9e66f1023145b6a52fd138c122a07fc10f7807fa18051", job="scaphandre"}')
STEP_IN_SECONDS = int(os.getenv('STEP_IN_SECONDS', '10'))


def prepare_results_for_model_input(results, scaler):
    """
    Takes the results from the prometheus/Thanos query and prepares them as an input for the model call.

    :param results: The results returned from prometheus/Thanos query, a list of tuples.
    :param scaler: The scaler to transform the data passed.
    :return:
    """
    # Extract the second value from each tuple that is the metric value
    extracted_values = [value[1] for value in results]
    # Desired size of the new list is the sequence size provided
    desired_size = SEQUENCE_SIZE
    # Prepend zeros if the extracted list is smaller than the desired size
    if len(extracted_values) < desired_size:
        extracted_values = [0] * (desired_size - len(extracted_values)) + extracted_values
    if len(extracted_values) > desired_size:
        extracted_values = extracted_values[len(extracted_values) - desired_size:]

    # Convert the list to a numpy array with the shape (1, desired_size, 1)
    result_array = np.array(extracted_values)
    result_array = result_array.reshape(-1, 1)
    result_array = scaler.transform(result_array)
    result_array = result_array.reshape(1, desired_size, 1)
    return result_array


def repeated_operation(model, model_name, model_scaler):
    # create the url for the query
    query_url = create_prometheus_range_query_url(BASE_URL, QUERY, STEP_IN_SECONDS, SEQUENCE_SIZE)
    try:
        # call the query url created to get the results
        query_results = call_prometheus_query_url_with_timeout(query_url, timeout=STEP_IN_SECONDS-1)
        # check that a result is returned
        if query_results is not None:
            # check if results is filled with data
            if len(query_results) > 0:
                # prepare the input data for the model
                model_input_data = prepare_results_for_model_input(query_results, model_scaler)
                # run the model and save the result
                model_result = run_model(model, model_scaler, model_input_data)
                model_result = model_result[0][0]
                response_code = post_model_result(model_name, model_result)
                print("HTTP call result {}".format(response_code))
        else:
            # If result is None, the call timed out
            print("HTTP call timed out, skipping to next iteration.")
    except Exception as e:
        print("An error occurred: {}".format(e))


if __name__ == '__main__':
    # load the saved model according to the model characteristics passed
    _model, _model_name = load_saved_model(MODEL_PARALLEL_INSTANCES_NUMBER)
    # load the saved model's scaler according to the model characteristics passed
    _model_scaler = load_scaler(MODEL_PARALLEL_INSTANCES_NUMBER)

    while True:
        start_time = time.time()
        # Run the repeated operation in a separate thread
        operation_thread = threading.Thread(target=repeated_operation, args=(_model, _model_name, _model_scaler))
        operation_thread.start()

        # Wait for the next time interval, taking into account the time already elapsed
        time_to_next_interval = max(STEP_IN_SECONDS - (time.time() - start_time), 0)
        time.sleep(time_to_next_interval)
