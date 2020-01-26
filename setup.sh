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

	ACTUAL_LOCK_NAME=${configuration_lockmanager[lockname]}
    lockname=$(echo "$ACTUAL_LOCK_NAME" | awk '{print tolower($0)}')
	lockfilename=$(echo "$ACTUAL_LOCK_NAME" | awk '{print tolower($0)}')

	if (false)
	then
	   echo $lockname
	   echo $lockfactoryname
	   echo $sensorname
	   echo $sensorfactoryname
	   echo $garageentityid 
	   echo $numcodes
	   echo $ACTUAL_LOCK_NAME
	fi

	if test -z "$numcodes" || test -z "$lockname" || test -z "$lockfactoryname" || test -z "$sensorname" || test -z "$sensorfactoryname" || test -z "$garageentityid"
	then
	      echo "lock_manager.ini is incomplete or does not exist"
	fi


	activelockheader="binary_sensor.active_LOCKNAME_" #ACTIVELOCKHEADER
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

	dlmc=$lockfilename"_lock_manager_common.yaml"
#	dlmc=$(echo "$dlmc" | awk '{print tolower($0)}')	
	ll=$lockfilename"_lovelace"
#	ll=$(echo "$ll" | awk '{print tolower($0)}')	

	rm lovelace 2> /dev/null
	for ((i=1; i<=$numcodes; i++))
	do
	   dm=$lockfilename"_lock_manager_"$i."yaml"
#       dm=$(echo "$dm" | awk '{print tolower($0)}')	
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
	      sed -i s/CASE_LOCK_NAME/$ACTUAL_LOCK_NAME/g $dlmc
	      sed -i s/LOCKFACTORYNAMEPREFIX/$lockfactoryname/g $dlmc
	      sed -i s/SENSORNAME/$sensorname/g $dlmc
	      sed -i s/SENSORFACTORYNAMEPREFIX/$sensorfactoryname/g $dlmc
	      sed -i s/GARAGEDOORENTITYID/$garageentityid/g $dlmc

	      sed -i s/INPUTLOCKPINHEADER/"$inputlockpinheaderENTITIES"/g $ll # INPUTLOCKPINHEADER
	      sed -i s/ACTIVELOCKHEADER/"$activelockheaderENTITIES"/g $ll # ACTIVELOCKHEADER
	      sed -i s/LOCKNAME/$lockname/g $ll
	      #read -p "Press enter to continue"
	      sed -i s/CASE_LOCK_NAME/$ACTUAL_LOCK_NAME/g $ll
	      sed -i s/LOCKFACTORYNAMEPREFIX/$lockfactoryname/g $ll
	      sed -i s/SENSORNAME/$sensorname/g $ll
	      sed -i s/SENSORFACTORYNAMEPREFIX/$sensorfactoryname/g $ll
	      sed -i s/GARAGEDOORENTITYID/$garageentityid/g $ll

	   fi

	   sed -i s/TEMPLATENUM/$i/g $dm
	   sed -i s/LOCKNAME/$lockname/g $dm
       sed -i s/CASE_LOCK_NAME/$ACTUAL_LOCK_NAME/g $dm
	   sed -i s/FACTORYNAMEPREFIX/$factoryname/g $dm

	   sed -i s/LOCKNAME/$lockname/g lovelace.$i
	   sed -i s/CASE_LOCK_NAME/$ACTUAL_LOCK_NAME/g lovelace.$i
	   sed -i s/TEMPLATENUM/$i/g lovelace.$i
	   cat lovelace.$i >> $ll
	   rm lovelace.$i
	done


	echo creating $lockfilename
	rm -rf $lockfilename
	mkdir $lockfilename

	mv *.yaml $lockfilename
	mv $ll $lockfilename\

done

#exit 0
