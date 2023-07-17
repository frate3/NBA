import dash
from dash import html, dcc, dash_table,callback,Input,Output
import pandas as pd
import plotly.express as px

dash.register_page(__name__, title="NBA Data Science Project - Players")

# Incorporate data

active_players = pd.read_csv("ActivePlayers.csv",index_col=0)
all_teams = pd.read_csv("Teams.csv",index_col=0)
standings = pd.read_csv("standings.csv",index_col=0)

player_stats = pd.read_csv("PlayerCareerStats.csv",index_col=0)
player_stats = player_stats.merge(active_players[["id","full_name"]], left_on="PLAYER_ID", right_on="id")
current_stats = player_stats[player_stats["SEASON_ID"]=="2022-23"]
cols_per_game = ['PTS','OREB','DREB','REB','AST','STL','BLK','TOV','PF']
for col in cols_per_game:
    current_stats[col+"_PG"] = (current_stats[col]/current_stats['GP']).round(2)
current_stats = current_stats[['full_name','TEAM_ABBREVIATION']+[c for c in current_stats.columns if '_PG' in c]]

def layout():
    return html.Div([
        html.H1('Players Dashboard',className='page-title'),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Team", className="menu-title"),
                        dcc.Dropdown(
                            id="choice",
                            options=all_teams['abbreviation'].values,
                            value="ATL",
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
                        id="player-graph",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dash_table.DataTable(
                        data=current_stats[current_stats['TEAM_ABBREVIATION']=='ATL'].sort_values('PTS_PG',ascending=False).to_dict('records'),
                        page_size=10,
                        columns=[{"name": i, 'id': i} for i in current_stats.columns],
                        id='player-table',
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
    [Output(component_id='player-graph', component_property='figure'),
     Output(component_id='player-table',component_property='data')],
    Input(component_id='choice', component_property='value')
)
def update_graph(col_chosen):
    global current_stats
    df=current_stats[current_stats['TEAM_ABBREVIATION']==col_chosen].sort_values('PTS_PG',ascending=False)
    fig = px.bar(df,x='full_name', y='PTS_PG')
    fig.update_layout(         
        title="{} 2022-23 Season".format(col_chosen),
        title_x=0.5)
    return fig,df.to_dict('records')
