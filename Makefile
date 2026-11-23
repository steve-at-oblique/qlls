PYTHON ?= python3

ls.zip: ls ls_rext LICENSE package_release.py
	$(PYTHON) package_release.py
