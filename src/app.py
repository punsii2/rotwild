from urllib.error import URLError

from cryptography.fernet import InvalidToken
import matplotlib
import numpy as np
import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

from data import read_data


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
    with st.sidebar:
        password = st.text_input("Password:", type="password")
        if not password:
            return

        try:
            df = read_data(password)
        except InvalidToken:
            st.error("Incorrect password..")
            return
        show_data = st.checkbox("Show data")

        # st.write(px.violin(df, y='lat', points=False))
        # st.write(px.violin(df, x='lon', points=False))

        if st.checkbox("Filter by Tag-ID"):
            tag_id = st.selectbox("Tag-ID:", df["tag-local-identifier"].unique())
            df = df[df["tag-local-identifier"] == tag_id]

    if show_data:
        st.write("Raw Data:")
        st.write(df.shape)
        st.write(df)

    st.header("Red Deer Map")
    animate = st.checkbox("Animate", True)
    # day_of_year = st.slider("Day of Year", 0, 356)
    # df = df[df["week-of-year"] == day_of_year]
    fig = px.density_mapbox(
        df,
        lat="lat",
        lon="lon",
        mapbox_style="stamen-terrain",
        radius=4,
        zoom=11,
        opacity=0.8,
        height=700,
        width=700,
        animation_frame="week-of-year" if animate else None,
        animation_group="tag-local-identifier",
    )
    fig.update_coloraxes(showscale=False)
    st.write(fig)

    # st.write(px.density_heatmap(df, x="week-of-year", y="height-above-ellipsoid"))
    st.write(px.density_contour(df, x="week-of-year", y="height-above-ellipsoid"))


if __name__ == "__main__":
    main()
