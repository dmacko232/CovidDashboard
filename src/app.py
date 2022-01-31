import collections
import dash
import pandas as pd
import plotly.express as px

from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

from dash import html
from dash import dcc
from dash import dash_table

# mapping of map views to column names in dataframe
MAP_VIEWS_TO_COLUMNS = {
    "New Covid-19 cases per million inhabitants": "new_cases_smoothed_per_million",
    "New Covid-19 deaths per million inhabitants": "new_deaths_smoothed_per_million",
    "Covid-19 hospitalized patients per million inhabitants": "hosp_patients_per_million",
    "Covid-19 ICU patients per million inhabitants": "icu_patients_per_million",
    "New Covid-19 ICU admissions per million inhabitants": "weekly_icu_admissions_per_million",
    "New Covid-19 hospitalization admissions per million inhabitants": "weekly_hosp_admissions_per_million",

    "New Covid-19 tests per thousand inhabitants": "new_tests_smoothed_per_thousand",
    "New Covid-19 vaccinations per million inhabitants": "new_vaccinations_smoothed_per_million",
    #"Hospital beds per thousand inhabitants": "hospital_beds_per_thousand"
}
MAP_VIEWS_TO_COLORS = {
    "New Covid-19 cases per million inhabitants": "reds",
    "New Covid-19 deaths per million inhabitants": "reds",
    "Covid-19 hospitalized patients per million inhabitants": "reds",
    "Covid-19 ICU patients per million inhabitants": "reds",
    "New Covid-19 ICU admissions per million inhabitants": "reds",
    "New Covid-19 hospitalization admissions per million inhabitants": "reds",

    "New Covid-19 tests per thousand inhabitants": "greens",
    "New Covid-19 vaccinations per million inhabitants": "greens",
    #"Hospital beds per thousand inhabitants": "greens"
}
MAP_VIEWS = sorted(list(MAP_VIEWS_TO_COLUMNS.keys()))

AGGREGATION_OPERATIONS_TO_PANDAS = {
    "Mean value for the date range in map": "mean",
    "Total (sum) value for the date range in map": "sum"
}
AGGREGATION_OPERATIONS = sorted(list(AGGREGATION_OPERATIONS_TO_PANDAS.keys()))

app = dash.Dash(__name__)

@app.callback(
    Output("date_store", "data"),
    Output("date-slider", "marks"),
    Input("date-slider", "value")
)
def update_date_slider(value):
    """Updates range slider."""

    slider_marks = {}
    for v in set(value + [0, len(dates) - 1]):
        if v not in slider_marks:
            slider_marks[v] = {"label": dates[v].strftime("%d.%m.%Y")}
    return (
        { 
            "from": value[0], 
            "to": value[1] 
        },
        slider_marks
    )

@app.callback(
    Output("map_type_store", "data"),
    Input("map-type", "value")
)
def update_dropdown(value):

    return value

@app.callback(
    Output("aggregation_operation_store", "data"),
    Input("aggregation-operation", "value")
)
def update_agg_dropdown(value):

    return value

@app.callback(
    Output("map", "figure"),
    Input("df_store", "data"),
    Input("map_type_store", "data"),
    Input("date_store", "data"),
    Input("aggregation_operation_store", "data")
)
def update_map(df_store_data,
               map_type_store_data, date_store_data, aggregation_operation_store_data):
    
    if map_type_store_data == "DISABLED" or aggregation_operation_store_data == "DISABLED":
        return None

    # read json from store
    df = pd.DataFrame.from_dict(df_store_data)
    df["date"] = pd.to_datetime(df["date"])

    # filter on date
    unique_dates = dates
    date_from = unique_dates[date_store_data["from"]]
    date_to = unique_dates[date_store_data["to"]]
    df = df[(df["date"] >= date_from) & (df["date"] <= date_to)]
    # group by location and aggregate by summing
    column = MAP_VIEWS_TO_COLUMNS[map_type_store_data]
    operation = AGGREGATION_OPERATIONS_TO_PANDAS[aggregation_operation_store_data]
    df = df.groupby(by=["location"]).agg({column: operation}).reset_index()
    # return chloroleth figure
    fig = px.choropleth(
        df,
        locationmode="country names",
        scope="europe",
        locations="location",
        color=column,
        hover_name="location",
        labels={column: f"{operation.capitalize()} {map_type_store_data}"},
        color_continuous_scale=MAP_VIEWS_TO_COLORS[map_type_store_data],
        title=f"{map_type_store_data} from {date_from.strftime('%d.%m.%Y')} to {date_to.strftime('%d.%m.%Y')}",
    )
    fig.update_layout(margin={"r":0,"t":80, "l":0,"b":30})
    fig.add_annotation(
        text="Clicking or selecting (using Plotly selection in upper right corner) countries changes the evolution graph",
        x=0.05,
        y=-0.05,
        xanchor="left",
        showarrow=False,
    )
    return fig
    
@app.callback(
    Output("time_evolution", "figure"),
    Input("df_store", "data"),
    Input("map_type_store", "data"),
    Input("date_store", "data"),
    Input("selected_countries_store", "data"),
    Input("aggregation_operation_store", "data")
)
def update_time_evolution(df_store_data, map_type_store_data, date_store_data,
     selected_countries_data, aggregation_operation_store_data):

    if map_type_store_data == "DISABLED":
        return None
    
    # read json from store
    df = pd.DataFrame.from_dict(df_store_data)
    df["date"] = pd.to_datetime(df["date"])

    if selected_countries_data is not None:
        df = df[df["location"].isin(selected_countries_data)]

    # filter on date
    unique_dates = dates
    date_from = unique_dates[date_store_data["from"]]
    date_to = unique_dates[date_store_data["to"]]
    df = df[(df["date"] >= date_from) & (df["date"] <= date_to)]
    column = MAP_VIEWS_TO_COLUMNS[map_type_store_data]
    
    fig = px.line(
        df,
        x="date",
        y=column,
        color="location",
        labels={ column: map_type_store_data, "location": "country" },
        title=f"{map_type_store_data} evolution from {date_from.strftime('%d.%m.%Y')} to {date_to.strftime('%d.%m.%Y')}",
    )
    fig.update_layout(margin={"r":0,"t":80, "l":0,"b":30})
    return fig

@app.callback(
    Output("selected_countries_store", "data"),
    Input("map", "selectedData"),
    Input("map", "clickData")
)
def select_or_click_location(map_selected_data, map_click_data):
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return None
    last_trigger = ctx.triggered[-1]
    return [p["location"] for p in last_trigger["value"]["points"]]

total_df = pd.read_csv("data/prepared_total.csv")
total_df["date"] = pd.to_datetime(total_df["date"])
total_df.sort_values(by="date", inplace=True, ascending=True)
locations = list(set(total_df["location"].to_list()))
dates = sorted(list(set(total_df["date"].to_list())))

app.layout = html.Div([

    dcc.Store(id="df_store", storage_type="memory", data=total_df.to_dict()),
    dcc.Store(id="map_type_store", storage_type="session"),
    dcc.Store(id="date_store", storage_type="session"),
    dcc.Store(id="aggregation_operation_store", storage_type="session"),
    dcc.Store(id="selected_countries_store", storage_type="session", data=None),

    html.H1("Covid-19 Europe dashboard", style={"text-align": "center"}),
    html.Div([
            dcc.Dropdown(
                id="aggregation-operation",
                options=[
                    {
                        "label": "Aggregation operation applied to be applied to data on map",
                        "disabled": True,
                        "value": "DISABLED"
                    }] + [{"label": t, "value": t} for t in AGGREGATION_OPERATIONS],
                value=AGGREGATION_OPERATIONS[0],
                style={'width': '100%'},
                searchable=False,
            ),
            dcc.Dropdown(
                id="map-type",
                options=[
                    {
                        "label": "Type of data to display",
                        "disabled": True,
                        "value": "DISABLED"
                    }] + [{"label": t, "value": t} for t in MAP_VIEWS],
                value=MAP_VIEWS[0],
                style={'width': '100%'},
                searchable=False,
            ),
    ], className="row", style={"display": "flex"}),

    # todo vypisat co to zobrazuje a od kedy do kedy
    html.Div([
        dcc.Graph(id="map", style={'width': '50%'}),
        dcc.Graph(id="time_evolution", style={'width': '50%'})
    ], className="row", style={"display": "flex"}),

    html.Div([
        dcc.RangeSlider(
            id="date-slider",
            min=0,
            max=len(dates)-1,
            step=1,
            value=[0, len(dates)-1],
            marks={
                0: {"label": dates[0].strftime("%d.%m.%Y")},
                len(dates)-1: {"label": dates[-1].strftime("%d.%m.%Y")}
            },
            updatemode="mouseup",
        ),
    ], className="row"),
])

if __name__ == "__main__":
    #app.run_server(debug=True)
    import os
    print(os.getcwd())
    app.run_server()
