#!/bin/bash
# Read and parse single section in INI file 


# Get/Set single INI section
GetINISection() {
  local filename="$1"
  local section="$2"

  array_name="configuration_${section}"
  declare -g -A ${array_name}
  eval $(awk -v configuration_array="${array_name}" \
             -v members="$section" \
             -F= '{ 
                    if ($1 ~ /^\[/) 
                      section=tolower(gensub(/\[(.+)\]/,"\\1",1,$1)) 
                    else if ($1 !~ /^$/ && $1 !~ /^;/) {
                      gsub(/^[ \t]+|[ \t]+$/, "", $1); 
                      gsub(/[\[\]]/, "", $1);
                      gsub(/^[ \t]+|[ \t]+$/, "", $2);
                      if (section == members) {
                        if (configuration[section][$1] == "")  
                          configuration[section][$1]=$2
                        else
                          configuration[section][$1]=configuration[section][$1]" "$2}
                      }
                    } 
                    END {
                        for (key in configuration[members])  
                          print configuration_array"[\""key"\"]=\""configuration[members][key]"\";"
                    }' ${filename}
        )
}


section="lockmanager"
files=(*.ini)
for item in ${files[*]}
do
        # printf "   %s\n" $item

	filename=$item

	GetINISection "$filename" "$section"

	sensorfactoryname=${configuration_lockmanager[sensorfactoryname]}
	sensorname=${configuration_lockmanager[sensorname]}
	lockname=${configuration_lockmanager[lockname]}
	lockfactoryname=${configuration_lockmanager[lockfactoryname]}
	garageentityid=${configuration_lockmanager[garageentityid]}
	numcodes=${configuration_lockmanager[numcodes]}

	if (false)
	then
	   echo $lockname
	   echo $lockfactoryname
	   echo $sensorname
	   echo $sensorfactoryname
	   echo $garageentityid 
	   echo $numcodes
	fi

	if test -z "$numcodes" || test -z "$lockname" || test -z "$lockfactoryname" || test -z "$sensorname" || test -z "$sensorfactoryname" || test -z "$garageentityid"
	then
	      echo "lock_manager.ini is incomplete or does not exist"
	fi


	activelockheader="binary_sensor.LOCKNAME_active_" #ACTIVELOCKHEADER
	activelockheaderENTITIES=

	inputlockpinheader="input_text.LOCKNAME_pin_" #INPUTLOCKPINHEADER
	inputlockpinheaderENTITIES=

	for ((i=1; i<=$numcodes; i++))
	do
	   activelockheaderENTITIES=$activelockheaderENTITIES$activelockheader$i
	   inputlockpinheaderENTITIES=$inputlockpinheaderENTITIES$inputlockpinheader$i
	   if [ $i -lt $numcodes ]
	   then
	      activelockheaderENTITIES=$activelockheaderENTITIES", "
	      inputlockpinheaderENTITIES=$inputlockpinheaderENTITIES", "
	   fi
	done

	dlmc=$lockname"_lock_manager_common.yaml"
	ll=$lockname"_lovelace"

	rm lovelace 2> /dev/null
	for ((i=1; i<=$numcodes; i++))
	do
	   dm=$lockname"_lock_manager_"$i."yaml"
	   cp lock_manager.txt $dm
	   cp lovelace.code lovelace.$i
	   if [ $i -eq 1 ]
	   then
	      # first pass, setup lock_manager_common
	      cp ./lock_manager_common.txt ./$dlmc
	      cat lovelace.head >> $ll

	      sed -i s/INPUTLOCKPINHEADER/"$inputlockpinheaderENTITIES"/g $dlmc # INPUTLOCKPINHEADER
	      sed -i s/ACTIVELOCKHEADER/"$activelockheaderENTITIES"/g $dlmc # ACTIVELOCKHEADER
	      sed -i s/LOCKNAME/$lockname/g $dlmc
	      sed -i s/LOCKFACTORYNAMEPREFIX/$lockfactoryname/g $dlmc
	      sed -i s/SENSORNAME/$sensorname/g $dlmc
	      sed -i s/SENSORFACTORYNAMEPREFIX/$sensorfactoryname/g $dlmc
	      sed -i s/GARAGEDOORENTITYID/$garageentityid/g $dlmc

	      sed -i s/INPUTLOCKPINHEADER/"$inputlockpinheaderENTITIES"/g $ll # INPUTLOCKPINHEADER
	      sed -i s/ACTIVELOCKHEADER/"$activelockheaderENTITIES"/g $ll # ACTIVELOCKHEADER
	      sed -i s/LOCKNAME/$lockname/g $ll
	      sed -i s/LOCKFACTORYNAMEPREFIX/$lockfactoryname/g $ll
	      sed -i s/SENSORNAME/$sensorname/g $ll
	      sed -i s/SENSORFACTORYNAMEPREFIX/$sensorfactoryname/g $ll
	      sed -i s/GARAGEDOORENTITYID/$garageentityid/g $ll

	   fi

	   sed -i s/TEMPLATENUM/$i/g $dm
	   sed -i s/LOCKNAME/$lockname/g $dm
	   sed -i s/FACTORYNAMEPREFIX/$factoryname/g $dm

	   sed -i s/LOCKNAME/$lockname/g lovelace.$i
	   sed -i s/X/$i/g lovelace.$i
	   cat lovelace.$i >> $ll
	   rm lovelace.$i
	done


	echo creating $lockname
	rm -rf $lockname
	mkdir $lockname

	mv $lockname*.yaml $lockname
	mv $ll $lockname\

done

#exit 0
