import urllib.parse
from datetime import datetime, timedelta
import requests


def create_prometheus_range_query_url(base_url, query, step_in_seconds, sequence_size, end_time=None):
    """
    Creates the URL that will ask prometheus/Thanos for the latest eco consumption values of a container.

    :param base_url: The base url of prometheus/Thanos API.
    :param query: The query to get the specific metric. Query must secure the uniqueness of the response results.
    :param step_in_seconds: The step at witch the query will get the past values of eco consumption from
                            prometheus/Thanos.
    :param sequence_size: How many past values are ideally wanted.
    :param end_time: Till what time to query. Default will be the current time that the function is called.
    :return: The url with all the info.
    """

    # Get the current time in ISO 8601 format with 'Z' to indicate UTC time
    end_timestamp = end_time
    if end_timestamp is None:
        end_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Convert string to datetime object
    start_timestamp = datetime.strptime(end_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    # Subtract the sequence_size * step_in_seconds
    start_timestamp = start_timestamp - timedelta(seconds=(sequence_size+1)*step_in_seconds)
    # Convert back to ISO 8601 format string with 'Z'
    start_timestamp = start_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

    # set step to a format of seconds that prometheus/Thanos understand
    step = str(step_in_seconds) + 's'

    # Construct the parameters
    params = {
        'query': query,
        'start': start_timestamp,
        'end': end_timestamp,
        'step': step
    }

    # URL encode the parameters
    encoded_params = urllib.parse.urlencode(params)

    # Combine with the base URL
    full_url = f"{base_url}?{encoded_params}"
    return full_url


def call_prometheus_query_url_with_timeout(url, timeout):
    """
    Call the url provided for querying prometheus/Thanos

    :param url: prometheus/Thanos query url.
    :param timeout: The amount of time in seconds to wait till the call is completed.
    :return: The results of the query in a list or tuples [(timestamp, value)]
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            res = response.json()
            if res['data']:
                if res['data']['result'] and len(res['data']['result']) > 0:
                    return res['data']['result'][0]['values']
                else:
                    return []
            else:
                return []
        else:
            return []
    except requests.exceptions.Timeout:
        print("Request timed out.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"An HTTP error occurred: {e}")
        return []
