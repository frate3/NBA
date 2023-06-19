from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# Incorporate data
df = pd.read_csv('standings.csv',index_col=0)
df = df[["TeamCity","TeamName","Conference","WINS","LOSSES","WinPCT"]]

active_players = pd.read_csv("ActivePlayers.csv")
all_teams = pd.read_csv("Teams.csv")

player_stats = pd.read_csv("PlayerCareerStats.csv",index_col=0)
player_stats = player_stats.merge(active_players[["id","full_name"]], left_on="PLAYER_ID", right_on="id")
player_stats["PPG"] = player_stats["PTS"]/player_stats["GP"]
current_stats = player_stats[player_stats["SEASON_ID"]=="2022-23"]
results=[]
for team in all_teams["abbreviation"].values:
    team_stats = current_stats[current_stats["TEAM_ABBREVIATION"] == team]
    top = team_stats.sort_values("PPG", ascending=False).iloc[0]
    results.append(top)

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='NBA Data Project'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.RadioItems(options=['WINS', 'LOSSES', 'WinPCT'], value='WINS', id='choice'),
    dcc.Graph(figure=px.bar(df,x='TeamName', y='WINS'),id='graph'),
    dcc.Graph(figure=px.scatter(df,x="WINS",y='LOSSES'))
])


@callback(
    Output(component_id='graph', component_property='figure'),
    Input(component_id='choice', component_property='value')
)
def update_graph(col_chosen):
    fig = px.bar(df,x='TeamName', y=col_chosen)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)