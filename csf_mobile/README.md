# CSF Research Mobile Web

Phone-friendly CSF-SWARA and CSF-CoCoSo application by Dr. Saeed Alinejad, Shiraz University, Iran.

Deploy `csf_mobile/app.py` on Streamlit Community Cloud with Python 3.12. The nearby requirements.txt supplies dependencies. Open the assigned HTTPS URL on Android, choose a method, upload an Excel workbook, and download results. Templates contain synthetic examples.

This is a web application; no APK is included. Uploaded files are processed on the hosting server. See METHOD_NOTES.md for numerical assumptions and limitations.

Local launch from repository root:
```bash
python -m pip install -r csf_mobile/requirements.txt
python -m streamlit run csf_mobile/app.py
```
