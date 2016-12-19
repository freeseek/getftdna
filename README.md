getftdna
========

This repositor contains a set of bash and python scripts used to download FamilyTreeDNA Y projects

get_ftdna_projects.sh
---------------------

Download the list of all Y-DNA projects and then download each single project separately.

To generate the list of available projects, you will need a FamilyTreeDNA Kit No. or Username and a FamilyTreeDNA Password.

As this script will connect to www.familytreedna.com thousands of times and ultimately download ~2GB of data, it is advised to run it overnight as FamilyTreeDNA server exhibits problems during day. With a fast connection, at the right time of the day, it can take as little as five hours for the script to run.

parse_ftdna_projects.py
-----------------------

This script will convert the html output from the previous script to tab delimited format tables and subsequently it will merge all files to a single table containing all FamilyTreeDNA Y chromosome data publicly available. A second non-redundant table with one chromosome per line will also be generated. The two tables take compressed ~13MB and ~5MB and include all of the Y chromosome data that can be downloaded from FamilyTreeDNA, including ~150K different Y chromosome haplotypes.

get_yfull_tree.py
-----------------

Download the full Y chromosome tree from http://yfull.com/tree in the form of a dictionary where every node is a key, and the values for each correspond to the nodes and leaves downstream of that key. The tree is then outputted into a yfull.txt file easily loadable with the python command json.load().

make_ftdna_plots.py
-------------------

Open the Y chromosome table with all FamilyTreeDNA Y chromosome data publicly available and generate a couple of figures showing the distance between the two Y chromosomes from the blog post and all other Y chromosomes. It requires the YFull YTree to run.

Examples
========

Download all FamilyTreeDNA projects as individual html files
------------------------------------------------------------

bash get_ftdna_projects.sh USERNAME PASSWORD

Merge all FamilyTreeDNA projects into a single table
----------------------------------------------------

python3 parse_ftdna_projects.py ftdna projects4.$(date +%Y%m%d).txt $(date +%Y%m%d)

Download the whole YFull YTree
------------------------------

python3 get_yfull_tree.py

Generate the plots for the blog post
------------------------------------

python3 make_ftdna_plots.py ftdna.lite.$(date +%Y%m%d).tsv.gz yfull.txt

Support
=======

To learn more about the data being retrieved by this tool, see <a href="http://apol1.blogspot.com/2016/12/what-can-we-learn-from-one-y-chromosome.html">here</a>

This set of programs is still in beta phase, and bugs are still present. Features will be added on request. It is provided as is

Current version was updated on December 19th 2016

Send questions, suggestions, or feature requests to giulio.genovese@gmail.com
