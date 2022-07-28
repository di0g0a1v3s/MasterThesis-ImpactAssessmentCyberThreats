1st Step: Fill "setup_config.json" with input parameters:
	BIA_Server_Address: address of server in which BIA is running
	Neo4j_Database_Address: address of Neo4j database
	Neo4j_Database_Username: username of Neo4j database
	Neo4j_Database_Password: password of Neo4j database
	Asset_Entrypoint: IP address of asset you wish to be the entrypoint
	Threat_Entrypoint: name of threat you wish to simulate (threat must exist in the database and must belong to the Asset_Entrypoint)
	PathsThroughSubnetsOnlyOnce: True/False - Allows trivial paths to go through the same subnet only once (True) or more than once (False)
	PathsThroughRoutersOnlyOnce: True/False - Allows trivial paths to go through the same router only once (True) or more than once (False)

2nd Step: Run "setup.py". The file "paths.txt" will be created.


3rd Step: Fill "merge_options.json" with input parameters:
	merge_option:
		"NO_MERGE" - Compute OCs for each path in "paths.txt" individually "MERGE_ACTIVITIES" - Compute OCs assuming each service compromises all its dependent activities simultaneously, i.e., merge the paths in "paths.txt" that are equal up to service 
		"MERGE_SERVICES" - Compute OCs assuming each asset compromises all its dependent services simultaneously, i.e, merge the paths in "paths.txt" that are equal up to the	last asset
		"MERGE_ASSETS" - Compute OCs assuming the entrypoint threat compromises every asset path simultaneously, i.e., merge all paths in "paths.txt"
		"CUSTOM_MERGE" - Merge set of selected paths (see "custom_merge_paths")

	custom_merge_paths: list of indices of paths you wish to merge from the file "paths.txt" (in case merge_option = "CUSTOM_MERGE"). E.g., "custom_merge_paths" : [0, 2, 5]

	ComputeOCsForSubnets: True/False - Compute Operational Capacities for Subnets (True) or not (False)
	ComputeOCsForRouters: True/False - Compute Operational Capacities for Routers (True) or not (False)
	
4th Step: Fill "entrypoint_IF.json" with input parameters:
		considerOriginalIF: True/False - if True, consider the entrypoint IF that comes from the BIA database; if False consider "changedIF" as the entrypoint IF.
		changedIF: float (0.0-1.0) - new value for the entrypoint IF in case considerOriginalIF=False

5th Step: Run "compute_impact.py"


6th Step: The file "output_impact.json" will be created.

This file contains:

	- An array "paths" containing "n" paths generated according to user specification (in the file "merge_options.json"). For each of these paths:

		- The field "vulnerability" is the name of the user-selected entrypoint threat

		- The array "asset_paths" will contain "k" asset paths. An asset path is a path exclusively through assets, subnets and routers. Each asset path comes from a trivial path (i.e., a path before the merge). So, the number of asset_paths - "k" - will be the same as the number of trivial paths merged. Each asset_path contains:
			- assets (type = "Asset"; id; ip) The first element in every "asset_path" will always be the entrypoint asset chosen by the user. The Operational Capacity (OC) of the asset, as determined by the impact algorithmm, is also presented. The field "exploited_vuln" exists in the case where the algorithm determines that a vulnerability is exploited in that asset (and the value of this field is the name of the exploited vulnerability). An asset_path always ends at an asset. In an asset_path, immediately after an "asset" can only be a "subnet". 
			- subnets (type = "Subnet"; subnet_prefix) The Operational Capacity (OC) of the subnet, as determined by the impact algorithmm, is also presented (except if ComputeOCsForSubnets=False - in this case OC=null). In the asset_path, immediately after a "subnet" can be either an "asset" or a "router".
			- routers (type = "Router"; id) The Operational Capacity (OC) of the router, as determined by the impact algorithmm, is also presented (except if ComputeOCsForRouters=False - in this case OC=null). In the asset_path, immediately after a "router" can be either another "router" or a "subnet".

		- The array "services" contains all the services affected by the merged path. Each entry of the array contains the service's "id" and "name", as well as its OC, as determined by the impact algorithmm

		- The array "activities" contains all the activities affected by the merged path. Each entry of the array contains the activity's "id" and "name", as well as its OC, as determined by the impact algorithmm

		- The array "processes" contains all the business-processes affected by the merged path. Each entry of the array contains the bp's "id" and "name", as well as its OC, as determined by the impact algorithmm

		- Lastly, the field "impact" contains a number between 0 and 1 that corresponds to the impact of the merged path, as determined by the algorithm. A value closer to 1 means the impact (i.e., the loss of operationality of the business processes) is greater

