# Public deployment

The release is ready to upload, but no public service is created merely by opening the local executable. A local `127.0.0.1` URL works only on that computer.

## Streamlit Community Cloud

1. Review the exact source package and methodological notes. Finalize the author-selected license before public release.
2. Sign into your GitHub and Streamlit Community Cloud accounts. Do not put passwords or access tokens in source files.
3. Create a repository containing the contents of this directory. Keep `app.py`, `core.py`, `service.py` and `requirements.txt` at the repository root, with `.streamlit/config.toml` in its folder. Do not upload `.venv`, local research datasets or the portable executable.
4. In Community Cloud, choose **Create app**, select the repository and branch, and set the entrypoint to `app.py`.
5. Select Python 3.12 in the advanced settings and deploy. Review the dependency build log if installation fails.
6. Open the assigned public URL. Upload both synthetic example workbooks and download their Excel reports before sharing the link.
7. Archive the tested release alongside the paper. Record its version/commit and persistent archive identifier; a live app URL alone is not a permanent research archive.

Sign-in, account creation, terms acceptance and repository authorization must be completed by the account owner. No accounts or public repositories were created as part of the local package build.

Official instructions:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

## Docker / institutional server

```bash
docker build -t csf-research-app:1.0.0 .
docker run --rm -p 127.0.0.1:8501:8501 csf-research-app:1.0.0
```

For an internet-facing institutional deployment, have the host's administrator configure HTTPS, the desired access policy, upload limits and retention policy. Keep XSRF protection enabled. The Dockerfile runs as a non-root user. The Docker build is provided as an alternative deployment configuration; it has not been executed on this Windows workstation.
