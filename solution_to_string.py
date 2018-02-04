def get_int(file_name):
	with open(file_name) as f:
		for line in f:
			for val in line.split():
				yield int(val)

indexed_champs = []
with open("map.txt") as f:
	for line in f:
		indexed_champs.append(line.split()[1])

SOL_FILE = "sol.txt"

def compute_overlap(champ_a, champ_b):
	for i in range(len(champ_a)):
		if champ_a[i:] == champ_b[:len(champ_a) - i]:
			return len(champ_a) - i
	return 0

num_champs = len(indexed_champs)

sol_int_generator = get_int(SOL_FILE)

# remove first two specifiers
next(sol_int_generator)
next(sol_int_generator)
series = []
for i in range(2 * num_champs):
	prev, _next, cost = next(sol_int_generator), next(sol_int_generator), next(sol_int_generator)
	if cost == 0:
		continue
	series.append(prev % num_champs)

def compute_sol_str(series):
	sol_str = ""
	for i in range(len(series)):
		prev = i - 1
		_next = i
		last = indexed_champs[series[prev]]
		curr = indexed_champs[series[_next]]
		overlap = compute_overlap(last, curr)
		if (overlap != 0):
			sol_str += curr[overlap:]
		else:
			sol_str += " " + curr
	return sol_str

forward = compute_sol_str(series)
series.reverse()
backward = compute_sol_str(series)
sol = forward if len(forward) < len(backward) else backward

cap_indices = set()
for champ in indexed_champs:
	cap_indices.add(sol.find(champ))

sol = " ".join(sorted("".join([str.upper(sol[i]) if i in cap_indices else sol[i] for i in range(len(sol))]).split(), key=len, reverse=True))

print sol
print "Total non-space characters:", len(sol.replace(" ", ""))
print "Total number of words:", len([el for el in sol.split(" ") if el != ""])
