from Setup.network_entities import Asset, Router, Subnet, Propagation_Path, Asset_Path

def computePaths(network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce):
    current_path = Asset_Path()
    explore_paths_starting_in_asset(network.getEntrypointAsset(), current_path, network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce)  
    


#recursive depth first search of paths starting at "asset" 
def explore_paths_starting_in_asset(asset, current_path, network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce):
    current_path.addAsset(asset)
    
    if isinstance(asset, Asset): #Asset -> Subnet
        for next_asset in asset.getSubnets():
            if (PathsThroughSubnetsOnlyOnce == True and not current_path.hasAsset(next_asset)) or PathsThroughSubnetsOnlyOnce == False:  #make sure a subnet does not appear twice in the path (if PathsThroughSubnetsOnlyOnce == True)
                explore_paths_starting_in_asset(next_asset, current_path.create_copy(), network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce) # the .create_copy() is needed because objects are passed by reference

    elif isinstance(asset, Subnet): #Subnet -> Router or Subnet -> Asset
        for next_asset in asset.getRouters():
            if (PathsThroughRoutersOnlyOnce == True and not current_path.hasAsset(next_asset)) or PathsThroughRoutersOnlyOnce == False:  #make sure a router does not appear twice in the path (if PathsThroughRoutersOnlyOnce == True)
                explore_paths_starting_in_asset(next_asset, current_path.create_copy(), network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce) # the .create_copy() is needed because objects are passed by reference
        for next_asset in asset.getAssets():
            if not current_path.hasAsset(next_asset):  #make sure an asset does not appear twice in the path
                explore_paths_starting_in_asset(next_asset, current_path.create_copy(), network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce) # the .create_copy() is needed because objects are passed by reference
    
    
    elif isinstance(asset, Router): #Router -> Router or Router -> Subnet
        for next_asset in asset.getRouters():
            if (PathsThroughRoutersOnlyOnce == True and not current_path.hasAsset(next_asset)) or PathsThroughRoutersOnlyOnce == False:  #make sure a router does not appear twice in the path (if PathsThroughRoutersOnlyOnce == True)
                explore_paths_starting_in_asset(next_asset, current_path.create_copy(), network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce) # the .create_copy() is needed because objects are passed by reference
        for next_asset in asset.getSubnets():
            if (PathsThroughSubnetsOnlyOnce == True and not current_path.hasAsset(next_asset)) or PathsThroughSubnetsOnlyOnce == False:  #make sure a subnet does not appear twice in the path (if PathsThroughSubnetsOnlyOnce == True)
                explore_paths_starting_in_asset(next_asset, current_path.create_copy(), network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce) # the .create_copy() is needed because objects are passed by reference
    
    
    if isinstance(asset, Asset):
        for service in asset.getListOfServices(): #if asset provides services
            for activity in service.getListOfActivities():
                for processElement in activity.getListOfProcessElements():
                    complete_current_path = Propagation_Path()
                    complete_current_path.setEntrypointVulnerability(network.getEntrypointVulnerability())
                    complete_current_path.addAssetPath(current_path)
                    complete_current_path.addService(service)
                    complete_current_path.addActivity(activity)
                    complete_current_path.addProcess(processElement.getProcess())
                    network.addPropagationPath(complete_current_path)