# Release Checklist

Before considering the project ready for portfolio publication:

- [ ] `python -m pytest` passes locally.
- [ ] GitHub Actions passes on `main`.
- [ ] `python main.py` launches the desktop app.
- [ ] `streamlit run streamlit_app.py` launches the web app.
- [ ] `outputs/ocr_debug/` is not tracked.
- [ ] `.venv/`, `*.egg-info/`, `__pycache__/`, build artifacts are ignored.
- [ ] README is readable on GitHub.
- [ ] License file is present.
- [ ] Streamlit deployment URL is added after deployment.
- [ ] Screenshots are added to `docs/assets/` when available.

Suggested release tag:

```powershell
git tag v1.0.0
git push origin v1.0.0
```