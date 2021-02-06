import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import altair as alt
from altair import datum
import pandas as pd
from preprocess import *

data_raw = pd.read_csv("data/raw/ucr_crime_1975_2015.csv")

def data_processing(data):
    data['state'] = data['ORI'].str[:2]
    states = pd.read_csv('data/raw/states.csv')
    data_with_state = pd.merge(data, states, how = 'left', left_on = 'state', right_on = 'Abbreviation')
    data_with_state = data_with_state.drop(['state', 'Abbreviation', 'url', 'source'], axis = 1)
    return data_with_state

data_crime = data_processing(data_raw)
state_list = data_crime['State'].unique().tolist()
state_list = [state for state in state_list if str(state) != 'nan']

color_discrete_map={"Homicide": "#ff7f0e",
                    "Rape": "#2ca02c",
                    "Larceny": "#1f77b4",
                    "Aggravated Assault": "#9467bd"}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1("Crime in United States",
    style = {
        'padding' : 20,
        'color': 'firebrick',
        'margin-top': 20,
        'margin-bottom': 20,
        'text-align': 'center',
        'font-size': '48px',
        'border-radius': 3,
        'font-family':'Georgia, Times, serif'
    }),
    dbc.Row([
        dbc.Col([
            html.Div('State'),
            html.Br(),
            dcc.Dropdown(
                id = 'state',
                options = [{'label': col, 'value': col} for col in state_list], 
                value = state_list[0:10],
                multi=True,
                style = {'border': '2px solid black'}),
            html.Br(),
            html.Div('Crime'),
            html.Br(),
            dcc.Dropdown(
                id = 'crime',
                style = {'width':'100%', 'border': '2px solid black'},
                options=[{'label': col, 'value': col} for col in crime_list], 
                value = crime_list,
                multi=True),
            html.Br(),
            html.Div('Year Range'),
            html.Br(),
            dcc.RangeSlider(
                id = 'year_range',
                min=1975, 
                max=2015, 
                marks={1975: '1975', 1985: '1985', 1995: '1995', 2005: '2005', 2015: '2015'},
                value=[data_crime['year'].min(), data_crime['year'].max()]
                ),
            html.Br(),
            html.Div('Metric'),
            html.Br(),
            dcc.Dropdown(
                id = 'metric',
                options=[
                {'label': 'Rate', 'value': 'Crime Rate'},
                {'label': 'Number', 'value': 'Crime Count'}
                ],
                value = 'Crime Rate',
                clearable=False,
                style = {'border': '2px solid black'}
            )
        ], md= 3,
        style = {
            'background-color' : '#e6e6e6',
            'padding' : 15,
            'border' : '8px solid black'
        }),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Geographical Plot", style = {'background-color': '#B22222'}),
                dbc.CardBody(
                    html.Iframe(
                        id = 'geochart',
                        style = {'border-width':'0', 'width': '125%', 'height': '400px', 'margin-top': '0', 'margin-left': '-5%'})
                )
            ], style={'border': 'none'}),
            html.Br(),
            dbc.Card([
                dbc.CardHeader("Trend Chart", style = {'background-color': '#B22222'}),
                dbc.CardBody(
                    html.Iframe(
                        id = 'trendchart',
                        style = {'border-width':'0', 'width': '125%', 'height': '400px'}),
                        style = {'margin-top': '0', 'margin-bottom' : '0', 'height': '400px'}
                )
            ], style={'border': 'none'})
        ], md = 6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TreeMap", style = {'background-color': '#B22222'}),
                dbc.CardBody(
                    dcc.Graph(id = "treemap",  style = {'border-width':'0', 'width': '125%', 'height': '1000px', 'margin-left':'-13%'}),
                    style = {"padding": '0', 'height': '100%'}
                )
            ], style={'border': '2 px solid white'})
        ], md = 3)
    ])
], style = {'max-width': '90%'})

@app.callback(
    Output('geochart', 'srcDoc'),
    Input('state', 'value'),
    Input('crime', 'value'),
    Input('year_range', 'value'),
    Input('metric', 'value')
)
def plot_geochart(state, crime, year_range, metric):
    print('You have selected "{}"'.format(state))
    print('You have selected "{}"'.format(year_range))
    print('You have selected "{}"'.format(crime))
    results_df = data_filtering_geochart(state, crime, metric, year_range, data_crime)
    states = alt.topo_feature(data.us_10m.url, 'states')
    geo_chart = alt.Chart(states).mark_geoshape(stroke = 'black').transform_lookup(
    lookup='id',
    from_=alt.LookupData(results_df, 'id', ['crime_count'])
    ).transform_calculate(
        crime_count = 'isValid(datum.crime_count) ? datum.crime_count : -1'
    ).encode(color = alt.condition(
        'datum.crime_count > 0',
        alt.Color('crime_count:Q', scale = alt.Scale(scheme = 'reds')),
        alt.value('#dbe9f6')
    )).properties(width=500, height=300
    ).project(type='albersUsa'
    ).configure_view(strokeWidth = 0)

    return geo_chart.to_html()

@app.callback(
    Output('trendchart', 'srcDoc'),
    Input('state', 'value'),
    Input('crime', 'value'),
    Input('year_range', 'value'),
    Input('metric', 'value')
)
def trend_chart(state, crime, year_range, metric):

    trend_chart_df = data_filtering_trendchart(state, crime, metric, year_range, data_crime)

    chart = alt.Chart(trend_chart_df).mark_line().encode(
        alt.X('year', title = "Year"),
        alt.Y('crime_count', title = metric),
        alt.Color('crime', title = 'Crime',
                    scale = alt.Scale(
                        domain=crime,
                        range=[color_discrete_map[c] for c in crime]
                    )))

    return chart.to_html()

@app.callback(
    Output('treemap', 'figure'),
    Input('state', 'value'),
    Input('crime', 'value'),
    Input('year_range', 'value'),
    Input('metric', 'value')
)
def tree_map(state, crime, year_range, metric):

    tree_map = data_filtering_treemap(state, crime, metric, year_range, data_crime)
    col_map = {c: color_discrete_map[c] for c in crime}

    fig = px.treemap(
        tree_map,
        path=['State', 'crime'],
        values = 'crime_count',
        color = 'crime',
        color_discrete_map=col_map
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug = True)