# Shim: Dell Spec Classifier (legacy path)

**This folder is a backward-compatibility shim.** The project root has been renamed to **`spec_classifier/`**.

- **Preferred:** Run and develop from **`spec_classifier/`**:
  ```bash
  cd spec_classifier
  python main.py --input test_data/dl1.xlsx --vendor dell
  pytest tests/ -v
  ```
- **This shim:** `python dell_spec_classifier/main.py` delegates to `spec_classifier/main.py` (same process, CWD set to `spec_classifier/`). Use it only if you rely on old paths or scripts.

See **`../spec_classifier/README.md`** for full documentation.
