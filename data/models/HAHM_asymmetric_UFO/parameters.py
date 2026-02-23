# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 12.0.0 for Linux x86 (64-bit) (April 7, 2019)
# Date: Sat 14 Sep 2024 14:34:15



from object_library import all_parameters, Parameter


from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
k = Parameter(name = 'k',
              nature = 'external',
              type = 'real',
              value = 1,
              texname = 'k',
              lhablock = 'HIDDEN',
              lhacode = [ 1 ])

ct1 = Parameter(name = 'ct1',
                nature = 'external',
                type = 'real',
                value = 1,
                texname = '\\text{ct1}',
                lhablock = 'HIDDEN',
                lhacode = [ 2 ])

ct2 = Parameter(name = 'ct2',
                nature = 'external',
                type = 'real',
                value = 1,
                texname = '\\text{ct2}',
                lhablock = 'HIDDEN',
                lhacode = [ 3 ])

cl = Parameter(name = 'cl',
               nature = 'external',
               type = 'real',
               value = 1,
               texname = '\\text{cl}',
               lhablock = 'HIDDEN',
               lhacode = [ 4 ])

Lambda = Parameter(name = 'Lambda',
                   nature = 'external',
                   type = 'real',
                   value = 1000,
                   texname = '\\text{Lambda}',
                   lhablock = 'HIDDEN',
                   lhacode = [ 5 ])

aEWM1 = Parameter(name = 'aEWM1',
                  nature = 'external',
                  type = 'real',
                  value = 127.9,
                  texname = '\\text{aEWM1}',
                  lhablock = 'SMINPUTS',
                  lhacode = [ 1 ])

Gf = Parameter(name = 'Gf',
               nature = 'external',
               type = 'real',
               value = 0.000011663900000000002,
               texname = '\\text{Gf}',
               lhablock = 'SMINPUTS',
               lhacode = [ 2 ])

aS = Parameter(name = 'aS',
               nature = 'external',
               type = 'real',
               value = 0.118,
               texname = '\\text{aS}',
               lhablock = 'SMINPUTS',
               lhacode = [ 3 ])

hbar = Parameter(name = 'hbar',
                 nature = 'external',
                 type = 'real',
                 value = 6.582119569e-25,
                 texname = '\\text{hbar}',
                 lhablock = 'SMINPUTS',
                 lhacode = [ 10 ])

c = Parameter(name = 'c',
              nature = 'external',
              type = 'real',
              value = 108458064,
              texname = 'c',
              lhablock = 'SMINPUTS',
              lhacode = [ 11 ])

Me = Parameter(name = 'Me',
               nature = 'external',
               type = 'real',
               value = 0.000511,
               texname = '\\text{Me}',
               lhablock = 'MASS',
               lhacode = [ 11 ])

MMU = Parameter(name = 'MMU',
                nature = 'external',
                type = 'real',
                value = 0.10566,
                texname = '\\text{MMU}',
                lhablock = 'MASS',
                lhacode = [ 13 ])

MTA = Parameter(name = 'MTA',
                nature = 'external',
                type = 'real',
                value = 1.777,
                texname = '\\text{MTA}',
                lhablock = 'MASS',
                lhacode = [ 15 ])

MU = Parameter(name = 'MU',
               nature = 'external',
               type = 'real',
               value = 0.00255,
               texname = 'M',
               lhablock = 'MASS',
               lhacode = [ 2 ])

MC = Parameter(name = 'MC',
               nature = 'external',
               type = 'real',
               value = 1.27,
               texname = '\\text{MC}',
               lhablock = 'MASS',
               lhacode = [ 4 ])

MT = Parameter(name = 'MT',
               nature = 'external',
               type = 'real',
               value = 172,
               texname = '\\text{MT}',
               lhablock = 'MASS',
               lhacode = [ 6 ])

MD = Parameter(name = 'MD',
               nature = 'external',
               type = 'real',
               value = 0.00504,
               texname = '\\text{MD}',
               lhablock = 'MASS',
               lhacode = [ 1 ])

MS = Parameter(name = 'MS',
               nature = 'external',
               type = 'real',
               value = 0.101,
               texname = '\\text{MS}',
               lhablock = 'MASS',
               lhacode = [ 3 ])

MB = Parameter(name = 'MB',
               nature = 'external',
               type = 'real',
               value = 4.7,
               texname = '\\text{MB}',
               lhablock = 'MASS',
               lhacode = [ 5 ])

mh = Parameter(name = 'mh',
               nature = 'external',
               type = 'real',
               value = 600,
               texname = '\\text{mh}',
               lhablock = 'MASS',
               lhacode = [ 25 ])

ms1 = Parameter(name = 'ms1',
                nature = 'external',
                type = 'real',
                value = 500,
                texname = '\\text{ms1}',
                lhablock = 'MASS',
                lhacode = [ 35 ])

ms2 = Parameter(name = 'ms2',
                nature = 'external',
                type = 'real',
                value = 500,
                texname = '\\text{ms2}',
                lhablock = 'MASS',
                lhacode = [ 36 ])

WT = Parameter(name = 'WT',
               nature = 'external',
               type = 'real',
               value = 1.50833649,
               texname = '\\text{WT}',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

WH = Parameter(name = 'WH',
               nature = 'external',
               type = 'real',
               value = 0.00282299,
               texname = '\\text{WH}',
               lhablock = 'DECAY',
               lhacode = [ 25 ])

Ws1 = Parameter(name = 'Ws1',
                nature = 'external',
                type = 'real',
                value = 1,
                texname = '\\text{Ws1}',
                lhablock = 'DECAY',
                lhacode = [ 35 ])

Ws2 = Parameter(name = 'Ws2',
                nature = 'external',
                type = 'real',
                value = 1,
                texname = '\\text{Ws2}',
                lhablock = 'DECAY',
                lhacode = [ 36 ])

aEW = Parameter(name = 'aEW',
                nature = 'internal',
                type = 'real',
                value = '1/aEWM1',
                texname = '\\text{aEW}')

G = Parameter(name = 'G',
              nature = 'internal',
              type = 'real',
              value = '2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)',
              texname = 'G')

v = Parameter(name = 'v',
              nature = 'internal',
              type = 'real',
              value = '1/(2**0.25*cmath.sqrt(Gf))',
              texname = 'v')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

y1 = Parameter(name = 'y1',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(cmath.pi)*cmath.sqrt((c*hbar*ms1**2*v**2)/(ct1*(3*MB**2*(-4*MB**2 + ms1**2)**1.5 + 3*MC**2*(-4*MC**2 + ms1**2)**1.5 + 3*MD**2*(-4*MD**2 + ms1**2)**1.5 + 3*MS**2*(-4*MS**2 + ms1**2)**1.5 + MTA**2*(ms1**2 - 4*MTA**2)**1.5 + 3*MU**2*(ms1**2 - 4*MU**2)**1.5)))',
               texname = '\\text{y1}')

y2 = Parameter(name = 'y2',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(cmath.pi)*cmath.sqrt((c*hbar*ms2**2*v**2)/(ct2*(3*MB**2*(-4*MB**2 + ms2**2)**1.5 + 3*MC**2*(-4*MC**2 + ms2**2)**1.5 + 3*MD**2*(-4*MD**2 + ms2**2)**1.5 + 3*MS**2*(-4*MS**2 + ms2**2)**1.5 + MTA**2*(ms2**2 - 4*MTA**2)**1.5 + 3*MU**2*(ms2**2 - 4*MU**2)**1.5)))',
               texname = '\\text{y2}')

