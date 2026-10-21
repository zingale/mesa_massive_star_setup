import numpy as np

import mkipp2

logs_dirs = ["LOGS"]

# first the default plot style

k = mkipp2.KippenhahnDiagram(xaxis="star_age",
                             time_units="yr",
                             identifier="net_nuclear_energy",
                             logs_dirs=logs_dirs)
k.plot(core_masses=["He", "CO", "ONe", "Fe"],
       size=(9, 7))


# next -- time to collapse

k = mkipp2.KippenhahnDiagram(xaxis="collapse",
                             time_units="yr",
                             identifier="net_nuclear_energy",
                             logs_dirs=logs_dirs)
k.plot(core_masses=["He", "CO", "ONe", "Fe"],
       density_contours=[1.e2, 1.e4, 1.e6, 1.e8],
       save_filename="Kippenhahn-collapse.png",
       size=(9, 7))


# instead, burning regions

k = mkipp2.KippenhahnDiagram(xaxis="collapse",
                             time_units="yr",
                             identifier="net_nuclear_energy",
                             load_profiles=True,
                             logs_dirs=logs_dirs)
k.plot_burning_regions(core_masses=["He", "CO", "ONe", "Fe"],
                       density_contours=[1.e2, 1.e4, 1.e6, 1.e8],
                       hybrid_mode=True,
                       save_filename="Kippenhahn-burning-regions.png",
                       size=(9, 7))


# finally, Si mass fraction

k = mkipp2.KippenhahnDiagram(xaxis="collapse",
                             time_units="yr",
                             identifier="si28",
                             logs_dirs=logs_dirs)
k.plot(levels=np.arange(-6, 0.5, 0.5),
       core_masses=["He", "CO", "ONe", "Fe"],
       density_contours=[1.e2, 1.e4, 1.e6, 1.e8],
       save_filename="Kippenhahn-si.png",
       size=(9, 7))



