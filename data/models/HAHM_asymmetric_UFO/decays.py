# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 12.0.0 for Linux x86 (64-bit) (April 7, 2019)
# Date: Sat 14 Sep 2024 14:34:15


from object_library import all_decays, Decay
import particles as P


Decay_h = Decay(name = 'Decay_h',
                particle = P.h,
                partial_widths = {(P.s1,P.s2):'(k**2*v**2*cmath.sqrt(mh**4 - 2*mh**2*ms1**2 + ms1**4 - 2*mh**2*ms2**2 - 2*ms1**2*ms2**2 + ms2**4))/(16.*cmath.pi*abs(mh)**3)',
                                  (P.G,P.G):'(2*cl**2*mh**6)/(cmath.pi*Lambda**2*abs(mh)**3)'})

Decay_s1 = Decay(name = 'Decay_s1',
                 particle = P.s1,
                 partial_widths = {(P.h,P.s2):'(k**2*v**2*cmath.sqrt(mh**4 - 2*mh**2*ms1**2 + ms1**4 - 2*mh**2*ms2**2 - 2*ms1**2*ms2**2 + ms2**4))/(16.*cmath.pi*abs(ms1)**3)',
                                   (P.ta__minus__,P.ta__plus__):'(((16*ms1**2*MTA**2*y1**2)/v**2 - (64*MTA**4*y1**2)/v**2)*cmath.sqrt(ms1**4 - 4*ms1**2*MTA**2))/(16.*cmath.pi*abs(ms1)**3)',
                                   (P.d,P.d__tilde__):'(((-192*MD**4*y1**2)/v**2 + (48*MD**2*ms1**2*y1**2)/v**2)*cmath.sqrt(-4*MD**2*ms1**2 + ms1**4))/(16.*cmath.pi*abs(ms1)**3)',
                                   (P.s,P.s__tilde__):'(((-192*MS**4*y1**2)/v**2 + (48*MS**2*ms1**2*y1**2)/v**2)*cmath.sqrt(-4*MS**2*ms1**2 + ms1**4))/(16.*cmath.pi*abs(ms1)**3)',
                                   (P.b,P.b__tilde__):'(((-192*MB**4*y1**2)/v**2 + (48*MB**2*ms1**2*y1**2)/v**2)*cmath.sqrt(-4*MB**2*ms1**2 + ms1**4))/(16.*cmath.pi*abs(ms1)**3)',
                                   (P.u,P.u__tilde__):'(((48*ms1**2*MU**2*y1**2)/v**2 - (192*MU**4*y1**2)/v**2)*cmath.sqrt(ms1**4 - 4*ms1**2*MU**2))/(16.*cmath.pi*abs(ms1)**3)',
                                   (P.c,P.c__tilde__):'(((-192*MC**4*y1**2)/v**2 + (48*MC**2*ms1**2*y1**2)/v**2)*cmath.sqrt(-4*MC**2*ms1**2 + ms1**4))/(16.*cmath.pi*abs(ms1)**3)',
                                   (P.t,P.t__tilde__):'(((48*ms1**2*MT**2*y1**2)/v**2 - (192*MT**4*y1**2)/v**2)*cmath.sqrt(ms1**4 - 4*ms1**2*MT**2))/(16.*cmath.pi*abs(ms1)**3)'})

Decay_s2 = Decay(name = 'Decay_s2',
                 particle = P.s2,
                 partial_widths = {(P.h,P.s1):'(k**2*v**2*cmath.sqrt(mh**4 - 2*mh**2*ms1**2 + ms1**4 - 2*mh**2*ms2**2 - 2*ms1**2*ms2**2 + ms2**4))/(16.*cmath.pi*abs(ms2)**3)',
                                   (P.ta__minus__,P.ta__plus__):'(((16*ms2**2*MTA**2*y2**2)/v**2 - (64*MTA**4*y2**2)/v**2)*cmath.sqrt(ms2**4 - 4*ms2**2*MTA**2))/(16.*cmath.pi*abs(ms2)**3)',
                                   (P.d,P.d__tilde__):'(((-192*MD**4*y2**2)/v**2 + (48*MD**2*ms2**2*y2**2)/v**2)*cmath.sqrt(-4*MD**2*ms2**2 + ms2**4))/(16.*cmath.pi*abs(ms2)**3)',
                                   (P.s,P.s__tilde__):'(((-192*MS**4*y2**2)/v**2 + (48*MS**2*ms2**2*y2**2)/v**2)*cmath.sqrt(-4*MS**2*ms2**2 + ms2**4))/(16.*cmath.pi*abs(ms2)**3)',
                                   (P.b,P.b__tilde__):'(((-192*MB**4*y2**2)/v**2 + (48*MB**2*ms2**2*y2**2)/v**2)*cmath.sqrt(-4*MB**2*ms2**2 + ms2**4))/(16.*cmath.pi*abs(ms2)**3)',
                                   (P.u,P.u__tilde__):'(((48*ms2**2*MU**2*y2**2)/v**2 - (192*MU**4*y2**2)/v**2)*cmath.sqrt(ms2**4 - 4*ms2**2*MU**2))/(16.*cmath.pi*abs(ms2)**3)',
                                   (P.c,P.c__tilde__):'(((-192*MC**4*y2**2)/v**2 + (48*MC**2*ms2**2*y2**2)/v**2)*cmath.sqrt(-4*MC**2*ms2**2 + ms2**4))/(16.*cmath.pi*abs(ms2)**3)',
                                   (P.t,P.t__tilde__):'(((48*ms2**2*MT**2*y2**2)/v**2 - (192*MT**4*y2**2)/v**2)*cmath.sqrt(ms2**4 - 4*ms2**2*MT**2))/(16.*cmath.pi*abs(ms2)**3)'})

