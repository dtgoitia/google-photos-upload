#!/bin/bash

FILE="kk.avi"
find . -type f -name "kk*" -delete
cp "./to_backup_in_gphotos/2001-2005/2005-09-14 - Instituto 2 (Miércoles)/PIC_0068.AVI" $FILE
# https://unix.stackexchange.com/questions/35746/encode-with-ffmpeg-using-avi-to-mp4
echo 'converting to mp4'
exit
# ffmpeg -i $FILE "${FILE}.mp4"

FILE="${FILE}.mp4"

# FILE="kk.jpg"
# find . -type f -name $FILE -delete
# cp to_backup_in_gphotos/2001-2005/2005-09-14\ -\ Instituto\ 2\ \(Miércoles\)/PIC_0018.JPG $FILE
# python -m gpy scan date $FILE
echo "exiftool -AllDates ${FILE}"
exiftool -AllDates $FILE
# FileDateReport(                 # no google date
#    path=PosixPath('kk.jpg'),
#    filename_date=None,
#    metadata_date=datetime.datetime(2005, 9, 14, 9, 7, 8),
#    google_date=None,
#    gps=None)

python -m gpy.cli.add_google_timestamp $FILE 2005-09-14T09:07:08+02:00

echo "exiftool -XMP:CreateDate ${FILE}"
exiftool -XMP:CreateDate $FILE
# python -m gpy scan date $FILE
# FileDateReport(                # habemus google date!!
#    path=PosixPath('kk.jpg'),
#    filename_date=None,
#    metadata_date=datetime.datetime(2005, 9, 14, 10, 7, 8),
#    google_date=datetime.datetime(2005, 9, 14, 10, 7, 8, tzinfo=datetime.timezone(datetime.timedelta(seconds=28800))),
#    gps=None)

# python -m gpy.cli.upload_single_file kk.jpg
# python -m gpy.cli.upload_single_file kk.jpg_original