from json.decoder import JSONDecoder


def decode_email(value: str):
    """
    Decodes a protected email from an HTML
    response. Generally, this is a x bits
    length string under `data-cfemail` that
    some websites put in place in order to
    prevent people from scrapping the email

    Parameters
    ----------

        value (str): a bits length string

    Returns
    -------

        str: the decoded email
    """
    decoded_elements = ''

    k = int(value[:2], 16)
    for i in range(2, len(value) - 1, 2):
        decoded_elements += chr(int(value[i:i+2], 16) ^ k)

    return decoded_elements
