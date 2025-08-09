We use a project-local virtual environment (`.venv`) to run Python in Quarto dynamic blocks.

Use the procedure below to recreate the `.venv` environment.

```python
# 0) From your project root
deactivate 2>/dev/null || true
rm -rf .venv

# 1) Create + enter venv
python3 -m venv .venv
source .venv/bin/activate

# 2) Make sure pip works (and fix SSL on some macOS set-ups)
python -m ensurepip --upgrade
export SSL_CERT_FILE="$(python - <<'PY'
import pip._vendor.certifi as c; print(c.where())
PY
)"
unset SSL_CERT_DIR REQUESTS_CA_BUNDLE CURL_CA_BUNDLE

# 3) Upgrade basics
python -m pip install --upgrade pip setuptools wheel

# 4) Install the minimal Quarto stack
# (ipykernel = Jupyter kernel; nbformat/nbclient = execute blocks; PyYAML = your parser)
python -m pip install ipykernel nbformat nbclient jupyter_client jupyter_core pyyaml

# 5) (Optional) any tools you use in .qmd cells
# python -m pip install pandas matplotlib

# 6) Register the kernel so Quarto picks the right Python
python -m ipykernel install --user --name rhythmpedia --display-name "Python (.venv)"

# 7) Sanity checks
python - <<'PY'
import sys, yaml
print("Python:", sys.version.split()[0])
print("PyYAML:", yaml.__version__)
PY

# 8) Ask Quarto to verify Python wiring
quarto check python
```
