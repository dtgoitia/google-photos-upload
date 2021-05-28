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

move_media_to_working_folder:
	rm -rf "to_backup_in_gphotos/2001-2005"
	mkdir -p "to_backup_in_gphotos/2001-2005/"
	# cp -R "2001-2005_backup/2001-2005/_____" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-09-18 - Con los primos en Lujua (Domingo)" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-09-19 - Instituto 3 (Lunes)" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-09-22 - Celebrando el Cumple de Javier en Telepizza 2005" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-09-23 - Broma a Laura (Viernes)" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-09-24 - Celebrando el Cumple de Javier en la ofi" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-10-02 - Polideportivo (Domingo)" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-10-05 - Instituto 4 (Jueves)" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-10-07 - Break en el Polideportivo Sakoneta" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-10-07 - Instituto 5 (Viernes)" "to_backup_in_gphotos/2001-2005/"
	cp -R "2001-2005_backup/2001-2005/2005-10-08 - Barandiaran Goikoa (Sábado)" "to_backup_in_gphotos/2001-2005/"

delete_backups:
	find to_backup_in_gphotos -type f -name "*_original" -delete

delete_pictures:
	find to_backup_in_gphotos -type f -name "*.JPG" -delete

.PHONY: install lint test coverage
