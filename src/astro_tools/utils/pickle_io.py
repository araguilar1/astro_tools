"""
pickle_io.py

Functions
--------
writeDataToPkl  : Write Data to Binary Pickle Format
readDataFromPkl : Read Data from Binary Pickle Format

"""

import pickle


def writeDataToPkl(data, filepath):
    """
    Parameters
    ----------
    data : any
        data to write
    filepath : str or pathlib.Path
        file path to write to

    Returns
    -------
    None
    """

    with open(filepath, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    return


def readDataFromPkl(filepath):
    """
    Parameters
    ----------
    filepath : str or pathlib.Path
        file path to read from

    Returns
    -------
    data : any
        Pickled Data
    """

    with open(filepath, "rb") as f:
        data = pickle.load(f)

    return data
