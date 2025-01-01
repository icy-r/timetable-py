#loop the git.sh file execution with yyyy mm dd arguments for 2025 jan 1 to 2025 dec 31, append log to log.txt and call git.sh

import os
import subprocess

#loop the git.sh file execution with yyyy mm dd arguments for 2025 jan 1 to 2025 jan 31, append log to log.txt and call git.sh
for i in range(1, 32):
    os.system("echo '2025 01 " + str(i) + "' >> log.txt")
    os.system("./git.sh 2025 01 " + str(i) + " >> log.txt")
    os.system("echo 'new' >> log.txt")
    #interval between executions
    os.system("sleep 1")
