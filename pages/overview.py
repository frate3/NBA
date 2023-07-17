import dash
from dash import html, dcc, dash_table,callback,Input,Output
import pandas as pd
import plotly.express as px

dash.register_page(__name__,path='/', title="NBA Data Science Project - Overview")

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

def layout():
    return html.Div([
        html.H1('Overview Dashboard',className='page-title'),
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
                # style={"width": "50%"}),
                )],
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
        )])

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

