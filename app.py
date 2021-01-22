import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import altair as alt
from altair import datum
import pandas as pd

data = pd.read_csv("./ucr_crime_1975_2015.csv")

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
                    {'label': 'Philadelphia', 'value': 'Philadelphia'},
                    {'label': 'Phoenix', 'value': 'Phoenix'}
                ], multi=True),
            html.Br(),
            html.Div('Crime'),
            dcc.Dropdown(
                id = 'crime',
                style = {'width':'100%'},
                options = [
                    {'label': 'Homicide', 'value': 'homicide'},
                    {'label': 'Larceny', 'value': 'larceny'}
                ], multi=True)
        ], md=3),
        dbc.Col(
            html.Iframe(
                id = 'trendchart',
                style = {'border-width':'0', 'width':'100%', 'height': '400px'})
        )
    ])
])
@app.callback(
    Output('trendchart', 'srcDoc'),
    Input('state', 'value'),
    Input('crime', 'value')
)
def plot_trendchart(state, crime):
    chart = alt.Chart(data).mark_line().encode(
        x = 'year',
        y = 'homs_sum'
    )
    return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug = True)