#


cp lovelace.head lovelace.tmp

for value in {1..6}

do
   if [ $value -gt 1 ]
   then
      cp lock_manager_1.yaml lock_manager_$value.yaml
      sed -i 's/_1/_'$value'/g' lock_manager_$value.yaml
   fi


   cp lovelace.code lovelace.$value
   sed -i 's/X/'$value'/g' lovelace.$value
   cat lovelace.$value  >> lovelace.tmp
   rm lovelace.$value
done
mv lovelace.tmp lovelace

