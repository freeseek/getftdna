#!/usr/bin/env python3
"""
   get_yfull_tree.py - extract Y-chromosome tree from yfull.com
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

import sys, re, xml, json

try:
  import requests
except ImportError:
  sys.stderr.write('You need to install the requests module first\n')
  sys.stderr.write('(run this in your terminal: "python3 -m pip install requests" or "python3 -m pip install --user requests")\n')
  exit(2)

# extract name from YFull XML code for a node
def get_text(li):
  return li[0][0].text if list(li[0]) else li[0].text

# extract tree from YFull XML code for a node
def get_tree(li, l=4):
  result = dict()
  if len(li) > l:
    for child in li[len(li)-1]:
      if len(child) > l:
        result.update(get_tree(child, l))
    result[get_text(li)] = [get_text(child) for child in li[len(li)-1]]
  return result

# return list of all leaves under a node
def get_set(tree, key):
  result = {key}
  if key in tree:
    for subkey in tree[key]:
      result = result.union(get_set(tree, subkey))
  return result

# download main lineages tree
url = 'http://yfull.com/tree'
r = requests.get(url)
text = re.findall(r'<div><ul id="tree" class="tree">.*?</div>', r.text, re.DOTALL | re.MULTILINE)[0]
li = xml.etree.ElementTree.fromstring(text)[0][0]
tree = get_tree(li, 1)
leaves = get_set(tree, 'ROOT (Y-Chromosome "Adam")') - tree.keys()

# download each lineage's subtree
for leaf in leaves:
  url = 'http://yfull.com/tree/' + leaf
  r = requests.get(url)
  text = re.findall(r'<div><ul id="tree" class="tree">.*?</div>', r.text, re.DOTALL | re.MULTILINE)[0]
  li = xml.etree.ElementTree.fromstring(text)[0][0]
  tree.update(get_tree(li))

# dump tree to file
with open('yfull.txt', 'w') as outfile:
  json.dump(tree, outfile)
