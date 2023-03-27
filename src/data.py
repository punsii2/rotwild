from io import StringIO

import numpy as np
import pandas as pd
import streamlit as st

from decrypt import decrypt_with_password


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={"location-lat": "lat", "location-long": "lon"})


def _filter_data(df: pd.DataFrame) -> pd.DataFrame:
    # remove marked outliers
    df = df[df["algorithm-marked-outlier"] != None]
    df = df[df["manually-marked-outlier"] != None]
    df = df.drop(columns=["manually-marked-outlier", "algorithm-marked-outlier"])

    # remove faulty gps measurements
    df = df.dropna(subset=["lat", "lon"])
    df = df[df["lat"] != 0]
    df = df[df["lon"] != 0]

    # drop useless columns
    df = df.drop(
        columns=[
            "comments",
            "cpu-temperature",
            "gps:fix-type-raw",
            "gps:satellite-count",
            "transmission-protocol", # probably irrelevant
            "mortality-status", # nan or 'nothing'
        ]
    )

    # "transmission-protocol", "sensor-type"])
    # diff = df['tag-local-identifier'] - df['individual-local-identifier']
    # df = df[diff!=0] ==> none are left => XXX these columns are identical
    df = df.drop(columns=['individual-local-identifier'])

    # drop all columns that contain only one value
    for column in df.columns.values:
        if len(df[column].unique()) == 1:
            df = df.drop(columns=[column])

    # look at all the possible values in order to find 'useful' ones
    for column in df.columns:
        print(column)
        print(df[column].unique())

    return df


def _transform_data(df: pd.DataFrame) -> pd.DataFrame:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    #df['day-of-year'] = df['timestamp'].dt.dayofyear
    return df


#@st.cache_data
def read_data(password: str) -> pd.DataFrame:
    FILENAME = "./red_deer_berchtesgarden_national_park.csv.enc"
    raw_data = decrypt_with_password(FILENAME, password)
    csv = StringIO(raw_data)

    df = pd.read_csv(csv)
    df = _rename_columns(df)
    df = _filter_data(df)
    return _transform_data(df)


# Data columns (total 22 columns):
# #   Column                           Non-Null Count   Dtype
# ---  ------                           --------------   -----
# 0   event-id                         253273 non-null  int64
# 1   visible                          253273 non-null  bool
# 2   timestamp                        253273 non-null  object
# 3   location-long                    252769 non-null  float64
# 4   location-lat                     252769 non-null  float64
# 5   algorithm-marked-outlier         0 non-null       float64
# 6   comments                         223011 non-null  object
# 7   cpu-temperature                  30262 non-null   float64
# 8   gps:dop                          253273 non-null  float64
# 9   gps:fix-type-raw                 253273 non-null  object
# 10  gps:satellite-count              30262 non-null   float64
# 11  gps:twilight                     30262 non-null   object
# 12  height-above-ellipsoid           240159 non-null  float64
# 13  height-raw                       12607 non-null   float64
# 14  manually-marked-outlier          0 non-null       float64
# 15  mortality-status                 30262 non-null   object
# 16  transmission-protocol            30262 non-null   object
# 17  sensor-type                      253273 non-null  object
# 18  individual-taxon-canonical-name  253273 non-null  object
# 19  tag-local-identifier             253273 non-null  int64
# 20  individual-local-identifier      253273 non-null  int64
# 21  study-name                       253273 non-null  object
# dtypes: bool(1), float64(9), int64(3), object(9)
