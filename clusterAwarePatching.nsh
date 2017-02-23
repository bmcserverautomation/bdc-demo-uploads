#
#
# This is the cluster patch demo script.  

###################
# PRINT FUNCTIONS
###################
 
print_info()
{
	print "[$(date)] [INFO] ${@}"
}
 
print_error()
{
	if [[ "${useColors}" = "true" ]]
		then
		print -u2 "[$(date)] ${COL_RED}[ERROR]${COL_RESET} ${@}"
	else
		print -u2 "[$(date)] [ERROR] ${@}"
	fi
	cleanupEnv
	exit 1
}
 
print_warn()
{
	if [[ "${useColors}" = "true" ]]
		then
		print "[$(date)] ${COL_LYELLOW}[WARN]${COL_RESET} ${@}"
	else
		print "[$(date)] [WARN] ${@}"
	fi
	return 0
}
 
grep print_debug1()
{
	if [[ "${useColors}" = "true" ]]
		then
		[[ "${DEBUGLEVEL}" -ge "1" ]] && print "[$(date)] ${COL_LBLUE}[DEBUG1]${COL_RESET} $@"
	else
		[[ "${DEBUGLEVEL}" -ge "1" ]] && print "[$(date)] [DEBUG1] $@"
	fi
	return 0
}

print_debug2()
{
	if [[ "${useColors}" = "true" ]]
		then
		[[ "${DEBUGLEVEL}" -ge "2" ]] && print "[$(date)] ${COL_CYAN}[DEBUG2]${COL_RESET} $@"
	else
		[[ "${DEBUGLEVEL}" -ge "2" ]] && print "[$(date)] [DEBUG2] $@"
	fi
	return 0
}
 
print_debug3()
{	
	if [[ "${useColors}" = "true" ]]
		then
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] ${COL_LCYAN}[DEBUG3]${COL_RESET} $@"
	else
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] [DEBUG3] $@"
	fi
	return 0
}
 
print_debug4()
{
	if [[ "${useColors}" = "true" ]]
		then
		[[ "${DEBUGLEVEL}" -ge "4" ]] && print "[$(date)] ${COL_PURPLE}[DEBUG4]${COL_RESET} $@"
	else
		[[ "${DEBUGLEVEL}" -ge "4" ]] && print "[$(date)] [DEBUG4] $@"
	fi
	return 0
}
 
print_debug5()
{
	if [[ "${useColors}" = "true" ]]
		then
		[[ "${DEBUGLEVEL}" -ge "5" ]] && print "[$(date)] ${COL_LPURPLE}[DEBUG5]${COL_RESET} $@"
	else
		[[ "${DEBUGLEVEL}" -ge "5" ]] && print "[$(date)] [DEBUG5] $@"
	fi
	return 0
}

print_variable()
{
	if [[ "${useColors}" = "true" ]]
		then
		#[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] [VARIABLE] ${1}: `eval printf '%q' \\$"${1}"`"
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] ${COL_GREEN}[VARIABLE]${COL_RESET} ${1}: ${(P)${1}//[[:cntrl:]]/ }"
	else
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] [VARIABLE] ${1}: ${(P)${1}//[[:cntrl:]]/ }"
	fi
	return 0
}

print_blexec()
{
	if [[ "${useColors}" = "true" ]]
		then
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] ${COL_LRED}[BLCLI_EXECUTE]${COL_RESET} $@"
	else
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] [BLCLI_EXECUTE] $@"
	fi
		
    return 0
}

print_blres()
{
	if [[ "${useColors}" = "true" ]]
		then
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] ${COL_LGREEN}[BLCLI_RESULT]${COL_RESET} ${@}"
	else
		[[ "${DEBUGLEVEL}" -ge "3" ]] && print "[$(date)] [BLCLI_RESULT] ${@}"
	fi
    return 0
}
###################
# BLCLI FUNCTIONS
###################
 
#####
# Establishes a connection to BladeLogic in preparation for using the 
# BLCLI Performance Commands.
openBLConnection()
{
	print_debug2 "Entering function: ${0}..."
	if [[ -n "${CLI_JVM_OPTS:-}" ]]
		then
		for cliOpt in ${CLI_JVM_OPTS}
			do
			print_debug1 "blcli_setjvmoption ${cliOpt}"
			blcli_setjvmoption "${cliOpt}"
		done
	fi	
	# CLI_INTERACTIVE gets set to false when a script runs from 
	# within BladeLogic.  So when it's NOT false, we must be running
	# from the command line and hence need to take a few extra steps
	# before trying to establish a BLCLI connection.
	# Note that we still need to have cached session credentials for
	# this to work!
	if [[ "${CLI_INTERACTIVE}" != "false" ]]
	then
		checkBlCreds
		blcli_setoption authType BLSSO
		blcli_setoption serviceProfileName ${blProfile}
		blcli_setoption roleName "${blRole}"
	fi
 
	print_info "Opening connection to BladeLogic"
	blcli_connect 
	print_debug2 "Exiting function: ${0}..."
}
 
closeBLConnection()
{
	print_info "Closing connection to BladeLogic"
	blcli_destroy
}

checkBlCreds()
{
	print_debug2 "Entering function: ${0}..."
	blcred cred -test -profile ${blProfile}
	if [[ $? -eq 1 ]]
		then
		print_error "Please establish BladeLogic SSO credentials by running \"blcred cred -acquire -profile ${blProfile}\"..."
	fi
	print_debug2 "Exiting function: ${0}..."
}

#####
# Simple function to execute a blcli command using the performance commands
# Output is stored in the environment variable RESPONSE
# Arguments:
#   $BLCLICMD must be set prior to calling this function!
# Returns:
#   0   Success
# 999   No BLCLI supplied
# Other [As returned by BLCLI call]
runBlcliCmd()
{
	print_debug2 "Entering function: ${0}..."
	local varName="${1}" 
	local errOnFail="${2}"

	if [[ -n ${BLCLICMD[@]} ]]
	then
		print_blexec "blcli_execute ${BLCLICMD[@]}"
		local silent="quietmode.enabled"
		if [[ "${CLI_JVM_OPT#*$silent}" = "${CLI_JVM_OPTS}" ]]
			then
			blcli_execute "${BLCLICMD[@]}"
		else
			blcli_execute "${BLCLICMD[@]}" > ${BLCLIOUT} 2> ${BLCLIERR}
		fi
		RETCODE=$?
 		if [[ $RETCODE -eq 0 ]] 
			then
			blcli_storeenv tmpRESULT 
			# storeenv exports the variable, we want to keep it local
			RESULT="${tmpRESULT}"
			unset tmpRESULT
			print_blres "$(echo ${RESULT} | tr -d '[:cntrl:]')"
			# set RESULT to the variable we passed in
            if [[ "${varName}x" != "x" ]]
              	then
 				eval ${varName}="\"${RESULT}\""
			fi
			if [[ "${errOnFail}x" != "x" ]]
				then
				blcliOut="pass"
			fi
			return $RETCODE
		else
			if [[ "${errOnFail}x" = "x" ]] 
				then
				if [[ ${blVersion} -ge 82 ]]
					then
					RESULT="blcli failed..."
				else
					RESULT="$(cat ${BLCLIERR} | cut -f2- -d:)"
				fi
				print_error "${RESULT}"
			else
				blcliOut="fail"
			fi
		fi
	else
		print_error "No BLCLI command supplied!"
		return 999
	fi
	print_debug2 "Exiting function: ${0}..."
}

###################
# UTILITY FUNCTIONS
###################
 
#####
# Generic Usage command
# TO-DO: Customise on a "per script" basis
#
# Arguments:				
#   $1   Required exit code - defaults to 1.
#
usage()
{
	if [[ "${1}" = "" ]]
	then
		USAGE_CODE=1
	else
		USAGE_CODE=${1}
	fi
 
	echo "Usage: $0 -d <level> --P <blProfile> -R <blRole>"
	echo "-d	<debug level>		Debug Log output, level 0-5.  Should be first option (int)"
	echo "-R	<blRole>         	BladeLogic RBAC Role to authenticate as"
	echo "-P	<blProfile>   		BladeLogic Authentication profile to authenticate as"
	echo "-j 	<fqPatchJobName>	Fully qualified path of the patching job to run"
	echo "-o	<resultTo>			Email address to send rollup of deploy job status to"
	echo "-s	<targetServerList>	List of servers for adhoc run of patching job"
	echo "-t	<templateDeployJob> Template Deploy job for remediation job"
	echo "-b	<parent group>		Parent Depot Group to store blpackages in"
	echo "-g	<parent group>		Parent Job Group to store deploy jobs in"
	echo "-p	<per Server>		Create a single deploy job per server"
	echo "-r	<rpm rollback>		Make modifications to allow for rpm rollback"
	echo "-e	<fqRemJobname>		Fully qualified path of a remediation job to process results"
	echo ""
	echo "Script Modes are:"
	echo "useLatestRunForResult		-	Uses the latest job run and gets the result of all patching and deploy jobs."
	echo "								If the job was not an auto-remediate job you must pass the fully qualified"
	echo "								path to the remediation job with the -e argument"
	echo "useLatestRunForGenerate	-	Uses the latest patching job result to generate deploy jobs"
	echo "useLatestRunForDeploy		-	Uses the latest patching job result to generate and run the deploy, cannot be"
	echo "								passed a template job"
	echo "runPatchingJobForResult	-	Runs just the patching job and gets the result, no generate or deploy"
	echo "runPatchingJobForGenerate	-	Runs the patching job and generates deploy jobs"
	echo "runPatchingJobForDeploy	-	Runs the patching job, generates the deploy and runs them"
	echo ""
	echo ""	
	echo "For the RPM Rollback option, you must put the line 'tsflags=repackage' in the NSH/share/patch/linux/linux-deploy.sh"
	echo "file on all applicaiton servers, you can put it after the 'bootloader=1' line in that file."

	exit $USAGE_CODE
}

#####
# In various situations we need to pipe the output of certain commands to
# NULL.  Since this differs depending on the system on which the script is
# being run, we set it dynamically here.
setNull()
{

	if [[ "${OS_NAME}" = "WindowsNT" ]]
	then
		print_debug5 "Setting NULL for a Windows platform"
		NULL="NUL"
	else
		print_debug5 "Setting NULL for a UNIX platform"
		NULL="/dev/null"
	fi
}

#####
# Temp File functions
initTmpFile()
{
	! [[ -d "${TMPDIR}" ]] && mkdir -p "${TMPDIR}"
	BLCLIOUT="${TMPDIR}/blcli.out"
	BLCLIERR="${TMPDIR}/blcli.err"
}

removeTmpFile()
{
	[[ -d "${TMPDIR}" ]] && [[ "${TMPDIR}" != "/" ]] && rm -rf "${TMPDIR}"
}
 
#####
# This function initialises the environment and MUST be called at the modify
# of the main code!
initScript()
{
	setNull
	[[ ${#@} -eq 0 ]] && usage
	processParameters "$@"
	initTmpFile
	openBLConnection
}
 
#####
# This function closes down, disconnects and generally cleans up the environment
# at the end of execution and should be called at the end of the main code.
cleanupEnv()
{
	if [[ "${cleanupFiles}" = "true" ]]
		then
		print_debug1 "Cleaning up temporary files in ${TMPDIR}..."
		removeTmpFile
	else
		print_warn "Not cleaning up temporary files in ${TMPDIR}..."
	fi
	closeBLConnection

}

#####
# All parameters should be handled in this function.
# TO-DO: Add in custom parameters for each script
processParameters()
{
	while getopts d:R:P:j:p:b:o:s:t:g:r:m:e:q:l:w:T:x: Option
	do
		case "${Option}" in
			d) DEBUGLEVEL="${OPTARG}"
			;;
			P) blProfile="${OPTARG}"
			   print_variable "blProfile"
			;;
			R) blRole="${OPTARG}"
			   print_variable "blRole"
			;;
			j) fqPatchingJobName="${OPTARG}"
			   print_variable "fqPatchingJobName"
			;;
			m) scriptMode="${OPTARG}"
			   print_variable "scriptMode"
			;;
			o) resultTo="${OPTARG}"
			   print_variable "resultTo"
			;;
			s) serverListFile="${OPTARG}"
			   print_variable "serverListFile"
			;;
			t) templateJob="${OPTARG}"
			   print_variable "templateJob"
			;;
			b) parentDepotGroup="${OPTARG}"
			   print_variable "parentDepotGroup"
			;;
			g) parentJobGroup="${OPTARG}"
			   print_variable "parentJobGroup"
			;;   
			p) perServerDeploy="${OPTARG}"
			   print_variable "perServerDeploy"
			;;
			q) perPatchDeploy="${OPTARG}"
			   print_variable "perPatchDeploy"
			;;
			r) allowRPMRollback="${OPTARG}"
			   print_variable "allowRPMRollback"
			   # in the per-patch mode this sets continue on deploy fail
			;;
			e) fqRemediationJobName="${OPTARG}"
			   print_variable "fqRemediationJobName"
  		    ;;
  		    l) parentServerGroup="${OPTARG}"
  		       print_variable "parentServerGroup"
  		    ;;
  		    w) maintWindow="${OPTARG}"
  		       print_variable "maintWindow"
  		    ;;
  		    T) testRun="${OPTARG}"
  		       print_variable "testRun"
  		    ;;
			x) skipCreation="${OPTARG}"
			   print_variable "skipCreation"
			;;
			*) usage
			;;
		esac
	done

	[[ "${DEBUGLEVEL}" -le "0" ]] && DEBUGLEVEL=0
	if [[ "${DEBUGLEVEL}" -ge "5" ]] 
		then
		DEBUGLEVEL=5
		cleanupFiles="false"
	fi
	[[ "${DEBUGLEVEL}" -gt "0" ]] && print_info "Running at Debug level ${DEBUGLEVEL}"
	[[ "${DEBUGLEVEL}" -ge "6" ]] && set -x

}


blProfile="defaultProfile"
blRole="BLAdmins"

openBLConnection
blcred cred -acquire -profile defaultProfile -username BLAdmin -password password

#
#
#
echo "Building Cluster Aware Batch Job"


serverGroup="/Cluster_Patching/Transaction Clearing Cluster - Prod"
depotGroup="/Cluster_Patching"
jobGroup="/Cluster_Patching"


# initScript

clusterName="$1"
#server=$1
#echo "Server: $server"

echo "...This is Cluster: $clusterName"
 
echo "...Finding all servers in cluster: $serverGroup ..."

BLCLICMD=(Server listServersInGroup "${serverGroup}")
runBlcliCmd servers
	# echo $servers

echo "...Find App or Cluster Shutdown/Failover Jobs..."

for server in $servers
do
  BLCLICMD=(Server printPropertyValue "${server}" "AppShutdownJob")
    runBlcliCmd AppShutdownJob
    echo $AppShutdownJob
  echo "AppShutdownJob: is $AppShutdownJob for $server in Cluster: $serverGroup"
  BLCLICMD=(Server printPropertyValue "${server}" "AppStartupJob")
    runBlcliCmd AppStartupJob
    echo $AppStartupJob
  echo "AppStartupJob: is $AppStartupJob for $server in Cluster: $serverGroup"
done

echo "...Identify correct Patching Remediation Job"

  BLCLICMD=(Job listAllByGroup "${jobGroup}")
  runBlcliCmd listOfJobs

#
# find a Remediation job named by the cluster or server.  
#   We can select more than one (one for each cluster member etc.) by
#   tweaking this logic...
#

echo "${listOfJobs}" | while read -r foo
do
  jobCandidate="`echo \"$foo\" | grep -i \"Remediate\" | grep -i \"$clusterName\"`"
  success="`echo "$jobCandidate" | wc -l`"
  # if 1, we found a job that matches, save it and keep moving
  if [ $success = 1 ]; then 
    echo "Found a job candidate!"
    remediateJob="$jobCandidate"
    echo "Welcome $jobCandidate!"
    break
  fi
done

# the loop above should work, but I'm not sure why it doesn't, and I need to troubleshoot it later
remediateJob="Remediate Transaction Clearing Cluster - bl-rhwww_RedHat Linux 6 and 7 Patch Catalog - reposync"

if [ "" != "$remediateJob" ]; then
  echo "Remediation Job found: $remediateJob"
else
  echo "Can't go forward without a remediation job, bailing out!"
  exit 1
fi

# Name of the new Batch Job.
batchJobName="Transaction_Clearing_Cluster_Remediation_Batch"

BLCLICMD=(JobGroup groupNameToId "${jobGroup}")
runBlcliCmd jobGroupId

  # Get JobDBKey for AppShutdown job
  jobName=$(basename $AppShutdownJob)
  BLCLICMD=(NSHScriptJob getDBKeyByGroupAndName "${jobGroup}" "${jobName}")
  runBlcliCmd appShutdownJobDBKey

  # Get JobDBKey for remediation job
  BLCLICMD=(PatchingJob getDBKeyByGroupAndName "${jobGroup}" "${remediateJob}")
  runBlcliCmd remediationJobDBKey

  # Get JobDBKey for AppStartup job
  jobName=$(basename $AppStartupJob)
  BLCLICMD=(NSHScriptJob getDBKeyByGroupAndName "${jobGroup}" "${jobName}")
  runBlcliCmd appStartupJobDBKey


  # Continue on error. Set to true if you want the Batch Job to continue on error.
  bContinueOnError="true"
  # Execute by stage. Set to true to execute by stage and false to execute by server.
  bExecuteByStage="true"
  # Override targets. Set to true to override member job targets and false to use member targets.
  bOverrideTargets="false"

# Run the command with the above values to create the Batch Job.

BLCLICMD=(BatchJob createBatchJob "${batchJobName}" ${jobGroupId} ${appShutdownJobDBKey} $bContinueOnError $bExecuteByStage $bOverrideTargets)
runBlcliCmd batchJobKey

# Use the returned DBKey to add more jobs to the Batch Job. 

# Add in the remediation Job
BLCLICMD=(BatchJob addMemberJobByJobKey "${batchJobKey}" ${remediationJobDBKey})
runBlcliCmd batchJobKey

# Add in the app/cluster startup Job
BLCLICMD=(BatchJob addMemberJobByJobKey "${batchJobKey}" ${appStartupJobDBKey})
runBlcliCmd batchJobKey
