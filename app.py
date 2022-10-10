### Importing libraries
import datetime
import pandas as pd # https://pandas.pydata.org/docs/
import plotly_express as px # https://plotly.com/python-api-reference/index.html
import streamlit as st # https://docs.streamlit.io/
import urllib


### Setting up webpage attributes
st.set_page_config(
    page_title="COVID19 in Italia",
    page_icon=":syringe:",
    layout="wide"
)


### Retrieving dataset
local_filename = 'covid19.csv'

def get_dataset():
    remote_url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv'
    try:
        urllib.request.urlretrieve(remote_url, local_filename)
    except urllib.error.URLError as err:
        reason = err.reason
        st.error(f"Network error: {reason}")

# '@' denotes a decorator
@st.cache(suppress_st_warning=True)
def load_dataset():
    get_dataset()
    df = pd.read_csv(local_filename, parse_dates=['data'])
    df['data'] = df['data'].dt.date
    return df

df = load_dataset()
df = df.dropna(axis=1)


### Filter sidebar
st.sidebar.header("Filtri")

states = st.sidebar.multiselect(
    "Regioni",
    options=df["denominazione_regione"].unique(),
    default=df["denominazione_regione"].unique()
)

start_date = st.sidebar.date_input(
    "Data di inizio",
    min_value=min(df["data"]),
    max_value=max(df["data"]),
    value=datetime.date(2022, 1, 1)
)

end_date = st.sidebar.date_input(
    "Data di fine",
    min_value=min(df["data"]),
    max_value=max(df["data"]),
    value=max(df["data"])
)

df_filtered = df[
    (df["denominazione_regione"].isin(states)) &
    (df["data"] >= start_date) &
    (df["data"] <= end_date)
    ]


### Title and last update section
last_update = max(df["data"])

st.title("COVID19 in Italia :flushed:")
st.text(f"Data ultimo aggiornamento: {last_update}")


### Showing dataset
st.dataframe(df_filtered)


### Line plots for positives and recovered
left_column, right_column = st.columns(2)

fig_positives = px.line(
    df_filtered,
    title="Positivi per regione",
    width=500,
    height=500,
    x="data",
    y="totale_positivi",
    color="denominazione_regione"
)

left_column.plotly_chart(fig_positives)

fig_recovered = px.line(
    df_filtered,
    title="Dimessi guariti per regione",
    width=500,
    height=500,
    x="data",
    y="dimessi_guariti",
    color="denominazione_regione"
)

right_column.plotly_chart(fig_recovered)


### Positives bubble map
lat_rome = 41.9027835
long_rome = 12.4963655

bubble_map = px.scatter_geo(
    df_filtered,
    title="Mappa dei positivi per regione",
    width=800,
    height=800,
    scope="europe",
    center=dict(lat=lat_rome, lon=long_rome),
    fitbounds="locations",
    size_max=50,
    lat="lat",
    lon="long",
    color="denominazione_regione",
    hover_name="denominazione_regione",
    size="totale_positivi",
    animation_frame="data"
)

st.plotly_chart(bubble_map)
