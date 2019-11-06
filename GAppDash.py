import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from iexfinance.stocks import get_historical_data
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests
import plotly.graph_objs as go
from iexfinance.stocks import get_historical_data

# df = get_historical_data("TSLA", start, end, output_format='pandas', token='pk_e7591c462d05417b8d9fdaf418d1fd61')

Gdata = pd.read_csv('newGApp.csv')
df = Gdata.groupby('Last Updated')['App'].count()

trace_line = go.Scatter(x=list(df.index),
                        y=list(df.values),
                        #visible=False,
                        name='Last Updated',
                        showlegend=False)


def update_news(): 
    url = 'https://cloud.iexapis.com/v1/stock/market/news/last/5?token=sk_f4c2aaac8f554dbcbbfffc4a128e23f8'
    r = requests.get(url)
    json_string = r.json()
    df = pd.DataFrame(json_string)
    df = pd.DataFrame(df[['headline', 'url']])
    return df

def generate_html_table(max_rows=10):
    df = update_news()
    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th()])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.A(
                                        df.iloc[i]['headline'],
                                        href=df.iloc[i]["url"],
                                        target='_blank'
                                    )
                                )
                            ]
                        )
                        for i in range(min(len(df), max_rows))
                    ]
                ),
                style={"height": "350px", "overflow": "scroll"},
            ),
        ],
        style={"height": "100%"},
    )


app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]) 


app.layout = html.Div([
    html.Div([
        html.H2("Google Play Store StatDash"),
        html.Img(src="https://cdn4.iconfinder.com/data/icons/free-colorful-icons/360/google_play.png"),
    ], className="banner"),

    html.Div([dcc.Input(id="feature-input", value="Last Updated", type="text", style={"margin-top": "20px"}),
    html.Button(id = 'submit-button', n_clicks=0, children='Submit')
    ]),

    html.Div([
        html.Div([
            dcc.Graph(
                id='graph_rating',
                style = {"height": "700px", "margin": "0 auto"}
            ), 
        ], className="six columns"),

        html.Div([
            html.H3("Market News"),
            generate_html_table()
        ], className="six columns"),
    ], className='row')
])

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

@app.callback(dash.dependencies.Output("graph_rating", "figure"),
            [Input("submit-button", "n_clicks")],
            [State("feature-input", "value")]
            )

def update_fig(n_clicks, input_value):
    Gdata = pd.read_csv('newGApp.csv')
    df = Gdata.groupby(input_value)['Rating'].mean()

    trace_line = go.Scatter(x=list(df.index),
                            y=list(df.values),
                            #visible=False,
                            name=input_value,
                            marker=dict(color='black'),
                            showlegend=False)

    trace_scatter = go.Scatter(x=list(df.index),
                                y=list(df.values),
                                mode='markers',
                                visible=False,
                                name=input_value,
                                marker=dict(color='black'),
                                showlegend=False)

    trace_bar = go.Bar(x=list(df.index),
                        y=list(df.values),
                        visible=False,
                        name=input_value,
                        # marker=dict(color='black'), 
                        showlegend=False)

    data = [trace_line, trace_scatter, trace_bar]

    updatemenus = list([
        dict(
            buttons = list([
                dict(
                    args=[{'visible': [True, False, False]}],
                    label='Line',
                    method='update'
                ),
                    dict(
                    args=[{'visible': [False, True, False]}],
                    label='Scatter',
                    method='update'
                ),
                    dict(
                    args=[{'visible': [False, False, True]}],
                    label='Bar',
                    method='update'
                )
            ]),
            direction='down',
            pad={'r':10, 't':10},
            x=0,
            xanchor='left',
            y=1.25,
            yanchor='top'
        ),
    ])


    layout = dict(
                title=f'{input_value} vs Mean App Rating', 
                updatemenus=updatemenus,
                autosize=False,
                )

    return {
        "data": data,   
        "layout": layout
    }
if __name__ == "__main__":
    app.run_server(debug=True, port=1997)