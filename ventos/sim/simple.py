import collections, pandas as pd, numpy as np
from ventos.lung import volume_from_pressure, pressure_from_volume
"""
							In men 	In women
				Vital capacity 	4.8 	3.1 	IRV + TV + ERV
		Inspiratory capacity 	3.8 	2.4 	IRV + TV
Functional residual capacity 	2.4 	1.8 	ERV + RV
		Total lung capacity 	6.0 	4.2 	IRV + TV + ERV + RV
"""
Patient_log = collections.namedtuple(
    'Patient_log',
    ['time', 'pressure_mouth', 'pressure_alveolus', 'pressure_intrapleural', 'lung_volume', 'flow'])

class Patient:
    def __init__(self,
                 height = 175, #cm
                 weight = 70, #kg
                 sex = 'M', # M or other
                 pressure_mouth = 0, #cmH2O
                 resistance = 10 # cmh2o/l/s or cmh2o per ml/ms
                ):
        self.time = 0 # miliseconds
        self.height = height
        self.weight = weight
        self.sex = sex
        self.TLC = 6000 if sex == 'M' else 4200 # todo calculate on age, height weight
        self.pressure_mouth = pressure_mouth
        self.resistance = resistance
        self.pressure_alveolus = pressure_mouth # start at equlibrium
        v_percent = volume_from_pressure(self.pressure_alveolus, 'Total') #assuming no resp effort
        self.lung_volume = self.TLC * v_percent / 100
        self.pressure_intrapleural = pressure_from_volume(v_percent, 'Chest')
        self.flow = 0
        self.log = []

    def status(self):
        return Patient_log(self.time, self.pressure_mouth, self.pressure_alveolus, self.pressure_intrapleural, self.lung_volume, self.flow)

    def advance(self, advance_time = 200, pressure_mouth = 0):
        self.time = self.time + advance_time # miliseconds
        self.pressure_mouth = pressure_mouth
        gradient = pressure_mouth - self.pressure_alveolus
        self.flow = gradient / self.resistance # l/second or ml/ms
        self.lung_volume += self.flow * advance_time
        v_percent = self.lung_volume * 100 / self.TLC
        self.pressure_alveolus = pressure_from_volume(v_percent, "Total")
        self.pressure_intrapleural = pressure_from_volume(v_percent, "Chest")
        status = self.status()
        self.log.append(status)
        return status


Ventilator_log = collections.namedtuple('Ventilator_log', ['time', 'phase', 'pressure', 'pressure_mouth'])
class Ventilator:
    def __init__(self, mode = "PCV", Pi = 15, PEEP = 5, rate = 10, IE=0.5):
        self.pressure = 0
        self.pressure_mouth = 0
        self.mode = mode
        self.Pi = Pi
        self.PEEP = PEEP
        self.rate = rate
        self.IE = IE
        self.phase = "E"
        self.log = []
        self.time = 0 # miliseconds

    def target_pressure(self):
        return self.PEEP if self.phase == "E" else self.Pi

    def status(self):
        return Ventilator_log(self.time, self.phase, self.pressure, self.pressure_mouth)

    def advance(self, advance_time = 200, pressure_mouth = 0):
        self.time = self.time + advance_time # miliseconds
        self.pressure_mouth = pressure_mouth # cmH2O
        # set phase
        breath_length = 60000 / self.rate # milliseconds
        time_since_inspiration_began = self.time % breath_length
        inspiration_length = breath_length * self.IE / (self.IE + 1)
        new_phase = "I" if time_since_inspiration_began < inspiration_length else "E"
        if new_phase != self.phase:
            self.phase = new_phase
            self.pressure = self.target_pressure()
            self.pressure_mouth = self.pressure # assume perfect ventilator
        status = self.status()
        self.log.append(status)
        return status

def loop(patient, ventilator,
        start_time = 0, end_time = 20000, time_resolution = 50, events = []):
    # print('starting', patient.status())
    patient_status = patient.advance(advance_time = 0)
    # print('vent starting', ventilator.status())
    for current_time in range(start_time, end_time, time_resolution):
        ventilator_status = ventilator.advance(advance_time = time_resolution, pressure_mouth = patient_status.pressure_mouth)
        patient_status = patient.advance(advance_time = time_resolution, pressure_mouth = ventilator_status.pressure_mouth)
        if len(events) and events[0]['time']*1000 <= current_time:
            e = events.pop(0)
            print(f'Event at {current_time}ms setting {e["attr"]} to {e["val"]}')
            setattr(ventilator, e["attr"], e["val"])
    df = pd.DataFrame.from_records(patient.log, columns=Patient_log._fields)
    if len(events):
        print(f'WARNING {len(events)} unprocessed')
    return df

## take a raw simple simulation and add noise sensor readers that match the sim
def decorate_sim(pdf, s):
    pdf['flow'] += np.random.normal(0, s['flow_noise_sd'], len(pdf))
    wave_length = s['heart_rate'] * np.pi * 2 / 60
    pdf['flow'] += np.sin(pdf['time'] * wave_length / 1000) * s['cardiac_amplitude']
    pdf['pressure_1'] = pdf['pressure_mouth'] + np.random.normal(0, s['pressure_noise_sd'], len(pdf)) #
    pdf['pressure_2'] = pdf['pressure_mouth'] + np.random.normal(0, s['pressure_noise_sd'], len(pdf)) #
    pdf['flow_i'] = pdf['flow'].clip(lower=0) + np.random.normal(0, s['flow_noise_sd'], len(pdf))
    pdf['flow_e'] = pdf['flow'].clip(upper=0) + np.random.normal(0, s['flow_noise_sd'], len(pdf))


# excecute a scenario (s)
# returns a dataframe
def execute_scenario(s):
    p = Patient(resistance=s['resistance'], pressure_mouth=s['PEEP'])
    v = Ventilator(PEEP=s['PEEP'], rate=s['rate'], IE=s['IE'], Pi = s['Pi'])
    pdf = loop(p, v,
              end_time = s['end_time'] * 1000, time_resolution=s['time_resolution'],
             events = s['events'])
    decorate_sim(pdf, s)
    return pdf

"""
Creating a PIRDS JSON file.

The Types are:

    P : Pressure: cm H2O (a medical standard) times 10
    F : Flow slm (liters at 0C per minute) times 1000


{ "event" : "M",
  "type" : "T",
  "loc" : "B",
  "num" : 2,
  "ms" : 35,
  "val" : 250
  }
"""

litres_per_second_to_ml_per_minute = 60*1000

def df_to_PIRDS(df):
    pirds = []
    for index, r in df.iterrows():
        pirds.append({"event": "M",
                      "type": "P", "loc":"I",
                      "ms": int(r.time), "val": int(round(r.pressure_1))})
        pirds.append({"event": "M",
                      "type": "P", "loc":"E",
                      "ms": int(r.time), "val": int(round(r.pressure_2))})
        pirds.append({"event": "M",
                      "type": "F", "loc":"I",
                      "ms": int(r.time), "val": int(round(r.flow_i * litres_per_second_to_ml_per_minute))})
        pirds.append({"event": "M",
                      "type": "F", "loc":"E",
                      "ms": int(r.time), "val": int(round(r.flow_e * litres_per_second_to_ml_per_minute))})
    return pd.DataFrame.from_records(pirds)

