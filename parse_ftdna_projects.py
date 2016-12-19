#!/usr/bin/env python3
"""
   parse_ftdna_projects.py - process projects downloaded with get_ftdna_projects.sh
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

import argparse, os, sys, pandas, re

try:
    import lxml
except ImportError:
    sys.stderr.write('You need to install the lxml module first\n')
    sys.stderr.write('(run this in your terminal: "python3 -m pip install lxml" or "python3 -m pip install --user lxml")\n')
    exit(2)

try:
    import html5lib
except ImportError:
    sys.stderr.write('You need to install the html5lib module first\n')
    sys.stderr.write('(run this in your terminal: "python3 -m pip install html5lib" or "python3 -m pip install --user html5lib")\n')
    exit(2)
    
parser = argparse.ArgumentParser(description = 'Convert html FamilyTreeDNA tables to tsvs (19 Dec 2016)', add_help = False, usage = 'parse_ftdna_projects.py <path> <table> <date>')
parser.add_argument('p', metavar = '<STR>', type = str, help = 'Path to html files')
parser.add_argument('t', metavar = '<STR>', type = str, help = 'Project table')
parser.add_argument('d', metavar = '<STR>', type = str, help = 'Date data was collected')

# extract arguments from the command line
try:
  parser.error = parser.exit
  args = parser.parse_args()
except SystemExit:
  parser.print_help()
  exit(2)

# path = '/home/genovese/Documents/ancestry/ydna/'; date = '20160729'
projects = pandas.read_csv(args.t, sep = '\t', header = None)[1]
projects = projects.str.replace(' ', '%20')
projects = projects[projects.notnull()]

# convert html files to tsv files
fail = list()
for proj in projects:
  try:
    print(args.p + os.sep + proj + '.' + args.d + '.html')
    html = open(args.p + os.sep + proj + '.' + args.d + '.html', 'r', encoding='utf-8').read()
    a = re.compile('<table cellpadding').search(html).span()[0]
    b = re.compile('/table>').search(html).span()[1]
    dfs = pandas.read_html(html[a:b])
    dfs[0].to_csv(args.p + os.sep + proj + '.' + args.d + '.tsv', sep = '\t', na_rep = 'NA', float_format = '%d', index = False)
  except:
    fail += [proj]
sys.stderr.write(str(fail))

# load tsv files
dfs = list()
fail = list()
for proj in projects:
  if os.path.isfile(args.p + os.sep + proj + '.' + args.d + '.tsv'):
    df = pandas.read_csv(args.p + os.sep + proj + '.' + args.d + '.tsv', sep = '\t', dtype = object)
    idx = df['Country'].isnull() & df['Haplogroup'].isnull()
    df.drop(df.index[idx], axis = 0, inplace = True)
    df['Project'] = proj
    df.set_index('Kit Number', drop = False, inplace = True)
    dfs.append(df)
  else:
    fail += [proj]
sys.stderr.write(str(fail))

# join tsv files in single table
df = pandas.concat(dfs)
info = ['Project', 'Row Number', 'Kit Number', 'Name', 'Paternal Ancestor Name', 'Country', 'Haplogroup']
strs = ['DYS393', 'DYS390', 'DYS19', 'DYS391', 'DYS385', 'DYS426', 'DYS388', 'DYS439', 'DYS389i', 'DYS392', 'DYS389ii', 'DYS458', 'DYS459', 'DYS455', 'DYS454', 'DYS447', 'DYS437', 'DYS448', 'DYS449', 'DYS464', 'DYS460', 'Y-GATA-H4', 'YCAII', 'DYS456', 'DYS607', 'DYS576', 'DYS570', 'CDY', 'DYS442', 'DYS438', 'DYS531', 'DYS578', 'DYF395S1', 'DYS590', 'DYS537', 'DYS641', 'DYS472', 'DYF406S1', 'DYS511', 'DYS425', 'DYS413', 'DYS557', 'DYS594', 'DYS436', 'DYS490', 'DYS534', 'DYS450', 'DYS444', 'DYS481', 'DYS520', 'DYS446', 'DYS617', 'DYS568', 'DYS487', 'DYS572', 'DYS640', 'DYS492', 'DYS565', 'DYS710', 'DYS485', 'DYS632', 'DYS495', 'DYS540', 'DYS714', 'DYS716', 'DYS717', 'DYS505', 'DYS556', 'DYS549', 'DYS589', 'DYS522', 'DYS494', 'DYS533', 'DYS636', 'DYS575', 'DYS638', 'DYS462', 'DYS452', 'DYS445', 'Y-GATA-A10', 'DYS463', 'DYS441', 'Y-GGAAT-1B07', 'DYS525', 'DYS712', 'DYS593', 'DYS650', 'DYS532', 'DYS715', 'DYS504', 'DYS513', 'DYS561', 'DYS552', 'DYS726', 'DYS635', 'DYS587', 'DYS643', 'DYS497', 'DYS510', 'DYS434', 'DYS461', 'DYS435']
df[info + strs].to_csv('ftdna.' + args.d + '.tsv.gz', sep = '\t', na_rep = 'NA', float_format = '%d', index = False, compression = 'gzip')
info = ['Kit Number', 'Country', 'Haplogroup']
df[info + strs].drop_duplicates().sort_index().to_csv('ftdna.lite.' + args.d + '.tsv.gz', sep = '\t', na_rep = 'NA', float_format = '%d', index = False, compression = 'gzip')
