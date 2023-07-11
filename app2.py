from dash import Dash, html, dash_table, dcc, callback, Output, Input, page_registry, page_container

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

app = Dash(__name__,external_stylesheets=external_stylesheets, use_pages=True)
app.title = "NBA Data Science Project"

def layout():
    return html.Div([
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
        html.Div([
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in page_registry.values()
        ]), 
        page_container])
app.layout = layout

if __name__ == '__main__':
    app.run_server(debug=True)