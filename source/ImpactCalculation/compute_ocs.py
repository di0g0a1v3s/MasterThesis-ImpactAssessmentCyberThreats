from ImpactCalculation.parallel_branches_business_process import getParallelBranches
from Setup.network_entities import Router, Subnet, Asset



def computeOCS(paths, network, ComputeOCsForSubnets, ComputeOCsForRouters): 

    OC_initial = 1

    #calculate Operational Capacities of nodes in each path
    for path in paths:

        path.initializeOCs()
    
        IF = path.getEntrypointVulnerability().getImpactFactor()

        for asset_path in path.getAssetPaths():
            first_asset = asset_path.getFirstAsset()
            
            updated_OC_A = min(path.getOC(first_asset), max(OC_initial - IF, 0))
            path.updateOC(first_asset, updated_OC_A)
            prev_asset = first_asset
            next_asset = asset_path.getNextAsset(first_asset)
            while next_asset is not None:
                current_asset = next_asset
                if isinstance(current_asset, Subnet) and ComputeOCsForSubnets == False: #ignore subnets (if ComputeOCsForSubnets == False)
                    path.updateOC(current_asset, None)
                    next_asset = asset_path.getNextAsset(current_asset)
                    continue
                if isinstance(current_asset, Router) and ComputeOCsForRouters == False: #ignore routers (if ComputeOCsForRouters == False)
                    path.updateOC(current_asset, None)
                    next_asset = asset_path.getNextAsset(current_asset)
                    continue
                OC_A = path.getOC(current_asset)
                OC_A_prev = path.getOC(prev_asset)
                if isinstance(current_asset, Asset): #OC_A := min(OC_A, OC_A_prev, 1-IF_V1, ..., 1-IF_Vn)
                    updated_OC_A = min(OC_A, OC_A_prev)
                    exploited_vuln = None
                    for vuln in current_asset.getListOfVulnerabilities():
                        if updated_OC_A > OC_initial - vuln.getImpactFactor():
                            exploited_vuln = vuln
                        updated_OC_A = min(updated_OC_A, OC_initial - vuln.getImpactFactor())
                    if exploited_vuln is not None:
                        path.setExploitedVuln(current_asset.getID(), exploited_vuln)
                    path.updateOC(current_asset, updated_OC_A)
                else:   #OC_A := min(OC_A, OC_A_prev)
                    path.updateOC(current_asset, min(OC_A, OC_A_prev))
                prev_asset = current_asset
                next_asset = asset_path.getNextAsset(current_asset)

        #From OCs of assets, calculate OCs of each service
        for service in path.getServices():
            sum_asset_ocs = 0
            number_assets = 0
            for asset in service.getListOfAssets():
                number_assets = number_assets + 1
                OC_A = path.getOC(asset)
                if OC_A is None:
                    OC_A = 1
                sum_asset_ocs = sum_asset_ocs + OC_A
            if number_assets == 0:
                OC_S = 1
            else:
                OC_S = sum_asset_ocs/number_assets #average of asset OCs

            path.updateOC(service, OC_S)

        #From OCs of services, calculate OCs of all activities
        for activity in path.getActivities():
            sum_service_ocs = 0
            number_services = 0
            for service in activity.getListOfServices():
                number_services = number_services + 1
                OC_S = path.getOC(service)
                if OC_S is None:
                    OC_S = 1
                sum_service_ocs = sum_service_ocs + OC_S
            if number_services == 0:
                OC_Ac = 1
            else:
                OC_Ac = sum_service_ocs/number_services #average of services OCs
                
            path.updateOC(activity, OC_Ac)

        #from OCs of activities, calculate OCs of business-processes
        for process in path.getProcesses():
            #get parallel branches for process (possible sets of activities that 
            # are executed from the beggining to the end of the process)
            branches = getParallelBranches(process)
            OC_branches = []
            for branch in branches:
                OC_branch = 1
                for activity in branch:
                    OC_act = path.getOC(activity)
                    if OC_act is None:
                        OC_act = 1
                    OC_branch = OC_branch * OC_act #OC of the branch is the multiplication of OCs of its activities
                OC_branches.append(OC_branch)
            
            OC_process_acc = 0
            num_branches = 0
            #OC of process is the average of OCs of its branches (execution threads)
            for OC_branch in OC_branches:
                num_branches = num_branches+1
                OC_process_acc = OC_process_acc + OC_branch
            OC_process = OC_process_acc/num_branches
            path.updateOC(process, OC_process)

        #impact of path is average of Operationality loss (1-OC) of processes in network
        number_processes = len(network.getProcesses())
        impact = 0
        for process in path.getProcesses():
            impact = impact + (1 - path.getOC(process))
        impact = impact/number_processes
        path.setImpact(impact)

    return paths


