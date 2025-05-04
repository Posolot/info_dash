from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

min_year = df['year'].min()
max_year = df['year'].max()
default_year = 2007

axis_options = [
    {"label": "Население", "value": "pop"},
    {"label": "Ожидаемая продолжительность жизни", "value": "lifeExp"},
    {"label": "ВВП на душу населения", "value": "gdpPercap"}
]

app.layout = html.Div([
    html.H1("Визуализация данных Dash", style={"textAlign": "center"}),

    html.Label("Выберите страны:"),
    dcc.Dropdown(
        options=[{"label": c, "value": c} for c in df.country.unique()],
        value=['Canada', 'United States'],
        multi=True,
        id="dropdown-selection"
    ),
    html.Label("Выберите показатель для оси Y:"),
    dcc.Dropdown(
        options=axis_options,
        value="pop",
        clearable=False,
        id="y-axis-selection"
    ),
    dcc.Graph(id="line-chart"),

    dcc.Graph(id="hover-bar-chart"),

    html.H3("Настройки пузырьковой диаграммы"),
    html.Label("Выберите год:"),
    dcc.Slider(
        id="bubble-year-slider",
        min=min_year,
        max=max_year,
        step=1,
        value=default_year,
        marks={str(year): str(year) for year in range(min_year, max_year+1, 2)}
    ),
    html.Label("Выберите показатель для оси X:"),
    dcc.Dropdown(
        options=axis_options,
        value="gdpPercap",
        clearable=False,
        id="bubble-x-axis"
    ),
    html.Label("Выберите показатель для оси Y:"),
    dcc.Dropdown(
        options=axis_options,
        value="lifeExp",
        clearable=False,
        id="bubble-y-axis"
    ),
    html.Label("Выберите показатель для размера пузырьков:"),
    dcc.Dropdown(
        options=axis_options,
        value="pop",
        clearable=False,
        id="bubble-size"
    ),
    dcc.Graph(id="bubble-chart"),

    html.H3("Топ-15 стран по численности населения"),
    html.Label("Выберите год:"),
    dcc.Slider(
        id="top15-year-slider",
        min=min_year,
        max=max_year,
        step=1,
        value=default_year,
        marks={str(year): str(year) for year in range(min_year, max_year+1, 2)}
    ),
    dcc.Graph(id="top15-population-chart"),
    html.H3("Распределение населения по континентам"),
    html.Label("Выберите год:"),
    dcc.Slider(
        id="pie-year-slider",
        min=min_year,
        max=max_year,
        step=1,
        value=default_year,  # Значение по умолчанию 2007
        marks={str(year): str(year) for year in range(min_year, max_year+1, 2)}
    ),
    dcc.Graph(id="pie-chart")
])

@callback(
    Output("line-chart", "figure"),
    Input("dropdown-selection", "value"),
    Input("y-axis-selection", "value")
)
def update_line_chart(selected_countries, y_measure):
    if not selected_countries:
        return {}
    dff_selected = df[df.country.isin(selected_countries)]
    return px.line(dff_selected, x="year", y=y_measure, color="country",
                   labels={"year": "Год", y_measure: "Значение"},
                   title="Динамика показателей по странам")

@callback(
    Output("hover-bar-chart", "figure"),
    Input("line-chart", "hoverData"),
    prevent_initial_call=True
)
def update_hover_bar(hover_data):
    year = int(hover_data['points'][0]['x'])
    dff_year = df[df.year == year]
    return px.bar(dff_year, x="country", y="pop",
                  title=f"Численность населения в {year}",
                  labels={"country": "Страна", "pop": "Население"})

@callback(
    Output("bubble-chart", "figure"),
    Input("bubble-year-slider", "value"),
    Input("bubble-x-axis", "value"),
    Input("bubble-y-axis", "value"),
    Input("bubble-size", "value")
)
def update_bubble_chart(selected_year, x_axis, y_axis, size_metric):
    dff_year = df[df.year == selected_year]
    return px.scatter(
        dff_year,
        x=x_axis,
        y=y_axis,
        size=size_metric,
        color="continent",
        hover_name="country",
        size_max=60,
        title=f"Пузырьковая диаграмма ({selected_year}) - {x_axis} vs {y_axis}",
        labels={x_axis: "Ось X", y_axis: "Ось Y", size_metric: "Размер пузырька"}
    )

@callback(
    Output("top15-population-chart", "figure"),
    Input("top15-year-slider", "value")
)
def update_top15_chart(selected_year):
    dff_year = df[df.year == selected_year]
    top15 = dff_year.sort_values(by="pop", ascending=False).head(15)
    return px.bar(
        top15,
        x="country",
        y="pop",
        title=f"Топ-15 стран по численности населения ({selected_year})",
        labels={"pop": "Население", "country": "Страна"}
    )

@callback(
    Output("pie-chart", "figure"),
    Input("pie-year-slider", "value")
)
def update_pie_chart(selected_year):
    dff_year = df[df.year == selected_year]
    df_grouped = dff_year.groupby("continent", as_index=False).agg({"pop": "sum"})
    return px.pie(
        df_grouped,
        names="continent",
        values="pop",
        title=f"Распределение населения по континентам ({selected_year})",
        labels={"continent": "Континент", "pop": "Численность населения"}
    )

if __name__ == "__main__":
    app.run(debug=True)
