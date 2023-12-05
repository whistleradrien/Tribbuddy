import streamlit as st
import app_module as op
import plotly.tools as tls

st.write("# Span-to-trib-width limit curves for PSL beams")

tab1, tab2, tab3 = st.tabs(["Span-to-trib-width limits", "Assumptions", "Beams factored resistances"])

with tab1:
    st.header("Span-to-trib-width limits")
    st.write('The curves combines the shear, moment, and deflection limits of each beam whichever is the most defavorable at a specific span. A secondary cuves includes also the bearing limits of the beams.')
    st.write('After filling the information on the right over the mouse over the curves to get the maximum tributary width a PSL beam can support for a specific span.')


    floor_depth = [9.5, 11.25, 11.875, 14, 16, 19]

    st.sidebar.write("## Floor thickness")
    min_floor_thickness = st.sidebar.selectbox("Minimum floor thickness", floor_depth)

    filtered_floor_depth = [depth for depth in floor_depth if depth >= min_floor_thickness]
    max_floor_thickness = st.sidebar.selectbox("Maximum floor thickness", filtered_floor_depth)

    section_data = op.weyer_sections()
    section_data.set_index('Name', inplace=True)
    section_data = op.sections_filter(section_data, 'ge', Depth=min_floor_thickness)
    section_data = op.sections_filter(section_data, 'le', Depth=max_floor_thickness)

    st.sidebar.write("## Occupancy Loading")
    occ1_D = st.sidebar.number_input(label = "Dead load (psf)", value = 20)
    occ1_L = st.sidebar.number_input(label = "Live load (psf)", value = 40)
    occ1_S = st.sidebar.number_input(label = "Snow load (psf)", value = 180)

    st.sidebar.write("## Deflection Limits")
    w_delt_L = st.sidebar.number_input(label = "Live = L/", value = 360)
    w_delt_T = st.sidebar.number_input(label = "Total = L/", value = 180)
    w_delt_P = st.sidebar.number_input(label = "Permanent = L/", value = 360)

    st.sidebar.write("## Bearing")
    pl_mat = st.sidebar.selectbox("Support material", 
                                ['D.Fir SS',
                                    'D.Fir No. 1/No. 2',
                                    'Hem-Fir L. No. 1/No. 2',
                                    'SPF No. 1/No. 2',
                                    'Northern No. 1/No. 2'], index = 1)

    brg_length = st.sidebar.number_input(label = "Bearing Length (in)", value = 5.5)

    fig = op.plot_beams(
        D = occ1_D,
        L = occ1_L, 
        S = occ1_S, 
        section_data = section_data, 
        w_delt_L = w_delt_L, 
        w_delt_T = w_delt_T, 
        w_delt_P = w_delt_P, 
        pl_mat = pl_mat, 
        brg_length = brg_length)

    plotly_fig = tls.mpl_to_plotly(fig)
    plotly_fig.update_layout(
        title_text='PSL Beams capacities', 
        title_x=0.35
        )
    fig = st.plotly_chart(plotly_fig, use_container_width=True)

with tab2:
    st.header("Assumptions")
    st.write('- Simply supported PSL beams loaded with uniformly distributed loads.')
    st.write('- The limits are calculated according to the CSA O86-19 standard.')
    st.write('- The beams compressive edge is held in line by direct connection of decking or joists spaced not more than 610 mm apart and bridging or blocking is installed at intervals not exceeding eight times the depth of the member, i.e. KL = 1.')
    st.write('- The size factor K_zb in bending is included in the bending resisance values provided in the beam properties tables from Weyerhaeuser.')
    st.write('- Takes in account the load duration factor K_D per CSA 086 19 cl 5.3.2.2')
    st.write('- Assumes a non repetitive member and accounts for a system factor K_H = 1')
    st.write('- Takes in account the load sharing factor K_L per CSA 086 19 cl 6.5.3.2')
    st.write('- Assumes the member works in dry condition without any preservative treatment K_S = 1 and K_T = 1 CSA 086 19 cl 15.3')

    st.write('- Load combinations for strength and stability is the maximum of:')
    st.latex(r'''LC1 = 1.4 * D''')
    st.latex(r'''LC2 = 1.25 * D + 1.5 * L + 0.5 * S''')
    st.latex(r'''LC3 = 1.25 * D + 1.5 * S + 0.5 * L''')

    st.write('- Load combinations for serviceability:')
    st.write('       Deflection under live load is the maximum of Live load or Snow load.')

    st.write('       Deflection under total load is the maximum of:')
    st.latex(r'''D + L + 0.5 * S''')
    st.latex(r'''D + 0.5 * L + S''')
    st.write('- Deflection limits calculated consider bending and shear deflection using the following equation:')
    st.latex(r'''\Delta = \frac{270 wL^4}{Ebd^3} + \frac{28.8 wL^2}{Ebd}''')
    


with tab3:
    st.header("Beams factored resistances")
    st.write('The material properties are taken from the Weyerhaeuser TJ-9505 PSL product guide.')
    st.write('The following table shows the properties of the PSL beams that are included in the app.')
    st.write(section_data)