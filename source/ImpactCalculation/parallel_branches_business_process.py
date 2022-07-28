from collections import deque

#returns the possible sets of activities that constitute a branch in a business process
def getParallelBranches(process):
    start_node = process.getStartElement()
    current_branch = []
    list_of_branches = [] #in the end, this list will contain all branches found
    list_of_branches.append(current_branch)
    return_here = deque()  #stack with set of nodes to return to
    for node in start_node.getNextElements():
        explore_branch(node, current_branch, return_here, list_of_branches)

    return list_of_branches
    
        
#recursive depth first search of branch starting in current_node
def explore_branch(current_node, current_branch, return_here, list_of_branches):
    #end is reached, if there are still nodes to return to in the stack, return to the first
    if current_node.getType() == 'End':  
        if len(return_here) == 0:
            return
        else:
            next_node  = return_here.pop()
            explore_branch(next_node, current_branch, return_here, list_of_branches)
        
    #EXCLUSIVEGATEWAY ou INCLUSIVEGATEWAY - split the branch
    elif (current_node.getType() == 'EXCLUSIVEGATEWAY' or current_node.getType() == 'INCLUSIVEGATEWAY') and 'Before' in current_node.getID():
        exclusive_branch_nodes = current_node.getNextElements()
        number_exclusive_branches = len(exclusive_branch_nodes)
        #outwards_branches will contain n copies of the current branch
        outwards_branches = []
        outwards_branches.append(current_branch)
        #outwards_return_here will contain n copies of the current stack of nodes to return to
        outwards_return_here = []
        outwards_return_here.append(return_here)
        for i in range(1,number_exclusive_branches):
            branch_copy = current_branch.copy()
            return_here_copy = return_here.copy()
            outwards_return_here.append(return_here_copy)
            list_of_branches.append(branch_copy)
            outwards_branches.append(branch_copy)
        
        #split this branch into n branches leaving the EXCLUSIVEGATEWAY or INCLUSIVEGATEWAY
        for i in range(number_exclusive_branches):
            explore_branch(exclusive_branch_nodes[i], outwards_branches[i], outwards_return_here[i], list_of_branches)
        
    #ignore LOOPGATEWAY as to not enter in a cycle
    elif current_node.getType() == 'LOOPGATEWAY' and 'After' in current_node.getID():
        for node in current_node.getNextElements():
            if node.getType() == 'LOOPGATEWAY' and 'Before'+current_node.getID().replace('After','') in node.getID():
                continue
            explore_branch(node, current_branch, return_here, list_of_branches)

    #add activity to current branch
    elif current_node.getType() == 'ActivityType':
        if current_node.getActivity() not in current_branch: #if the activity visited is not yet in the branch, add it and continue the search
            current_branch.append(current_node.getActivity())
            for node in current_node.getNextElements():
                explore_branch(node, current_branch, return_here, list_of_branches)
        else: #if the activity is already in the branch, we've already been here - exit the search here 
            if len(return_here) == 0:
                return
            else:
                next_node  = return_here.pop()
                explore_branch(next_node, current_branch, return_here, list_of_branches)
    
    #PARALLELGATEWAY - explore the fisrt branch that leaves the gateway and place the
    #rest in the return_here stack
    elif current_node.getType() == 'PARALLELGATEWAY' and 'Before' in current_node.getID():
        i = 0
        for node in current_node.getNextElements():
            if i == 0:
                next_node = node
            else:
                return_here.append(node)
            i = i+1

        explore_branch(next_node, current_branch, return_here, list_of_branches)
    #default - continue exploring branch
    else:
        for node in current_node.getNextElements():
            explore_branch(node, current_branch, return_here, list_of_branches)

    
