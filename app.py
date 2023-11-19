import streamlit as st
import app_module as op
import plotly.tools as tls

st.write("# EWP Beam capacities graph")
st.write('Find your beam section from knowing your span and tributary load.')
st.write('Assumes the beams compressive edge is held in line by direct connection of decking or joists spaced not more than 610 mm apart and bridging or blocking is installed at intervals not exceeding eight times the depth of the member, i.e. KL = 1.')

floor_depth = [9.25, 9.5, 11.25, 11.875, 14, 16, 19]

st.sidebar.write("## Floor thickness")
min_floor_thickness = st.sidebar.selectbox("Minimum floor thickness", floor_depth)

filtered_floor_depth = [depth for depth in floor_depth if depth >= min_floor_thickness]
max_floor_thickness = st.sidebar.selectbox("Maximum floor thickness", filtered_floor_depth)

section_data = op.weyer_sections()
section_data.set_index('Name', inplace=True)
section_data = op.sections_filter(section_data, 'ge', Depth=min_floor_thickness)
section_data = op.sections_filter(section_data, 'le', Depth=max_floor_thickness)

st.sidebar.write("## Loading")
occ1_D = st.sidebar.number_input(label = "Occupancy 1 Dead load (psf)", value = 20)
occ1_L = st.sidebar.number_input(label = "Occupancy 1 Live load (psf)", value = 40)
occ1_S = st.sidebar.number_input(label = "Occupancy 1 Snow load (psf)", value = 180)

st.sidebar.write("## Deflection Limits")
w_delt_L = st.sidebar.number_input(label = "Live = L/", value = 360)
w_delt_T = st.sidebar.number_input(label = "Total = L/", value = 180)
w_delt_P = st.sidebar.number_input(label = "Permanent = L/", value = 360)

streamlit_theme = st.get_option("theme.primaryColor")
is_dark_theme = streamlit_theme == "#FFFFFF"
text_color = 'white' if is_dark_theme else 'black'

fig = op.plot_beams(occ1_D, occ1_L, occ1_S, section_data, w_delt_L, w_delt_T, w_delt_P, text_color)
plotly_fig = tls.mpl_to_plotly(fig)
plotly_fig.update_layout(
    title_text='Plotly Figure with Title', 
    title_x=0.35
    )
fig = st.plotly_chart(plotly_fig, use_container_width=True)



