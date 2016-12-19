#!/usr/bin/env python3
"""
   make_ftdna_plots.py - generate plots for the blogpost
   Copyright (C) 2016 Giulio Genovese

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

   Written by Giulio Genovese <giulio.genovese@gmail.com>
"""

import argparse, json, pandas, numpy, matplotlib.pyplot

parser = argparse.ArgumentParser(description = 'Generate plots for blog post (19 Dec 2016)', add_help = False, usage = 'make_ftdna_plots.py <table> <yfull>')
parser.add_argument('t', metavar = '<STR>', type = str, help = 'Y chromosome table')
parser.add_argument('y', metavar = '<STR>', type = str, help = 'Yfull tree')

# extract arguments from the command line
try:
  parser.error = parser.exit
  args = parser.parse_args()
except SystemExit:
  parser.print_help()
  exit(2)

# load yfull tree
with open(args.y, 'r') as infile:
  tree = json.load(infile)  

# load STR table
df = pandas.read_csv(args.t, sep = '\t', index_col = 'Kit Number')
df.replace(0.0, numpy.nan, inplace = True)
df['Kit Number'] = df.index

# return list of all leaves under a node
def get_set(tree, key):
  result = {key}
  if key in tree:
    for subkey in tree[key]:
      result = result.union(get_set(tree, subkey))
  return result

# select non-fastchanging STRs
strs = ['DYS393', 'DYS390', 'DYS19', 'DYS391', 'DYS385', 'DYS426', 'DYS388', 'DYS439', 'DYS389i', 'DYS392', 'DYS389ii', 'DYS458', 'DYS459', 'DYS455', 'DYS454', 'DYS447', 'DYS437', 'DYS448', 'DYS449', 'DYS464', 'DYS460', 'Y-GATA-H4', 'YCAII', 'DYS456', 'DYS607', 'DYS576', 'DYS570', 'CDY', 'DYS442', 'DYS438', 'DYS531', 'DYS578', 'DYF395S1', 'DYS590', 'DYS537', 'DYS641', 'DYS472', 'DYF406S1', 'DYS511', 'DYS425', 'DYS413', 'DYS557', 'DYS594', 'DYS436', 'DYS490', 'DYS534', 'DYS450', 'DYS444', 'DYS481', 'DYS520', 'DYS446', 'DYS617', 'DYS568', 'DYS487', 'DYS572', 'DYS640', 'DYS492', 'DYS565', 'DYS710', 'DYS485', 'DYS632', 'DYS495', 'DYS540', 'DYS714', 'DYS716', 'DYS717', 'DYS505', 'DYS556', 'DYS549', 'DYS589', 'DYS522', 'DYS494', 'DYS533', 'DYS636', 'DYS575', 'DYS638', 'DYS462', 'DYS452', 'DYS445', 'Y-GATA-A10', 'DYS463', 'DYS441', 'Y-GGAAT-1B07', 'DYS525', 'DYS712', 'DYS593', 'DYS650', 'DYS532', 'DYS715', 'DYS504', 'DYS513', 'DYS561', 'DYS552', 'DYS726', 'DYS635', 'DYS587', 'DYS643', 'DYS497', 'DYS510', 'DYS434', 'DYS461', 'DYS435']
multi = ['DYS385', 'DYS459', 'DYS464', 'YCAII', 'CDY', 'DYF395S1', 'DYS413']
fastchanging = ['DYS385', 'DYS439', 'DYS458', 'DYS449', 'DYS464', 'DYS456', 'DYS576', 'DYS570', 'CDY', 'DYS413', 'DYS557', 'DYS481', 'DYS446']
struse = set(strs).difference(multi).difference(fastchanging)
str111 = df[strs].notnull().sum(axis=1)>100

output = {333499: '333499.png', 456438: '456438.png'}
slct1 = {333499: (df[str111]['DYS445']<=7) & (df[str111]['DYS391']==9), 456438: df[str111]['Haplogroup'].isin(get_set(tree, 'R-P312'))}
slct2 = {333499: df[str111]['Haplogroup'].isin(get_set(tree, 'J-L24')), 456438: df[str111]['Haplogroup'].isin(get_set(tree, 'R-M269'))}
slct3 = {333499: df[str111]['Haplogroup'].isin(get_set(tree, 'J2')), 456438: df[str111]['Haplogroup'].isin(get_set(tree, 'R-M417'))}
ttl = {333499: 'Blue: J2a-L70, Green: other J2a-L24, Red: other J2-M172, Cyan: all others', 456438: 'Blue: R1b-P312, Green: other R1b-M269, Red: R1a-M417, Cyan: all others'}
xlbl = {333499: '# discordant non-fast-changing STRs when comparing to my Y', 456438: '# discordant non-fast-changing STRs when comparing to my grandpa\'s Y'}

# plot one figure for each Y chromosome
for kit in [333499, 456438]:
  m = df.ix[str111, struse].convert_objects(convert_numeric = True).values
  d = numpy.nansum(m != m[df.index[str111] == kit], axis = 1)
  x = d[numpy.where(slct1[kit])]
  y = d[numpy.where(~slct1[kit] & slct2[kit])]
  z = d[numpy.where(~slct1[kit] & ~slct2[kit] & slct3[kit])]
  w = d[numpy.where(~slct1[kit] & ~slct2[kit] & ~slct3[kit])]
  matplotlib.pyplot.figure()
  matplotlib.pyplot.hist([x,y,z,w], bins=range(10, max(max(x),max(y),max(z),max(w)) + 1, 1), stacked = True)
  matplotlib.pyplot.ylim((1, 5000))
  matplotlib.pyplot.xlabel(xlbl[kit])
  matplotlib.pyplot.ylabel('Y chromosome count in FamilyTreeDNA')
  matplotlib.pyplot.yscale('log')
  matplotlib.pyplot.title(ttl[kit])
  matplotlib.pyplot.savefig(output[kit])
