import sys

from os.path import isdir, isfile, join, splitext
from os import listdir, walk
from pathlib import Path
import pandas as pd
from glob import iglob
from pathlib import Path

directory = sys.argv[1]


def handle_ds(filepath):
    print(f"ds: {filepath}")
    df = pd.read_csv(filepath)
    print(df.iloc[:10])


def handle_tg(filepath):
    print(f"tg: {filepath}")



for filename in iglob(directory, recursive=True):

    if not isfile(filename):
        continue

    file = Path(filename)
    parent = file.parent.name
    if file.parent.name == 'ds':
        handle_ds(filename)
    elif file.parent.name == 'tg':
        handle_tg(filename)
    else:
        print(f'Cannot process file of {parent} type')


  
# example: python convert_to_schema.py "/media/nmi/Data/discord_channels/data/**"