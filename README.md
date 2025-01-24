# Astro Virtual Lab

The **Astro Virtual Lab** is an AI-human collaboration platform for astronomical research adapted from the brilliant work of Kyle Swanson with Virtual La @Stanford. In this Lab, a human researcher works with a team of large language model (LLM) **agents** to perform astronomical research and data analysis. Interaction between the human researcher and the LLM agents occurs via a series of **team meetings**, where all the LLM agents discuss a scientific agenda posed by the human researcher, and **individual meetings**, where the human researcher interacts with a single LLM agent to solve particular astronomical tasks.

## Features

The Astro Virtual Lab is equipped with powerful tools for astronomical research:

- Data analysis and visualization using standard astronomy packages (astropy, matplotlib)
- Access to astronomical databases and catalogs through astroquery
- Image processing capabilities with photutils
- Spectral analysis tools with specutils
- Solar physics research capabilities with sunpy
- Machine learning applications in astronomy with astroML

## Installation

The Astro Virtual Lab can be installed using pip or by cloning the repo and installing the required packages. Installation should only take a couple of minutes.

Optionally, first create a conda environment:

```bash
conda create -y -n astro_virtual_lab python=3.12
conda activate astro_virtual_lab
```

Install via pip:

```bash
pip install astro-virtual-lab
```

For additional astronomy-specific functionality, install with optional dependencies:

```bash
pip install "astro-virtual-lab[astronomy]"
```

## Usage

In the future, the Astro Virtual Lab can be used for various astronomical research tasks such as:
- Analyzing astronomical images and spectra
- Querying astronomical databases
- Processing and analyzing observational data
- Performing statistical analysis of astronomical datasets
- Applying machine learning to astronomical problems

Example notebooks demonstrating these capabilities will be available in the `examples` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
