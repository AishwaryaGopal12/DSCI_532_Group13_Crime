import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import altair as alt
from altair import datum
import pandas as pd
from vega_datasets import data

crime_list = ['Homicide', 'Rape', 'Larceny', 'Violent']
sum_list = ['homs_sum', 'rape_sum', 'rob_sum', 'violent_crime']
rate_list = ['homs_per_100k', 'rape_per_100k', 'rob_per_100k', 'violent_per_100k']
# sum_dict = {crime_list[i]: sum_list[i] for i in range(len(crime_list))} 
# rate_dict = {crime_list[i]: rate_list[i] for i in range(len(crime_list))}

data_raw = pd.read_csv("./ucr_crime_1975_2015.csv")

def data_processing(data):
    data['state'] = data['ORI'].str[:2]
    states = pd.read_csv('./states.csv')
    data_with_state = pd.merge(data, states, how = 'left', left_on = 'state', right_on = 'Abbreviation')
    data_with_state = data_with_state.drop(['state', 'Abbreviation', 'url', 'source'], axis = 1)
    return data_with_state

data_crime = data_processing(data_raw)

def data_filtering_geochart(state, crime, year_range, data_crime):
    pop = data.population_engineers_hurricanes()
    if year_range is not None:
        data_crime = data_crime.loc[data_crime["year"].between(year_range[0], year_range[1])]
    results = data_crime.groupby('State')['violent_per_100k'].sum()
    results.to_frame()
    results_df = pd.merge(results, pop, how = 'right', left_on = 'State', right_on = 'state')
    return results_df

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div('State'),
            html.Br(),
            dcc.Dropdown(
                id = 'state',
                options = [
                    {'label': 'Colorado', 'value': 'Colorado'},
                    {'label': 'Texas', 'value': 'Texas'},
                    {'label': 'Georgia', 'value': 'Georgia'}
                ], 
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
                multi=True)
        ], md=3),
        dbc.Col(
            html.Iframe(
                id = 'geochart',
                style = {'border-width':'0', 'width':'100%', 'height': '400px'})
        )
    ]),
    dbc.Row([
        dbc.Col([
            html.Div('Year Range'),
            html.Br(),
            dcc.RangeSlider(
                id = 'year_range',
                min=1975, 
                max=2015, 
                marks={1975: '1975', 1985: '1985', 1995: '1995', 2005: '2005', 2015: '2015'},
                ),
            html.Br(),
            html.Div('Metric'),
            html.Br(),
            dcc.Dropdown(
                id = 'metric',
                options=[
                {'label': 'Rate', 'value': 0},
                {'label': 'Number', 'value': 1}
            ],
            value = 0
            )
        ], md = 3),
        dbc.Col([
            html.Iframe(
                id = 'trendchart',
                style = {'border-width':'0', 'width':'100%', 'height': '400px'})
        ])
    ])
])
@app.callback(
    Output('geochart', 'srcDoc'),
    Output('trendchart', 'srcDoc'),
    Input('state', 'value'),
    Input('crime', 'value'),
    Input('year_range', 'value'),
    Input('metric', 'value')
)
def plot_geochart(state, crime, year_range, metric):
    print('You have selected "{}"'.format(state))
    print('You have selected "{}"'.format(year_range))
    print('You have selected "{}"'.format(crime))
    results_df = data_filtering_geochart(state, crime, year_range, data_crime)
    states = alt.topo_feature(data.us_10m.url, 'states')
    geo_chart = alt.Chart(states).mark_geoshape().encode(color='violent_per_100k:Q'
    ).transform_lookup(
    lookup='id',
    from_=alt.LookupData(results_df, 'id', ['violent_per_100k'])
    ).properties(width=500, height=300
    ).project(type='albersUsa'
    )

    trend_chart = alt.Chart(data_crime).mark_line().encode(
        x = 'year',
        y = 'homs_sum'
    )

    return geo_chart.to_html(), trend_chart.to_html()


if __name__ == '__main__':
    app.run_server(debug = True)