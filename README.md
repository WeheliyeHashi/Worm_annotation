# Worm_annotation

This is a Gui to annotate deeptangle labels.
## Installation

Installation steps:
* git clone, or download, this repository in a folder of your computer
* git clone https://github.com/WeheliyeHashi/Worm_annotation.git
* open a terminal window in that folder


```bash
conda env create -f requirements.yml
conda activate Worm_annotation
pip install -e .
```


## Starting the program

Now that the GUI is installed, you can launch it by executing
`worm_annotator` in your terminal window (provided the `Worm_annotation`
environment is active)


### Updating an existing installation

Assuming that this code was cloned or donwloaded to desktop and that the `Worm_annotation` environment has already been created, you can update the code by executing
```bash
cd ~/Worm_annotation
conda activate Worm_annotation
git pull
pip install -e .
```