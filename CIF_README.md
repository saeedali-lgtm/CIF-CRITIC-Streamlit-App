# CIF Decision Analytics Suite

Circular Intuitionistic Fuzzy Sets · DEMATEL · SWARA · WASPAS

Developed by Dr. Saeed Alinejad, Shiraz University, Iran.

## Run the Python application

Python 3.10 or later. From the repository root:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run ".\CIF_DEMATEL_SWARA_WASPAS_Final.py"
```

Streamlit normally opens http://localhost:8501. For port 8803, add
`--server.port 8803`. The entry filename matches the supplementary material.
The three modules operate independently; outputs are not automatically passed
between modules. Download the template for the selected method and upload the
completed Excel workbook. Results include downloadable intermediate matrices.

[Open CIF online](https://cif-dematel-swara-waspas.streamlit.app/)

## Web and Android editions

The online edition runs the same Python analytical code. The Android edition
displays that HTTPS application inside the app and requires an internet
connection. Uploaded workbooks are sent to the Streamlit server for processing;
this is not an offline or on-device calculation service. Avoid uploading
confidential or personally identifying research data to the public deployment.
The application does not deliberately save uploaded workbooks to disk, but the
hosting provider controls infrastructure and logging. Export results before
closing or refreshing the session. Upload limit: 10 MB; expanded XLSX limit:
100 MB. Keep Android System WebView updated.

## Content and source

`cif_content.json` contains the title, developer attribution and introductory text.
`cif_theme.css` controls presentation. Computational functions remain in the root
Python file. The interface update is not independent scientific validation of
the original methods. CSF/WISE files in this repository are separate software.
Signing keys, passwords and tokens are not included in releases.
