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
sum_dict = {crime_list[i]: sum_list[i] for i in range(len(crime_list))} 
rate_dict = {crime_list[i]: rate_list[i] for i in range(len(crime_list))}
crime_dict = {'sum_dict': sum_dict, 'rate_dict': rate_dict}

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

def data_filtering_geochart(state, crime, metric, year_range, data_crime):
    pop = data.population_engineers_hurricanes()
    if year_range is not None:
        data_crime = data_crime.loc[data_crime["year"].between(year_range[0], year_range[1])]
    results = data_crime.groupby('State')['violent_per_100k'].sum()
    # crimes = [crime_dict[metric][x] for x in crime]
    # results = data_crime.groupby('State')[[crimes]].sum()
    results.to_frame()
    results_df = pd.merge(results, pop, how = 'right', left_on = 'State', right_on = 'state')
    return results_df

def data_filtering_trendchart(state, crime, metric, year_range, data_crime):
    
    crimes = [crime_dict[metric][x] for x in crime]
    trend_data = data_crime[data_crime['State'].isin(state)]
    trend_data = trend_data[(trend_data['year']>=year_range[0]) & (trend_data['year']<=year_range[1])]
    trend_data = trend_data.groupby('year')[crimes].mean().reset_index()
    trend_data = trend_data.melt(id_vars = "year", var_name = "crime", value_name = "crime_count")

    return trend_data

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
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
                value=[data_crime['year'].min(), data_crime['year'].max()]
                ),
            html.Br(),
            html.Div('Metric'),
            html.Br(),
            dcc.Dropdown(
                id = 'metric',
                options=[
                {'label': 'Rate', 'value': 'rate_dict'},
                {'label': 'Number', 'value': 'sum_dict'}
            ],
            value = 'rate_dict'
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
    geo_chart = alt.Chart(states).mark_geoshape().encode(color='violent_per_100k:Q'
    ).transform_lookup(
    lookup='id',
    from_=alt.LookupData(results_df, 'id', ['violent_per_100k'])
    ).properties(width=500, height=300
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
        alt.X('year'),
        alt.Y('crime_count'),
        alt.Color('crime'))

    return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug = True)