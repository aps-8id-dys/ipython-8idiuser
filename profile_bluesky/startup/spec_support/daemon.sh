#!/bin/sh
#
# description: start/stop/restart/checkup the spec_DM_support workflow helper
#
# NOTE: install this on workstation "snow"
# That's where this helper runs.
# crontab line (run every 5 minutes)
#*/5 * * * * /home/beams/8IDIUSER/.ipython-bluesky/profile_bluesky/startup/spec_support/daemon.sh checkup 2>&1 > /dev/null

WORKING_DIR=/home/beams/8IDIUSER/.ipython-bluesky/profile_bluesky/startup/spec_support
PROCESS_NAME=spec_DM_support
PROCESS_CMD=spec_DM_support_daemon

# Change YES to NO in the following line to disable screen-PID lookup 
GET_SCREEN_PID=YES

# Commands needed by this script
ECHO=echo
ID=id
PGREP=pgrep
SCREEN=screen
KILL=kill
BASENAME=basename
DIRNAME=dirname
READLINK=readlink
PS=ps
# Explicitly define paths to commands if commands aren't found
#!ECHO=/bin/echo
#!ID=/usr/bin/id
#!PGREP=/usr/bin/pgrep
#!SCREEN=/usr/bin/screen
#!KILL=/bin/kill
#!BASENAME=/bin/basename
#!DIRNAME=/usr/bin/dirname
#!READLINK=/bin/readlink
#!PS=/bin/ps

#####################################################################

SNAME=${BASH_SOURCE:-$0}
SELECTION=$1


#####################################################################

cd ${WORKING_DIR}


screenpid() {
    if [ -z ${SCREEN_PID} ] ; then
        ${ECHO}
    else
        ${ECHO} " in a screen session (pid=${SCREEN_PID})"
    fi
}

checkpid() {
    MY_UID=`${ID} -u`
    # The '\$' is needed in the pgrep pattern to select process, but not process.sh
    PROCESS_PID=`${PGREP} ${PROCESS_NAME}\$ -u ${MY_UID}`
    #!${ECHO} "PROCESS_PID=${PROCESS_PID}"

    if [ "${PROCESS_PID}" != "" ] ; then
        # Assume the process is down until proven otherwise
        PROCESS_DOWN=1

        # At least one instance of the process binary is running; 
        # Find the binary that is associated with this process
        for pid in ${PROCESS_PID}; do
            BIN_CWD=`${READLINK} /proc/${pid}/cwd`
            PROCESS_CWD=`${READLINK} -f ${WORKING_DIR}`
            
                if [ "$BIN_CWD" = "$PROCESS_CWD" ] ; then
                    # The process is running; the binary with PID=$pid is the process that was run from $WORKING_DIR
                    PROCESS_PID=${pid}
                    PROCESS_DOWN=0
                    
                    SCREEN_PID=""

                    if [ "${GET_SCREEN_PID}" = "YES" ] ; then
                        # Get the PID of the parent of the process (shell or screen)
                        P_PID=`${PS} -p ${PROCESS_PID} -o ppid=`
                        
                        # Get the PID of the grandparent of the process (sshd, screen, or ???)
                        GP_PID=`${PS} -p ${P_PID} -o ppid=`

                        #!${ECHO} "P_PID=${P_PID}, GP_PID=${GP_PID}"

                        # Get the screen PIDs
                        S_PIDS=`${PGREP} screen`
                    
                        for s_pid in ${S_PIDS} ; do
                            #!${ECHO} ${s_pid}

                            if [ ${s_pid} -eq ${P_PID} ] ; then
                                SCREEN_PID=${s_pid}
                                break
                            fi
                    
                            if [ ${s_pid} -eq ${GP_PID} ] ; then
                                SCREEN_PID=${s_pid}
                                break
                            fi
                    
                        done
                    fi
                    
                    break
                    #else
                    #    ${ECHO} "PATHS are different"
                    #    ${ECHO} ${BIN_CWD}
                    #    ${ECHO} ${PROCESS_CWD}
                fi
        done
    else
        # process is not running
        PROCESS_DOWN=1
    fi

    return ${PROCESS_DOWN}
}

start() {
    if checkpid; then
        ${ECHO} -n "${PROCESS_NAME} is already running (pid=${PROCESS_PID})"
        screenpid
    else
        ${ECHO} "Starting ${PROCESS_NAME}"
        cd ${WORKING_DIR}
        # Run process inside a screen session
        ${SCREEN} -dm -S ${PROCESS_NAME} -h 5000 ${PROCESS_CMD}
    fi
}

stop() {
    if checkpid; then
        ${ECHO} "Stopping ${PROCESS_NAME} (pid=${PROCESS_PID})"
        ${KILL} ${PROCESS_PID}
    else
        ${ECHO} "${PROCESS_NAME} is not running"
    fi
}

restart() {
    stop
    start
}

status() {
    if checkpid; then
        ${ECHO} -n "${PROCESS_NAME} is running (pid=${PROCESS_PID})"
        screenpid
    else
        ${ECHO} "${PROCESS_NAME} is not running"
    fi
}

checkup() {
    if checkpid; then
        : # report nothing if process is running
    else
        ${ECHO} "${PROCESS_NAME} is not running"
        start
    fi
}

console() {
    if checkpid; then
        ${ECHO} "Connecting to ${PROCESS_NAME}'s screen session"
        # The -r flag will only connect if no one is attached to the session
        #!${SCREEN} -r ${PROCESS_NAME}
        # The -x flag will connect even if someone is attached to the session
        ${SCREEN} -x ${PROCESS_NAME}
    else
        ${ECHO} "${PROCESS_NAME} is not running"
    fi
}

run() {
    if checkpid; then
        ${ECHO} -n "${PROCESS_NAME} is already running (pid=${PROCESS_PID})"
        screenpid
    else
        ${ECHO} "Starting ${PROCESS_NAME}"
        cd ${WORKING_DIR}
        # Run process outside of a screen session, which is helpful for debugging
        ${PROCESS_CMD}
    fi
}

usage() {
    ${ECHO} "Usage: $(${BASENAME} ${SNAME}) {start|stop|restart|status|checkup|console|run}"
}

#####################################################################

if [ ! -d ${WORKING_DIR} ] ; then
    ${ECHO} "Error: ${WORKING_DIR} doesn't exist."
    ${ECHO} "WORKING_DIR in ${SNAME} needs to be corrected."
else
    case ${SELECTION} in
        start)
        start
        ;;

        stop | kill)
        stop
        ;;

        restart)
        restart
        ;;

        status)
        status
        ;;

        checkup)
        checkup
        ;;

        console)
            console
        ;;

        run)
            run
        ;;

        *)
        usage
        ;;
    esac
fi
