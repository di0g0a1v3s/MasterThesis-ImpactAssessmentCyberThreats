class Network:
    def __init__(self):
        self._processes = {}
        self._activities = {}
        self._services = {}
        self._assets = {}
        self._asset_entrypoint = None
        self._vulnerability_entrypoint = None
        self._propagation_paths = []
        self._routers = {}
        self._subnets = {}

    def addRouter(self, router):
        self._routers[router.getID()] = router

    def getRouter(self, router_id):
        if router_id in self._routers:
            return self._routers[router_id]
        else:
            return None

    def addSubnet(self, subnet):
        self._subnets[subnet.getSubnetPrefix()] = subnet

    def getSubnet(self, subnet_prefix):
        if subnet_prefix in self._subnets:
            return self._subnets[subnet_prefix]
        else:
            return None

    def addPropagationPath(self, path):
        self._propagation_paths.append(path)

    def getPropagationPaths(self):
        return self._propagation_paths.copy()


    def setEntrypoint(self, vulnerability, asset_id):
        self._asset_entrypoint = self.getAsset(asset_id)
        self._vulnerability_entrypoint = vulnerability

    def setEntrypointIF(self, IF):
        self._vulnerability_entrypoint.setImpactFactor(IF) 

    def getEntrypointAsset(self):
        return self._asset_entrypoint
    
    def getEntrypointVulnerability(self):
        return self._vulnerability_entrypoint

    def addProcess(self, process):
        self._processes[process.getID()] = process
    def addActivity(self, activity):
        self._activities[activity.getID()] = activity
    def addService(self, service):
        self._services[service.getID()] = service
    def addAsset(self, asset):
        self._assets[asset.getID()] = asset

    def hasProcess(self, process_id):
        if process_id in self._processes:
            return True
        else:
            return False
    
    def hasActivity(self, activity_id):
        if activity_id in self._activities:
            return True
        else:
            return False

    def hasService(self, service_id):
        if service_id in self._services:
            return True
        else:
            return False
    
    def hasAsset(self, asset_id):
        if asset_id in self._assets:
            return True
        else:
            return False
    
    def getProcess(self, process_id):
        if process_id in self._processes:
            return self._processes[process_id]
        else:
            return None
    
    def getActivity(self, activity_id):
        if activity_id in self._activities:
            return self._activities[activity_id]
        else:
            return None

    def getService(self, service_id):
        if service_id in self._services:
            return self._services[service_id]
        else:
            return None
    
    def getAsset(self, asset_id):
        if asset_id in self._assets:
            return self._assets[asset_id]
        else:
            return None
        
    def getAssetByIp(self, asset_ip):
        for asset_id in self._assets:
            asset = self._assets[asset_id]
            if asset.getIP() == asset_ip:
                return asset
        return None    

    def getServices(self):
        return self._services.values()

    def getActivities(self):
        return self._activities.values()
    
    def getProcesses(self):
        return self._processes.values()

    def __str__(self):
        return "Processes: " + str(self._processes.keys()) + "; Activities: " + str(self._activities.keys()) + "; Services: " + str(self._services.keys()) + "; Assets: " + str(self._assets.keys()) + "; Eytrypoint: ("+ str(self._vulnerability_entrypoint) + "," + str(self._asset_entrypoint) + ")"

    def as_dict(self):
        network_dict = {}
        network_dict['assets'] = []
        for asset_id in self._assets:
            network_dict['assets'].append(self._assets[asset_id].as_dict())

        network_dict['services'] = []
        for service_id in self._services:
            network_dict['services'].append(self._services[service_id].as_dict())

        network_dict['activities'] = []
        for activity_id in self._activities:
            network_dict['activities'].append(self._activities[activity_id].as_dict())

        network_dict['processes'] = []
        for process_id in self._processes:
            network_dict['processes'].append(self._processes[process_id].as_dict())

        
        network_dict['asset_entrypoint'] = self._asset_entrypoint.getID()

        network_dict['vulnerability_entrypoint'] = self._vulnerability_entrypoint.as_dict()
        
        network_dict['routers'] = []
        for router_id in self._routers:
            network_dict['routers'].append(self._routers[router_id].as_dict())

        network_dict['subnets'] = []
        for subnet_prefix in self._subnets:
            network_dict['subnets'].append(self._subnets[subnet_prefix].as_dict())

        network_dict['propagation_paths'] = []
        for propagation_path in self._propagation_paths:
            network_dict['propagation_paths'].append(propagation_path.as_dict())

        return network_dict
    
    @staticmethod
    def load_from_dict(network_dict):
        network = Network()
        for asset_dict in network_dict['assets']:
            network.addAsset(Asset.load_from_dict(asset_dict))

        for router_dict in network_dict['routers']:
            network.addRouter(Router.load_from_dict(router_dict))

        for subnet_dict in network_dict['subnets']:
            network.addSubnet(Subnet.load_from_dict(subnet_dict))

        for service_dict in network_dict['services']:
            network.addService(Service.load_from_dict(service_dict))

        for activity_dict in network_dict['activities']:
            network.addActivity(Activity.load_from_dict(activity_dict))

        process_elements = {}
        process_elements_dicts = {}
        for process_dict in network_dict['processes']:
            network.addProcess(Process.load_from_dict(process_dict))
            process = network.getProcess(process_dict['id'])
            for process_element_dict in process_dict['process_elements']:
                process_element = ProcessElement.load_from_dict(process_element_dict, process)
                process_elements[process_element_dict['id']] = process_element
                process_elements_dicts[process_element_dict['id']] = process_element_dict
                process.addProcessElement(process_element)

        for process_element_dict in process_elements_dicts.values():
            process_element = process_elements[process_element_dict['id']]
            activity = network.getActivity(process_element_dict['activity'])
            process_element.setActivity(activity)
            for next_element_id in process_element_dict['next_elements']:
                next_element = process_elements[next_element_id]
                process_element.addNextElement(next_element)
            for prev_element_id in process_element_dict['prev_elements']:
                prev_element = process_elements[prev_element_id]
                process_element.addPrevElement(prev_element)

        for activity_dict in network_dict['activities']:
            activity = network.getActivity(activity_dict['id'])
            for service_id in activity_dict['services']:
                activity.addService(network.getService(service_id))
            for process_element_id in activity_dict['process_elements']:
                activity.addProcessElement(process_elements[process_element_id])

        for service_dict in network_dict['services']:
            service = network.getService(service_dict['id'])
            for activity_id in service_dict['activities']:
                service.addActivity(network.getActivity(activity_id))
            for asset_id in service_dict['assets']:
                service.addAsset(network.getAsset(asset_id))

        for asset_dict in network_dict['assets']:
            asset = network.getAsset(asset_dict['id'])
            for subnet_prefix in asset_dict['subnets']:
                asset.addSubnet(network.getSubnet(subnet_prefix))
            for service_id in asset_dict['services']:
                asset.addService(network.getService(service_id))

        for router_dict in network_dict['routers']:
            router = network.getRouter(router_dict['id'])
            for subnet_prefix in router_dict['subnets']:
                router.addSubnet(network.getSubnet(subnet_prefix))
            for router_id in router_dict['routers']:
                router.addRouter(network.getRouter(router_id))

        for subnet_dict in network_dict['subnets']:
            subnet = network.getSubnet(subnet_dict['subnet_prefix'])
            for asset_id in subnet_dict['assets']:
                subnet.addAsset(network.getAsset(asset_id))
            for router_id in subnet_dict['routers']:
                subnet.addRouter(network.getRouter(router_id))

        entrypoint_vulnerability = Vulnerability.load_from_dict(network_dict['vulnerability_entrypoint'])
        entrypoint_asset_id = network_dict['asset_entrypoint']
        network.setEntrypoint(entrypoint_vulnerability, entrypoint_asset_id)

        
        for propagation_path_dict in network_dict['propagation_paths']:
            propagation_path = Propagation_Path()
            propagation_path.setEntrypointVulnerability(network.getEntrypointVulnerability())
            for asset_path_dict in propagation_path_dict['asset_paths']:
                asset_path = Asset_Path()
                for asset in asset_path_dict['assets']:
                    if asset['type'] == 'Asset':
                        asset_path.addAsset(network.getAsset(asset['id']))
                    elif asset['type'] == 'Subnet':
                        asset_path.addAsset(network.getSubnet(asset['subnet_prefix']))
                    elif asset['type'] == 'Router':
                        asset_path.addAsset(network.getRouter(asset['id']))
                    
                propagation_path.addAssetPath(asset_path)
            for service_id in propagation_path_dict['services']:
                propagation_path.addService(network.getService(service_id))
            for activity_id in propagation_path_dict['activities']:
                propagation_path.addActivity(network.getActivity(activity_id))      
            for process_id in propagation_path_dict['processes']:
                propagation_path.addProcess(network.getProcess(process_id))     

            network.addPropagationPath(propagation_path)

        return network        


        

class Vulnerability:

    def __init__(self, name):
        self._name = name
        self._impact_factor = 0
        self._stride_classification = None

    def getName(self):
        return self._name[:]

    def setImpactFactor(self, impact_factor):
        self._impact_factor = impact_factor

    def getImpactFactor(self):
        return self._impact_factor

    def setStrideClassification(self, stride_classification):
        self._stride_classification = stride_classification

    def getStrideClassification(self):
        return self._stride_classification

    def __str__(self):
        return "Vulnerability <name: "+str(self._name)+">" 

    def as_dict(self):
        vulnerability_dict = {}
        vulnerability_dict['name'] = self.getName()
        vulnerability_dict['impact_factor'] = self.getImpactFactor()
        vulnerability_dict['stride_classification'] = self.getStrideClassification()
        return vulnerability_dict

    @staticmethod
    def load_from_dict(vulnerability_dict):
        vulnerability = Vulnerability(vulnerability_dict['name'])
        vulnerability.setImpactFactor(vulnerability_dict['impact_factor'])
        vulnerability.setStrideClassification(vulnerability_dict['stride_classification'])
        return vulnerability

class Router:
    def __init__(self, id):
        self._id = id
        self._subnets = []
        self._routers = []

    def getID(self):
        return self._id

    def addSubnet(self, subnet):
        if subnet not in self._subnets:
            self._subnets.append(subnet)

    def getSubnets(self):
        return self._subnets.copy()

    def addRouter(self, router):
        if router not in self._routers:
            self._routers.append(router)

    def getRouters(self):
        return self._routers.copy()

    def __str__(self):
        return "Router <id: "+str(self._id)+">"  

    def as_dict(self):
        router_dict = {}
        router_dict['id'] = self.getID()
        router_dict['subnets'] = []
        for subnet in self.getSubnets():
            router_dict['subnets'].append(subnet.getSubnetPrefix())
        router_dict['routers'] = []
        for router in self.getRouters():
            router_dict['routers'].append(router.getID())
        return router_dict

    @staticmethod
    def load_from_dict(router_dict):
        router = Router(router_dict['id'])
        return router

class Subnet:
    def __init__(self, subnet_prefix):
        self._subnet_prefix = subnet_prefix
        self._assets = []
        self._routers = []

    def getSubnetPrefix(self):
        return self._subnet_prefix

    def addAsset(self, asset):
        if asset not in self._assets:
            self._assets.append(asset)
    
    def addRouter(self, router):
        if router not in self._routers:
            self._routers.append(router)

    def getAssets(self):
        return self._assets.copy()

    def getRouters(self):
        return self._routers.copy()

    def __str__(self):
        return "Subnet <prefix: "+str(self._subnet_prefix)+">"  

    def as_dict(self):
        subnet_dict = {}
        subnet_dict['subnet_prefix'] = self.getSubnetPrefix()
        subnet_dict['assets'] = []
        for asset in self.getAssets():
            subnet_dict['assets'].append(asset.getID())
        subnet_dict['routers'] = []
        for router in self.getRouters():
            subnet_dict['routers'].append(router.getID())
        return subnet_dict

    @staticmethod
    def load_from_dict(subnet_dict):
        subnet = Subnet(subnet_dict['subnet_prefix'])
        return subnet

class Asset:
    def __init__(self, id, ip):
        self._id = id
        self._ip = ip
        #subnets asset is connected to
        self._subnets = []
        #services that the asset runs
        self._services = {}
        #asset's vulnerabilities
        self._vulnerabilities = {}

    def getID(self):
        return self._id[:]

    def getIP(self):
        return self._ip

    def addSubnet(self, subnet):
        if subnet not in self._subnets:
            self._subnets.append(subnet)

    def addService(self, service):
        if service.getID() not in self._services:
            self._services[service.getID()] = service

    def addVulnerability(self, vulnerability):
        if vulnerability.getName() not in self._vulnerabilities:
            self._vulnerabilities[vulnerability.getName()] = vulnerability

    def getSubnets(self):
        return self._subnets

    def getListOfServices(self):
        return list(self._services.values())

    def getVulnerability(self, vuln_name):
        if vuln_name in self._vulnerabilities:
            return self._vulnerabilities[vuln_name]
        else:
            return None

    def getListOfVulnerabilities(self):
        return list(self._vulnerabilities.values())

    def __str__(self):
        return "Asset <ip: "+str(self._ip)+">" 

    def as_dict(self):
        asset_dict = {}
        asset_dict['id'] = self.getID()
        asset_dict['ip'] = self.getIP()
        asset_dict['subnets'] = []
        asset_dict['vulnerabilities'] = []
        for subnet in self.getSubnets():
            asset_dict['subnets'].append(subnet.getSubnetPrefix())
        asset_dict['services'] = []
        for service in self.getListOfServices():
            asset_dict['services'].append(service.getID())
        for vulnerability in self.getListOfVulnerabilities():
            asset_dict['vulnerabilities'].append(vulnerability.as_dict())
        return asset_dict

    @staticmethod
    def load_from_dict(asset_dict):
        asset = Asset(asset_dict['id'], asset_dict['ip'])
        for vulnerability_dict in asset_dict['vulnerabilities']:
            vulnerability = Vulnerability.load_from_dict(vulnerability_dict)
            asset.addVulnerability(vulnerability)
        return asset



class Service:
    def __init__(self, id, name, network_port):
        self._id = id
        self._network_port = network_port
        self._name = name
        #activities that the service provides
        self._activities = {}
        #assets that run the service
        self._assets = {}

    def getID(self):
        return self._id[:]
    
    def getName(self):
        return self._name[:]

    def getNetworkPort(self):
        return self._network_port

    def addActivity(self, activity):
        if activity.getID() not in self._activities:
            self._activities[activity.getID()] = activity

    def getListOfActivities(self):
        return list(self._activities.values())

    def addAsset(self, asset):
        if asset.getID() not in self._assets:
            self._assets[asset.getID()] = asset

    def getListOfAssets(self):
        return list(self._assets.values())

    def __str__(self):
        return "Service <name: "+str(self._name)+ ",id:" + str(self._id) + ">" 

    def as_dict(self):
        service_dict = {}
        service_dict['id'] = self.getID()
        service_dict['name'] = self.getName()
        service_dict['network_port'] = self.getNetworkPort()
        service_dict['activities'] = []
        for activity in self.getListOfActivities():
            service_dict['activities'].append(activity.getID())
        service_dict['assets'] = []
        for asset in self.getListOfAssets():
            service_dict['assets'].append(asset.getID())
        return service_dict

    @staticmethod
    def load_from_dict(service_dict):
        service = Service(service_dict['id'], service_dict['name'], service_dict['network_port'])
        return service



class Activity:
    def __init__(self, id, name):
        self._id = id
        self._name = name
        #process elements associated with the activity
        self._processElements = {}
        #services that provide the activity
        self._services = {}       
    

    def getID(self):
        return self._id[:]

    def getName(self):
        return self._name[:]
    
    def addService(self, service):
        if service.getID() not in self._services:
            self._services[service.getID()] = service

    def getListOfServices(self):
        return list(self._services.values())

    def addProcessElement(self, processElement):
        if processElement.getID() not in self._processElements:
            self._processElements[processElement.getID()] = processElement

    def getListOfProcessElements(self):
        return list(self._processElements.values())

    def __str__(self):
        return "Activity <name: "+str(self._name)+">" 

    def as_dict(self):
        activity_dict = {}
        activity_dict['id'] = self.getID()
        activity_dict['name'] = self.getName()
        activity_dict['process_elements'] = []
        for process_element in self.getListOfProcessElements():
            activity_dict['process_elements'].append(process_element.getID())
        activity_dict['services'] = []
        for service in self.getListOfServices():
            activity_dict['services'].append(service.getID())
        return activity_dict

    @staticmethod
    def load_from_dict(activity_dict):
        activity = Activity(activity_dict['id'], activity_dict['name'])
        return activity


class Process:
    def __init__(self, id, name):
        self._id = id
        self._name = name
        self._processElements = {}

    def getID(self):
        return self._id[:]

    def getName(self):
        return self._name[:]
    
    def hasProcessElement(self, processElement_id):
        if processElement_id in self._processElements:
            return True
        else:
            return False

    def addProcessElement(self, processElement):
        if processElement.getID() not in self._processElements:
            self._processElements[processElement.getID()] = processElement

    def getProcessElements(self):
        return self._processElements.values()

    def getProcessElement(self, processElement_id):
        if processElement_id in self._processElements:
            return self._processElements[processElement_id]
        else:
            return None

    def getStartElement(self):
        for element in self._processElements.values():
            if element.getType() == 'Start':
                return element

    def getEndElement(self):
        for element in self._processElements.values():
            if element.getType() == 'End':
                return element

    
    def __str__(self):
        return "Process <name: "+str(self._name)+">" 

    def as_dict(self):
        process_dict = {}
        process_dict['id'] = self.getID()
        process_dict['name'] = self.getName()
        process_dict['process_elements'] = []
        for process_element in self.getProcessElements():
            process_dict['process_elements'].append(process_element.as_dict())
        return process_dict

    @staticmethod
    def load_from_dict(process_dict):
        process = Process(process_dict['id'], process_dict['name'])
        return process

class ProcessElement():
    def __init__(self, id, name, type, process):
        self._id = id
        self._name = name
        self._type = type
        self._process = process
        self._activity = None
        self._nextElements = []
        self._prevElements = []

    def getID(self):
        return self._id[:]

    def getName(self):
        return self._name[:]

    def getType(self):
        return self._type[:]

    def getProcess(self):
        return self._process

    def setActivity(self, activity):
        self._activity = activity

    def getActivity(self):
        return self._activity
    
    def addNextElement(self, nextElement):
        self._nextElements.append(nextElement)

    def addPrevElement(self, prevElement):
        self._prevElements.append(prevElement)

    def getNextElements(self):
        return self._nextElements
    
    def getPrevElements(self):
        return self._prevElements
    
    def __str__(self):
        return "ProcessElement <name:" + self._name + ", type:" + self._type + ">"

    def as_dict(self):
        process_element_dict = {}
        process_element_dict['id'] = self.getID()
        process_element_dict['name'] = self.getName()
        process_element_dict['type'] = self.getType()
        process_element_dict['process'] = self.getProcess().getID()
        if self.getActivity() is None:
            process_element_dict['activity'] = ''
        else:
            process_element_dict['activity'] = self.getActivity().getID()
        process_element_dict['next_elements'] = []
        for next_element in self.getNextElements():
            process_element_dict['next_elements'].append(next_element.getID())
        process_element_dict['prev_elements'] = []
        for prev_element in self.getPrevElements():
            process_element_dict['prev_elements'].append(prev_element.getID())
        return process_element_dict

    @staticmethod
    def load_from_dict(process_element_dict, process):
        process_element = ProcessElement(process_element_dict['id'], process_element_dict['name'], process_element_dict['type'], process)
        return process_element


class Asset_Path:
    def __init__(self):
        self._assets = []

    def getFirstAsset(self):
        return self._assets[0]
    
    def getNextAsset(self, current_asset):
        i = 0
        for asset in self._assets:
            i = i + 1
            if current_asset == asset:
                break
        try:
            return self._assets[i]
        except:
            return None
    
    def getAssets(self):
        return self._assets

    def addAsset(self, asset):
        self._assets.append(asset)

    def hasAsset(self, asset_id):
        if asset_id in self._assets:
            return True
        else:
            return False

    def create_copy(self):
        new_asset_path = Asset_Path()
        new_asset_path._assets = self._assets.copy()
        return new_asset_path

    def __str__(self):
        path_str = ""
        for asset in self._assets:
            path_str = path_str + " -> " + str(asset) 
        return path_str

    def __eq__(self, other):
        if self._assets == other._assets:
            return True
        else:
            return False

    def as_dict(self):
        asset_path_dict = {}
        asset_path_dict['assets'] = []
        for asset in self.getAssets():
            if isinstance(asset, Asset):
                asset_path_dict['assets'].append({"type":"Asset", "id": asset.getID(), "ip": asset.getIP()})
            elif isinstance(asset, Router):
                asset_path_dict['assets'].append({"type":"Router", "id": asset.getID()})
            elif isinstance(asset, Subnet):
                asset_path_dict['assets'].append({"type":"Subnet", "subnet_prefix": asset.getSubnetPrefix()})
        return asset_path_dict

class Propagation_Path:
    def __init__(self):
        self._entrypoint_vulnerability = None
        self._asset_paths = []
        self._services = []
        self._activities = []
        self._processes = []
        self._OCs = {}
        self._impact = 0
        self._exploited_vulns = {}

    def getImpact(self):
        return self._impact

    def setImpact(self,impact):
        self._impact = impact

    def getAssetPaths(self):
        return self._asset_paths
    
    def getEntrypointVulnerability(self):
        return self._entrypoint_vulnerability

    def getServices(self):
        return self._services
    
    def getActivities(self):
        return self._activities
    
    def getProcesses(self):
        return self._processes

    def setEntrypointVulnerability(self, entrypoint_vulnerability):
        self._entrypoint_vulnerability = entrypoint_vulnerability

    def addAssetPath(self, asset_path):
        if asset_path not in self._asset_paths:
            self._asset_paths.append(asset_path)

    def addService(self, service):
        if service not in self._services:
            self._services.append(service)

    def addActivity(self, activity):
        if activity not in self._activities:
            self._activities.append(activity)

    def addProcess(self, process):
        if process not in self._processes:
            self._processes.append(process)

    def initializeOCs(self):
        for asset_path in self._asset_paths:
            for asset in asset_path.getAssets():
                self._OCs[asset] = 1

        for service in self._services:
            self._OCs[service] = 1

        for activity in self._activities:
            self._OCs[activity] = 1
        
        for process in self._processes:
            self._OCs[process] = 1

    def getOC(self, node):
        if node in self._OCs:
            return self._OCs[node]
        else:
            return None

    def getAssetOC(self, asset_id):
        for node in self._OCs:
            if isinstance(node, Asset) and node.getID() == asset_id:
                return self.getOC(node)
        return 1

    def getRouterOC(self, router_id):
        for node in self._OCs:
            if isinstance(node, Router) and node.getID() == router_id:
                return self.getOC(node)
        return 1

    def getSubnetOC(self, subnet_prefix):
        for node in self._OCs:
            if isinstance(node, Subnet) and node.getSubnetPrefix() == subnet_prefix:
                return self.getOC(node)
        return 1

    def getServiceOC(self, service_id):
        for node in self._OCs:
            if isinstance(node, Service) and node.getID() == service_id:
                return self.getOC(node)
        return 1
    
    def getActivityOC(self, activity_id):
        for node in self._OCs:
            if isinstance(node, Activity) and node.getID() == activity_id:
                return self.getOC(node)
        return 1

    def getProcessOC(self, process_id):
        for node in self._OCs:
            if isinstance(node, Activity) and node.getID() == process_id:
                return self.getOC(node)
        return 1

    def updateOC(self, node, value):
        if node in self._OCs:
            self._OCs[node] = value

    def setExploitedVuln(self, asset_id, vuln):
        self._exploited_vulns[asset_id] = vuln


    def create_copy(self):
        new_path = Propagation_Path()
        new_path._entrypoint_vulnerability = self._entrypoint_vulnerability
        for asset_path in self._asset_paths:
            new_path.addAssetPath(asset_path.create_copy())
        new_path._services = self._services.copy()
        new_path._activities = self._activities.copy()
        new_path._processes = self._processes.copy()
        return new_path


    #outputs a string containing the sequence of assets whose ids are in asset_path
    def __str__(self):
        path_string = str(self._entrypoint_vulnerability)
        for asset_path in self._asset_paths:
            path_string = path_string + str(asset_path) + "," 
        path_string = path_string + " -> "
        for service in self._services:
            path_string = path_string + str(service) + ","
        path_string = path_string + " -> "
        for activity in self._activities:
            path_string = path_string + str(activity) + ","
        path_string = path_string + " -> "
        for process in self._processes:
            path_string = path_string + str(process) + ","
        return path_string

    def as_dict(self):
        propagation_path_dict = {}
        propagation_path_dict['entrypoint_vulnerability'] = self.getEntrypointVulnerability().getName()
        propagation_path_dict['asset_paths'] = []
        for asset_path in self.getAssetPaths():
            propagation_path_dict['asset_paths'].append(asset_path.as_dict())
        propagation_path_dict['services'] = []
        for service in self.getServices():
            propagation_path_dict['services'].append(service.getID())
        propagation_path_dict['activities'] = []
        for activity in self.getActivities():
            propagation_path_dict['activities'].append(activity.getID())
        propagation_path_dict['processes'] = []
        for process in self.getProcesses():
            propagation_path_dict['processes'].append(process.getID())

        return propagation_path_dict

    def as_dict_with_impact(self):
        propagation_path_dict = {}
        propagation_path_dict['vulnerability'] = self.getEntrypointVulnerability().getName()
        propagation_path_dict['asset_paths'] = []
        for asset_path in self.getAssetPaths():
            asset_path_dict = asset_path.as_dict()
            for asset in asset_path_dict['assets']:
                if asset['type'] is 'Asset':
                    asset_id = asset['id']
                    asset['OC'] = self.getAssetOC(asset_id)
                    if asset_id in self._exploited_vulns:
                        asset['exploited_vuln'] = self._exploited_vulns[asset_id].getName()
                elif asset['type'] is 'Router':
                    router_id = asset['id']
                    asset['OC'] = self.getRouterOC(router_id)
                elif asset['type'] is 'Subnet':
                    subnet_prefix = asset['subnet_prefix']
                    asset['OC'] = self.getSubnetOC(subnet_prefix)
            propagation_path_dict['asset_paths'].append(asset_path_dict)

        propagation_path_dict['services'] = []
        for service in self.getServices():
            propagation_path_dict['services'].append({'id': service.getID(), 'name':service.getName(), "OC": self.getOC(service)})
        propagation_path_dict['activities'] = []
        for activity in self.getActivities():
            propagation_path_dict['activities'].append({"id":activity.getID(), 'name':activity.getName(),  "OC":self.getOC(activity)})
        propagation_path_dict['processes'] = []
        for process in self.getProcesses():
            propagation_path_dict['processes'].append({"id":process.getID(), 'name':process.getName(),  "OC":self.getOC(process)})
        
        propagation_path_dict['impact'] = self.getImpact()
        
        return propagation_path_dict

