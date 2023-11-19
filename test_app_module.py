import app_module as wb
import numpy as np
import forallpeople as us
us.environment('structural')
import pandas as pd
import math

def test_factored_bearing_resistance():

    my_beam = wb.WeyerBeam(
        Name='5.25x9.5 PSL',            
        Material='PSL',
        Width=5.250 * us.inch,
        Depth=9.500 * us.inch,
        Vr=16160.000 * us.lb,
        Mr=32580.000 * us.lbft,
        E=2126000.000 * us.psi, 
        I=375.000 * us.inch**4, 
        Weight=16.000 * us.lb_ft, 
        f_cp=1135.000 * us.psi, 
        f_v=540.000 * us.psi)

    assert math.isclose(my_beam.factored_bearing_resistance(), 31.283 * us.kip, rel_tol=1e-2)
    assert math.isclose(my_beam.factored_bearing_resistance(length=10), 59.588 * us.kip, rel_tol=1e-2)


def test_get_KD():
    d = 20
    s = 20
    l = 0
    expected = 1
    kd  = wb.get_KD(d, s, l)
    assert math.isclose(kd, expected, rel_tol=1e-2)

    d = 20
    s = 0
    l = 40
    expected = 1
    kd  = wb.get_KD(d, s, l)
    assert math.isclose(kd, expected, rel_tol=1e-2)

    d = 100
    s = 0
    l = 40
    expected = 0.80
    kd  = wb.get_KD(d, s, l)
    assert math.isclose(kd, expected, rel_tol=1e-2)

    d = 100
    s = 60
    l = 40
    expected = 0.923
    kd  = wb.get_KD(d, s, l)
    assert math.isclose(kd, expected, rel_tol=1e-2)

    d = 100
    s = 19
    l = 40
    expected = 0.796
    kd  = wb.get_KD(d, s, l)
    assert math.isclose(kd, expected, rel_tol=1e-2)


def test_gravity_loads():
    # Test case 1
    result = wb.load_factors.gravity_loads(D=100, L=50, S=30)
    assert result[0] == 200.0 * us.psf
    assert result[1] == 150.0 * us.psf
    assert result[2] == 50.0 * us.psf
    assert result[3] == 100.0 * us.psf

    # Test case 2
    result = wb.load_factors.gravity_loads(D=150, L=50, S=100)
    assert result[0] == 337.5 * us.psf
    assert result[1] == 250.0 * us.psf
    assert result[2] == 100.0 * us.psf
    assert result[3] == 150.0 * us.psf


def test_sections_filter():
    test_df = pd.DataFrame(data = [
        ["X", "A", 200, 300], 
        ["X", "B", 250, 250], 
        ["Y", "C", 400, 600], 
        ["Y", "D", 500, 700]], 
        columns=["Type", "Section", "Ix", "Sy"]
    )
    selection = wb.sections_filter(test_df, 'ge', Ix=400)
    assert selection.iloc[0, 1] == "C"
    assert selection.iloc[1, 1] == "D"   
    
    selection = wb.sections_filter(test_df, 'le', Sy=300)
    assert selection.iloc[0, 1] == "A"
    assert selection.iloc[1, 1] == "B" 

def test_WeyerBeam_prop():
    section_data = pd.DataFrame({
        'Material': "PSL",
        'Width': 3.5,
        'Depth': 9.25,
        'Factored Moment Resistance (ft-lbs)': 20655,
        'Factored Shear Resistance (lbs)': 10490,
        'Moment of Inertia (in.4)': 231,
        'Weight (plf)': 10,  
        'Apparent Modulus of Elasticity (psi)': 2126000,        
        'Compression Perpendicular to Grain (psi)': 1135,   
        'Horizontal Shear Parallel to Grain (psi)': 540
    }, index=['3.5x9.25 PSL'])

    sec = wb.WeyerBeam_prop(section_data, '3.5x9.25 PSL')


    assert sec.Name == '3.5x9.25 PSL'
    assert sec.E == 2126000	* us.psi
    assert sec.Vr == 10490 * us.lb


def test_working_load ():
    
    my_beam = wb.WeyerBeam(
        Name='5.25x9.5 PSL',            
        Material='PSL',
        Width=5.250 * us.inch,
        Depth=9.500 * us.inch,
        Vr=16160.000 * us.lb,
        Mr=32580.000 * us.lbft,
        E=2126000.000 * us.psi, 
        I=375.000 * us.inch**4, 
        Weight=16.000 * us.lb_ft, 
        f_cp=1135.000 * us.psi, 
        f_v=540.000 * us.psi)

    L = 18.5
    delta_T = 180
    delta_L = 240
    delta_P = 360
    kd  = 0.65
    expected = wb.working_load(my_beam =  my_beam, L = L, delta_T = delta_T, delta_L = delta_L, delta_P = delta_P, kd = kd)
    assert math.isclose(1135.57 * us.lb_ft, expected[0], rel_tol=1e-2)
    assert math.isclose(495.01 * us.lb_ft, expected[1], rel_tol=1e-2)
    assert math.isclose(373.08 * us.lb_ft, expected[2], rel_tol=1e-2)
    assert math.isclose(279.81 * us.lb_ft, expected[3], rel_tol=1e-2)
    assert math.isclose(186.52 * us.lb_ft, expected[4], rel_tol=1e-2)
    

def test_get_trib():
    specified_loads = (85, 60, 40, 20)
    max_loads = (135.57 * us.lb_ft, 495.01 * us.lb_ft, 373.08 * us.lb_ft, 279.81 * us.lb_ft, 186.52 * us.lb_ft)
    expected = 2.26
    trib = wb.get_trib(specified_loads, max_loads)
    assert math.isclose(trib, expected, rel_tol=1e-2)

    specified_loads = (25, 20, 0, 20)
    max_loads = (135.57 * us.lb_ft, 495.01 * us.lb_ft, 373.08 * us.lb_ft, 279.81 * us.lb_ft, 186.52 * us.lb_ft)
    expected = 6.779
    trib = wb.get_trib(specified_loads, max_loads)
    assert math.isclose(trib, expected, rel_tol=1e-2)