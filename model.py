import math

"""
Symbol	Description	Unit
CC	Collapsible airway compliance	l/cmH 2O
Ccw	Chest wall compliance	l/cmH 2O
CL	Lung compliance	l/cmH2O
Csyst	Compliance of the lung-chest wall system	l/cmH2O
F	Airflow at the mouth	l/s
PA	Alveolar pressure	cmH2O
PC	Collapsible airway pressure	cmH2O
Pcw	Chest wall pressure	cmH2O
Pel	Dynamic lung elastic recoil	cmH2O
Pext	Pressure at mouth	cmH2O
Pl	Static lung elastic recoil	cmH2O
Pmus	Muscular pressure	cmH2O
Ppl	Pleural pressure	cmH2O
Pref	Environmental pressure	cmH2O
Psyst	Elastic recoil of the lung-chest wall system	cmH2O
Ptm	Transmural pressure	cmH2O
RC	Collapsible airway resistance	cmH2O/l-1/s
RLT     Lung tissue resistance cmH2O/l-1/s
RS	Small airways resistance	cmH2O/l-1/s
RU	Upper airway resistance	cmH2O/l-1/s
TLC	Total lung capacity	l
VA	Alveolar space volume	l
VC	Collapsible airway volume	l
Vcw	Chest wall volume	l
VD	Dead space volume	l
VL	Total lung volume	l
VR	Residual volume	l
"""
# Parameter = Value	Unit
Ac = 7.09 # cmH2O
A1c = 5.6 # cmH2O
Acw = 1.4 # cmH2O
Al = 0.2 # cmH2O
As = 2.2 # cmH2O/l-1/s
Au = 0.34 # cmH2O/l-1/s
Bc = 37.3 # cmH2O
B1c = 3.73 # cmH2O
Bcw = 3.5 # cmH2O
Bl = 0.5 # cmH2O
Bs = 0.02 # cmH2O/l-1/s
Dc = 0.7 #
D1c = 0.999 #
Dcw = 0.999 #


Fmin = -6.2 # l/s

Fmax = 8.3 # l/s

Kl = 1.00 #
Ks = 10.9 #
Ku = 0.46 # cmH2O/l-2/s2
Kc = 0.21 # cmH2O/l-1/s
RLT = 0.2 # cmH2O/l-1/s
TLC = 5.19 # l
Vstar = 5.3 # l
V0A = 2.2 # l
V0C = 0.05 # l
VCmin = 0.015 # l
VCmax = 0.185 # l
VD = 0.05 # l
VR = 1.42 #

# function 15
Ptmmid = A1c - B1c*math.log(2-D1c)
# Eq 15 - volume of collapsible airway for certain airway volume
def VC(Ptm):
    if (Ptm < Ptmmid):
        return max(VCmin, VCmax * (Dc - math.sqrt((Ac-Ptm)/Bc)))
    else:
        return min(VCmax / (D1c + math.exp((A1c-Ptm)/B1c)), VCmax)

def RC(VC):
    return Kc * (VCmax/VC)**2

def test():
    print (f'Ptmmid {Ptmmid}')
    for p in range(-15, 40, 5):
        print (f'Ptmmid {p} -> VC {VC(p):.2f}, RC = {RC(VC(p)):.2f}')



test()




