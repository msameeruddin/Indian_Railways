import warnings
warnings.filterwarnings('ignore')

import dash
import os
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import dash_daq as daq

from dash import (
    html,
    dcc,
    dash_table as dt
)
from dash.dependencies import (
    Input,
    Output
)
from plotly import graph_objects as go

from file_reader import read_shp_file
from plotting_functions import (
    plot_stations,
    plot_train_paths,
    fetch_trains_info
)
from miscellaneous import (
    states,
    from_stations
)


########################################
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = 'Inian Railways App'
server = app.server
########################################


# Data Reading
states_stations = read_shp_file(dir_name='states_stations')
states_data = read_shp_file(dir_name='IND_states')
trains_states = read_shp_file(dir_name='trains_states')
ind_boundary = read_shp_file(dir_name='IND_boundary')

# App Layout
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '10px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '5px solid #d6d6d6',
    'borderBottom': '3px solid #d6d6d6',
    'backgroundColor': '#7E8483',
    'color': 'white',
    'padding': '6px'
}

app.layout = html.Div([
    html.Meta(charSet='UTF-8'),
    html.Meta(name='viewport', content='width=device-width, initial-scale=1.0'),

    html.Div([
        html.H3(app.title)
    ], style={'textAlign' : 'center', 'paddingTop' : 10}),

    html.Div([
        html.Div([
            dcc.Tabs(
                id='input-tabs',
                value='stations',
                children=[
                    dcc.Tab(
                        label='Stations',
                        value='stations',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[
                            html.Div([
                                html.P('Select State')
                            ], style={'paddingTop' : 30}),
                            html.Div([
                                dcc.Dropdown(
                                    id='state-selector',
                                    options=[{'label' : v, 'value' : v} for v in states],
                                    value='All',
                                    clearable=False
                                )
                            ], style={'textAlign' : 'center', 'paddingTop' : 10}),
                            html.Div([
                                daq.ToggleSwitch(
                                    id='boundary-mode',
                                    size=60,
                                    label='Show Boundary',
                                    labelPosition='top',
                                    color='#717171',
                                    value=False,
                                )
                            ], style={'paddingTop' : 30}),
                        ]
                    ),
                    dcc.Tab(
                        label='Trains',
                        value='trains',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.P('From Station: ')
                                    ], style={'paddingTop' : 30}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='from-station-selector',
                                            options=[{'label' : k, 'value' : k} for k in from_stations],
                                            value='',
                                            clearable=False
                                        )
                                    ], style={'textAlign' : 'center', 'paddingTop' : 5}),  
                                ], className='six columns'),
                                html.Div([
                                    html.Div([
                                        html.P('To Station: ')
                                    ], style={'paddingTop' : 30}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='to-station-selector',
                                            clearable=False
                                        )
                                    ], style={'textAlign' : 'center', 'paddingTop' : 5}),  
                                ], className='six columns'),  
                            ], className='row'),
                            html.Div([
                                dcc.Checklist(
                                    id='train-stops-switch',
                                    options=[{'label' : 'Show Stops on Map', 'value' : 'show stops'}],
                                    value=['show stops']
                                )
                            ], style={'paddingTop' : 30}),
                            html.Div([
                                html.Div(id='train-info')
                            ], style={'paddingTop' : 30})
                        ]
                    )
                ]
            )
        ], className='four columns', style={'paddingTop' : 10}),

        html.Div([
            html.Div(id='map-output')
        ], className='eight columns')

    ], className='row', style={'paddingTop' : 30})

])

############################

@app.callback(
    Output('map-output', 'children'),
    [Input('input-tabs', 'value')]
)
def set_output_layout(which_tab):
    if (which_tab == 'stations'):
        output_layout = html.Div([
            html.Div( 
                children= [
                    dcc.Loading(
                        id='loading-op',
                        type='dot',
                        children=html.Div(id='output-map-stations')
                    )
                ],
                style={'textAlign' : 'center', 'paddingTop' : 10}
            )
        ])

    else:
        output_layout = html.Div([
            html.Div( 
                children= [
                    dcc.Loading(
                        id='loading-op',
                        type='dot',
                        children=html.Div(id='output-map-trains')
                    )
                ],
                style={'textAlign' : 'center', 'paddingTop' : 10}
            )
        ])

    return output_layout


############################


@app.callback(
    Output('output-map-stations', 'children'),
    [Input('state-selector', 'value'), Input('boundary-mode', 'value')]
)
def display_stations(state_name, with_boundary):
    if with_boundary:
        if (state_name != 'All'):
            title, fig = plot_stations(
                stations_gdf=states_stations,
                state_name=state_name,
                bbox_gdf=states_data,
                with_boundary=with_boundary
            )
        else:
            title, fig = plot_stations(stations_gdf=states_stations, state_name=state_name)
    else:
        title, fig = plot_stations(stations_gdf=states_stations, state_name=state_name)

    return html.Div([
        html.P(str(title)),

        dcc.Graph(
            id='state-stations-plot',
            figure=fig
        )
    ])


############################


def get_to_stations(from_, trains_gdf=trains_states):
    trains_gdf = trains_gdf[trains_gdf['from_sta_1'] == from_]
    to_stations = list(np.unique(trains_gdf['to_stati_1']))
    return to_stations

@app.callback(
    [Output('to-station-selector', 'options'),
     Output('to-station-selector', 'value')],
    [Input('from-station-selector', 'value')]
)
def update_to_stations(from_):
    to_stations = get_to_stations(from_=from_)
    
    if len(to_stations) == 1:
        val = to_stations[0]
    else:
        to_stations.insert(0, 'All')
        val = 'All'
        
    return [{'label' : i, 'value' : i} for i in to_stations], val

@app.callback(
    [Output('output-map-trains', 'children'),
     Output('train-info', 'children')],
    [Input('from-station-selector', 'value'),
     Input('to-station-selector', 'value'),
     Input('train-stops-switch', 'value')]
)
def display_train_paths(from_, to_, stops_switch):
    if to_ == 'All':
        tinfo = html.Div([
            html.P('The information cannot be displayed for `All` the stations.')
        ], style={'textAlign' : 'center'})
    else:
        tinfo_df = fetch_trains_info(from_=from_, to_=to_, trains_gdf=trains_states)
        data = tinfo_df.to_dict('rows')
        columns =  [{"name": i, "id": i,} for i in (tinfo_df.columns)]
        tinfo = html.Div([
            dt.DataTable(data=data, columns=columns)
        ], style={'textAlign' : 'center'})
    
    if from_ and to_:
        fig = plot_train_paths(
            from_=from_,
            to_=to_,
            stops_switch=stops_switch,
            trains_gdf=trains_states,
            stations_gdf=states_stations
        )

        fig_info = html.Div([
            html.P(str(from_) + ' - ' + str(to_)),

            dcc.Graph(
                id='from-to-train-path-plot',
                figure=fig
            )
        ])
        
        return fig_info, tinfo
    
    fig_info = html.Div([
        html.P('From an To are required.')
    ], style={'textAlign' : 'center', 'padding' : 100})
    
    tinfo = html.Div([
        html.P('The information cannot be displayed if `from` is empty.')
    ], style={'textAlign' : 'center'})
    
    return fig_info, tinfo


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)