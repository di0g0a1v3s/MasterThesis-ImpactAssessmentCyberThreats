from Setup.network_entities import Propagation_Path

NO_MERGE = 0 #Compute OCs for each path individually
MERGE_ACTIVITIES = 1 #Compute OCs assuming each service compromises all its dependent activities simultaneously
MERGE_SERVICES = 2 #Compute OCs assuming each asset compromises all its dependent services simultaneously
MERGE_ASSETS = 3 #Compute OCs assuming the entrypoint threat compromises every asset path simultaneously (full merge)
CUSTOM_MERGE = 4 #Merge paths selected by user

#creates the list of propagation paths based on the merge option chosen
def createPaths(network, merge_parameters):
    merge_option = parseMergeOption(merge_parameters)
    paths = []
    #no merge - the list of paths is simply the one that already exists
    if merge_option is NO_MERGE:
        for path in network.getPropagationPaths():
            paths.append(path.create_copy())

    #MERGE_ACTIVITIES - merge the paths that are equal up to service 
    #(e.g, PATH: Asset <ip: ['192.168.19.1']> -> Asset <ip: ['192.168.20.2']> -> Service <name: SCADA> -> Activity <name: Turn off BAGWARE> -> Process <name: SCADA Process Diagram> 
    # and  PATH: Asset <ip: ['192.168.19.1']> -> Asset <ip: ['192.168.20.2']> -> Service <name: SCADA> -> Activity <name: Turn On BAGWARE> -> Process <name: SCADA Process Diagram>
    # merge to PATH: Asset <ip: ['192.168.19.1']> -> Asset <ip: ['192.168.20.2']> -> Service <name: SCADA> -> Activity <name: Turn off BAGWARE>, Activity <name: Turn On BAGWARE> -> Process <name: SCADA Process Diagram>
    elif merge_option is MERGE_ACTIVITIES:
        for path in network.getPropagationPaths():
            path_ =  pathAlreadyInList(path, paths, MERGE_ACTIVITIES)
            if path_ is None:
               paths.append(path.create_copy())
            else:
                path_.addActivity(path.getActivities()[0])
                path_.addProcess(path.getProcesses()[0])


    #MERGE_SERVICES - merge the paths that are equal up to the last asset
    elif merge_option is MERGE_SERVICES:
        for path in network.getPropagationPaths():
            path_ =  pathAlreadyInList(path, paths, MERGE_SERVICES)
            if path_ is None:
               paths.append(path.create_copy())
            else:
                path_.addService(path.getServices()[0])
                path_.addActivity(path.getActivities()[0])
                path_.addProcess(path.getProcesses()[0])

    #MERGE_ASSETS - merge all paths
    elif merge_option is MERGE_ASSETS:
        for path in network.getPropagationPaths():
            path_ =  pathAlreadyInList(path, paths, MERGE_ASSETS)
            if path_ is None:
               paths.append(path.create_copy())
            else:
                path_.addAssetPath(path.getAssetPaths()[0])
                path_.addService(path.getServices()[0])
                path_.addActivity(path.getActivities()[0])
                path_.addProcess(path.getProcesses()[0])

    #CUSTOM_MERGE - Merge paths chosen by user
    elif merge_option is CUSTOM_MERGE:
        network_paths = network.getPropagationPaths()
        number_total_paths = len(network_paths)
        try:
            path_indices = merge_parameters['custom_merge_paths']
            valid = True
            for index in path_indices:
                if index < 0 or index > number_total_paths-1:
                    valid = False
                    print("Error in custom_merge_paths argument")
                    exit()
        except:
            print("Error in custom_merge_paths argument")
            exit()
            
        path_merged = None
        for i in path_indices:
            path_to_merge = network_paths[i]
            if path_merged is None:
                path_merged = path_to_merge.create_copy()
            else:
                path_merged.addAssetPath(path_to_merge.getAssetPaths()[0])
                path_merged.addService(path_to_merge.getServices()[0])
                path_merged.addActivity(path_to_merge.getActivities()[0])
                path_merged.addProcess(path_to_merge.getProcesses()[0])

        if path_merged is not None:
            paths.append(path_merged)



    return paths


def pathAlreadyInList(path, paths_list, merge_option):
    if merge_option is MERGE_ACTIVITIES:
        for path_ in paths_list:
            if path.getEntrypointVulnerability() == path_.getEntrypointVulnerability() and path.getAssetPaths()[0] == path_.getAssetPaths()[0] and path.getServices()[0] == path_.getServices()[0]:
                return path_
        return None

    if merge_option is MERGE_SERVICES:
        for path_ in paths_list:
            if path.getEntrypointVulnerability() == path_.getEntrypointVulnerability() and path.getAssetPaths()[0] == path_.getAssetPaths()[0]:
                return path_
        return None

    if merge_option is MERGE_ASSETS:
        for path_ in paths_list:
            if path.getEntrypointVulnerability() == path_.getEntrypointVulnerability():
                return path_
        return None

def parseMergeOption(merge_parameters):
    merge_option_str = merge_parameters['merge_option']
    if merge_option_str == 'CUSTOM_MERGE':
        return CUSTOM_MERGE
    if merge_option_str == 'MERGE_ASSETS':
        return MERGE_ASSETS
    if merge_option_str == 'MERGE_SERVICES':
        return MERGE_SERVICES
    if merge_option_str == 'MERGE_ACTIVITIES':
        return MERGE_ACTIVITIES
    return NO_MERGE