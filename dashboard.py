import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
# import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
from streamlit_folium import st_folium, folium_static
import os
import matplotlib.pyplot as plt
import seaborn as sns
from src import processing, visualization

# @st.experimental_memo

# @st.cache
def get_data(file_path, update=False):
    
    # TODO: put in try block
    if not update:
        try:
            data = pd.read_csv(processing.CLEAN_DATA_PATH)
        except FileNotFoundError:
            data = processing.get_clean_data(update=update)
    else:
        data = processing.get_clean_data(
                                  update=update)
    return data

refresh_status = False

df = get_data(processing.CLEAN_DATA_PATH)

st.set_page_config(
    page_title="BC EV Charging Stations",
    page_icon="✅",
    layout="wide",
)

# row 1: dashboard title
st.title("BC EV Charging Stations Dashboard") 
st.caption("Data Source: Natural Resources Canada [link](https://natural-resources.canada.ca/energy-efficiency/transportation-alternative-fuels/electric-charging-alternative-fuelling-stationslocator-map/20487#/analyze?region=CA-BC&fuel=ELEC&status=E&status=P&country=CA)")
st.caption("Source code: [github](https://github.com/akin-aroge/bc-ev-charging-analysis)")
with st.sidebar:
    
    connect_to_api = st.button(label="Refresh Data from API" )
    # connect_to_api = st.checkbox(label="Refresh Data from API")
    # refresh = st.button(label="refresh data")

    if connect_to_api:
        df = get_data(processing.CLEAN_DATA_PATH, update=True)
    

    # Charging level, drop select
    st.write("Charging Levels")

    charging_levels = ('ev_level1_evse_num','ev_level2_evse_num', 'ev_dc_fast_num')
    charging_levels_rename = ['level 1', 'level 2', 'level 3 (DCFC)']
    charging_levels_select_list = ['all'] + charging_levels_rename
    charging_levels_name_dict = dict(zip(charging_levels_rename, charging_levels))
    select_charging_level = st.selectbox(label='select charging level:', options=charging_levels_select_list)

    if select_charging_level != "all":
        level = charging_levels_name_dict.get(select_charging_level)
        df = df[df[level].notnull()]
        df['n_evse_ports'] = df[level].values
    else:
        df['n_evse_ports'] = df[list(charging_levels)].sum(axis=1)
    
    st.write("Number of EVSE ports")

    # number of ports, slider
    col_name = "n_evse_ports"
    n_ports= df[col_name].dropna().astype('int').unique().tolist()
    init_slider_min = df[col_name].quantile(0.1)
    init_slider_max = df[col_name].quantile(0.9)
    slider_max =  df[col_name].max()
    slider_min =  df[col_name].min()
    select_n_evse_ports = st.slider(label='set range:',
                                min_value=int(slider_min),
                                max_value=int(slider_max),
                                value=(int(init_slider_min), int(init_slider_max)))
    
    mask_n_evse_ports = df['n_evse_ports'].between(*select_n_evse_ports)

    # connector types, multiselect
    st.write("Connector Types")

    from ast import literal_eval

    col_name = 'ev_connector_types'
    temp_df = (df[col_name].copy()
    .rename('Connector Types')
    .dropna()
    .apply(literal_eval)  # change list like string to lists
    )
    connector_types = temp_df.dropna().explode().unique().tolist()
    default_conn_type = connector_types[0]
    select_conn_types = st.multiselect(label='select connector types:',
                   options=connector_types,
                   default=default_conn_type)

    mask_conn_types = temp_df.apply(lambda x: bool(set(x) & set(select_conn_types)))




# filtered data
df = df[mask_n_evse_ports & mask_conn_types]

# Body

# row KPIs
kpi1, kpi2 = st.columns(2)

# col number of stations:
status_col_name = 'status_code'
mask_open = df[status_col_name] == 'E'
mask_only_open_date = (df['open_date'].notnull())
temp_df = df[mask_open & mask_only_open_date]

open_date = pd.to_datetime(temp_df['open_date']).dt.to_period('M')
open_date_year_month= (pd.DataFrame({'open_date':open_date,'value': np.ones(len(open_date))})
                    .dropna()
                    )
current_year_month =  pd.to_datetime('today').to_period('M')

n_working_stns = open_date_year_month.sum(numeric_only=True)[0]
n_working_stns_till_last_month = (open_date_year_month[open_date_year_month['open_date'] < current_year_month]
                               .sum(numeric_only=True)[0])
n_working_stns_delta = n_working_stns - n_working_stns_till_last_month

kpi1.metric(
    label="# of EV stations ⏳",
    value=int(n_working_stns),
    delta=int(n_working_stns_delta),
)

# col number of planned stations:
mask_planned = df[status_col_name] == 'P'
mask_only_expected_date = (df['open_date'].isnull()) & (df['expected_date'].notnull())
temp_df = df[mask_planned & mask_only_expected_date]

expected_date = pd.to_datetime(temp_df['expected_date']).dt.to_period('M')
expected_date_year_month= (pd.DataFrame({'expected_date':expected_date,'value': np.ones(len(expected_date))}))

n_planned_stns = expected_date_year_month.sum(numeric_only=True)[0]
n_planned_stns_till_last_month = (expected_date_year_month[expected_date_year_month['expected_date'] < current_year_month]
                               .sum(numeric_only=True)[0])
n_planned_stns_delta = n_planned_stns - n_planned_stns_till_last_month

kpi2.metric(
    label="# of *Planned* EV stations ⏳",
    value=int(n_planned_stns),
    # delta=int(n_planned_stns_delta),
)

# row: yearly count

open_date = df['open_date'].copy()
# transformation
open_date_agg_df = (pd.DataFrame({'open_date':pd.to_datetime(open_date),'value': np.ones(len(open_date))})
                    .dropna()
                    .resample(rule='Y', on='open_date').agg({'value':np.sum})
                    .assign(cumsum = lambda x: np.cumsum(x['value']))
                    .assign(year=lambda x: x.index.year)
                    .reset_index())


# 
# sns.set_style("darkgrid")
# fig, ax = plt.subplots()
# sns.lineplot(x='year', y='value', marker='o', data=open_date_agg_df, label='Yearly Total', ax=ax)
# sns.lineplot(x='year', y='cumsum', marker='o', data=open_date_agg_df, label='Cumulative Total', ax=ax)
# ax.set_ylabel('Number of Stations');
# ax.set_xlabel('Year')
# ax.set_title('Yearly Available EV Station Growth (with Level 2 and DC Fast EVSE)');
# st.pyplot(fig)
# col1, col2 = st.columns(2)
col1 = st.container()
with col1:
    st.write("Yearly Available EV Station Growth:")
    import plotly.express as px
    fig = px.line(open_date_agg_df, x='year', y=['value', 'cumsum'], markers=True)
    fig.update_layout(yaxis_title='value')
    st.plotly_chart(fig, use_container_width=True)

col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    st.write("Map of EV Locations:")
    m = visualization.map_plot(select_df=df)
    folium_static(m)



# row: map plot


