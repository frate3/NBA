from dash import Dash, html, dash_table, dcc, callback, Output, Input, page_registry, page_container
import dash
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


dash.register_page(__name__)

def layout():
    return html.Div([
        html.H1('Regression of Top Player Stats to Team Wins',className='page-title'),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Metric", className="menu-title"),
                        dcc.Dropdown(
                            id='x-var',
                            options=options,
                            value="PTS_PER_GAME",
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
                        id="stat-vs-win",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                )],
            className="wrapper",
        ),
        # html.Div(
        #     dcc.Graph(figure=fig, id="stat-vs-win",className='card')
        # )
        ])

@callback(
    Output(component_id="stat-vs-win",component_property="figure"),
    Input(component_id='x-var',component_property='value')
)
def update_regression(col):
    model, r_squared, x_line,y_line,x,y,score = regression_model.regress_wins_from_top_players(top_players,standings,x_var=col)
    fig = go.Figure()
    fig.add_scatter(x=x,y=y,name="Actual Data", mode="markers")
    fig.add_trace(go.Line(x=x_line,y=y_line,name="Regression Result"))
    fig.update_layout(
        title='Team Wins vs {}<br><sup>R Squared Value:{}</sup>'.format(col,round(score,3)),
        title_x=0.5,
        xaxis_title=col,
        yaxis_title='Team Wins',
        legend_title='Legend'
    )
    return fig
