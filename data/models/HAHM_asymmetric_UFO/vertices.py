# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 12.0.0 for Linux x86 (64-bit) (April 7, 2019)
# Date: Sat 14 Sep 2024 14:34:15


from object_library import all_vertices, Vertex
import particles as P
import couplings as C
import lorentz as L


V_1 = Vertex(name = 'V_1',
             particles = [ P.h, P.s1, P.s2 ],
             color = [ '1' ],
             lorentz = [ L.SSS1 ],
             couplings = {(0,0):C.GC_7})

V_2 = Vertex(name = 'V_2',
             particles = [ P.G, P.G, P.h ],
             color = [ 'Identity(1,2)' ],
             lorentz = [ L.VVS1 ],
             couplings = {(0,0):C.GC_4})

V_3 = Vertex(name = 'V_3',
             particles = [ P.ta__plus__, P.ta__minus__, P.s1 ],
             color = [ '1' ],
             lorentz = [ L.FFS1 ],
             couplings = {(0,0):C.GC_13})

V_4 = Vertex(name = 'V_4',
             particles = [ P.ta__plus__, P.ta__minus__, P.s2 ],
             color = [ '1' ],
             lorentz = [ L.FFS1 ],
             couplings = {(0,0):C.GC_20})

V_5 = Vertex(name = 'V_5',
             particles = [ P.G, P.G, P.G, P.h ],
             color = [ 'f(1,2,3)' ],
             lorentz = [ L.VVVS1 ],
             couplings = {(0,0):C.GC_5})

V_6 = Vertex(name = 'V_6',
             particles = [ P.G, P.G, P.G, P.G, P.h ],
             color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
             lorentz = [ L.VVVVS1, L.VVVVS2, L.VVVVS3 ],
             couplings = {(1,1):C.GC_6,(0,0):C.GC_6,(2,2):C.GC_6})

V_7 = Vertex(name = 'V_7',
             particles = [ P.G, P.G, P.G ],
             color = [ 'f(1,2,3)' ],
             lorentz = [ L.VVV1 ],
             couplings = {(0,0):C.GC_1})

V_8 = Vertex(name = 'V_8',
             particles = [ P.G, P.G, P.G, P.G ],
             color = [ 'f(-1,1,2)*f(3,4,-1)', 'f(-1,1,3)*f(2,4,-1)', 'f(-1,1,4)*f(2,3,-1)' ],
             lorentz = [ L.VVVV1, L.VVVV2, L.VVVV3 ],
             couplings = {(1,1):C.GC_3,(0,0):C.GC_3,(2,2):C.GC_3})

V_9 = Vertex(name = 'V_9',
             particles = [ P.d__tilde__, P.d, P.s1 ],
             color = [ 'Identity(1,2)' ],
             lorentz = [ L.FFS1 ],
             couplings = {(0,0):C.GC_10})

V_10 = Vertex(name = 'V_10',
              particles = [ P.s__tilde__, P.s, P.s1 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_11})

V_11 = Vertex(name = 'V_11',
              particles = [ P.b__tilde__, P.b, P.s1 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_8})

V_12 = Vertex(name = 'V_12',
              particles = [ P.d__tilde__, P.d, P.s2 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_17})

V_13 = Vertex(name = 'V_13',
              particles = [ P.s__tilde__, P.s, P.s2 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_18})

V_14 = Vertex(name = 'V_14',
              particles = [ P.b__tilde__, P.b, P.s2 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_15})

V_15 = Vertex(name = 'V_15',
              particles = [ P.u__tilde__, P.u, P.s1 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_14})

V_16 = Vertex(name = 'V_16',
              particles = [ P.c__tilde__, P.c, P.s1 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_9})

V_17 = Vertex(name = 'V_17',
              particles = [ P.t__tilde__, P.t, P.s1 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_12})

V_18 = Vertex(name = 'V_18',
              particles = [ P.u__tilde__, P.u, P.s2 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_21})

V_19 = Vertex(name = 'V_19',
              particles = [ P.c__tilde__, P.c, P.s2 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_16})

V_20 = Vertex(name = 'V_20',
              particles = [ P.t__tilde__, P.t, P.s2 ],
              color = [ 'Identity(1,2)' ],
              lorentz = [ L.FFS1 ],
              couplings = {(0,0):C.GC_19})

V_21 = Vertex(name = 'V_21',
              particles = [ P.u__tilde__, P.u, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_22 = Vertex(name = 'V_22',
              particles = [ P.c__tilde__, P.c, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_23 = Vertex(name = 'V_23',
              particles = [ P.t__tilde__, P.t, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_24 = Vertex(name = 'V_24',
              particles = [ P.d__tilde__, P.d, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_25 = Vertex(name = 'V_25',
              particles = [ P.s__tilde__, P.s, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

V_26 = Vertex(name = 'V_26',
              particles = [ P.b__tilde__, P.b, P.G ],
              color = [ 'T(3,2,1)' ],
              lorentz = [ L.FFV1 ],
              couplings = {(0,0):C.GC_2})

