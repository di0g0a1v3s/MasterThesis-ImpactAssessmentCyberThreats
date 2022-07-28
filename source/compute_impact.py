import json
from ImpactCalculation.merge_paths import createPaths
from ImpactCalculation.compute_ocs import computeOCS
from Setup.network_entities import Network

NETWORK_FILE = 'Impact Assessment/network.json'
MERGE_OPTIONS_FILE = 'Impact Assessment/merge_options.json'
OUTPUT_FILE = 'Impact Assessment/output_impact.json'
ENTRYPOINT_IF_FILE = 'Impact Assessment/entrypoint_IF.json'

def main():

    #load the network object from file
    with open(NETWORK_FILE, 'r') as f:
        network = Network.load_from_dict(json.load(f))

    entrypoint_IF = getConfigurationEntrypointIF()
    if entrypoint_IF is not None: #user chose to rewrite entrypoint IF
        network.setEntrypointIF(entrypoint_IF)

    #load merge parameters
    with open(MERGE_OPTIONS_FILE, 'r') as f:
        merge_parameters = json.load(f)
    
    #create the list of paths for which the impact will be calculated, based on the option chosen
    paths = createPaths(network, merge_parameters)

    ComputeOCsForSubnets = True
    if merge_parameters['ComputeOCsForSubnets'].lower() == 'false':
        ComputeOCsForSubnets = False
    ComputeOCsForRouters = True
    if merge_parameters['ComputeOCsForRouters'].lower() == 'false':
        ComputeOCsForRouters = False

    #compute OCS of nodes in each path
    paths_OCS = computeOCS(paths, network, ComputeOCsForSubnets, ComputeOCsForRouters)

    #write impact of each path to output file
    writeOutputFile(paths_OCS)

def writeOutputFile(paths):
    output_dict = {}
    output_dict['paths'] = []
    for path in paths:
        output_dict['paths'].append(path.as_dict_with_impact())

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_dict, f, indent = 2)

def getConfigurationEntrypointIF():
    with open(ENTRYPOINT_IF_FILE, 'r') as f:
        entrypoint_if_parameters = json.load(f)
    if entrypoint_if_parameters['considerOriginalIF'].lower() == "false":
        new_IF = entrypoint_if_parameters['changedIF']
        return new_IF
    else: 
        return None
    



main()