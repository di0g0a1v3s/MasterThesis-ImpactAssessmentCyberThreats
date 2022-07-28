from neo4j import GraphDatabase

class Neo4j(object):


    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
    
    #GET /DB/processes/ -> Returns list of all ids of processes
    def get_processes_ids(self):
        output = []
        with self._driver.session() as session:
            result = session.read_transaction(self._query_get_processes_ids)

        for record in result:
            output.append(record[0])

        return output

    @staticmethod
    def _query_get_processes_ids(tx):
        result = tx.run("MATCH (p:Process) RETURN p.process_id ")
        return result


    #GET /DB/processes/<int:process_id>/ -> Returns dict with name of process with id=process_id
    def get_process_info(self, process_id):
        output = {}
        with self._driver.session() as session:
            process = session.read_transaction(self._query_get_process, process_id)

        process_info = process.single()[0]
        output['process_id'] = process_info['process_id']
        output['name'] = process_info['name']
        

        return output

    @staticmethod
    def _query_get_process(tx, process_id):
        result = tx.run("MATCH (p:Process{process_id:$process_id}) RETURN p LIMIT 1", process_id=process_id)
        return result



    #GET /DB/processes/<int:process_id>/activities/ -> Returns list of all ids of activities that SUPPORT process with id=process_id
    def get_process_activities(self, process_id):
        output = []
        with self._driver.session() as session:
            activities = session.read_transaction(self._query_get_process_activities, process_id)

        for activity in activities:
            output.append(activity[0])

        return output

    @staticmethod
    def _query_get_process_activities(tx, process_id):
        result = tx.run("MATCH (:Process{process_id:$process_id})-[:SUPPORTS]-(activity:Activity) RETURN activity.activity_id", process_id=process_id)
        return result

    #GET /DB/processes/<int:process_id>/process_flows/ -> Returns list of all ids of process_flows that the process with id=process_id HAS
    def get_process_processflows(self, process_id):
        output = []
        with self._driver.session() as session:
            processflows = session.read_transaction(self._query_get_process_processflows, process_id)

        for processflow in processflows:
            output.append(processflow[0])

        return output

    @staticmethod
    def _query_get_process_processflows(tx, process_id):
        result = tx.run("MATCH (:Process{process_id:$process_id})-[:COMPOSED]-(processflow:Process_Flow) RETURN processflow.id", process_id=process_id)
        return result



    #GET /DB/process_flows/<int:process_flow_id>/ -> Returns dict with name, branch_id, and ids of process_elements corresponding to prevElement and nextElement of process_flow with id=process_flow_id
    def get_process_processflow_info(self, processflow_id):
        output = {}
        with self._driver.session() as session:
            processflow = session.read_transaction(self._query_get_processflow, processflow_id)
        
        processflow_info = processflow.single()[0]
        
        output['id'] = processflow_info['id']
        output['branch_id'] = processflow_info['branch_id']
        output['name'] = processflow_info['name']
        

        with self._driver.session() as session:
            nextprocessElement = session.read_transaction(self._query_get_next_processElement, processflow_id)
        
        nextprocessElement_info = nextprocessElement.single()[0]
        output['nextProcessElement_id'] = nextprocessElement_info['id']


        with self._driver.session() as session:
            prevprocessElement = session.read_transaction(self._query_get_prev_processElement, processflow_id)
        
        prevprocessElement_info = prevprocessElement.single()[0]
        output['prevProcessElement_id'] = prevprocessElement_info['id']
        
        return output

    @staticmethod
    def _query_get_processflow(tx, processflow_id):
        result = tx.run("MATCH (pf:Process_Flow{id:$processflow_id}) RETURN pf LIMIT 1", processflow_id=processflow_id)
        return result   

    @staticmethod
    def _query_get_next_processElement(tx, processflow_id):
        result = tx.run("MATCH (:Process_Flow{id:$processflow_id})-[:NextElement]-(processElement:Process_Element) RETURN processElement", processflow_id=processflow_id)
        return result 

    @staticmethod
    def _query_get_prev_processElement(tx, processflow_id):
        result = tx.run("MATCH (:Process_Flow{id:$processflow_id})-[:PrevElement]-(processElement:Process_Element) RETURN processElement", processflow_id=processflow_id)
        return result 

    #GET /DB/process_elements/<int:process_element_id>/ -> Returns dict with name, type and id of activity that corresponds to process_element with id=process_element_id
    def get_processElement_info(self, processElement_id):
        output = {}
        with self._driver.session() as session:
            processElement = session.read_transaction(self._query_get_processElement, processElement_id)

        processElement_info = processElement.single()[0]
        output['id'] = processElement_info['id']
        output['name'] = processElement_info['name']
        output['type'] = processElement_info['elementType']

        with self._driver.session() as session:
            activity = session.read_transaction(self._query_get_processElement_Activity, processElement_id)
        
        try:
            activity_info = activity.single()[0]
            output['activity_id'] = activity_info['activity_id']
        except:
            output['activity_id'] = None #there is no activity assotiated with the process element

        return output

    @staticmethod
    def _query_get_processElement(tx, processElement_id):
        result = tx.run("MATCH (pe:Process_Element{id:$processElement_id}) RETURN pe LIMIT 1", processElement_id=processElement_id)
        return result

    @staticmethod
    def _query_get_processElement_Activity(tx, processElement_id):
        result = tx.run("MATCH (pe:Process_Element{id:$processElement_id})-[:IS_A]-(a:Activity) RETURN a", processElement_id=processElement_id)
        return result

    #GET /DB/activities/<int:activity_id>/ -> Returns dict with name of activity with id=activity_id
    def get_activity_info(self, activity_id):
        output = {}
        with self._driver.session() as session:
            activity = session.read_transaction(self._query_get_activity, activity_id)

        activity_info = activity.single()[0]
        output['activity_id'] = activity_info['activity_id']
        output['name'] = activity_info['name']
        
        return output

    @staticmethod
    def _query_get_activity(tx, activity_id):
        result = tx.run("MATCH (a:Activity{activity_id:$activity_id}) RETURN a LIMIT 1", activity_id=activity_id)
        return result


    #GET /DB/activities/<int:activity_id>/services/ -> Returns list of all ids of services that PROVIDE activity with id=activity_id
    def get_activity_services(self, activity_id):
        output = []
        with self._driver.session() as session:
            services = session.read_transaction(self._query_get_activity_services, activity_id)

        for service in services:
            output.append(service[0])

        return output

    @staticmethod
    def _query_get_activity_services(tx, activity_id):
        result = tx.run("MATCH (:Activity{activity_id:$activity_id})-[:PROVIDES]-(s:Service) RETURN s.service_id", activity_id=activity_id)
        return result

    #GET /DB/services/<int:service_id>/ -> Returns dict with Network_service name and Network_service network_port of service with id=service_id
    def get_service_info(self, service_id):
        output = {}
        with self._driver.session() as session:
            networkService = session.read_transaction(self._query_get_service_networkService, service_id)

        networkService_info = networkService.single()[0]
        output['service_id'] = service_id
        output['name'] = networkService_info['name']
        output['network_port'] = networkService_info['network_port']

        return output

    @staticmethod
    def _query_get_service_networkService(tx, service_id):
        result = tx.run("MATCH (s:Service{service_id:$service_id})-[:IS_A]-(ns:Network_Service) RETURN ns", service_id=service_id)
        return result
    
    
    #GET /DB/services/<int:service_id>/assets/ -> Returns list of all ids of assets that RUN service with id=service_id
    def get_service_assets(self, service_id):
        output = []
        with self._driver.session() as session:
            assets = session.read_transaction(self._query_get_service_assets, service_id)

        for asset in assets:
            output.append(asset[0])

        return output

    @staticmethod
    def _query_get_service_assets(tx, service_id):
        result = tx.run("MATCH (:Service{service_id:$service_id})-[:RUNS]-(a:Asset) RETURN a.asset_id", service_id=service_id)
        return result

    #GET /DB/assets/<int:asset_id>/ -> Returns dict with Network_interface's ip_address and list of Type classifications of asset with id=asset_id
    def get_asset_info(self, asset_id):
        output = {}
        with self._driver.session() as session:
            network_interface = session.read_transaction(self._query_get_asset_network_interface, asset_id)

        network_interface_info = network_interface.single()[0]
        output['asset_id'] = asset_id
        output['ip'] = network_interface_info['ip_address']
    
        with self._driver.session() as session:
            types = session.read_transaction(self._query_get_asset_types, asset_id)

        output['types'] = []        
        for type in types:
            output['types'].append(type[0]['classification'])

        return output

    @staticmethod
    def _query_get_asset_network_interface(tx, asset_id):
        result = tx.run("MATCH (:Asset{asset_id:$asset_id})-[:HAS]-(ni:Network_interface) RETURN ni", asset_id=asset_id)
        return result

    @staticmethod
    def _query_get_asset_types(tx, asset_id):
        result = tx.run("MATCH (:Asset{asset_id:$asset_id})-[:BELONGS_TO]-(t:Type) RETURN t", asset_id=asset_id)
        return result
    
    #GET /DB/assets/<int:asset_id>/threats/ -> Returns list of all names of threats that asset with id=asset_id HAS
    def get_asset_threats(self, asset_id):
        output = []
        with self._driver.session() as session:
            threats = session.read_transaction(self._query_get_asset_threats, asset_id)

        for threat in threats:
            output.append(threat[0])

        return output

    @staticmethod
    def _query_get_asset_threats(tx, asset_id):
        result = tx.run("MATCH (:Asset{asset_id:$asset_id})-[:HAS]-(t:Threat) RETURN t.name", asset_id=asset_id)
        return result


    #GET /DB/threats/<str:threat_name>/ -> Returns dict with vulnerability_impact, probability and STRIDE Classification of threat with name=threat_name
    def get_threat_info(self, threat_name):
        output = {}
        with self._driver.session() as session:
            threat = session.read_transaction(self._query_get_threat, threat_name)

        threat_info = threat.single()[0]
        output['name'] = threat_info['name']
        output['vulnerability_impact'] = threat_info['vulnerability_impact']
        output['probability'] = threat_info['probability']

        with self._driver.session() as session:
            stride = session.read_transaction(self._query_get_threat_stride, threat_name)

        stride_info = stride.single()[0]
        output['stride_classification'] = stride_info['classification']

        return output

    @staticmethod
    def _query_get_threat(tx, threat_name):
        result = tx.run("MATCH (t:Threat{name:$threat_name}) RETURN t LIMIT 1 ", threat_name=threat_name)
        return result

    @staticmethod
    def _query_get_threat_stride(tx, threat_name):
        result = tx.run("MATCH (:Threat{name:$threat_name})-[:BELONGS]-(s:STRIDE) RETURN s", threat_name=threat_name)
        return result

