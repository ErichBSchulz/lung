import matplotlib
import importlib
import ventos.signal as signal
import ventos.sim.simple as simple
import pandas as pd, matplotlib.pyplot as plt
from pprint import pprint

def vent_plots(pdf, title):
    fig, plots = plt.subplots(3, sharex=True) # , gridspec_kw={'hspace': 0}
    (ax1, ax2, ax3) = plots
    for ax in plots:
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
    plots[-1].spines['bottom'].set_visible(True)

    fig.suptitle(title)
    ax1.plot(pdf['time'] / 1000, pdf['flow'], 'dimgray')
    ax1.plot(pdf['time'] / 1000, pdf['flow_i'], 'tab:orange')
    ax1.plot(pdf['time'] / 1000, pdf['flow_e'], 'tab:blue')

    ax1.set(ylabel = 'Flow (l/s)')
    ax2.plot(pdf['time'] / 1000, pdf['pressure_mouth'], 'dimgray')
    ax2.plot(pdf['time'] / 1000, pdf['pressure_1'], 'tab:green')
    ax2.plot(pdf['time'] / 1000, pdf['pressure_2'], 'tab:green')

    ax2.set(ylabel = 'P (cmH2O)')
    ax3.plot(pdf['time'] / 1000, pdf['lung_volume'], 'tab:orange')
    ax3.set(ylabel = 'Volume (ml)', xlabel = 'time (seconds)')
    ax1.label_outer()
    ax2.label_outer()
    plt.show()

def run_and_output(scenario):
    pprint(scenario)
    pdf = simple.execute_scenario(scenario)
    vent_plots(pdf, title=scenario['title'])
    return pdf


base_scenario = dict(
    title = 'Base',
    resistance = 20,
    PEEP = 5,
    IE = 0.5,
    Pi = 15,
    rate = 10,
    end_time = 30,
    time_resolution = 50,
    flow_noise_sd = 0.05,
    pressure_noise_sd = 1,
    heart_rate = 85,
    cardiac_amplitude = 0.05,
    events = []
)

def scenarios():
    sample_frequency = 1000
    start = 40
    fix = 120
    badness = [
        dict(attr = 'PEEP', val = 10, time=start),
        dict(attr = 'Pi', val = 15, time=start+6),
        dict(attr = 'Pi', val = 13, time=start+10),
        dict(attr = 'PEEP', val = 13, time=start+15),
        dict(attr = 'PEEP', val = 5, time=fix),
        dict(attr = 'Pi', val = 20, time=fix+1),
    ]
    e= 30
    r= 500
    c= 0.1
    simple_badness = [
        dict(attr = 'PEEP', val = 10, time=4),
        dict(attr = 'Pi', val = 15, time=6),
        dict(attr = 'Pi', val = 13, time=10),

    ]
    scenarios = [
        base_scenario,
        dict(base_scenario, title='All rounder',
            Pi=20, PEEP=5,
            time_resolution = round(1000/sample_frequency), end_time = 240,
            events = badness),
        dict(base_scenario, title='Simple Badness',
             cardiac_amplitude = c, end_time = e, heart_rate = 60, time_resolution = r,
             events=simple_badness),
        dict(base_scenario, title='Cardiac 30', cardiac_amplitude = c, end_time = e, heart_rate = 30, time_resolution = r),
        dict(base_scenario, title='Cardiac 120', cardiac_amplitude = c, end_time = e, heart_rate = 120, time_resolution = r),
        dict(base_scenario, title='High Resistance', resistance = 80),
        dict(base_scenario, title='Low Pressure', Pi = 7),
        dict(base_scenario, title='Wimpy', PEEP = 7, Pi=10),
        dict(base_scenario, title='High Pressure', PEEP = 14),
        dict(base_scenario, title='Stuck High', PEEP = 14, Pi = 14),
        dict(base_scenario, title='Crazy fast', rate = 60),
        dict(base_scenario, title='Too slow', rate = 3),
        dict(base_scenario, title='No expiration time', rate = 12, IE = 5),
    ]
    return scenarios

def scenario(title):
    scenario = next((s for s in scenarios() if s["title"] == title), None)
    return scenario

def run_all():
    for s in scenarios():
        run_and_output(s)
