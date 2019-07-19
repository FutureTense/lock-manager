#

cp lock_manager_1.yaml lock_manager_2.yaml
cp lock_manager_1.yaml lock_manager_3.yaml
cp lock_manager_1.yaml lock_manager_4.yaml
cp lock_manager_1.yaml lock_manager_5.yaml
cp lock_manager_1.yaml lock_manager_6.yaml

sed -i 's/_1/_2/g' lock_manager_2.yaml
sed -i 's/_1/_3/g' lock_manager_3.yaml
sed -i 's/_1/_4/g' lock_manager_4.yaml
sed -i 's/_1/_5/g' lock_manager_5.yaml
sed -i 's/_1/_6/g' lock_manager_6.yaml
