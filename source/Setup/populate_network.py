from Setup.network_entities import Network, Process, ProcessElement, Activity, Service, Asset, Vulnerability, Router, Subnet


def populateNetwork(db, data):
    #populate network's processes/activities/services/assets/vulnerabilities from the database info
    network = Network()
    business_processes_ids = db.get_processes_ids()
    for process_id in business_processes_ids:
        addProcess(network, db, process_id)  #populate from the top to bottom: processes -> process elements (activities) -> services -> assets
    
    #complete network with rest of compromised assets
    for asset_data in data['compromised_assets']:
        asset_id = asset_data[0]['id']
        if not network.hasAsset(asset_id):
            asset_info = db.get_asset_info(asset_id)
            asset = Asset(asset_info['asset_id'], asset_info['ip'])
            addAsset(asset, db, network)

    #populate connections between assets/routers/subnets
    for connectivity in data['explored_connectivity_routers']:
        src_ip = connectivity[0]['ip_src']
        dst_ip = connectivity[0]['ip_dst']
        
        if isAsset(src_ip) and isSubnet(dst_ip):
            src = network.getAssetByIp(src_ip)
            dst = network.getSubnet(dst_ip)
            if dst == None:
                dst = Subnet(dst_ip)
                network.addSubnet(dst)
            dst.addAsset(src)
            src.addSubnet(dst)
            
        if isAsset(dst_ip) and isSubnet(src_ip):
            dst = network.getAssetByIp(dst_ip)
            src = network.getSubnet(src_ip)
            if src == None:
                src = Subnet(src_ip)
                network.addSubnet(src)
            src.addAsset(dst)
            dst.addSubnet(src)

        if isSubnet(src_ip) and isRouter(dst_ip):
            dst = network.getRouter(dst_ip)
            if dst == None:
                dst = Router(dst_ip)
                network.addRouter(dst)
            src = network.getSubnet(src_ip)
            if src == None:
                src = Subnet(src_ip)
                network.addSubnet(src)
            src.addRouter(dst)
            dst.addSubnet(src)

        if isSubnet(dst_ip) and isRouter(src_ip):
            src = network.getRouter(src_ip)
            if src == None:
                src = Router(src_ip)
                network.addRouter(src)
            dst = network.getSubnet(dst_ip)
            if dst == None:
                dst = Subnet(dst_ip)
                network.addSubnet(dst)
            dst.addRouter(src)
            src.addSubnet(dst)

        if isRouter(dst_ip) and isRouter(src_ip):
            src = network.getRouter(src_ip)
            if src == None:
                src = Router(src_ip)
                network.addRouter(src)
            dst = network.getRouter(dst_ip)
            if dst == None:
                dst = Router(dst_ip)
                network.addRouter(dst)
            dst.addRouter(src)
            src.addRouter(dst)

        
    

    #entrypoint asset is the first asset in the compromised assets list
    entrypoint_asset_id = data['compromised_assets'][0][0]['id']

    #entrypoint threat is the first (and only) listed threat of the first asset in the compromised assets list
    entrypoint_threat_name = data['compromised_assets'][0][0]['threats'][0]
    entrypoint_threat = network.getAsset(entrypoint_asset_id).getVulnerability(entrypoint_threat_name)
    
    network.setEntrypoint(entrypoint_threat, entrypoint_asset_id)

    return network



def addProcess(network, db, process_id):
    process_info = db.get_process_info(process_id)
    process = Process(process_info['process_id'], process_info['name'])
    network.addProcess(process)
    process_flows = db.get_process_processflows(process_id)
    for process_flow_id in process_flows:
        process_flow_info = db.get_process_processflow_info(process_flow_id)
        prev_processElement_id = process_flow_info['prevProcessElement_id']
        next_processElement_id = process_flow_info['nextProcessElement_id']
        prev_processElement = addProcessElement(process, network, db, prev_processElement_id)
        next_processElement = addProcessElement(process, network, db, next_processElement_id)
        prev_processElement.addNextElement(next_processElement)
        next_processElement.addPrevElement(prev_processElement)
    return process


def addProcessElement(process, network, db, processElement_id):
    if process.hasProcessElement(processElement_id):
        processElement = process.getProcessElement(processElement_id)
    else:
        processElement_info = db.get_processElement_info(processElement_id)
        processElement = ProcessElement(processElement_info['id'], processElement_info['name'], processElement_info['type'], process)
        processElement_activity_id = processElement_info['activity_id']
        if processElement_activity_id is not None:
            processElement_activity = addActivity(processElement, network, db, processElement_activity_id)
            processElement.setActivity(processElement_activity)
        process.addProcessElement(processElement)
    return processElement


def addActivity(processElement, network, db, activity_id):
    if network.hasActivity(activity_id):
        activity = network.getActivity(activity_id)
        activity.addProcessElement(processElement)
    else:
        activity_info = db.get_activity_info(activity_id)
        activity = Activity(activity_info['activity_id'], activity_info['name'])
        activity.addProcessElement(processElement)
        network.addActivity(activity)
        activity_services = db.get_activity_services(activity_id)
        for service_id in activity_services:
            if network.hasService(service_id):
                service = network.getService(service_id)
                service.addActivity(activity)
                activity.addService(service)
            else:
                service_info = db.get_service_info(service_id)
                service = Service(service_info['service_id'], service_info['name'], service_info['network_port'])
                service.addActivity(activity)
                activity.addService(service)
                network.addService(service)  
                service_assets = db.get_service_assets(service_id)
                for asset_id in service_assets:
                    if network.hasAsset(asset_id):
                        asset = network.getAsset(asset_id)
                        asset.addService(service)
                        service.addAsset(asset)
                    else:
                        asset_info = db.get_asset_info(asset_id)
                        asset = Asset(asset_info['asset_id'], asset_info['ip'])
                        asset.addService(service)
                        addAsset(asset, db, network)
                        service.addAsset(asset)
    return activity


def addAsset(asset, db, network):
    vulnerabilities_names = db.get_asset_threats(asset.getID())
    for vuln_name in vulnerabilities_names:
        vuln = Vulnerability(vuln_name)
        vuln_info = db.get_threat_info(vuln_name)
        vuln.setImpactFactor(float(vuln_info['vulnerability_impact'])/10)
        vuln.setStrideClassification(vuln_info['stride_classification'])
        asset.addVulnerability(vuln)
    network.addAsset(asset)
    



#determines if "ip" in the json's field "explored_connectivity_routers" corresponds to an asset
def isAsset(ip):
    if not isSubnet(ip) and not isRouter(ip):
        return True
    return False
#determines if "ip" in the json's field "explored_connectivity_routers" corresponds to a subnet
def isSubnet(ip):
    if '/' in ip:
        return True
    return False
#determines if "ip" in the json's field "explored_connectivity_routers" corresponds to a router
def isRouter(ip):
    if 'router' in ip:
        return True
    return False