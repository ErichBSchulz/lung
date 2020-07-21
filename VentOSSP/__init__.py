"""
Algorithm from https://arxiv.org/pdf/2006.03664.pdf
"""
from dataclasses import dataclass
@dataclass
class VentilatorStatus:
    p: float = 0 # current pressure (cmH2O)
    vhigh: float  = 0 # high pressure envelope
    vlow: float  = 0 # low pressure envelope
    Vhigh: float  = 0 # breath cycle maximum pressure
    Vlow: float  = 0 # breath cycle minimum pressure
    Thigh: float  = 0 # samples since most recent breath cycle maximum
    Tlow: float  = 0 # samples since most recent breath cycle minimum
    Tpeak: float  = 0 # samples since previous breath cycle maximmum
    PIP: float  = 0 # smoothed peak inspriratory pressure
    PEEP: float  = 0 # smoothed end expiratory pressure
    RR: float  = 0 # respiratory rate (per minute)
    inhaling: bool = False

@dataclass
class VentilatorConfig:
    alphaA: float  = 0.9 #envelope attack coefficient (0-1)
    alphaR: float  = 0.99 #envelope release coefficient (0-1)
    alphaS: float  = 0.9 # smoothing coefficient (0-1)
    sample_frequency: float  = 10 # sample rate (Hz)

# generic smoothing function to apply return a weighted average of a new and old value
# alpha is between and 1, the higher the alpha the slower the movement away
def recursive_smooth(alpha, current, new):
    return alpha * current + (1-alpha) * new

# config = config
# state = status - mutated by function
# p = latest pressure from pressure sensor
def smooth(config, state, p):
    state.p = p # store value in state
    state.Tpeak = state.Tpeak + 1
    if p >= state.vhigh:
        state.vhigh = recursive_smooth(config.alphaA, state.vhigh, p)
        state.Vhigh = p
        state.Thigh = 0
        if not state.inhaling:
            state.inhaling = True
            state.PEEP = recursive_smooth(config.alphaS, state.PEEP, state.Vlow)
        else:
            state.vhigh = recursive_smooth(config.alphaR, state.vhigh, state.p)
            state.Thigh = state.Thigh + 1
    if p <= state.vlow:
        state.vlow = recursive_smooth(config.alphaA, state.vlow, p)
        state.Vlow = p
        state.Tlow = 0
        if state.inhaling:
            state.inhaling = False
            state.PIP = recursive_smooth(config.alphaS, state.PIP, state.Vhigh)
            if state.RR > 0:
                state.RR = 1 / recursive_smooth(config.alphaS, 1/state.RR, (state.Tpeak - state.Thigh) / (60 * config.sample_frequency))
            else: # modification to prevent division by zero error
                state.RR = (60 * config.sample_frequency) / (state.Tpeak - state.Thigh)
            state.Tpeak = state.Thigh
    else:
        state.vlow = recursive_smooth(config.alphaR, state.vlow, p)
        state.Tlow = state.Tlow + 1