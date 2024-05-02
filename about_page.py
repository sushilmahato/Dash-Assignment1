import dash
from dash import dcc, html, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
import io
import json
import os

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
)
df = df[["country", "continent", "pop", "lifeExp"]]


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Loading the config_about JSON file
current_directory = os.path.dirname(os.path.realpath(__file__))

file_path = os.path.join(current_directory, "Description", "config_about.json")
# file_path = '''/Description/config_about.json'''

with open(file_path, "r") as file:
    table = json.load(file)


app.layout = html.Div(
    [
        dbc.Row(html.H2("Introduction TO GapMinder", style={"text-align": "center"})),
        dbc.Row(
            html.P(table["intro_part1"]),
        ),
        html.Ol(
            [
                html.Li(table["intro_part1_list1"]),
                html.Li(table["intro_part1_list2"]),
                html.Li(table["intro_part1_list3"]),
                html.Li(table["intro_part1_list4"]),
            ]
        ),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id="country-dropdown",
                                options=[
                                    {"label": country, "value": country}
                                    for country in df["country"].unique()
                                ],
                                value=[],
                                multi=True,
                                placeholder="Select Country Name",
                            )
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="continent-dropdown",
                                options=[
                                    {"label": continent, "value": continent}
                                    for continent in df["continent"].unique()
                                ],
                                value=[],
                                multi=True,
                                placeholder="Select Continent Name",
                            )
                        ),
                        dbc.Col(
                            [
                                html.Label("Population Slider"),
                                dcc.RangeSlider(
                                    id="pop-slider",
                                    min=df["pop"].min(),
                                    max=df["pop"].max(),
                                    step=300000000,
                                    value=[df["pop"].min(), df["pop"].max()],
                                    marks={
                                        i: str(i)
                                        for i in range(
                                            int(df["pop"].min()),
                                            int(df["pop"].max()) + 1,
                                            300000000,
                                        )
                                    },
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                html.Label("LifeExp Slider"),
                                dcc.RangeSlider(
                                    id="lifeExp-slider",
                                    min=int(df["lifeExp"].min()),
                                    max=int(df["lifeExp"].max()),
                                    step=10,
                                    value=[
                                        int(df["lifeExp"].min()),
                                        int(df["lifeExp"].max()),
                                    ],
                                    marks={
                                        i: str(i)
                                        for i in range(
                                            int(df["lifeExp"].min()),
                                            int(df["lifeExp"].max()) + 1,
                                            10,
                                        )
                                    },
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Show number of Rows"),
                dcc.Dropdown(
                    id="page-size-dropdown",
                    value=10,
                    clearable=False,
                    style={"width": "35%"},
                    options=[10, 25, 50, 100],
                ),
            ]
        ),
        dbc.Button("Download CSV", id="button", color="success"),
        dcc.Download(id="download-data"),
        html.Div(id="show-table"),
    ]
)


@callback(
    Output("show-table", "children"),
    [
        Input("country-dropdown", "value"),
        Input("continent-dropdown", "value"),
        Input("pop-slider", "value"),
        Input("lifeExp-slider", "value"),
        Input("page-size-dropdown", "value"),
    ],
)
def update_fliter(country, continent, pop, lifeExp, page_size):
    filtered_df = df[
        (df["country"].isin(country) if country else True)
        & (df["continent"].isin(continent) if continent else True)
        & (df["pop"].between(pop[0], pop[1]))
        & (df["lifeExp"].between(lifeExp[0], lifeExp[1]))
    ]

    return dash_table.DataTable(
        data=filtered_df.to_dict("records"), page_size=page_size
    )


@callback(
    Output("download-data", "data"),
    Input("button", "n_clicks"),
    [
        State("country-dropdown", "value"),
        State("continent-dropdown", "value"),
        State("pop-slider", "value"),
        State("lifeExp-slider", "value"),
    ],
)
def generate_csv(nclick, country, continent, pop, lifeExp):
    if not nclick:
        raise PreventUpdate

    filtered_df = df[
        (df["country"].isin(country) if country else True)
        & (df["continent"].isin(continent) if continent else True)
        & (df["pop"].between(pop[0], pop[1]))
        & (df["lifeExp"].between(lifeExp[0], lifeExp[1]))
    ]

    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return dict(content=csv_buffer.getvalue(), filename="GapMinder_Filtered_Data.csv")


if __name__ == "__main__":
    app.run_server(debug=True)
