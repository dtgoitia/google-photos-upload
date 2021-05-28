reconcile:
	python -m gpy.cli.reconcile

refresh:
	python -m gpy.cli.refresh_gsheet

clean_logs:
	find . -name "*.log" -delete

requirements:
	rm requirements.txt
	pip-compile --no-header --no-emit-index-url --verbose requirements.in --output-file requirements.txt

install:
	pip install -r requirements.txt

lint:
	flake8
	black --check --diff .
	isort --check --diff .
	python -m mypy --config-file setup.cfg --pretty .

test:
	pytest tests -vv

type-check:
	python -m mypy --config-file setup.cfg --pretty .

coverage:
	pytest tests --cov=gpy --cov-report=html
	python -m webbrowser -t file://$(realpath htmlcov/index.html)

copy_files:
	rm -rf "to_backup_in_gphotos/2001-2005"
	mkdir -p "to_backup_in_gphotos"
	scp -rp \
	  dtg@dtg:"/home/dtg/imagenes/to_backup_in_gphotos/2001-2005" \
	  "to_backup_in_gphotos"

copy_one_file:
	rm -rf "to_backup_in_gphotos/2001-2005"
	mkdir -p "to_backup_in_gphotos/2001-2005/2005-09-14 - Instituto 2 (Miércoles)"
	# last not uploaded picture: 2005-09-14 - Instituto 2 (Miércoles)
	scp dtg@dtg:"/home/dtg/imagenes/to_backup_in_gphotos/2001-2005/2005-09-14\ -\ Instituto\ 2\ \(Miércoles\)/PIC_0023.JPG" "to_backup_in_gphotos/2001-2005/2005-09-14 - Instituto 2 (Miércoles)/PIC_0023.JPG"


.PHONY: install lint test coverage
