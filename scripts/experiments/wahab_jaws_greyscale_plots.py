"""
Plot things from the segmentation of Wahab's jaws.

Won't work on other jaws - this script extracts metadata from Wahab's spreadsheet
from the filepath (the files are named ak_n.tif; we use the value of n to find
which fish we're dealing with).
"""

import pathlib
import argparse

import tifffile
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

from fishlib.inference import read
from fishlib.visualisation import images_3d


def _all_plots(
    ages: list[int],
    volumes: list[float],
    lengths: list[float],
    genotypes: list[str],
    out_path: pathlib.Path,
):
    """
    Create all plots for the given ages, volumes, and lengths.
    """
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))

    ages = np.array(ages)
    volumes = np.array(volumes)
    lengths = np.array(lengths)
    genotypes = np.array(genotypes)

    # Colour code based on genotype
    unique_genotypes = np.unique(genotypes)
    for g in unique_genotypes:
        a = ages[genotypes == g]
        v = volumes[genotypes == g]
        l = lengths[genotypes == g]

        axes[0].scatter(a, v, alpha=0.5)
        axes[0].set_xlabel("Age")
        axes[0].set_ylabel("Vol")

        axes[1].scatter(a, l, alpha=0.5)
        axes[1].set_xlabel("Age")
        axes[1].set_ylabel("Length")

        axes[2].scatter(v, l, alpha=0.5, label=g)
        axes[2].set_xlabel("Vol")
        axes[2].set_ylabel("Length")

    axes[2].legend(loc="lower right")

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _plot_vol_vs_age(ages: list[int], volumes: list[float], out_path: pathlib.Path):
    """
    Plot volume vs age
    """
    # Perform a simple linear fit to get the trendline
    z, cov = np.polyfit(ages, volumes, 1, cov=True)
    p = np.poly1d(z)

    fig, axis = plt.subplots(figsize=(8, 6))
    axis.scatter(ages, volumes, alpha=0.5)
    axis.set_xlabel("Age (months)")
    axis.set_ylabel(r"Volume $\left(mm^3\right)$")

    unique_ages = list(set(ages))
    axis.plot(unique_ages, p(unique_ages), color="red", linestyle="--")

    axis.set_title(
        f"Average increase: {z[0]:.3f}$\pm${np.sqrt(cov[0, 0]):.3f} $mm^3$/month\nN={len(ages)}"
    )

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _scatter_plots(
    masks: list[np.ndarray], in_mask_paths: list[pathlib.Path], output_dir: pathlib.Path
) -> None:
    """
    Make scatter plots showing volume, size, etc. against metadata
    """
    ages = []
    volumes = []
    lengths = []
    genotypes = []

    for path, mask in zip(tqdm(in_mask_paths, desc="Making scatter plots"), masks):
        fish_n = read.fish_number(path)
        if read.is_excluded(fish_n, exclude_train_data=False, exclude_unknown_age=True):
            continue

        metadata: read.Metadata = read.metadata(fish_n)
        vol = np.sum(mask) * metadata.voxel_volume

        volumes.append(vol)
        ages.append(metadata.age)
        lengths.append(metadata.length)
        genotypes.append(metadata.genotype)

    _plot_vol_vs_age(ages, volumes, output_dir / "volume_age_plot.png")
    _all_plots(ages, volumes, lengths, genotypes, output_dir / "scatter_plots.png")


def _calculate_point_size(axis: plt.Axes, img_size: tuple[int, int, int]) -> float:
    """Calculate point size so each point is roughly 1 pixel"""
    assert set(img_size) == {img_size[0]}, "Image must be cubic"

    fig_width_px = (
        axis.figure.get_figwidth() * axis.figure.dpi * axis.get_position().width
    )
    return (fig_width_px / img_size[0]) ** 2


def _plot_3d(
    img: np.ndarray, mask: np.ndarray, out_path: pathlib.Path, title: str
) -> None:
    """
    Plot projections of the jaw in 3D
    """
    fig, (ax1, ax2) = plt.subplots(
        1, 2, subplot_kw={"projection": "3d"}, figsize=(12, 5)
    )

    plot_kw = {
        "marker": "s",
        "cmap": "inferno",
        "vmin": 0,
        "vmax": 2**16,
        # Calculate point size so each point is roughly 1 pixel
        # Assumes all the images are the same size, which they probably
        # are
        "s": _calculate_point_size(ax2, img.shape),
    }

    co_ords = np.argwhere(mask)
    greyscale_vals = img[co_ords[:, 0], co_ords[:, 1], co_ords[:, 2]]

    for a in (ax1, ax2):
        scatter = a.scatter(
            co_ords[:, 0], co_ords[:, 1], co_ords[:, 2], **plot_kw, c=greyscale_vals
        )
        a.axis("off")

    fig.colorbar(scatter, ax=[ax1, ax2], shrink=0.5, aspect=20)

    ax1.view_init(elev=45, azim=-90, roll=-140)
    ax2.view_init(elev=180, azim=30)

    fig.suptitle(title)

    fig.savefig(out_path)
    plt.close(fig)


def _plot_slice(
    img: np.ndarray, mask: np.ndarray, out_path: pathlib.Path, title: str
) -> None:
    """
    Plot a slice through the jaw
    """
    fig, _ = images_3d.plot_slices(img, mask)
    fig.suptitle(title)
    fig.tight_layout()

    fig.savefig(out_path)
    plt.close(fig)


def main(input_dir: pathlib.Path, output_dir: pathlib.Path):
    """
    Read in pairs of images and masks, plot slices and save them
    """
    img_in_dir = input_dir / "imgs"
    mask_in_dir = input_dir / "masks"

    in_img_paths = sorted(list(img_in_dir.glob("*.tif")))
    in_mask_paths = sorted(list(mask_in_dir.glob("*.tif")))

    # Check they match up
    assert len(in_img_paths) == len(
        in_mask_paths
    ), f"Got {len(in_img_paths)} images but {len(in_mask_paths)} masks"
    for img_path, mask_path in zip(in_img_paths, in_mask_paths):
        assert (
            img_path.name == mask_path.name
        ), f"Got {img_path.name=} but {mask_path.name=}. Do the masks and images match up?"

    # Read in all the masks - we need them to make the intial plots, and the bottleneck
    # is reading in the images (which we will do later)
    masks = [
        tifffile.imread(path) for path in tqdm(in_mask_paths, desc="Reading masks")
    ]

    # Use the masks to make scatter plots of things like volume
    _scatter_plots(masks, in_mask_paths, output_dir)

    slice_dir = output_dir / "slices"
    slice_dir.mkdir(parents=True, exist_ok=True)

    projection_dir = output_dir / "projections"
    projection_dir.mkdir(parents=True, exist_ok=True)

    for img_path, mask in zip(tqdm(in_img_paths), masks, strict=True):
        metadata = read.metadata(read.fish_number(img_path))

        img = tifffile.imread(img_path)
        _plot_slice(
            img, mask, slice_dir / img_path.with_suffix(".png").name, str(metadata)
        )
        _plot_3d(
            img, mask, projection_dir / img_path.with_suffix(".png").name, str(metadata)
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        "-i",
        help="The location of the data. Must have imgs/ and masks/ subdirectories",
        required=True,
        type=pathlib.Path,
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Where the plots will be saved",
        type=pathlib.Path,
        default="wahab_greyscale_output/",
    )
    args = parser.parse_args()

    main(**vars(args))
