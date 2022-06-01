#!/bin/bash
WORK_DIR=$(cd $(dirname $0); pwd)
TARGETID=${WORK_DIR}/lib/libpoppler.dylib
# echo ${TARGETID}

install_name_tool -id ${TARGETID} ${TARGETID}

array=($(otool -L ${TARGETID}))

for eachValue in ${array[@]}; do
  if [[ "${eachValue}" == /* ]]; then
    # echo ${eachValue}
    ARR=(${eachValue//// })
    if [[ "${ARR[${#ARR[@]}-1]}" != libpoppler.dylib* ]]; then
      echo ${ARR[${#ARR[@]}-1]}
      # cp ${eachValue} ${WORK_DIR}/lib/${ARR[${#ARR[@]}-1]}
      TARGETID=${eachValue}
      NEWTARGETID=${WORK_DIR}/${ARR[${#ARR[@]}-1]}
      install_name_tool -change ${TARGETID} ${NEWTARGETID} ${WORK_DIR}/lib/libpoppler.dylib
    fi
  fi
done

binarray=($(ls ${WORK_DIR}/bin/))

for Value in ${binarray[@]}; do
  echo ${Value}
  array=($(otool -L ${WORK_DIR}/bin/${Value}))
  for eachValue in ${array[@]}; do
    if [[ "${eachValue}" == /* ]]; then
      # echo ${eachValue}
      ARR=(${eachValue//// })
      BINFILE=${WORK_DIR}/bin/${Value}
      TARGETID=${eachValue}
      if [[ "${ARR[${#ARR[@]}-1]}" == libpoppler.121.dylib ]]; then
        NEWTARGETID=${WORK_DIR}/lib/libpoppler.dylib
      else
        NEWTARGETID=${WORK_DIR}/lib/${ARR[${#ARR[@]}-1]}
      fi
      if [[ "${ARR[${#ARR[@]}-1]}" != .* ]]; then
        install_name_tool -change ${TARGETID} ${NEWTARGETID} ${BINFILE}
      fi
    fi
  done
done
