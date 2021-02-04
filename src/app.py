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

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1("Crime in United States"),
    dbc.Row([
        dbc.Col([
            html.Div('State'),
            html.Br(),
            dcc.Dropdown(
                id = 'state',
                options = [{'label': col, 'value': col} for col in state_list], 
                value = ['Texas'],
                multi=True),
            html.Br(),
            html.Div('Crime'),
            html.Br(),
            dcc.Dropdown(
                id = 'crime',
                style = {'width':'100%'},
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
                clearable=False
            )
        ], md= 3),
        dbc.Col([
            html.Iframe(
                id = 'geochart',
                style = {'border-width':'0', 'width': '200%', 'height': '400px'}),
            html.Iframe(
                id = 'trendchart',
                style = {'border-width':'0', 'width': '200%', 'height': '400px'})
        ], md = 6),
        dbc.Col([
            dcc.Graph(id = "treemap", style = {'border-width':'0', 'width': '150%', 'height': '800px'})
        ], md = 3)
    ])
])
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
        alt.Color('crime_count:Q'),
        alt.value('#dbe9f6')
    )).properties(width=500, height=300
    ).project(type='albersUsa'
    )

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
        alt.Color('crime', title = 'Crime'))

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

    fig = px.treemap(
        tree_map,
        path=['State', 'crime'],
        values = 'crime_count'
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug = True)