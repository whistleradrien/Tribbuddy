from dataclasses import dataclass
import matplotlib.pyplot as plt
import pandas as pd
import math
import forallpeople as us
import numpy as np
us.environment('structural')

MODULE_PATH = __file__
if "/" in MODULE_PATH:
    WEYER_DB_US_PATH = MODULE_PATH.rsplit("/", 1)[0] + "/" + "Weyerhaeuser_beam_data.csv"
elif "\\" in MODULE_PATH:
    WEYER_DB_US_PATH = MODULE_PATH.rsplit("\\", 1)[0] + "\\" + "Weyerhaeuser_beam_data.csv"
    

@dataclass
class Beam:
    Name: str # Size of beam (e.g. '3.5x11.875 PSL')
    Material: str
    Width: float
    Depth: float


@dataclass
class WeyerBeam(Beam):
    Vr: float # Shear resistance
    Mr: float # Moment resistance about x-axis
    E: float # Young's Modulus
    I: float # Moment of Invertia about x-axis
    Weight : float # Weight per foot
    f_cp: float # Compressive strength perpendicular to grain
    f_v: float # Horizontal Shear strength parallel to grain

    def factored_bearing_resistance(self, length = None) -> float:
        """
        Returns the bactored bearing resistance of a beam in kip. 
        Optional length parameter to provide bearing length in inches. By default it is equal to the width of the beam.
        """
        width = self.Width
        if length == None:
            length = width
        else:
            length = length * us.inch
        Br = width * length * self.f_cp
        return Br.to('kip')

def weyer_sections () -> pd.DataFrame:
    """
    Function that will load the appropriate sections based on the unit system that is entered. Opens US by default.
    """
    data = pd.read_csv(WEYER_DB_US_PATH)
    return data

def get_KD (d: float = 0, s: float = 0, l: float = 0) -> float:
    """
    Return the load duration factor K_D per CSA 086 19 cl 5.3.2.1 assuming 
    Standard term condition loading where the duration of specified loads
    exceeds that of short-term loading, but is less than long-term loading.
    Examples include snow loads, live loads due to occupancy, wheel loads on
    bridges, and long-term loads in combination with the above.
    
    Return the load duration factor K_D per CSA 086 19 cl 5.3.2.2 if the specified
    long-term load, PL, is greater than the specified standard-term load, Ps.
    
    Args:
        - d: dead load
        - l: live load
        - s: snow load
    """
    pl = d

    if s != 0 and l != 0:
        ps = min(s + 0.5 * l, l + 0.5 * s)
    
    elif s == 0 :
        ps = l

    elif l == 0:
        ps = s

    else:
        ps = min(s, l)

    if ps >=pl:
        return 1
    
    else:
        kd = 1 - 0.5 * math.log(pl/ps, 10)
        return max(0.65, kd)
    

def gravity_loads(D: float = 0, L: float = 0, S: float = 0) -> tuple:
    """ 
    Determine the required design loads for an assembly only subject to Dead load Live load
    and Snow load.
    When entering Dead Live and Snow, it will return:
        - the max linear factored load per table 4.1.3.2.-A
        - the max linear live load (between Live and Snow load)
        - the max total load.
    It assumes the max factored load is either from snow or live load whichever govern.
    """
    
    D = D * us.psf
    L = L * us.psf
    S = S * us.psf
    
    case_1 = 1.4 * D
    case_2 = 1.25 * D + 1.5 * L + 0.5 * S
    case_3 = 1.25 * D + 1.5 * S + 0.5 * L

    w_f = max(case_1, case_2, case_3)
    w = max(D + L, D + S)
    w_L = max(L, S)
    w_D = D
    return (w_f, w, w_L, w_D)


def sections_filter(df: pd.DataFrame, operator: str, **kwargs) -> pd.DataFrame:
    """
    Return a selection of sections where the column name are greater than or less than the value given in the dict.
    If the operator = 'ge' it will return all the sections with kwarg greater than the given values. 
    If the operator = 'le' it will return all the sections with kwarg greater than the given values. 
    """
    data = df.copy()
    for k, v in kwargs.items():
        if operator.lower() == 'ge':
            mask = data[k] >= v
            data = data.loc[(mask)]
            if data.empty:
                print(f"No records match all of the parameters: {kwargs}")
        elif operator.lower() == 'le':
            mask = data[k] <= v
            data = data.loc[(mask)]
            if data.empty:
                print(f"No records match all of the parameters: {kwargs}")
        else:
            raise ValueError(f"The second parameter of the function can only be 'ge' or 'le' not {operator}")
    return data


def WeyerBeam_prop(section_data: pd.DataFrame, name: str) -> WeyerBeam:
    """
    Returns a WeyerBeam instance populated with the section_record data and steel material properties from the inputs.
    """
    Name = name
    material = section_data.loc[name, 'Material']
    width = section_data.loc[name, 'Width'] * us.inch
    depth = section_data.loc[name, 'Depth'] * us.inch
    Vr = section_data.loc[name, 'Factored Shear Resistance (lbs)'] * us.lb
    Mr = section_data.loc[name, 'Factored Moment Resistance (ft-lbs)'] * us.lbft
    weight = section_data.loc[name, 'Weight (plf)'] * us.lb_ft
    E = section_data.loc[name, 'Apparent Modulus of Elasticity (psi)'] * us.psi
    I = section_data.loc[name, 'Moment of Inertia (in.4)'] * us.inch**4
    f_cp = section_data.loc[name, 'Compression Perpendicular to Grain (psi)'] * us.psi
    f_v = section_data.loc[name, 'Horizontal Shear Parallel to Grain (psi)'] * us.psi

    return WeyerBeam(Name = Name, Material = material, Width = width, Depth = depth, Vr = Vr, Mr = Mr, E = E, I = I, Weight = weight, f_cp = f_cp, f_v = f_v)


def working_load (my_beam: Beam, L: float, delta_T: float, delta_L: float, delta_P: float, kd: float) -> float:
    """
    Function that returns the maximum UDL a beam can support with a given span and factored resistance.
    The beam capacity inputs are:
    my_beam: a WeyerBeam instance
    L: Span of the beam in ft
    delta_T: Deflection/span retio limit for total load
    delta_L: Deflection/span retio limit for live load
    delta_D: Deflection/span retio limit for dead load
    KD: Load duration factor    
    """
    L = L * us.ft
    Vr = my_beam.Vr * kd
    Mr = my_beam.Mr * kd

    E = my_beam.E
    I = my_beam.I

    delta_P = L / delta_P
    delta_L = L / delta_L
    delta_T = L / delta_T

    w_Vr = Vr * 2 / L 
    w_Mr = Mr * 8 / (L**2)
    w_delt_T = (delta_T * 384 * E * I / (5 * L**4)).to('lb_ft')
    w_delt_L = (delta_L * 384 * E * I / (5 * L**4)).to('lb_ft')
    w_delt_P = (delta_P * 384 * E * I / (5 * L**4)).to('lb_ft')

    return (w_Vr, w_Mr, w_delt_T, w_delt_L, w_delt_P)


def get_trib (specified_loads: tuple, max_loads: tuple)-> float:
    """
    Function that returns the maximum tributary area a beam can support based on the specified loads area loads that are applied to it.
    Specified_loads: Tuple with the following values (w_f, w, w_L, w_D)
    Resisting_loads: Tuple with the following values (w_Vr, w_Mr, w_delt_T, w_delt_L, w_delt_D)
    """

    
    w_f = min(max_loads[0], max_loads[1]) / specified_loads[0]
    w_D = max_loads[4] / specified_loads[3]
    if specified_loads[1] == 0:     #ensure the program does not divide by zero
        w = 0   
    else:
        w = max_loads[2] / specified_loads[1]
    if specified_loads[2] == 0:     #ensure the program does not divide by zero
        return min(w_f, w, w_D)
    else:
        w_L = max_loads[3] / specified_loads[2]
        return min(w_f, w, w_L, w_D)





def plot_beams (D: float, L: float, S: float, section_data: pd.DataFrame, w_delt_L, w_delt_T, w_delt_P, text_color) -> None:
    """
    Function that plots the working load for a list of beams with a given span.
    """

    lengths = list(np.arange(5, 32, 0.25))

    fig, ax = plt.subplots() # First step: Create a Figure and Axes

    specified_loads = gravity_loads(D, L, S)
    kd = get_KD(D ,L, S)

    section_list = section_data.index.tolist()

    for section in section_list:
        my_beam = WeyerBeam_prop(section_data, section)
        w_min = []
        spans = []
        for length in lengths:
            max_loads = working_load(my_beam, length, w_delt_L, w_delt_T, w_delt_P, kd)
            trib = get_trib(specified_loads, max_loads)
            if trib <= 2 * us.ft or trib >= 25 * us.ft:
                continue
            else:
                spans.append(length)
                w_min.append(trib)
        ax.plot(spans, w_min, label=section)

    ax.set_xlabel('Span (ft)') # Add an x-label to the axes.
    ax.xaxis.label.set_color('darkgray')
    ax.xaxis.label.set_size(16)
    ax.set_ylabel('Trib width (ft)') # Add a y-label to the axes.
    ax.yaxis.label.set_color('darkgray')
    ax.yaxis.label.set_size(16)
    ax.set_title("Working Load vs Span") # Add a title to the axes.
    ax.title.set_color('darkgray')
    ax.title.set_size(20)
    # ax.set_ylim(bottom=2)
    # ax.legend() # Add a legend.
    legend = ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1))
    legend_texts = legend.get_texts()
    for text in legend_texts:
        text.set_color('darkgray')
    return fig