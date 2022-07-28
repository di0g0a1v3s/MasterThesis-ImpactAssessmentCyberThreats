import json
from network_entities import Process, ProcessElement, Activity
from parallel_branches_business_process import getParallelBranches

f = open('Impact Assessment/ParallelTest2.json', 'r')
data = json.load(f)
f.close()

process_info = data['businessProcesses'][0]['process']
process = Process(process_info['id'], process_info['name'])
for element in process_info['elements']:
    new_process_element = ProcessElement(element['id'], element['name'],  element['elementType'], process)
    
    if element['elementType'] == 'ActivityType':
        act = Activity(element['id'], element['name'])
        new_process_element.setActivity(act)
    
    process.addProcessElement(new_process_element)

for branch in process_info['branches']:
    prev_element = process.getProcessElement(branch['prevElement'])
    next_element = process.getProcessElement(branch['nextElement'])
    
    prev_element.addNextElement(next_element)
    next_element.addPrevElement(prev_element)

branches = getParallelBranches(process)

for branch in branches:
    print('\n\nBRANCH:')
    st = ''
    for activity in branch:
        st = st + str(activity) + ','
    print(st)
