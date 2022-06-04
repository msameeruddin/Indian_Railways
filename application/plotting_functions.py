import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px

from plotly import graph_objects as go

def plot_stations(stations_gdf, state_name=None, bbox_gdf=None, with_boundary=False):
    if with_boundary:
        if (state_name != 'All'): bbox_gdf = bbox_gdf[bbox_gdf['statename'] == state_name]
        else: pass

    if state_name:
        if (state_name != 'All'):
            stations_gdf = stations_gdf[stations_gdf['statename'] == state_name]
            # mean of the state_name's latitude and longitude
            clat = np.mean(stations_gdf.geometry.y)
            clon = np.mean(stations_gdf.geometry.x)
            zoom = 6
            size = 5
            title = state_name
        else:
            # India latitude and longitude
            with_boundary = False
            clat = 20.5937
            clon = 78.9629
            zoom = 4
            size = 4
            title = 'India'

        graph_data = []

        if with_boundary:
            blats = []
            blons = []

            for idx, row in bbox_gdf.iterrows():
                if (row['geometry'].geom_type == 'MultiPolygon'):
                    for poly in list(row['geometry']):
                        lon_vals, lat_vals = poly.exterior.coords.xy
                        blats.append(list(lat_vals))
                        blons.append(list(lon_vals))
                else:
                    lon_vals, lat_vals = row['geometry'].exterior.coords.xy
                    blats.append(list(lat_vals))
                    blons.append(list(lon_vals))

            blat_len = len(blats)
            blon_len = len(blons)

            if (blat_len == blon_len == 1):
                graph_data.append(
                    go.Scattermapbox(
                        lat=blats[0],
                        lon=blons[0],
                        mode='lines',
                        marker=dict(color='#808B96'),
                        showlegend=False,
                        text=state_name,
                        hoverinfo='text'
                    )
                )

            if (blat_len == blon_len) and (blat_len != 1):
                for i in range(blat_len):
                    graph_data.append(
                        go.Scattermapbox(
                            lat=blats[i],
                            lon=blons[i],
                            mode='lines',
                            marker=dict(color='#808B96'),
                            showlegend=False,
                            text=state_name,
                            hoverinfo='text'
                        )
                    )

        graph_data.append(
            go.Scattermapbox(
                lat=stations_gdf.geometry.y,
                lon=stations_gdf.geometry.x,
                mode='markers',
                marker=dict(color='#85C1E9', size=size),
                showlegend=False,
                text=stations_gdf['name'],
                hoverinfo='text'
            )
        )

        graph_layout = go.Layout(
            autosize=True,
            height=400,
            margin=dict(l=10, r=10, t=0, b=0),
            mapbox_style='carto-positron',
            mapbox=dict(
                center=dict(
                    lat=clat,
                    lon=clon
                ),
                zoom=zoom
            )
        )

        fig = go.Figure(data=graph_data, layout=graph_layout)
    
        return title, fig

    return None, None


def plot_train_paths(from_, to_, stops_switch, trains_gdf, stations_gdf):
    trains_gdf = trains_gdf[trains_gdf['from_sta_1'] == from_]

    if (to_ != 'All'):
        trains_gdf = trains_gdf[trains_gdf['to_stati_1'] == to_]
    
    from_code = trains_gdf.iloc[0]['from_stati']
    from_coords = stations_gdf[stations_gdf['code'] == from_code]['geometry']
    clat, clon = from_coords.y.tolist(), from_coords.x.tolist()
    
    if clat and clon:
        clat = clat[0]
        clon = clon[0]
    else:
        clat = 20.5937
        clon = 78.9629
    
    to_codes = trains_gdf['to_station'].to_list()
    to_names = trains_gdf['to_stati_1'].to_list()
    
    to_lats = []; to_lons = []
    for tc in to_codes:
        to_coords = stations_gdf[stations_gdf['code'] == tc]['geometry']
        tlat, tlon = to_coords.y.tolist(), to_coords.x.tolist()
        if tlat and tlon:
            to_lats.append(tlat[0])
            to_lons.append(tlon[0])

    graph_data = []
    
    # graph data
    for idx, row in trains_gdf.iterrows():
        if stops_switch:
            lons, lats = row['geometry'].coords.xy
            lons, lats = list(lons), list(lats)
            mode = 'lines+markers'
        else:
            row_coords = list(row['geometry'].coords)
            flon, flat = row_coords[0]
            tlon, tlat = row_coords[-1]
            lons = [flon, tlon]
            lats = [flat, tlat]
            mode = 'lines'
        
        # line plot (joining the coordinates)
        gd = go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode=mode,
            marker=dict(
                size=5,
                color='#85C1E9'
            ),
            opacity=0.7,
            showlegend=False,
            text=row['name'],
            hoverinfo='text'
        )
        
        graph_data.append(gd)
    
    # to stations' (scatter plot)
    graph_data.append(
        go.Scattermapbox(
            lat=to_lats,
            lon=to_lons,
            mode='markers',
            marker=dict(
                color='#D35400',
                size=8
            ),
            showlegend=False,
            text=to_names,
            hoverinfo='text'
        )
    )
    
    # from station (scatter plot)
    graph_data.append(
        go.Scattermapbox(
            lat=[clat],
            lon=[clon],
            mode='markers',
            marker=dict(
                color='#7D3C98',
                size=10
            ),
            showlegend=False,
            text=from_,
            hoverinfo='text'
        )
    )
    
    # graph layout
    layout = go.Layout(
        autosize=True,
        height=400,
        margin=dict(l=10, r=10, t=0, b=0),
        mapbox_style='carto-positron',
        mapbox=dict(
            center=dict(
                lat=clat,
                lon=clon
            ),
            zoom=5
        )
    )
    
    # graph figure
    fig = go.Figure(data=graph_data, layout=layout)
    
    return fig


def fetch_trains_info(from_, to_, trains_gdf):
    trains_gdf = trains_gdf[trains_gdf['from_sta_1'] == from_]
    if (to_ != 'All'): trains_gdf = trains_gdf[trains_gdf['to_stati_1'] == to_]
    cols = ['arrival', 'departure', 'first_clas', 'duration_m', 'sleeper', 'distance']
    df = trains_gdf[cols]
    df.columns = ['Arrival', 'Departure', '1st Class', 'Time (m)', 'Sleeper', 'Dist (KM)']
    return df