PYTHON ?= python3

ls_zip: ls ls_rext LICENSE package_release.py
	$(PYTHON) package_release.py
