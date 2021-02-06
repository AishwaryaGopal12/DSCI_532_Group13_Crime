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

alt.renderers.set_embed_options(actions=False)

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

color_discrete_map={'(?)':'#B22222',
                    "Homicide": "#ff7f0e",
                    "Rape": "#2ca02c",
                    "Larceny": "#1f77b4",
                    "Aggravated Assault": "#9467bd"}


button_style_white = {'background-color': 'white', 'width': '185px', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '18px'}
hom_button = {'background-color': "#ff7f0e", 'width': '185px', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '18px'}
larc_button = {'background-color': "#1f77b4",  'width': '185px', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '18px'}
rape_button = {'background-color': "#2ca02c",  'width': '185px', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '18px'}
agg_button = {'background-color': "#9467bd",  'width': '185px', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '18px'}

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
                value = state_list[0:25],
                multi=True,
                style = {'border': '2px solid black'}),
            html.Br(),
            html.Div('Crime'),
            html.Button('Homicide', id='hom_click', n_clicks=0, style = hom_button),
            html.Button('Rape', id='rape_click', n_clicks=0, style = rape_button),
            html.Br(),
            html.Br(),
            html.Button('Larceny', id='larc_click', n_clicks=0, style = larc_button),
            html.Button('Aggarvated Assault', id='agg_click', n_clicks=0, style = agg_button),
            html.Br(),
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
            ),
            html.Br(),
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
    Input('year_range', 'value'),
    Input('metric', 'value'),
    Input('hom_click', 'n_clicks'),
    Input('rape_click', 'n_clicks'),
    Input('larc_click', 'n_clicks'),
    Input('agg_click', 'n_clicks')
)
def plot_geochart(state, year_range, metric, hom_click, rape_click, larc_click, agg_click):
    print('You have selected "{}"'.format(state))
    print('You have selected "{}"'.format(year_range))
    # print('You have selected "{}"'.format(crime))

    crime = ['Homicide', 'Rape', 'Larceny', 'Aggravated Assault']
    if hom_click % 2  != 0:
        crime.remove('Homicide')
    if rape_click % 2  != 0:
        crime.remove('Rape')
    if larc_click % 2  != 0:
        crime.remove('Larceny')
    if agg_click % 2  != 0:
        crime.remove('Aggravated Assault')
    if not crime:
        crime = ['Homicide', 'Rape', 'Larceny', 'Aggravated Assault']

    if not state:
        state = state_list

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
    Input('year_range', 'value'),
    Input('metric', 'value'),
    Input('hom_click', 'n_clicks'),
    Input('rape_click', 'n_clicks'),
    Input('larc_click', 'n_clicks'),
    Input('agg_click', 'n_clicks')
)
def trend_chart(state, year_range, metric, hom_click, rape_click, larc_click, agg_click):
    crime = ['Homicide', 'Rape', 'Larceny', 'Aggravated Assault']
    if hom_click % 2  != 0:
        crime.remove('Homicide')
    if rape_click % 2  != 0:
        crime.remove('Rape')
    if larc_click % 2  != 0:
        crime.remove('Larceny')
    if agg_click % 2  != 0:
        crime.remove('Aggravated Assault')
    if not crime:
        crime = ['Homicide', 'Rape', 'Larceny', 'Aggravated Assault']

    if not state:
        state = state_list

    trend_chart_df = data_filtering_trendchart(state, crime, metric, year_range, data_crime)

    chart = alt.Chart(trend_chart_df).mark_line().encode(
        alt.X('year', title = "Year"),
        alt.Y('crime_count', title = metric),
        alt.Color('crime', title = 'Crime', legend = None,
                    scale = alt.Scale(
                        domain=crime,
                        range=[color_discrete_map[c] for c in crime])
                    ))

    return chart.to_html()

@app.callback(
    Output('treemap', 'figure'),
    Input('state', 'value'),
    Input('year_range', 'value'),
    Input('metric', 'value'),
    Input('hom_click', 'n_clicks'),
    Input('rape_click', 'n_clicks'),
    Input('larc_click', 'n_clicks'),
    Input('agg_click', 'n_clicks')
)
def tree_map(state, year_range, metric, hom_click, rape_click, larc_click, agg_click):

    crime_selected = ['Homicide', 'Rape', 'Larceny', 'Aggravated Assault']
    if hom_click % 2  != 0:
        crime_selected.remove('Homicide')
    if rape_click % 2  != 0:
        crime_selected.remove('Rape')
    if larc_click % 2  != 0:
        crime_selected.remove('Larceny')
    if agg_click % 2  != 0:
        crime_selected.remove('Aggravated Assault')
    if not crime_selected:
        crime_selected = ['Homicide', 'Rape', 'Larceny', 'Aggravated Assault']

    if not state:
        state = state_list
    tree_map = data_filtering_treemap(state, crime_selected, metric, year_range, data_crime)
    
    fig = px.treemap(
        tree_map,
        path=['State', 'crime'],
        values = 'crime_count',
        color = 'crime',
        color_discrete_map=color_discrete_map
    )
    

    return fig


@app.callback(
    Output('larc_click', 'style'),
    Output('hom_click', 'style'),
    Output('rape_click', 'style'),
    Output('agg_click', 'style'),
    Input('hom_click', 'n_clicks'),
    Input('rape_click', 'n_clicks'),
    Input('larc_click', 'n_clicks'),
    Input('agg_click', 'n_clicks'))
def all_button_style(clicks_hom, clicks_rape, clicks_larc, clicks_agg):

    if (clicks_hom % 2  != 0):
        hom_but = button_style_white
    else:
        hom_but = hom_button

    if clicks_rape % 2  != 0:
        rape_but = button_style_white
    else:
        rape_but = rape_button

    if clicks_larc % 2  != 0:
        larc_but = button_style_white
    else:
        larc_but = larc_button

    if clicks_agg % 2  != 0:
        agg_but = button_style_white
    else:
        agg_but = agg_button

    if ((clicks_hom % 2  != 0) & (clicks_rape % 2  != 0) & (clicks_larc % 2  != 0) & (clicks_agg % 2  != 0)):
        return larc_button, hom_button, rape_button, agg_button
    
    return larc_but, hom_but, rape_but, agg_but

if __name__ == '__main__':
    app.run_server(debug = True)