# Author: Nicolas Legrand <nicolas.legrand@cfin.au.dk>

import time
import numpy as np
import pandas as pd
import os.path as op
from tqdm import tqdm
import requests
import io

ddir = op.dirname(op.realpath(__file__))

__all__ = ["import_ppg", "import_rr", "serialSim", "import_dataset1"]


# Simulate serial inputs from ppg recording
# =========================================
class serialSim():
    """Simulate online data acquisition using pre recorded signal and realistic
    sampling rate (75 Hz).
    """

    def __init__(self):
        self.sfreq = 75
        self.ppg = import_ppg().ppg.to_numpy()
        self.start = time.time()

    def inWaiting(self):
        if time.time() - self.start > 1 / self.sfreq:
            self.start = time.time()
            lenInWating = 5
        else:
            lenInWating = 0

        return lenInWating

    def read(self, lenght):

        if len(self.ppg) == 0:
            self.ppg = import_ppg().ppg.to_numpy()

        # Read 1rst item of ppg signal
        rec = self.ppg[:1]
        self.ppg = self.ppg[1:]

        # Build valid paquet
        paquet = [1, 255, rec[0], 127]
        paquet.append(sum(paquet) % 256)

        return paquet[0], paquet[1], paquet[2], paquet[3], paquet[4]

    def reset_input_buffer(self):
        print('Reset input buffer')


def import_ppg():
    """Import a 5 minutes long PPG recording.

    Returns
    -------
    df : :py:class:`pandas.DataFrame`
        Dataframe containing the PPG signale.
    """
    path = ('https://github.com/embodied-computation-group/systole/raw/'
            'master/systole/datasets/')
    response = requests.get(f'{path}/ppg.npy')
    response.raise_for_status()
    ppg = np.load(io.BytesIO(response.content), allow_pickle=True)
    df = pd.DataFrame({'ppg': ppg})
    df['time'] = np.arange(0, len(df))/75

    return df


def import_rr():
    """Import PPG recording.

    Returns
    -------
    rr : :py:class:`pandas.DataFrame`
        Dataframe containing the RR time-serie.
    """
    path = ('https://github.com/embodied-computation-group/systole/raw/'
            'master/systole/datasets/')
    rr = pd.read_csv(op.join(path, 'rr.txt'))

    return rr


def import_dataset1(modalities=['ECG', 'EDA', 'Respiration', 'Stim']):
    """Import PPG recording.

    Returns
    -------
    df : :py:class:`pandas.DataFrame`
        Dataframe containing the RR time-serie.

    Notes
    -----
    Load a 20 minutes recording of ECG, EDA and respiration of a young healthy
    participant undergoing the emotional task (valence rating of neutral and
    disgusting images) described in _[1].

    References
    ----------
    [1] : Legrand, N., Etard, O., Vandevelde, A., Pierre, M., Viader, F.,
        Clochon, P., Doidy, F., Peschanski, D., Eustache, F. & Gagnepain, P.
        (2018). Preprint version 3.0.
        doi: https://www.biorxiv.org/content/10.1101/376954v3
    """
    path = ('https://github.com/embodied-computation-group/systole/raw/'
            'master/systole/datasets/Task1_')
    pbar = tqdm(modalities, position=0, leave=True)
    data = {}
    for item in pbar:
        pbar.set_description(f"Downloading {item} channel")
        response = requests.get(f'{path}{item}.npy')
        response.raise_for_status()
        data[item.lower()] = np.load(io.BytesIO(response.content),
                                     allow_pickle=True)

    df = pd.DataFrame(data)
    df['time'] = np.arange(0, len(df))/1000

    return df
