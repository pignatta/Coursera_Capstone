# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

vector=[{'label': i, 'value': i} for i in spacex_df['Launch Site'].unique()]
vector.append({'label':'ALL', 'value':'ALL'})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                 dcc.Dropdown(
                                    id='site-dropdown',
                                    options=vector,
                                    value='ALL',
                                    placeholder='Select a launch site here...',
                                    searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload,max_payload]
                                    ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_figure(dropdown):
    
    df = spacex_df

    if dropdown == 'ALL':

        data = df.groupby(by='Launch Site').mean()['class']
        piechart = px.pie( 
            data_frame = data,
            names = list(data.index),
            values = data.values
        )
    
    else:

        df['fail'] = 1-df['class']
        data = df.groupby(by='Launch Site').mean()[['class','fail']]
        piechart = px.pie(
            data_frame = data.loc[dropdown],
            names = data.columns,
            values = data.loc[dropdown].values
        )

    return(piechart)    

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')]
)
def scatter_plot(dropdown, slider):

    df = spacex_df

    if dropdown == 'ALL':

        sub_df = df[(df['Payload Mass (kg)']>slider[0]) & (df['Payload Mass (kg)']<slider[1])]
        scatter = px.scatter(
            data_frame = df,
            x = sub_df['Payload Mass (kg)'],
            y = sub_df['class'],
            color = sub_df['Booster Version Category'],
            labels={'x':'Payload Mass (kg)', 'y':'class', 'title':'Correlation between payload and success for all sites', 'color':'Booster Version Category'}
        )
    
    else:

        sub_df = df[(df['Payload Mass (kg)']>slider[0]) & (df['Payload Mass (kg)']<slider[1]) & (df['Launch Site']==dropdown)]
        scatter = px.scatter(
            data_frame = df,
            x = sub_df['Payload Mass (kg)'],
            y = sub_df['class'],
            color = sub_df['Booster Version Category'],
            labels={'x':'Payload Mass (kg)', 'y':'class', 'title':'Correlation between payload and success for the selected site', 'color':'Booster Version Category'}
        )

    return(scatter)    

# Run the app
if __name__ == '__main__':
    app.run_server()
