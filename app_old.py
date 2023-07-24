from dash import Dash, html, dash_table, dcc, callback, Output, Input, page_registry, page_container
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import regression_model

# Incorporate data
df = pd.read_csv('standings.csv',index_col=0)
df = df[["TeamCity","TeamName","Conference","WINS","LOSSES","WinPCT"]]

active_players = pd.read_csv("ActivePlayers.csv",index_col=0)
all_teams = pd.read_csv("Teams.csv",index_col=0)
standings = pd.read_csv("standings.csv",index_col=0)

player_stats = pd.read_csv("PlayerCareerStats.csv",index_col=0)
player_stats = player_stats.merge(active_players[["id","full_name"]], left_on="PLAYER_ID", right_on="id")
player_stats["PPG"] = player_stats["PTS"]/player_stats["GP"]
current_stats = player_stats[player_stats["SEASON_ID"]=="2022-23"]
results=[]
for team in all_teams["abbreviation"].values:
    team_stats = current_stats[current_stats["TEAM_ABBREVIATION"] == team]
    top = team_stats.sort_values("PPG", ascending=False).iloc[0]
    results.append(top)
top_players = pd.concat(results, axis = 1).T.set_index("TEAM_ID")
cols_per_game = ['PTS','OREB','DREB','REB','AST','STL','BLK','TOV','PF']
for col in cols_per_game:
    top_players[col+"_PER_GAME"] = top_players[col]/top_players['GP']
    


model, r_squared, x_line,y_line,x,y,score = regression_model.regress_wins_from_top_players(top_players,standings)
fig = go.Figure()
fig.add_scatter(x=x,y=y,name="Actual Data", mode="markers")
fig.add_trace(go.Line(x=x_line,y=y_line,name="Regression Result"))
fig.update_layout(
    title='Team Wins vs Top Player Points<br><sup>R Squared Value:{}</sup>'.format(round(score,3)),
    title_x=0.5,
    xaxis_title='PPG',
    yaxis_title='Team Wins',
    legend_title='Legend'
)

options=[col+'_PER_GAME' for col in cols_per_game]
options+=['PLAYER_AGE','GP','GS','MIN','FGM','FGA','FG_PCT','FG3M','FG3A','FG3_PCT','FTM','FTA','FT_PCT']
# fig1=px.scatter(x=x,y=y)
# fig2=px.line(x=x_line,y=y_line)
# fig2.update_traces(line=dict(color = 'rgba(50,50,50,0.2)'))
# fig3 = go.Figure(data=fig1.data + fig2.data)

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
# Initialize the app
app = Dash(__name__,external_stylesheets=external_stylesheets, use_pages=True)
app.title = "NBA Data Science Project"

# App layout
app.layout = html.Div([
    html.Div(
        children=[
            html.P(children="🏀📈", className="header-emoji"),
            html.H1(
                children="Basketball Analytics", className="header-title"
            ),
            html.P(
                children=(
                    "Exploring data science concepts using NBA data from the 2022-23 season."
                ),
                className="header-description",
            ),
        ],
        className="header"
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Metric", className="menu-title"),
                    dcc.Dropdown(
                        id="choice",
                        options=['WINS', 'LOSSES', 'WinPCT'],
                        value="WINS",
                        clearable=False,
                        className="dropdown",
                    ),
                ],
            style={"width": "50%"}),
        ],
        className="menu",
    ),
    html.Div(
        children=[
            html.Div(
                children=dcc.Graph(
                    # figure=px.bar(df,x='TeamName', y='WINS'),
                    id="wins-per-team",
                    config={"displayModeBar": False},
                ),
                className="card",
            ),
            html.Div(
                children=dash_table.DataTable(
                    data=df.to_dict('records'),
                    page_size=10,
                    columns=[{"name": i, 'id': i} for i in df.columns],
                    id='wins-table',
                    filter_action="native",
                    filter_options={"placeholder_text": "Filter...",'case':'insensitive'},
                    sort_action="native"
                ),
                className="card",
            ),
        ],
        className="wrapper",
    ),
    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in page_registry.values()
        ]
    ),

	page_container
])
    # dcc.Dropdown(options=['WINS', 'LOSSES', 'WinPCT'], value='WINS', id='choice'),
    # dcc.Graph(figure=px.bar(df,x='TeamName', y='WINS'),id='wins-per-team',className='card'),
    # dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    # dcc.Dropdown(options=options, value='PTS_PER_GAME', id='x-var'),
    # dcc.Graph(figure=fig, id="stat-vs-win",className='card')


@callback(
    [Output(component_id='wins-per-team', component_property='figure'),
     Output(component_id='wins-table',component_property='data')],
    Input(component_id='choice', component_property='value')
)
def update_graph(col_chosen):
    global df
    df=df.sort_values(col_chosen,ascending=False)
    fig = px.bar(df,x='TeamName', y=col_chosen)
    fig.update_layout(         
        title="{} 2022-23 Season".format(col_chosen),
        title_x=0.5)
    return fig,df.to_dict('records')

# @callback(
#     Output(component_id="stat-vs-win",component_property="figure"),
#     Input(component_id='x-var',component_property='value')
# )
# def update_regression(col):
#     model, r_squared, x_line,y_line,x,y,score = regression_model.regress_wins_from_top_players(top_players,standings,x_var=col)
#     fig = go.Figure()
#     fig.add_scatter(x=x,y=y,name="Actual Data", mode="markers")
#     fig.add_trace(go.Line(x=x_line,y=y_line,name="Regression Result"))
#     fig.update_layout(
#         title='Team Wins vs {}<br><sup>R Squared Value:{}</sup>'.format(col,round(score,3)),
#         title_x=0.5,
#         xaxis_title=col,
#         yaxis_title='Team Wins',
#         legend_title='Legend'
#     )
#     return fig

if __name__ == '__main__':
    app.run_server(debug=True)