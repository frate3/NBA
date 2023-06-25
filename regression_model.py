import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def regress_wins_from_top_players(players,standings,x_var="PPG"):
    X = players[[x_var]].sort_index()
    y = standings.set_index("TeamID")["WINS"].sort_index()

    model = LinearRegression()
    model.fit(X,y)
    r_squared = model.score(X,y)

    x_line = np.linspace(X[x_var].min(),X[x_var].max(),500)
    y_line = model.predict(x_line.reshape(-1,1))
    score = model.score(X,y)

    return model, r_squared, x_line,y_line,X[x_var],y,score