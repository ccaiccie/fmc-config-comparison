# fmc-config-comparison

NOTE: this is a Proof of Concept script, please test before using in production!

For the first/initial run - execute fmc_create_gold.py script to save FMC "gold" configuration. Then run fmc_config_compare.py script manually or as a crone job to obtain the diff between "gold" and actual configuration. This script pulls Access Control Policies, Host and Networs Objects and Network Group Objects from FMC. Then it compares these actual configurations to previously saved gold configuration. If any of the objects have changed, it saves the changes in report.csv file.
