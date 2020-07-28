#!/usr/bin/env python3.7
import sys
import matplotlib, json
import pandas as pd, matplotlib.pyplot as plt
from datetime import datetime
from pprint import pprint
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ventos.sim import simple

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

def run_and_output(scenario):
    pprint(scenario)
    pdf = simple.execute_scenario(scenario)
    vent_plots(pdf, title=scenario['title'])
    plt.show()
    return pdf

sample_frequency = 20
time_resolution = round(1000/sample_frequency)

base_scenario = dict(
    title = 'Base',
    resistance = 20,
    PEEP = 5,
    IE = 0.5,
    Pi = 15,
    rate = 10,
    end_time = 30,
    time_resolution = time_resolution, # ms between cycles
    flow_noise_sd = 0.05,
    pressure_noise_sd = 1, # cmH2O
    heart_rate = 85,
    cardiac_amplitude = 0.05,
    events = []
)

badnesses = dict(
    Creeping = [
        dict(attr = 'PEEP', val = 7),
        dict(attr = 'PEEP', val = 10, time=3),
        dict(attr = 'Pi', val = 15, time=6),
        dict(attr = 'PEEP', val = 14, time=10),
    ],
    HiPressure = [
        dict(attr = 'Pi', val = 45),
        dict(attr = 'PEEP', val = 33),
    ],
    LoPressure = [
        dict(attr = 'Pi', val = 7),
        dict(attr = 'PEEP', val = 5),
    ],
    Cardiac30 = [
        dict(attr = 'cardiac_amplitude', val = 0.1),
        dict(attr = 'heart_rate', val = 30)
        ],
    Cardiac120 = [
        dict(attr = 'cardiac_amplitude', val = 0.1),
        dict(attr = 'heart_rate', val = 120)
        ],
    HighResistance = [
        dict(attr = 'resistance', val = 80)
        ],
    LowPressure = [
        dict(attr = 'Pi', val = 7)
        ],
    Wimpy = [
        dict(attr = 'PEEP', val = 7),
        dict(attr = 'Pi', val = 10),
        ],
    HighPressure = [
        dict(attr = 'PEEP', val = 14)
        ],
    StuckHigh = [
        dict(attr = 'PEEP', val = 14),
        dict(attr = 'Pi', val = 14)
        ],
    CrazyFast = [
        dict(attr = 'rate', val = 60)
        ],
    ToosLow = [
        dict(attr = 'rate', val = 3)
        ],
    NoExpirationTime = [
        dict(attr = 'rate', val = 12),
        dict(attr = 'IE', val = 5)
        ],
    )

# factory for a list of scenarios
# uses and event record:
#     eg dict(attr = 'Pi', val = 15, time=start+6)
def scenarios(badnesses=badnesses,
        badness_start = 40, fix = 120,
        duration = 240, sample_frequency = 20):
    def add_new_events(current_events, new_events, offset, unwind_at=0, base=[]):
        for e in new_events:
            current_events.append(dict(e, time=e.get('time',0)+offset))
        return unwind_badness(current_events,  new_events, unwind_at, base) if unwind_at else current_events
    # loop over daranged attributes and restore them
    def unwind_badness(current_events, badness, offset, base):
        for deranged in set([b['attr'] for b in badness]):
            current_events.append(dict(attr = deranged, val=base[deranged], time=offset))
        return current_events
    base = dict(base_scenario, time_resolution = round(1000/sample_frequency))
    scenarios = {}
    for title, badness in badnesses.items():
        scenarios[title] = dict(base,
            title = title,
            end_time = duration,
            events = add_new_events([], new_events = badness, offset = badness_start, unwind_at = fix, base=base))
    return scenarios

# retrieve a specific scenario by name
def scenario(title):
    scenario = next((s for s in scenarios() if s["title"] == title), None)
    return scenario

# this is a simple 5 column format
def make_not_pirds(df):
    d = df[['time','pressure_1', 'pressure_1', 'flow_i', 'flow_e']].copy()
    d.columns = ['time', 'PI', 'PE', 'FI', 'FE']
    d['FI'] *= simple.litres_per_second_to_ml_per_minute
    d['FE'] *= simple.litres_per_second_to_ml_per_minute
    return d.astype(int)

def update_files(scenario, path, pirds = False, csv = False, not_pirds= False, plot = False):
    #pprint(scenario)
    name = f"""{scenario['title'].title().replace(' ', '')}_{
         round(1000/scenario['time_resolution'])}x{scenario['end_time']}"""
    filestem = os.path.join(path, name)
    print(f'name stem: {filestem}')
    pdf = simple.execute_scenario(scenario)
    if pirds or csv:
        pirds_df = simple.df_to_PIRDS(pdf)
    if pirds:
        pirds_df.to_json(f"{filestem}.pirds.json", orient="records",lines=True)
    if csv:
        pirds_df.to_csv(f"{filestem}.pirds.csv", index=False)
    if not_pirds:
        make_not_pirds(pdf).to_csv(f"{filestem}.csv", index=False)
    if plot:
        vent_plots(pdf, title=scenario['title'])
        plt.savefig(f"{filestem}.png")

def run_all():
    for s in scenarios()[:0]:
        run_and_output(s)

def sys_info():
    return f'python {sys.version.split(" ")[0]} at {datetime.now()} in {os.getcwd()}'

def main():
    # pprint(scenarios()[:2])
    path = os.path.join(os.getcwd(),'test_traces')
    for title, s in scenarios(badnesses).items():
        print(f"################## {title} {round(1000/s['time_resolution'])}Hz for {s['end_time']}s")
        #pprint(s)
        update_files(s, path, pirds=True, csv=False, not_pirds=False, plot=True)

if __name__ == "__main__":
    print("starting", sys_info())
    main()
    print("done", sys_info())
