import numpy as np, math
from pynverse import inversefunc

# a set of three bi-directional lung and chest wall curves allowing calculation
# of pressure from volume, and volume from pressure
# exports both simple and vectorized forms

# see https://docs.google.com/spreadsheets/d/1BO59dnA8dqs8TdPTD3WMBnii7FRxPDB1FVFzTB6eVsU/edit?usp=sharing for curves

def lung(p):
    return 6.66 + 27.9 * math.log(p if p>0 else 0.000000001)
def chest_wall(p):
    return 51.3 * math.exp(0.0635 * p)
def total(p):
    b =46.2134
    a = -261.437
    c = -9.68139
    d = 11.6401
    f = 1.2952
    return b + c * math.sin((p+a)/d) + f * p

switch_v_p = {"Total": total,
              "Lung": lung,
              "Chest": chest_wall}
switch_p_v = {"Total": inversefunc(total),
              "Lung": inversefunc(lung),
              "Chest": inversefunc(chest_wall)}
switch_v_p_vectorized = {"Total": np.vectorize(total),
              "Lung": np.vectorize(lung),
              "Chest": np.vectorize(chest_wall)}
switch_p_v_vectorized = {"Total": np.vectorize(inversefunc(total)),
              "Lung": np.vectorize(inversefunc(lung)),
              "Chest": np.vectorize(inversefunc(chest_wall))}

# report volumes as % of total TLC
def volume_from_pressure(p, type = "Total"):
    func = switch_v_p.get(type, lambda: 'error bad type')
    return func(p)

def pressure_from_volume(v, type = "Total"):
    func = switch_p_v.get(type, lambda: 'error bad type')
    return func(v)

def volume_from_pressure_vectorized(p, type = "Total"):
    func = switch_v_p_vectorized.get(type, lambda: 'error bad type')
    return func(p)

def pressure_from_volume_vectorized(v, type = "Total"):
    func = switch_p_v_vectorized.get(type, lambda: 'error bad type')
    return func(v)
