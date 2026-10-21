import mesa_reader as mr
import numpy as np


history = mr.MesaData("LOGS/history.data")
print(type(history))

# for exhaustion, look at the center_{nuc} field for when the species
# goes to 1.e-3.

threshold = 1.e-3

last_idx = 0

exhaustion = {}

stages = ["h1", "he4", "c12", "o16", "si28"]

for nuc in stages:

    cnuc = getattr(history, f"center_{nuc}")

    # index 0 is the start of the simulation
    for i in range(last_idx, len(cnuc)):
        if cnuc[i] < threshold:
            exhaustion[nuc] = i
            last_idx = i
            break

print("profile index where core exhaustion occurs: ")
for k, v in exhaustion.items():
    print(f"  {k:4} : {v}")
print("")

# for core burning, we will mark the abundance at the end of the
# previous nuclei's exhaustion and then look for the point when we
# drop to 90% of that.  This will give a rough estimate.

initial_core_values = {"h1": history.center_h1[0]}  # initial core H abundance

for n in range(1, len(stages)):
    current_nuc = stages[n]
    previous_nuc = stages[n-1]

    initial_core_values[current_nuc] = getattr(history, f"center_{current_nuc}")[exhaustion[previous_nuc]]

print("initial core values (at start of burning): ")
for k, v in initial_core_values.items():
    print(f"  {k:4} : {v}")
print("")

core_burning = {}

# now we look for an index > exhaustion of the previous element where
# the core abundance drops to 0.9 of the initial abundance
for n, nuc in enumerate(stages):

    cnuc = getattr(history, f"center_{nuc}")

    # start searching at the point where the previous burning
    # stage ended.
    if nuc == "h1":
        start = 0
    else:
        start = exhaustion[stages[n-1]]

    for i in range(start, len(cnuc)):
        if cnuc[i] < 0.9 * initial_core_values[nuc]:
            core_burning[nuc] = i
            break

print("profile index where we are in core burning: ")
for k, v in core_burning.items():
    print(f"  {k:4} : {v}")
print("")


# find some key times just before collapse

age_in_minutes = history.star_age_min

star_age = np.max(age_in_minutes)

# times (in minutes) at which we are interested in setting the profile
pre_collapse_times_min = [1, 5, 10, 20, 30]

key_times = {}

for it, time in enumerate(pre_collapse_times_min):

    for i in range(len(age_in_minutes)):

        if (star_age - age_in_minutes[i]) < pre_collapse_times_min[it]:
            key_times[time] = i
            break

print("some key profile indices just before collapse:")
for k, v in reversed(key_times.items()):
    print(f"  {k:2} minutes before collapse : {v}")
