from urllib.error import URLError
import matplotlib
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


@st.cache_data
def read_data() -> pd.DataFrame:
    df = pd.read_csv("../red_deer_berchtesgarden_national_park.csv")
    df = df.rename(columns={"location-lat": "lat", "location-long": "lon"})
    # XXX remove unused columns, but maybe use the 'manually-marked-outlier' column previously
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

    # diff = df['tag-local-identifier'] - df['individual-local-identifier']
    # df = df[diff!=0] ==> none are left => these columns are identical
    # XXX cleanup data
    df = df.dropna(subset=["lat", "lon"])
    df = df[df["algorithm-marked-outlier"] != None]
    df = df[df["manually-marked-outlier"] != None]
    df = df.drop(columns=["manually-marked-outlier", "algorithm-marked-outlier"])

    df = df.drop(columns=["comments"])
    # XXX remove this line
    #df = df.dropna()
    df.info()
    return df


@st.cache_data
def from_data_file(filename: str):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename
    )
    return pd.read_json(url)


def example_app():
    try:
        ALL_LAYERS = {
            "Bike Rentals": pdk.Layer(
                "HexagonLayer",
                data=from_data_file("bike_rental_stats.json"),
                get_position=["lon", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                extruded=True,
            ),
            "Bart Stop Exits": pdk.Layer(
                "ScatterplotLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius="[exits]",
                radius_scale=0.05,
            ),
            "Bart Stop Names": pdk.Layer(
                "TextLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_text="name",
                get_color=[0, 0, 0, 200],
                get_size=10,
                get_alignment_baseline="'bottom'",
            ),
            "Outbound Flow": pdk.Layer(
                "ArcLayer",
                data=from_data_file("bart_path_stats.json"),
                get_source_position=["lon", "lat"],
                get_target_position=["lon2", "lat2"],
                get_source_color=[200, 30, 0, 160],
                get_target_color=[200, 30, 0, 160],
                auto_highlight=True,
                width_scale=0.0001,
                get_width="outbound",
                width_min_pixels=3,
                width_max_pixels=30,
            ),
        }
        st.sidebar.markdown("### Map Layers")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)
        ]
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style=None,
                    initial_view_state={
                        "latitude": 37.76,
                        "longitude": -122.4,
                        "zoom": 11,
                        "pitch": 50,
                    },
                    layers=selected_layers,
                )
            )
        else:
            st.error("Please choose at least one layer above.")
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )


def main():
    # example_app()
    df = read_data()
    st.write("shape:")
    st.write(df.shape)
    st.write(df)



    groups = df.groupby("tag-local-identifier")
    st.write(groups)
    st.write(groups.groups)
    for name, group in groups:
        st.write(name)
        st.write(group)
        st.map(group)

    #st.write(pd.plotting.scatter_matrix(df._get_numeric_data()))


if __name__ == "__main__":
    main()
