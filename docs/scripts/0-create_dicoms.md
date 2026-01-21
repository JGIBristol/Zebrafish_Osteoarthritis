Create Dicoms
====
Create local DICOM files holding our training data that will be used for the rest of the analysis.

## Usage
#### 1. Change the right configuration options
You will need to tell the script:

1. Where you have mounted the RDSF.
> [!NOTE]
> Change `rdsf_dir` in `userconf.yml` to point to your RDSF mount.

2. Where you want to save the DICOM files
> [!NOTE]
> Change `dicom_dirs` in `userconf.yml` to choose where you want the DICOMs to be saved.

Don't overthink this too much - just change the three directories to something sensible.

<details>
<summary> Why three directories? </summary>
This needs to be a list of three directories - one for each of the directories of labels
in `config.yml`'s `label_dirs` list.
</details>

<details>
<summary> What about telling the script where the original data is? </summary>
The location of the original data (the TIF images and labels) on the RDSF is hard-coded in `config.yml`, so you don't need to
do anything about this.
</details>

#### 2. Check if everything is set up correctly:
```
uv run scripts/0-create_dicoms.py --dry-run
```
You should get a lot of print output like:
```
...
Would write /home/YOUR_NAME/Zebrafish_Osteoarthritis/dicoms/Training set 4 (Wahab resegmented by felix)/441.dcm
...
```

#### 3. Do it for real:
```
uv run scripts/0-create_dicoms.py
```
This will take around an hour to run, but might depend on your internet speed.
It's safe to stop halfway and continue later - it will skip creating files that already exist.

#### 4. Check the DICOM files exist:
```
find dicoms/ -type f -name '*.dcm'
```
Replace `dicoms/` above with wherever you have set your dicoms to go (the `dicom_dirs` entry in `userconf.yaml`).

## More information
<details>
<summary>Why this script exists and what a DICOM is </summary>
This is step 0 (i.e. a preprocessing step) in the analysis pipeline.

The raw data (scans of zebrafish, and the matching labels) are scattered across the RDSF - some of them are saved
in different directories, some as 3D TIF images and some as directories containing 2D TIF images. This is really
annoying to work with, and is slow since the RDSF is a network drive.

A DICOM is a medical imaging file which contains:
- an image
- a label
- metadata (we don't care about this too much here)

There are two advantages to creating our own DICOM files instead of reading directly from the RDSF every time we want to access the data:

1) we don't have to worry about accidentally matching the wrong label up with our images.
2) It's much faster to deal with local files than read from the network drive each time.

(PS \#1 is especially likely here, since there are two naming schemes, old_n and new_n. See `data/uCT_mastersheet.csv` for a spreadsheet
of metadata that contains both old_n and new_n. I think old_n was the original naming scheme, and new_n came later to make the names start
from 1. We'll never know why there are two schemes.)
</details>
