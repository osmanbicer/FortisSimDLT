from InputsConfig import InputsConfig as p
from Block import Block
from Transaction import Transaction
from Node import Node
#from Attacker import Attacker
from Results import Results
import random

# class Event, which is needed to create an event as an object from this class
class Event(object):
    def __init__(self,type, node, time, block):
        self.type = type
        self.node = node
        self.time = time
        self.block = block

    def run_event (event): # run the event from the event list
        from Scheduler import Scheduler

        miner = p.NODES[event.block.miner]
        minerId = miner.id
        eventTime = event.time

        blockDepth = event.block.depth
        blockId = event.block.id # block id
        blockPrev = event.block.previous # previous block id
        blockTime = event.block.timestamp
        blockTrans = event.block.transactions
        blockSize = event.block.size

        ##################################### Block Creation Event #######################################################
        if event.type == "create_block":
            if (blockPrev == miner.last_block().id and miner.currentMode == "public"):
                miner.mined_blocks+=1
                Results.totalBlocks += 1 # count # of total blocks created!
                if p.hasTrans and p.Ttechnique == "Light": blockTrans,blockSize = Transaction.execute_transactions_light()
                elif p.hasTrans and p.Ttechnique == "Full": blockTrans,blockSize = Transaction.execute_transactions_full(miner,blockTime)
                event.block.transactions = blockTrans
                if p.hasUncles:
                    blockUncles = Node.add_uncles(miner) # add uncles to the block
                    event.block.uncles = blockUncles

                b= Block(blockDepth,blockId,blockPrev,blockTime,minerId,blockTrans,blockSize,[])
                miner.blockchain.append(b)

                if p.hasTrans and p.Ttechnique == "Light":
                    Transaction.create_transactions_light() # generate transactions
                
                #Add the block to the dictionary
                miner.network_blocks[event.block.id] = b
                miner.longest_branch_length = blockDepth
                miner.longest_branches = [blockId]
                #Add the block to the list of longest branches
                # if(blockDepth > miner.longest_branch_length):
                #     miner.longest_branch_length = blockDepth
                #     miner.longest_branches = [blockId]
                # elif(blockDepth == miner.longest_branch_length):
                #     miner.longest_branches += [blockId]
             
                currentTime = eventTime
                event.time = blockTime
               
                #Send block to all the other nodes
                Scheduler.receive_block_event(event)
 
                miner.check_switch(time = currentTime, blocktime = blockTime)
  
                #attacker in private mode starts building a private block on top of this block 
                if(miner.currentMode == "private"):
  
                    Scheduler.create_private_block_event(miner,currentTime)
                    if(miner.type == "oracle"):
                        Scheduler.oracle_attack_end_event(minerId,blockTime,b)
                #node in public mode starts building a regular block
                else:
                    Scheduler.create_block_event(miner,currentTime)

                #####
                # if(miner.type != "honest"):
                #     print("mined block ", blockId, " at time ", currentTime, " on ", blockPrev)

        
        ##################################### Private Block Creation Event #######################################################
        elif event.type == "create_private_block":
            if (miner.currentMode == "private" and miner.privateblockchain != [] and blockPrev == miner.last_private_block().id):
                #print("depth of mainchain: ", miner.last_block().depth)
                #print("Depth of private chain: ", miner.privateblockchain[len(miner.privateblockchain)-1].depth)
                #print("Totalblocks: ", Results.totalBlocks)
                miner.mined_blocks+=1
                Results.totalBlocks += 1 # count # of total blocks created!
                if p.hasTrans and p.Ttechnique == "Light": blockTrans,blockSize = Transaction.execute_transactions_light()
                elif p.hasTrans and p.Ttechnique == "Full": blockTrans,blockSize = Transaction.execute_transactions_full(miner,blockTime)
                event.block.transactions = blockTrans

                if p.hasUncles:
                    blockUncles = Node.add_uncles(miner) # add uncles to the block
                    event.block.uncles = blockUncles

                b= Block(blockDepth,blockId,blockPrev,blockTime,minerId,blockTrans,blockSize,[])
                miner.privateblockchain.append(b)

                if p.hasTrans and p.Ttechnique == "Light":
                    Transaction.create_transactions_light() # generate transactions
                
                miner.network_blocks[event.block.id] = b
                
                currentTime = eventTime
                # print("new private block ",blockId, " at ", currentTime)
                eventTime=blockTime
            
                miner.check_switch(time = currentTime, blocktime = blockTime)
                if(miner.currentMode == "public"):
                    #publish block if attack becomes successful
                    #Scheduler.receive_block_event(event)
                    Scheduler.receive_private_blocks_event(event)
                    Scheduler.create_block_event(miner,currentTime)
                    #Add the block to the list of longest branches
                    miner.longest_branch_length = blockDepth
                    miner.longest_branches = [blockId]

                else:
                    #Create private block if attack continues
                    Scheduler.create_private_block_event(miner,currentTime)

                #####
                # if(miner.type != "honest"):
                #     print("mined private block ", blockId, " at time ", currentTime, " on ", blockPrev)

        ##################################### Block Receiving Event #######################################################
        elif event.type == "receive_block":

            #print(event.node," recieved: ",blockId)
            node = p.NODES[event.node] # recipint
            node.network_blocks[event.block.id] = event.block
            lastBlockId= node.last_block().id # the id of last block
            blockUncles = event.block.uncles
            # if(node.id == 16):
            #     print("recieved block ",blockId," mined at ", blockTime," at ",eventTime, "depth: ", blockDepth)

            #### case 1: the received block is built on top of the last block according to the recipient's blockchain ####
            if blockPrev == lastBlockId:
                #Add the block to the list of longest branches
                node.longest_branch_length = blockDepth
                node.longest_branches = [blockId]
                
                block=Block(blockDepth,blockId, blockPrev,blockTime,minerId,blockTrans,blockSize,blockUncles) # construct the block
                node.blockchain.append(block) # append the block to local blockchain
                if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node, event.block)
                currentTime = eventTime + random.randint(-3,3) # set the time when to start mining the next block
                
                if(node.type != "honest"):
                    #If attacker is in public mode, it checks if it can attack
                    if(node.currentMode == "public"):
                        node.check_switch(time = currentTime)
                        if(node.currentMode == "private"):
                            Scheduler.create_private_block_event(node,currentTime)
                    #If attacker is in private mode, it checks if the attack can continue
                    else:
                        node.check_switch(time = currentTime)
                        #If attack unsuccessful, check the possibility of attacking again
                        if(node.currentMode == "public"):
                            node.check_switch(time = currentTime)
                            if(node.currentMode == "private"):
                                Scheduler.create_private_block_event(node,currentTime)

                if(node.currentMode == "public"):
                    Scheduler.create_block_event(node,currentTime)

            #### case 2: the received block is  not built on top of the last block ####
            else:
                depth = blockDepth + 1
                #### 1- if depth of the received block > depth of the last block
                if (depth > len(node.blockchain)):
                    #Add the block to the list of longest branches
                    node.longest_branch_length = blockDepth
                    node.longest_branches = [blockId]

                    if(node.last_block().miner == 16 and node.id == 0):
                        print("block ", node.last_block().id, " kicked from main chain")
                    Node.update_local_blockchain(node,miner,depth)
                    #Node.update_local_blockchain_new(node,blockId)
                    currentTime = eventTime
                    
                    if(node.type != "honest"):
                        #If attacker is in public mode, check if it can begin attacking
                        if(node.currentMode == "public"):
                            node.check_switch(time = currentTime)
                            #If attack starts, start mining private block
                            if(node.currentMode == "private"):
                                Scheduler.create_private_block_event(node,currentTime)
                        #If attacker is already attacking, check if it becomes unsuccessful
                        else:
                            node.check_switch(time = currentTime)
                            #If attack unsuccessful, check the possibility of attacking again
                            if(node.currentMode == "public"):
                                node.check_switch(time = currentTime)
                                if(node.currentMode == "private"):
                                    Scheduler.create_private_block_event(node,currentTime)

                    if(node.currentMode == "public"):
                        Scheduler.create_block_event(node,currentTime)
                
                #### 2- if depth of the received block = depth of the last block
                elif (depth == len(node.blockchain)):
                    node.longest_branches.append(blockId)
                    #code to check main chain
                    if (p.ConsensusType=="FP"):
                        # freshest_branch = node.longest_branches[0]
                        # freshest_timestamp = node.network_blocks[node.longest_branches[0]].timestamp
                        # for branch in node.longest_branches[1:]:
                        #     if(node.network_blocks[branch].timestamp > freshest_timestamp):
                        #         freshest_branch = branch
                        #         freshest_timestamp = node.network_blocks[branch].timestamp
                        # #update based on freshest branch
                        # if(lastBlockId != freshest_branch):

                        #If received block is fresher, update local blockchain
                        if(node.last_block().timestamp < blockTime):
                            # if(minerId == 16 and node.id == 0):
                            #     print("block ", blockId, " accepted. timestamp: ", blockTime)
                            Node.update_local_blockchain(node,miner,depth)
                            #Node.update_local_blockchain_new(node,freshest_branch)
                            currentTime = eventTime
                            if(node.currentMode == "public"):
                                Scheduler.create_block_event(node,currentTime)
                        else:
                            # if(minerId == 16 and node.id == 0):
                            #     print("block ", blockId, " not accepted in main chain FP")
                            uncle = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # construct the uncle block
                            node.unclechain.append(uncle)
                    
                    if(p.ConsensusType == "FORTIS"):
                        #There should be at least 2 longest branches
                        if(len(node.longest_branches) == 1):
                            print("Error")
                        
                        #choose fresher branch with probability fortis_prob when there are two longest branches
                        if(len(node.longest_branches) == 2):
                            if( (blockTime <= node.last_block().timestamp) ^ (random.random() <= p.fortis_prob)):
                                Node.update_local_blockchain(node,miner,depth)
                                #Node.update_local_blockchain_new(node,freshest_branch)
                                currentTime = eventTime
                                if(node.currentMode == "public"):
                                    Scheduler.create_block_event(node,currentTime)
                            else:
                                uncle = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # construct the uncle block
                                node.unclechain.append(uncle)
                        
                        #Choose any branch with a uniform probability if there are more than 2 longest branches
                        else:
                            branch = random.choice(node.longest_branches)
                            if(node.last_block().id != branch):
                                block = node.network_blocks[branch]
                                miner = p.NODES[block.miner]
                                #longest_branch not being updated properly
                                Node.update_local_blockchain(node,miner,depth)
                                #Node.update_local_blockchain_new(node,random.choice(longest_branches))
                            #if received block is not chosen, add it to uncle chain
                            elif(branch != blockId):
                                uncle = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # construct the uncle block
                                node.unclechain.append(uncle)
                    #If no consensus algorithm is active, add it to uncle chain
                    else:
                        uncle = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # construct the uncle block
                        node.unclechain.append(uncle)



                    #code to update local chain

                #### 3- if depth of the received block < depth of the last block, then reject the block (add it to unclechain) ####
                else:
                    # if(minerId == 16 and node.id == 0):
                    #     print("block ", blockId, " not accepted in main chain(not deep enough). Chain depth: ", len(node.blockchain), " block depth: ",depth)
                        # for i in node.blockchain:
                        #     print ("id: ", i.id, " timestamp: ", i.timestamp, " miner: ", i.miner, "prev: ", i.previous)
                    uncle = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # construct the uncle block
                    node.unclechain.append(uncle)

            if p.hasUncles: Node.update_unclechain(node)
            if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node,event.block) # not sure yet.

        ############################ Attack end Event ################################
        elif (event.type == "oracle_attack_end"):
            currentTime = eventTime
            miner.currentMode = "public"
            if(len(miner.privateblockchain) >= len(miner.blockchain)):
                # print("successful attack at ", currentTime)
                miner.blockchain=[]
                miner.blockchain = miner.privateblockchain.copy()
                event.block = miner.privateblockchain[-1]

                if(event.block.depth > miner.longest_branch_length):
                    miner.longest_branch_length = blockDepth
                    miner.longest_branches = [event.block.id]
                elif(event.block.depth == miner.longest_branch_length):
                    miner.longest_branches += [event.block.id]
                
                Scheduler.receive_private_blocks_event(event)
                miner.successfulAttacks +=1
            else:
                # print("unsuccessful attack")
                miner.unsuccessfulAttacks +=1
                Scheduler.create_block_event(miner,currentTime)

            # print("Switched to public mode")

            miner.privateblockchain = []