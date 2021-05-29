backup="00.png_backup"
file="00.png"
remote_dir="/storage/self/primary/DCIM/Camera"
remote_

echo "Deleting ${file}"
rm $file
echo "done"
echo ""

echo "Restoring file from backup..."
cp $backup $file
echo "done"
echo ""

echo "Checking dates in ${file}"
exiftool -XMP:CreateDate $file
echo "There must be nothing over this line"

echo "Adding timestamp to ${file}"
exiftool -XMP:CreateDate="2021:04:01 00:00:00+03:00" $file
echo "done"
echo ""

echo "Checking dates in ${file}"
exiftool -XMP:CreateDate $file
echo "There must be a date over this line"
echo ""

set -x
echo "adb push ${PWD}/${file} /storage/self/primary/DCIM/Camera/${file}"
adb push "${PWD}/${file}" "${remote_dir}/${file}"
echo "done"
echo ""


# adb shell "ls ${remote_dir}"