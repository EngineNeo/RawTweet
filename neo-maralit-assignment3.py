import plotly.express as px
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import dash

# Dataset
df = pd.read_csv('ProcessedTweets.csv')

# Month is string
df['Month'] = df['Month'].astype(str)

app = dash.Dash(__name__)
server = app.server

months = df['Month'].unique()
sentiment_range = [df['Sentiment'].min(), df['Sentiment'].max()]
subjectivity_range = [df['Subjectivity'].min(), df['Subjectivity'].max()]

app.layout = html.Div([
    html.Div([
        html.Label('Month'),
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': month} for month in months],
            value=months[0], 
            className='custom-dropdown'
        ),
        html.Label('Sentiment Score'),
        dcc.RangeSlider(
            id='sentiment-slider',
            min=sentiment_range[0],
            max=sentiment_range[1],
            step=0.01,
            marks={i: str(i) for i in range(
                int(sentiment_range[0]), int(sentiment_range[1])+1)},
            value=sentiment_range,
            className='custom-slider'
        ),
        html.Label('Subjectivity Score'),
        dcc.RangeSlider(
            id='subjectivity-slider',
            min=subjectivity_range[0],
            max=subjectivity_range[1],
            step=0.01,
            marks={i: str(i) for i in range(
                int(subjectivity_range[0]), int(subjectivity_range[1])+1)},
            value=subjectivity_range,
            className='custom-slider'
        ),
    ], className='range-slider-container'),

    dcc.Graph(id='tweet-scatter-plot'),
    dash_table.DataTable(
        id='tweet-table',
        columns=[{"name": "RawTweet", "id": "RawTweet"}],
        page_size=10,  # Pagination
        style_table={'overflowY': 'False', 'overflowX': 'True'},
        style_header={'textAlign': 'center', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center'},
    )
])

@app.callback(
    Output('tweet-scatter-plot', 'figure'),
    [Input('month-dropdown', 'value'),
     Input('sentiment-slider', 'value'),
     Input('subjectivity-slider', 'value')]
)
def update_figure(selected_month, sentiment_range, subjectivity_range):
    filtered_df = df[(df['Month'] == selected_month) &
                     (df['Sentiment'] >= sentiment_range[0]) & (df['Sentiment'] <= sentiment_range[1]) &
                     (df['Subjectivity'] >= subjectivity_range[0]) & (df['Subjectivity'] <= subjectivity_range[1])]

    fig = px.scatter(filtered_df, x='Dimension 1', y='Dimension 2', color='Sentiment',
                     hover_data=['RawTweet'])
    fig.update_layout(transition_duration=500, dragmode='lasso', 
                      yaxis={'visible': False, 'showticklabels': False},
                      xaxis={'visible': False, 'showticklabels': False},
                      coloraxis_showscale=False
                      )

    return fig


@app.callback(
    Output('tweet-table', 'data'),
    [Input('tweet-scatter-plot', 'selectedData')],
    prevent_initial_call=True 
)
def display_selected_tweets(selectedData):
    if selectedData is None:
        return []

    indices = [point['pointIndex'] for point in selectedData['points']]
    filtered_df = df.iloc[indices]
    table_data = filtered_df[['RawTweet']].to_dict('records')

    return table_data

if __name__ == '__main__':
    app.run_server(debug=False)
