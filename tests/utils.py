"""Ida's test utils."""
import os


def template_data(data: str):
    """Replace all ${} enclosed strings with their value in `os.environ`.

    Parameters
    ----------
    data : str
        The data to replace data in

    Returns
    -------
    data : str
        A copy of the data with all template variables replaced.
    """
    start = None
    while (template_start := data.find("${", start)) != -1:
        template_end = data.find("}", template_start)
        replace_str = data[template_start : template_end + 1]
        environ_str = data[template_start + 2 : template_end]
        new_str = os.environ[environ_str]
        start = template_end
        data = data.replace(replace_str, new_str)
    return data
