#!/bin/bash

###
### Run this script with:
###
###   run.sh
###

# Get argument (number of MPI processes)
HOST_FILE="/tmp/mpi_host_file"
NB_PROCESSES=`cat /tmp/mpi_host_file.size`
DATA_DIR="/opt/paraview/ParaViewData-v4.1/Data"

# Set up cluster-specific variables
PARAVIEW_DIR="/opt/paraview/ParaView-4.2.0-RC1-Linux-64bit"
PV_PYTHON="${PARAVIEW_DIR}/bin/pvpython"
APPS_DIR="lib/paraview-4.2/site-packages/paraview/web"
VISUALIZER="${PARAVIEW_DIR}/${APPS_DIR}/pv_web_visualizer.py"
PROXIES="/opt/paraview/defaultProxies.json"
CONTENT="${PARAVIEW_DIR}/share/paraview-4.2/www"
RC_PORT="54321"
REVERSE="--reverse-connect-port ${RC_PORT}"

# Set the display environment variable
export DISPLAY=:0.0

# Run in MPI mode
MPIPROG="${PARAVIEW_DIR}/lib/paraview-4.2/mpiexec"
PV_SERVER="${PARAVIEW_DIR}/bin/pvserver"

# First run pvpython with the reverse connect port
${PV_PYTHON} ${VISUALIZER} --port 8080 --content ${CONTENT} --proxies ${PROXIES} --data-dir ${DATA_DIR} ${REVERSE} &

# Give pvpython a few seconds to bind to reverse connect port
sleep 10

# Now run pvserver and tell it to reverse connect
${MPIPROG} -f ${HOST_FILE} -n ${NB_PROCESSES} ${PV_SERVER} -rc --server-port=${RC_PORT}
