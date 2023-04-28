import folium
from IPython.display import  display

def plot_map(data, status='all', min_l2_ports=0, min_dcfc_ports=0, free_charging=False):

    """
    Generates a folium map using data available in `data` and filtered by the other function arguments
    """

    if status=='all':
        select_df = data.copy()
    else:
        select_df = data[data['status_code'] ==status].copy()
    

    condition = (select_df['ev_level2_evse_num']>=min_l2_ports) & (select_df['ev_dc_fast_num']>=min_dcfc_ports)
    
    select_df = select_df[condition].copy()
    
    if free_charging:
        select_df = select_df[select_df['free_charging']==free_charging].copy()

    def _plot(select_df):
        
        m = folium.Map(location=[49.2827, -123.1207], tiles="OpenStreetMap", zoom_start=9)
        
        for _, id in enumerate(select_df.id):

            row = select_df[select_df['id']==id]

            status_code = row['status_code'].iloc[0]
            n_l2_ports = row['ev_level2_evse_num'].iloc[0]
            n_dcfc_ports = row['ev_dc_fast_num'].iloc[0]
            address = row['street_address'].iloc[0]

            popup = folium.Popup(f"# of L2 ports:{n_l2_ports} <br> \
                                # of DCFC ports:{n_dcfc_ports} <br> \
                                 status: {status_code} <br> \
                                 address: {address}", 
                                min_width=300, max_width=300)
            folium.CircleMarker([row.latitude, row.longitude],
                                popup=popup,
                                #icon=folium.Icon(color='green', icon='charging-station', prefix='fa')
                                radius=(n_l2_ports+n_dcfc_ports) / 4.0,
                                opacity=0.8
                               ).add_to(m)

        return m
    
    m = _plot(select_df)
    display(m)
    
    return m   


def map_plot(select_df):
    
    # f = folium.Figure(width=500, height=500)
    m = folium.Map(location=[49.2827, -123.1207], tiles="OpenStreetMap", zoom_start=9)
    
    for _, id in enumerate(select_df.id):

        row = select_df[select_df['id']==id]

        status_code = row['status_code'].iloc[0]
        n_l2_ports = row['ev_level2_evse_num'].iloc[0]
        n_dcfc_ports = row['ev_dc_fast_num'].iloc[0]
        address = row['street_address'].iloc[0]
        n_ports = row['n_evse_ports'].iloc[0]

        popup = folium.Popup(f"# of L2 ports:{n_l2_ports} <br> \
                            # of DCFC ports:{n_dcfc_ports} <br> \
                                status: {status_code} <br> \
                                address: {address}", 
                            min_width=300)
        folium.CircleMarker([row.latitude, row.longitude],
                            popup=popup,
                            #icon=folium.Icon(color='green', icon='charging-station', prefix='fa')
                            # radius=(n_l2_ports+n_dcfc_ports) / 4.0,
                            radius=n_ports / 4.0,
                            opacity=0.8
                            ).add_to(m)
        
    return m