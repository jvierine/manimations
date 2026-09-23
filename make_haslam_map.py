"""Generate the Haslam 408 MHz opening visual and its HDF5 data product.

Run with:
    conda run -n base python make_haslam_map.py
"""

from pathlib import Path

import h5py
import healpy as hp
import matplotlib.pyplot as plt
import numpy as np
from pygdsm import HaslamSkyModel


OUTPUT_DIR = Path(__file__).resolve().parent / "assets"
PNG_PATH = OUTPUT_DIR / "haslam_408mhz.png"
H5_PATH = OUTPUT_DIR / "haslam_408mhz.h5"
BACKGROUND = "#07111F"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    frequency_mhz = 408.0
    model = HaslamSkyModel(freq_unit="MHz", include_cmb=False)
    temperature_k = np.asarray(model.generate(frequency_mhz), dtype=np.float32)

    with h5py.File(H5_PATH, "w") as h5:
        dataset = h5.create_dataset(
            "brightness_temperature_k",
            data=temperature_k,
            compression="gzip",
            compression_opts=4,
            shuffle=True,
        )
        dataset.attrs["unit"] = "K"
        dataset.attrs["healpix_ordering"] = "RING"
        dataset.attrs["coordinate_system"] = "Galactic"
        h5.attrs["frequency_mhz"] = frequency_mhz
        h5.attrs["nside"] = model.nside
        h5.attrs["source_model"] = "pyGDSM HaslamSkyModel"
        h5.attrs["include_cmb"] = False
        h5.attrs["script"] = Path(__file__).name

    plt.close("all")
    hp.mollview(
        temperature_k,
        coord="G",
        nest=False,
        norm="log",
        min=8.0,
        max=5000.0,
        cmap="inferno",
        title="",
        unit="Brightness temperature [K]",
        bgcolor=BACKGROUND,
        badcolor=BACKGROUND,
        xsize=1800,
        cbar=True,
        notext=True,
    )
    figure = plt.gcf()
    figure.set_size_inches(16, 7.6)
    figure.patch.set_facecolor(BACKGROUND)
    hp.graticule(dpar=30, dmer=30, color="#C5D2DF", alpha=0.30, linewidth=0.7)

    for axis in figure.axes:
        axis.set_facecolor(BACKGROUND)
        axis.tick_params(colors="#E8EEF5", labelsize=11)
        for spine in axis.spines.values():
            spine.set_edgecolor("#9DB0C3")
        for item in axis.texts:
            item.set_color("#F3F7FA")
        axis.xaxis.label.set_color("#F3F7FA")
        axis.yaxis.label.set_color("#F3F7FA")

    figure.text(
        0.5,
        0.025,
        "Galactic coordinates",
        ha="center",
        color="#C5D2DF",
        fontsize=14,
    )
    figure.savefig(
        PNG_PATH,
        dpi=150,
        facecolor=BACKGROUND,
        bbox_inches=None,
        pad_inches=0,
    )
    plt.close(figure)

    print(f"wrote {PNG_PATH}")
    print(f"wrote {H5_PATH}")
    print(
        "temperature range: "
        f"{float(np.nanmin(temperature_k)):.3f} to "
        f"{float(np.nanmax(temperature_k)):.3f} K"
    )


if __name__ == "__main__":
    main()
