#!/bin/bash
#
#  get_ftdna_projects.sh - download Y chromosome FamilyTreeDNA projects
#  Copyright (C) 2016 Giulio Genovese
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Written by Giulio Genovese <giulio.genovese@gmail.com>
#

# input FamilyTreeDNA username
if [ $# -lt 1 ]; then
  echo -n "Insert FamilyTreeDNA Kit No. or Username: "
  read username
else
  username="$1"
fi

# input FamilyTreeDNA password
if [ $# -lt 2 ]; then
  echo -n "Insert FamilyTreeDNA Password: "
  read -s password
else
  password="$2"
fi

# retrieve variables __VIEWSTATE and __EVENTVALIDATION
url="https://www.familytreedna.com/my/default.aspx"
read v e <<< $(wget -qO- "$url" | grep "\"__VIEWSTATE\"\|\"__EVENTVALIDATION\"" |
  sed -e 's/^.*value="\(.*\)".*$/\1/g' -e 's/+/%2B/g' -e 's/\//%2F/g' -e 's/=/%3D/g')

# check whether variables __VIEWSTATE and __EVENTVALIDATION correctly retrieved
if [ -z $v ] || [ -z $e ]; then
  echo "Failed to retrieve variables __VIEWSTATE or __EVENTVALIDATION"
  exit -1
else
  echo "__VIEWSTATE variable retrieved: $v"
  echo "__EVENTVALIDATION variable retrieved: $e"
fi

# retrieve FTDNAAuth cookie from FamilyTreeDNA
url="https://www.familytreedna.com/login.aspx"
c="ctl00%24MainContent%24PublicLogin%24LoginView1%24Login1%24"
data="__VIEWSTATE=${v}&__EVENTVALIDATION=${e}&${c}UserName=${username}&${c}Password=${password}&${c}LoginButton=Sign+In"
read FTDNAAuth <<< $(wget -qSO- "$url" --max-redirect 0 --post-data "$data" 2>&1 |
  grep ".FTDNAAuth" | sed 's/^.*.FTDNAAuth=\([0-9A-Z]*\);.*$/\1/g')

# check whether FTDNAAuth cookie correctly retrieved
if [ -z $FTDNAAuth ]; then
  echo "Failed to retrieve FTDNAAuth cookie"
  exit -1
else
  echo "FTDNAAuth cookie retrieved: $FTDNAAuth"
fi

date="$(date +%Y%m%d)"

# download list of FamilyTreeDNA projects initials
wget -qO- "https://www.familytreedna.com/my/group-join.aspx" --post-data ".FTDNAAuth=$FTDNAAuth" |
  grep -o "\"/my/group-join.aspx?let=.*&amp;projecttype=.*\"" | tr -d '"' | sed 's/\&amp;/\&/g' | cut -d? -f2 > projects1.$date.txt

# download list of FamilyTreeDNA projects
for proj in $(cat projects1.$date.txt); do
  wget -qO- "https://www.familytreedna.com/my/group-join.aspx?$proj" --post-data ".FTDNAAuth=$FTDNAAuth" |
    grep -o "\"/my/group-join.aspx?group=.*\"" | tr -d '"' | cut -d= -f2 | uniq |
    awk -v proj="$proj" '{print proj"\t"$0}'
done > projects2.$date.txt

# download list of FamilyTreeDNA projects URL names
for proj in $(cut -f2 projects2.$date.txt); do
  wget -qO- "https://www.familytreedna.com/my/group-join.aspx?group=$proj" --post-data ".FTDNAAuth=$FTDNAAuth" |
    grep -o ">www.familytreedna.com\/groups\/.*<" | tr -d '<>' | cut -d/ -f3 |
    awk -v proj="$proj" '{print proj"\t"$0}'
done > projects3.$date.txt

# download list of FamilyTreeDNA projects Y-DNA URL names
for proj in $(cut -f2 projects3.$date.txt); do
  wget -qO- "https://www.familytreedna.com/groups/$proj/dna-results" |
    grep -o "\"/public/.*?iframe=yresults\"" | tr -d '"' | cut -d? -f1 | cut -d/ -f3 |
    awk -v proj="$proj" '{print proj"\t"$0}'
done | uniq | sed -e 's/\&#242;/ò/g' -e 's/\&amp;/\&/g' -e 's/&#180;/´/g' -e 's/ $//' > projects4.$date.txt

# download Y-DNA projects one by one
mkdir -p ftdna
for proj in $(cut -f2 projects4.$date.txt | grep -v ^$ | sed 's/ /%20/g'); do
  proj="${proj//\%20/ }"
  url="https://www.familytreedna.com/public/$proj?iframe=yresults"

  # download first page
  for i in {1..3}; do
    # download first page
    wget -qO "ftdna/$proj.$date.html" "$url"
    if [ ! -s "ftdna/$proj.$date.html" ]; then sleep 10; continue; fi
    break
  done

  # retrieve number of pages
  read pages <<< $(cat "ftdna/$proj.$date.html" | grep "__doPostBack" | tail -n1 | tr ' ' '\n' | tail -n1 | tr -d '\r')

  # download all pages (if multiple)
  if [ ! -z $pages ]; then
    read v e <<< $(cat "ftdna/$proj.$date.html" | grep "\"__VIEWSTATE\"\|\"__EVENTVALIDATION\"" |
      sed -e 's/^.*value="\(.*\)".*$/\1/g' -e 's/+/%2B/g' -e 's/\//%2F/g' -e 's/=/%3D/g')
    data="__VIEWSTATE=${v}&__EVENTVALIDATION=${e}&ctl00%24MainContent%24classic1%24tbPageSize=$((500 * pages))"
    for i in {1..3}; do
      wget -qO "ftdna/$proj.$date.html" --post-data "$data" "$url"
      if [ ! -s "ftdna/$proj.$date.html" ]; then sleep 10; continue; fi
      break
    done
  fi
done
