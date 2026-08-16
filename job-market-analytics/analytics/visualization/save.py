"""
Visualization styling and file saving helper module.
"""

from pathlib import Path
from typing import List, Optional
import matplotlib.pyplot as plt
import seaborn as sns


def configure_plot_style():
    """Set uniform aesthetic styling for matplotlib and seaborn charts."""
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["figure.titlesize"] = 16


def save_chart(fig: plt.Figure, file_path: Path, dpi: int = 300) -> Path:
    """
    Save matplotlib figure to high-resolution PNG file and close figure.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(file_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return file_path
