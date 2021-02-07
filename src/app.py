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
import plotly.graph_objects as go

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
                    "Homicide": "#9467bd",
                    "Rape": "#ff7f0e",
                    "Larceny": "#2ca02c",
                    "Aggravated Assault": "#1f77b4"}


button_style_white = {'background-color': 'white', 'width': '48%', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '10px'}
hom_button = {'background-color': "#9467bd", 'width': '48%', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '14px'}
larc_button = {'background-color': "#2ca02c",  'width': '48%', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '14px'}
rape_button = {'background-color': "#ff7f0e",  'width': '48%', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '14px'}
agg_button = {'background-color': "#1f77b4",  'width': '48%', 'height': '75px', 'margin': '0.5px 2px', 'font-size': '10px'}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
tab_height = '5vh'
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
            html.Div('State:'),
            html.Br(),
            dcc.Dropdown(
                id = 'state',
                options = [{'label': col, 'value': col} for col in state_list], 
                value = state_list,
                multi=True,
                style = {'border': '2px solid black'}),
            html.Br(),
            html.Br(),
            html.Div('Crime:'),
            html.Br(),
            html.Button('Homicide', id='hom_click', n_clicks=0, style = hom_button),
            html.Button('Rape', id='rape_click', n_clicks=0, style = rape_button),
            html.Br(),
            html.Br(),
            html.Button('Larceny', id='larc_click', n_clicks=0, style = larc_button),
            html.Button('Aggravated Assault', id='agg_click', n_clicks=0, style = agg_button),
            html.Br(),
            html.Br(),
            html.Div('Crime Metric:'),
            dcc.Dropdown(
                id = 'metric',
                options=[
                {'label': 'Rate (Crimes per 100k People)', 'value': 'Crime Rate (Crimes Committed Per 100,000 People)'},
                {'label': 'Number of Crimes Committed', 'value': 'Number of Crimes Committed'}
                ],
                value = 'Crime Rate (Crimes Committed Per 100,000 People)',
                clearable=False,
                style = {'border': '2px solid black'}
            ),
            html.Br(),
            html.Br(),
            html.Div('Year Range:'),
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
                dbc.CardHeader("Crime Rate/Crime Count By Region",
                style = {'background-color': '#B22222','textAlign': 'center', 'font-weight': 'bold'}),
                dbc.CardBody(
                    html.Iframe(
                        id = 'geochart',
                        style = {'border-width':'0', 'width': '125%', 'height': '400px', 'margin-top': '0', 'margin-left': '-5%'})
                )
            ], style={'border': 'none'}),
            html.Br(),
            dbc.Card([
                dbc.CardHeader("Crime Rate/Crime Count Over the Years",
                style = {'background-color': '#B22222','textAlign': 'center', 'font-weight': 'bold', 'font-size': '16px'}),
                dbc.CardBody(
                    html.Iframe(
                        id = 'trendchart',
                        style = {'border-width':'0', 'width': '125%', 'height': '400px'}),
                        style = {'margin-top': '0', 'margin-bottom' : '0', 'height': '400px'}
                )
            ], style={'border': 'none'})
        ], md = 6),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Distribution of Crime Based On:",
                style = {'background-color': '#B22222','textAlign': 'center', 'font-weight': 'bold', 'font-size': '16px', 'border-bottom': 'none'}),
                dbc.CardBody(
                    dbc.Tabs(
                [
                    dbc.Tab(label="Crime Type", tab_id="tab-1",
                            tab_style={"width": "50%"}, label_style={"color": "black"}),
                    dbc.Tab(label="State", tab_id="tab-2",
                            tab_style={"width": "50%"}, label_style={"color": "black"}),
                ],
                id="card-tabs",
                card=True,
                active_tab="tab-1",
                style={'border' : '0px', 'background-color': '#B22222', 'height':tab_height}
            ), style = {'background-color': '#B22222','textAlign': 'center', 'font-weight': 'bold', 'padding-top' : '0'}),
                dbc.CardBody(html.P(id="card-content", className="card-text"), style = {"padding": '0', 'height': '100%'}),
            ], style={'border': '2 px solid white'}),
        ], md = 3)
    ]), html.Hr(),
    html.P([f'''
    This dashboard was made by Aditya, Aishwarya and Charles Suresh. ''',
    ''' The city-crimes dataset collected as part of The Marshall Project has been used. Here is the link to the code: ''',
    html.A('Github Link', href = "https://github.com/UBC-MDS/DSCI_532_Group13_Crime")])
], style = {'max-width': '90%'})

@app.callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")]
)
def tab_content(active_tab):
    if active_tab == "tab-1":
        return dcc.Graph(id = "treemap",  style = {'border-width':'0', 'width': '125%', 'height': '1000px', 'margin-left':'-13%'})
    elif active_tab == "tab-2":
        return dcc.Graph(id = "treemap_2",  style = {'border-width':'0', 'width': '125%', 'height': '1000px', 'margin-left':'-13%'})

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
    
    geo_chart = alt.Chart(states).mark_geoshape(stroke = 'black', tooltip = True).transform_lookup(
    lookup='id',
    from_=alt.LookupData(results_df, 'id', ['crime_count'])
    ).transform_calculate(
        crime_count = 'isValid(datum.crime_count) ? datum.crime_count : -1'
    ).encode(color = alt.condition(
        'datum.crime_count > 0',
        alt.Color('crime_count:Q', scale = alt.Scale(scheme = 'reds'), title = metric),
        alt.value('#dbe9f6')
    )).properties(width=500, height=300
    ).project(type='albersUsa'
    ).configure_view(strokeWidth = 0)
    geo_chart = geo_chart.configure_legend(orient='none', direction= "horizontal",
                                    legendX=45, legendY= 300, gradientVerticalMinLength = 400,
                                     titleAnchor= alt.TitleAnchor('middle'), titleLimit=350)
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

    crime_metric = "Crime Rate"
    if metric == 'Number of Crimes Committed':
        crime_metric = "Crime Count"

    trend_chart_df = data_filtering_trendchart(state, crime, metric, year_range, data_crime)

    chart = alt.Chart(trend_chart_df).encode(
        alt.X('year', title = "Year", axis=alt.Axis(format="d", tickCount=10)),
        alt.Y('crime_count', title = metric),
        alt.Color('crime', title = 'Crime', legend = None,
                    scale = alt.Scale(
                        domain=crime,
                        range=[color_discrete_map[c] for c in crime])),
        tooltip=[alt.Tooltip('crime_count', title=crime_metric, formatType="number", format=".0f"),
                alt.Tooltip('crime', title='Crime Type'),
                alt.Tooltip('year', title='Year')])

    trend_plot = chart.mark_line(size=3) + chart.mark_circle(size=30)
    return trend_plot.to_html()

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
    tree_map['more_crimes'] = tree_map['crime']
    fig = px.treemap(
        tree_map,
        path=['crime', 'State'],
        values = 'crime_count',
        color = 'crime',
        color_discrete_map=color_discrete_map
    )
    fig.update_layout(margin_l= 50, margin_r=50,margin_t=10)

    return fig

@app.callback(
    Output('treemap_2', 'figure'),
    Input('state', 'value'),
    Input('year_range', 'value'),
    Input('metric', 'value'),
    Input('hom_click', 'n_clicks'),
    Input('rape_click', 'n_clicks'),
    Input('larc_click', 'n_clicks'),
    Input('agg_click', 'n_clicks')
)
def tree_map_2(state, year_range, metric, hom_click, rape_click, larc_click, agg_click):

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
    tree_map = data_filtering_treemap_2(state, crime_selected, metric, year_range, data_crime)
    tree_map['more_crimes'] = tree_map['crime']
    fig = px.treemap(
        tree_map,
        path=['State', 'crime'],
        values = 'crime_count',
        color = 'crime',
        color_discrete_map=color_discrete_map
    )
    fig.update_layout(margin_l= 50, margin_r=50, margin_t=10)
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
    app.run_server(dev_tools_ui=False,dev_tools_props_check=False)