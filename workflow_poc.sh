rm -rf kk.jpg kk.jpg_original
cp to_backup_in_gphotos/2001-2005/2005-09-14\ -\ Instituto\ 2\ \(Miércoles\)/PIC_0018.JPG kk.jpg
python -m gpy scan date kk.jpg
# FileDateReport(                 # no google date
#    path=PosixPath('kk.jpg'),
#    filename_date=None,
#    metadata_date=datetime.datetime(2005, 9, 14, 9, 7, 8),
#    google_date=None,
#    gps=None)

python -m gpy.cli.add_google_timestamp kk.jpg  2005-09-14T09:07:08+02:00

python -m gpy scan date kk.jpg
# FileDateReport(                # habemus google date!!
#    path=PosixPath('kk.jpg'),
#    filename_date=None,
#    metadata_date=datetime.datetime(2005, 9, 14, 10, 7, 8),
#    google_date=datetime.datetime(2005, 9, 14, 10, 7, 8, tzinfo=datetime.timezone(datetime.timedelta(seconds=28800))),
#    gps=None)

# python -m gpy.cli.upload_single_file kk.jpg
# python -m gpy.cli.upload_single_file kk.jpg_original