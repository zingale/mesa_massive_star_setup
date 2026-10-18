import matplotlib.pyplot as plt

import numpy as np

import mkipp2

logs_dirs = ["LOGS"]

# first the default plot style

a = mkipp2.KippArgs(xaxis="star_age",
                    time_units="yr",
                    identifier="net_nuclear_energy",
                    logs_dirs=logs_dirs)
mkipp2.kipp_plot(a, decorate_plot=True,
                 core_masses=["He", "CO", "ONe", "Fe"])


# next -- time to collapse

histories = [mkipp2.mesa_data.MesaData(f"{log_dir}/history.data",
                                     read_data_cols=["star_age"])
             for log_dir in logs_dirs]
max_age = max(max(history.get("star_age")) for history in histories)
min_age = min(min(history.get("star_age")) for history in histories)
time_offset = 1.e-5  # years; the final model is plotted at log10(time_offset)


def transform_age(age):
    return np.log10((max_age - age) + time_offset)


fig, ax = plt.subplots()

a = mkipp2.KippArgs(xaxis="star_age",
                    time_units="yr",
                    identifier="net_nuclear_energy",
                    logs_dirs=logs_dirs,
                    function_on_xaxis=transform_age)
kipp_plot = mkipp2.kipp_plot(a, axis=ax,
                             core_masses=["He", "CO", "ONe", "Fe"],
                             decorate_plot=False, save_file=False)
# Use the history extent explicitly, without Matplotlib's automatic margins.
ax.set_xlim(np.log10(time_offset), transform_age(min_age))

cbar = fig.colorbar(kipp_plot.contour_plot, pad=0.05)
cbar.set_label(r"$\log_{10} |\epsilon_\mathrm{net}|$")
ax.set_xlabel(r"$\log_{10} (t_f-t)$ [yrs]")
ax.set_ylabel("Mass (solar masses)")

fig.set_size_inches(9, 7)
fig.tight_layout()
fig.savefig("Kippenhahn-collapse.png")



# finally, Si mass fraction

fig, ax = plt.subplots()

a = mkipp2.KippArgs(xaxis="star_age",
                    time_units="yr",
                    identifier="si28",
                    logs_dirs=logs_dirs,
                    function_on_xaxis=transform_age)
kipp_plot = mkipp2.kipp_plot(a, axis=ax,
                             levels=np.arange(-6, 0.5, 0.5),
                             core_masses=["He", "CO", "ONe", "Fe"],
                             decorate_plot=False, save_file=False)
# Use the history extent explicitly, without Matplotlib's automatic margins.
ax.set_xlim(np.log10(time_offset), transform_age(min_age))

cbar = fig.colorbar(kipp_plot.contour_plot, pad=0.05)
cbar.set_label(r"$\log_{10} (X({}^{28}\mathrm{Si}))$")
ax.set_xlabel(r"$\log_{10} (t_f-t)$ [yrs]")
ax.set_ylabel("Mass (solar masses)")

fig.set_size_inches(9, 7)
fig.tight_layout()
fig.savefig("Kippenhahn-si.png")


