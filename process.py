import json
import re

# + INFINITY denotes edges that cannot be taken. -INFINITY denotes edges that
# must be taken.
INFINITY = 10**4

# SPACE_PENALTY is the penalty for starting a new word. Setting this to one
# optimizes for true length.
SPACE_PENALTY = 1

# get champs.json using simple riot api call.
with open("champs.json") as f:
	champ_set = {re.sub(r'\W+', '', champ["name"]).lower()
					for champ in json.load(f)["data"].values()}

# remove all champions which are substrings of other champions.
removed = set()
for champ_a in champ_set:
	for champ_b in champ_set:
		if champ_a in champ_b and champ_a != champ_b:
			removed.add(champ_a)

champ_set = champ_set - removed

# slow because it's not worth optimizing this. Computes the overlap between
# the end of champ_a and the start of champ_b
def compute_overlap(champ_a, champ_b):
	for i in range(len(champ_a)):
		if champ_a[i:] == champ_b[:len(champ_a) - i]:
			return len(champ_a) - i
	return 0

# using a dictionary as a graph (because I'm lazy). Each key is a champ name,
# and maps to another dictionary, which maps champ_name to edge length. Edge
# length is -(size of overlap) if an overlap exists, or SPACE_PENALTY if no
# overlap exists.

graph = {}
for champ_a in champ_set:
	graph[champ_a] = {}
	for champ_b in champ_set:
		if (champ_a == champ_b):
			continue
		overlap = compute_overlap(champ_a, champ_b)
		if overlap > 0:
			graph[champ_a][champ_b] = -overlap
		else:
			graph[champ_a][champ_b] = SPACE_PENALTY

# convert asymmetric TSP probem to a symmetric problem.
# each champion has a two nodes in the symmetric graph (one input, one output).
# The edges between these nodes cost -INFINITY and therefore must be taken.
# (Everything is scaled up by INFINITY to keep edge weights positive).
sym_graph = {}
for champ in champ_set:
	sym_graph[champ] = {}
	sym_graph[champ + "'"] = {}

for champ_a in champ_set:
	sym_graph[champ_a][champ_a + "'"] = 0
	sym_graph[champ_a][champ_a] = 0
	sym_graph[champ_a + "'"][champ_a] = 0
	sym_graph[champ_a + "'"][champ_a + "'"] = 0
	for champ_b in champ_set:
		if (champ_b == champ_a):
			continue
		sym_graph[champ_a][champ_b + "'"] = INFINITY + graph[champ_a][champ_b]
		sym_graph[champ_b + "'"][champ_a] = INFINITY + graph[champ_a][champ_b]
		sym_graph[champ_a][champ_b] = 2 * INFINITY
		sym_graph[champ_a + "'"][champ_b + "'"] = 2 * INFINITY

# map each champ in champ_set to an int
indexed_champs = list(champ_set)

# write out the mapping
with open("map.txt", "w") as map_file:
	for i in range(len(indexed_champs)):
		map_file.write(str(i) + " " + str(indexed_champs[i]) + "\n")

# print out symmetric TSP problem in TSPLIB format
with open("lol.tsplib", "w") as tsp_file:
	tsp_file.write("NAME : LOL_CHAMPS\n")
	tsp_file.write("TYPE : TSP\n")
	tsp_file.write("DIMENSION : " + str(len(champ_set) * 2) + "\n")
	tsp_file.write("EDGE_WEIGHT_TYPE : EXPLICIT\n")
	tsp_file.write("EDGE_WEIGHT_FORMAT : FULL_MATRIX\n")
	tsp_file.write("EDGE_DATA_FORMAT : EDGE_LIST\n")
	tsp_file.write("EDGE_WEIGHT_SECTION \n")
	for i in range(len(champ_set)):
		for j in range(len(champ_set)):
			tsp_file.write(str(sym_graph[indexed_champs[i]][indexed_champs[j]]) + " ")
		for j in range(len(champ_set)):
			tsp_file.write(str(sym_graph[indexed_champs[i]][indexed_champs[j] + "'"]) + " ")
	for i in range(len(champ_set)):
		for j in range(len(champ_set)):
			tsp_file.write(str(sym_graph[indexed_champs[i] + "'"][indexed_champs[j]]) + " ")
		for j in range(len(champ_set)):
			tsp_file.write(str(sym_graph[indexed_champs[i] + "'"][indexed_champs[j] + "'"]) + " ")
