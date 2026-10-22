import re
from pathlib import Path
import shutil

import mesa_reader as mr
import numpy as np
import matplotlib.pyplot as plt


class ImportantProfiles:
    """a container to hold information about important profiles in the
    MESA simulation."""

    def __init__(self, stages):
        self.stages = stages
        self.exhaustion = {}
        self.initial_core_values = {}
        self.core_burning = {}
        self.key_times = {}


def parse_profile_index(log_dir="LOGS/"):
    """Open profiles.index and make a mapping between MESA model step
    and the profile index.

    """

    profile_indices = {}

    with open(f"{log_dir}/profiles.index") as pf:

        for i, line in enumerate(pf):
            # first line is a header
            if i == 0:
                continue

            model, _, index = line.split()

            profile_indices[int(model)] = int(index)

    return profile_indices


def find_closest_profile(index, profile_numbers):
    """Given a MESA model index / step, find the nearest match
    to the stored profiles, enumerated in profile_numbers"""

    closest = min(profile_numbers, key=lambda x: abs(x - index))
    return closest


def get_nuclei(model, use_log=True):

    # the species may be written as log_he4, etc. in the
    # "bulk names" section of the header
    species_re = re.compile(r"log_([a-z]+[\d]+)")

    # sometimes they may be without the log_.  In this case,
    # restrict the element name to 1-2 characters
    species_nolog_re = re.compile(r"^([a-z]{1,2}[\d]+)$")

    nuc_re = species_re if use_log else species_nolog_re

    nuclei = []
    for field in model.bulk_names:
        if g := nuc_re.match(field):
            nuclei.append(g.group(1))

    # sometimes MESA uses "neut" for neutrons
    if "neut" in model.bulk_names:
        nuclei.append("neut")

    # sometimes MESA uses "prot" for photodistintegration protons
    if "prot" in model.bulk_names:
        nuclei.append("prot")

    return nuclei


def find_important_profiles(log_dir="LOGS/"):

    history = mr.MesaData(f"{log_dir}/history.data")

    stages = ["h1", "he4", "c12", "o16", "si28"]

    c = ImportantProfiles(stages)

    # for exhaustion, look at the center_{nuc} field for when the species
    # goes to 1.e-3.

    threshold = 1.e-3

    last_idx = 0

    for nuc in stages:

        cnuc = getattr(history, f"center_{nuc}")

        # index 0 is the start of the simulation
        for i in range(last_idx, len(cnuc)):
            if cnuc[i] < threshold:
                c.exhaustion[nuc] = i
                last_idx = i
                break

    # for core burning, we will mark the abundance at the end of the
    # previous nuclei's exhaustion and then look for the point when we
    # drop to 90% of that.  This will give a rough estimate.

    c.initial_core_values = {"h1": history.center_h1[0]}  # initial core H abundance

    for n in range(1, len(stages)):
        current_nuc = stages[n]
        previous_nuc = stages[n-1]

        c.initial_core_values[current_nuc] = getattr(history, f"center_{current_nuc}")[c.exhaustion[previous_nuc]]

    # now we look for an index > exhaustion of the previous element where
    # the core abundance drops to 0.9 of the initial abundance
    for n, nuc in enumerate(stages):

        cnuc = getattr(history, f"center_{nuc}")

        # start searching at the point where the previous burning
        # stage ended.
        if nuc == "h1":
            start = 0
        else:
            start = c.exhaustion[stages[n-1]]

        for i in range(start, len(cnuc)):
            if cnuc[i] < 0.9 * c.initial_core_values[nuc]:
                c.core_burning[nuc] = i
                break

    # find some key times just before collapse

    age_in_minutes = history.star_age_min

    star_age = np.max(age_in_minutes)

    # times (in minutes) at which we are interested in setting the profile
    pre_collapse_times_min = [1, 5, 10, 20, 30]

    for it, time in enumerate(pre_collapse_times_min):

        for i in range(len(age_in_minutes)):

            if (star_age - age_in_minutes[i]) < pre_collapse_times_min[it]:
                c.key_times[time] = i
                break

    return c


def plot_structure(profile):

    model = mr.MesaData(profile)

    fig, (axt, axb) = plt.subplots(2, 1, height_ratios=[1, 2],
                                   layout="constrained", figsize=(6, 10))

    r = model.radius
    rho = 10.0**model.logRho
    T = 10.0**model.logT
    ye = model.ye

    l1 = axt.plot(r, rho, label=r"$\rho$")
    l2 = axt.plot(r, T, label=r"$T$")

    axt.set_xscale("log")
    axt.set_yscale("log")

    #axt.set_xlabel("r [cm]")
    axt.set_ylabel(r"$\rho~[\rm{g/cm^3}]$, $T~[K]$")

    axt.grid(color="b", alpha=0.5, ls=":")

    axt.set_ylim(None, 1.e10)

    ax2 = axt.twinx()

    ax2.set_ylabel(r"$Y_e$")
    l3 = ax2.plot(r, ye, color="C2", label="$Y_e$")

    lns = l1 + l2 + l3
    labs = [l.get_label() for l in lns]
    axt.legend(lns, labs, frameon=False, loc="best", fontsize="small")

    # get the nuclei from the model file
    nuclei = get_nuclei(model)

    axt.margins(0.0)

    threshold = 0.01
    skip_value = 5.e-4

    high_color_index = 0
    low_color_index = 0
    trace_color_index = 0

    for nuc in nuclei:
        X = getattr(model, f"{nuc}")
        Xmax = X.max()

        if Xmax < skip_value:
            continue

        if Xmax > threshold:
            if Xmax > 0.25:
                lw = 2.5
                ls = "-"
                color = f"C{high_color_index}"
                high_color_index += 1
            else:
                lw = 1.5
                ls = "--"
                color = f"C{low_color_index}"
                low_color_index += 1
        else:
            lw = 1
            ls = ":"
            color = f"C{trace_color_index}"
            trace_color_index += 1

        axb.plot(r, X, label=f"{nuc!s}", lw=lw, ls=ls, color=color)

    axb.set_xscale("log")
    axb.set_yscale("log")

    axb.set_xlabel(r"r [$R_\odot$]")
    axb.set_ylabel("mass fraction")

    axb.margins(0)
    axb.set_ylim(skip_value, 1.1)

    axb.grid(color="b", alpha=0.5, ls=":")
    axb.legend(frameon=True, edgecolor="w",
              ncol=2, framealpha=0.5, fontsize="small")

    return fig


if __name__ == "__main__":

    log_dir = Path("LOGS")

    # get the mapping between MESA step number and stored profile
    profile_mapping = parse_profile_index()

    # look at the history and find the important points in the
    # simulation corresponding to major burning stages
    pinfo = find_important_profiles()

    print("profile index where core exhaustion occurs: ")
    for k, v in pinfo.exhaustion.items():
        print(f"  {k:4} : {v}")
    print("")

    print("initial core values (at start of burning): ")
    for k, v in pinfo.initial_core_values.items():
        print(f"  {k:4} : {v}")
    print("")

    print("profile index where we are in core burning: ")
    for k, v in pinfo.core_burning.items():
        print(f"  {k:4} : {v}")
    print("")

    print("some key profile indices just before collapse:")
    for k, v in reversed(pinfo.key_times.items()):
        print(f"  {k:2} minutes before collapse : {v}")

    # plot profiles
    groups = (("exhaustion", pinfo.exhaustion),
              ("core_burning", pinfo.core_burning),
              ("key_times", pinfo.key_times))

    # copy the interesting profiles to a separate directory
    odir = Path("interesting_profiles")
    odir.mkdir(exist_ok=True)

    for name, collection in groups:
        for key in collection:

            # find the nearest saved profile to the model identified in
            # the history.  Then map the MESA step to the profile index.

            idx = find_closest_profile(collection[key],
                                       list(profile_mapping.keys()))
        
            pf = log_dir / f"profile{profile_mapping[idx]}.data"

            fig = plot_structure(pf)

            if key in pinfo.stages:
                # the key is a nucleus
                fig.suptitle(f"{key.capitalize()} {name.replace('_', ' ')}")
                fig.savefig(f"{name}_{key}.png")

                # for the copy
                new_file_name = odir / f"profile_{name}_{key}.data"

            else:
                # the key is a time before collapse (in minutes)
                fig.suptitle(f"{key} minutes before collapse...")
                fig.savefig(f"collapse_in_{key}_minutes.png")

                # for the copy
                new_file_name = odir / f"profile_collapse_in_{key}_minutes.data"

            shutil.copy(pf, new_file_name)
