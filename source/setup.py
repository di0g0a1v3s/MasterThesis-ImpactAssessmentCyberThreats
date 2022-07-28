import json
import requests
import Setup.db_queries as db_queries
from Setup.populate_network import populateNetwork
from Setup.compute_paths import computePaths

CONFIG_FILE = 'Impact Assessment/setup_config.json'
BIA_OUTPUT_FILE = 'Impact Assessment/bia_output.json'
NETWORK_FILE = 'Impact Assessment/network.json'
PATHS_FILE = 'Impact Assessment/paths.txt'

def main():
    #obtain configuration arguments
    args = getConfigurationArguments()

    #initialize database handler
    db = db_queries.Neo4j(args['Neo4j_Database_Address'], args['Neo4j_Database_Username'], args['Neo4j_Database_Password'])
    
    #retrieve .json file exported from BIA
    json_data = retrieveBIAOutput(args['BIA_Server_Address'], args['Asset_Entrypoint'], args['Threat_Entrypoint'])

    #write JSON data to file (OPTIONAL)
    with open(BIA_OUTPUT_FILE, 'w') as f:
        json.dump(json_data, f, indent = 2)

    #populate the network with information from the database and the .json file
    network = populateNetwork(db, json_data)
         
    PathsThroughSubnetsOnlyOnce = True
    if args['PathsThroughSubnetsOnlyOnce'].lower() == 'false':
        PathsThroughSubnetsOnlyOnce = False
    PathsThroughRoutersOnlyOnce = True
    if args['PathsThroughRoutersOnlyOnce'].lower() == 'false':
        PathsThroughRoutersOnlyOnce = False

    #identify complete individual paths
    computePaths(network, PathsThroughSubnetsOnlyOnce, PathsThroughRoutersOnlyOnce)

    #save network in .json file
    with open(NETWORK_FILE, 'w') as f:
        json.dump(network.as_dict(), f, indent = 2)

    save_paths_in_file(PATHS_FILE, network.getPropagationPaths())

    
    

def retrieveBIAOutput(bia_address, entrypoint, threat):

    response = requests.get(bia_address + "/simulate?entrypoint=" + entrypoint + "&threat=" + threat)
    response = requests.get(bia_address + "/export-results")
    return response.json()


def getConfigurationArguments():
    with open(CONFIG_FILE, 'r') as f:
        args = json.load(f)
    return args

def save_paths_in_file(file, paths):
    with open(file, 'w') as f:
        i = 0
        for path in paths:
            f.write("PATH " + str(i) + ": " + str(path) + '\n\n')
            i = i+1

main()
