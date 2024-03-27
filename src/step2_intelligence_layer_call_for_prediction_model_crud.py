from keras.models import load_model
from pickle import load


def load_saved_model(parallel_instances_number):
    """
    Loads the model given the specific characteristics for parallel_instances_number.

    :param parallel_instances_number: The specific parallel instances number to filter by.
    :return: The saved model.
    """
    model_name = 'eco_efficiency_model_for_crud_parallel_instances_{}'.format(parallel_instances_number)
    model = load_model('./models/{}'.format(model_name))
    return model, model_name


def load_scaler(parallel_instances_number):
    """
    Loads the scaler of the model given the specific characteristics for parallel_instances_number.

    :param parallel_instances_number: The specific parallel instances number to filter by.
    :return: The saved scaler for the model.
    """
    scaler_name = 'eco_efficiency_scaler_for_crud_parallel_instances_{}'.format(parallel_instances_number)
    scaler = load(open('./scalers/{}'.format(scaler_name), 'rb'))
    return scaler


def run_model(model, scaler, data, pre_scale=False):
    """
    Accepts a model, a scale and data. It scales the data based on the scaler, fits them to the model, reverse scales
    the result

    :param model: The model to run.
    :param scaler: The scaler for the model.
    :param data: Input data. The data must be reshaped as (1, sequence_size, 1) to get a single output value.
    :param pre_scale: If the data needs to be scaled before model prediction.
    :return: The result
    """

    #  Why data already scaled
    scaled_data = data
    if pre_scale:
        scaled_data = scaler.transform(data)
    result = model.predict(scaled_data)
    result = scaler.inverse_transform(result)
    return result
