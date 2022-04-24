from Block import Block
#from Scheduler import Scheduler
#import time
k=1 #k value for bold mining
class Node(object):
    def __init__(self,id, hashPower, nodeType = "honest"):
        '''Initialize a new miner named name with hashrate measured in hashes per second.'''
        self.id= id
        self.hashPower = hashPower
        self.network_blocks = {}
        self.longest_branches = []
        self.longest_branch_length = 0
        self.blockchain= [] # create an array for each miner to store chain state locally
        self.transactionsPool= []
        self.unclechain = []
        self.mined_blocks = 0
        self.blocks=0 # total number of blocks mined in the main chain
        self.uncles=0 # total number of uncle blocks included in the main chain
        self.balance= 0 # to count all reward that a miner made
        self.blocks_changed=0 # total number of blocks mined in the main chain
        self.uncles_changed=0 # total number of uncle blocks included in the main chain
        self.balance_changed= 0 # to count all reward that a miner made
        self.type= nodeType
        self.attack_start = 0
        self.currentMode = "public"
        if(self.type != "honest"):
            self.privateblockchain = []
            self.successfulAttacks = 0
            self.unsuccessfulAttacks = 0
            if(self.type == "oracle"):
                # t = 0
                attack_completion = 0

    def generate_gensis_block():
        from InputsConfig import InputsConfig as p
        for node in p.NODES:
            genesis_block = Block(0,0,-1,0,None,[],0,[])
            node.blockchain.append(genesis_block)
            node.network_blocks[0] = genesis_block

    def add_uncles(miner):
        from InputsConfig import InputsConfig as p
        maxUncles = p.Buncles
        uncles=[]

        j=0
        while j < len (miner.unclechain):
            uncleDepth = miner.unclechain[j].depth
            blockDepth = miner.last_block().depth
            if maxUncles>0 and uncleDepth > blockDepth - p.Ugenerations : # to check if uncle block is received and there is space to include it, also check within 6 generation
                uncles.append(miner.unclechain[j])
                del miner.unclechain[j] # delete uncle after inclusion
                j-=1
                maxUncles-=1 # decrease allowable uncles by 1
            j+=1

        return uncles

    def update_local_blockchain(node,miner,depth):
        # the node here is the one that needs to update its blockchain, while miner here is the one who owns the last block generated
        # the node will update its blockchain to mach the miner's blockchain
        from InputsConfig import InputsConfig as p
        # print("depth = ",depth)
        # print("node's blockchain. ID ", node.id)
        # for i in node.blockchain:
        #     print("id: ", i.id, " timestamp: ", i.timestamp, " miner: ", i.miner, "depth: ", i.depth)
        # print("Miner's blockchain. ID ", miner.id)
        # for i in miner.blockchain:
        #     print("id: ", i.id, " timestamp: ", i.timestamp, " miner: ", i.miner, "depth: ", i.depth)
        i=0
        while (i < depth):
            if (i < len(node.blockchain)):
                if (node.blockchain[i].id != miner.blockchain[i].id): # and (self.node.blockchain[i-1].id == Miner.blockchain[i].previous) and (i>=1):
                    node.unclechain.append(node.blockchain[i]) # move block to unclechain
                    newBlock = miner.blockchain[i]
                    node.blockchain[i]= newBlock
                    node.network_blocks[newBlock.id]=newBlock
                    if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node,newBlock)
            else:
                newBlock = miner.blockchain[i]
                node.blockchain.append(newBlock)
                node.network_blocks[newBlock.id]=newBlock
                if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node,newBlock)
            i+=1

    def update_local_blockchain_new(node,blockid):
        # the node here is the one that needs to update its blockchain, while miner here is the one who owns the last block generated
        # the node will update its blockchain to mach the miner's blockchain
        from InputsConfig import InputsConfig as p
        block = node.network_blocks[blockid]
        depth = block.depth+1
        new_chain = [block]
        print(node.id,node.network_blocks)
        print(block.id,block.previous)
        while block.id!=0:
            block = node.network_blocks[block.previous]
            new_chain.append(block)
        new_chain.reverse()
        i=0
        while (i < depth):
            if (i < len(node.blockchain)):
                if (node.blockchain[i].id != new_chain[i].id): # and (self.node.blockchain[i-1].id == Miner.blockchain[i].previous) and (i>=1):
                    node.unclechain.append(node.blockchain[i]) # move block to unclechain
                    newBlock = new_chain[i]
                    node.blockchain[i]= newBlock
                    node.network_blocks[newBlock.id]=newBlock
                    if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node,newBlock)
            else:
                newBlock = new_chain[i]
                node.blockchain.append(newBlock)
                node.network_blocks[newBlock.id]=newBlock
                if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node,newBlock)
            i+=1

    def update_unclechain(node):
        ### remove all duplicates uncles in the miner's unclechain
        a = set()
        x=0
        while x < len(node.unclechain):
            if node.unclechain[x].id in a:
                del node.unclechain[x]
                x-=1
            else:
                a.add(node.unclechain[x].id)
            x+=1

        j=0
        while j < len (node.unclechain):
            for k in node.blockchain:
                if node.unclechain[j].id == k.id:
                    del node.unclechain[j] # delete uncle after inclusion
                    j-=1
                    break
            j+=1

        j=0
        while j < len (node.unclechain):
            c="t"
            for k in node.blockchain:
                u=0
                while u < len(k.uncles):
                    if node.unclechain[j].id == k.uncles[u].id:
                        del node.unclechain[j] # delete uncle after inclusion
                        j-=1
                        c="f"
                        break
                    u+=1
                if c=="f":
                    break
            j+=1


    def update_transactionsPool(node,block):
        j=0
        while j < len(block.transactions):
            for t in node.transactionsPool:
                if  block.transactions[j].id == t.id:
                    del t
                    break
            j+=1

    def last_block(self):
        return self.blockchain[len(self.blockchain)-1]

    def last_private_block(self):
        return self.privateblockchain[len(self.privateblockchain)-1]
        
    def blockchain_length(self):
        return len(self.blockchain)-1

    def check_switch(self, time=0,blocktime=1):
        #Decide when to switch between public and private branches for an attacker type
        if(self.type == "bold"):
            if(self.currentMode == "public"):
                #If none of the last k blocks is by the attacker, switch to private mode
                if(self.blockchain_length() >= k):
                    switch = 1
                    for curBlock in self.blockchain[len(self.blockchain)-k:]:
                        if(curBlock.miner == self.id):
                            switch = 0
                            break
                    if(switch):
                        self.privateblockchain = self.blockchain[:len(self.blockchain)-k].copy()
                        for i in self.blockchain[len(self.blockchain)-k:]:
                            self.unclechain.append(i)
                        #print("Last block of mainchain: ",self.last_block().previous," Last block of private chain: ",self.privateblockchain[len(self.privateblockchain)-1].id)
                        #print("switched to private mode at ",time)
                        self.currentMode = "private"
                        self.attack_start = self.privateblockchain[-1].id
                        # print("Attacking from block ", self.attack_start)
                        #self.start = len(self.blockchain)
                        #print("Attack started, length of blockchain: ", self.start)
            else:
                #Attack is unsuccessful if the public blockchain is k+1 blocks longer than the attacker's private blockchain
                if(len(self.blockchain) - len(self.privateblockchain) >= k+1):
                    #print("Unsuccessful attack at ", time)
                    # print("mainchain")
                    # for i in self.blockchain:
                    #     print ("id: ", i.id, " timestamp: ", i.timestamp, " miner: ", i.miner, "prev: ", i.previous)
                    # print("private chain")
                    # for i in self.privateblockchain:
                    #     print ("id: ", i.id, " timestamp: ", i.timestamp, " miner: ", i.miner, "prev: ", i.previous)
                    self.privateblockchain = []
                    self.currentMode = "public"
                    self.unsuccessfulAttacks +=1
                #Attack is successful if the attacker's private blockchain becomes as long as the public blockchain
                elif((len(self.privateblockchain) >= len(self.blockchain)) ):
                    self.currentMode = "public"
                    if(len(self.privateblockchain) >= len(self.blockchain)):
                        # print("Successful attack. Block ID: ", self.privateblockchain[len(self.privateblockchain)-1].id, " at ", time, " depth ", self.privateblockchain[len(self.privateblockchain)-1].depth)

                        if((len(self.privateblockchain)-1) > self.longest_branch_length):
                            self.longest_branch_length = len(self.privateblockchain)-1
                            self.longest_branches = [self.last_private_block]
                        elif((len(self.privateblockchain)-1) == self.longest_branch_length):
                            self.longest_branches += [self.last_private_block]
                        
                        # print("Successful attack at ", time)
                        # print("old chain")
                        # for i in self.blockchain:
                        #     print ("id: ", i.id, " timestamp: ", i.timestamp, " miner: ", i.miner, "prev: ", i.previous)
                        # print("new chain")
                        # for i in self.privateblockchain:
                        #     print ("id: ", i.id, " timestamp: ", i.timestamp, " miner: ", i.miner, "prev: ", i.previous)
                        self.blockchain=[]
                        self.blockchain = self.privateblockchain.copy()
                        self.successfulAttacks +=1
                    else:
                        # print("Unsuccessful attack")
                        self.unsuccessfulAttacks +=1
                    #Use udpate localchain instead of copying private chain once it uses dictionary
                    self.privateblockchain = []
                    
        
        elif(self.type == "oracle"):
            if(self.currentMode == "public"):
                if((self.last_block().miner == self.id) and (time != blocktime)):
                    self.privateblockchain = self.blockchain.copy()
                    self.attack_start = self.privateblockchain[-1].id
                    self.currentMode = "private"
                    # print("Started attack at ", time," block to be published at ", blocktime)
            else:
                #Attack is unsuccessful if the public blockchain is 2 blocks longer than the attacker's private blockchain
                if(len(self.blockchain) - len(self.privateblockchain) >= 2):
                    # print("Unsuccessful attack")
                    self.privateblockchain = []
                    self.currentMode = "public"
                    # print("switched to public mode")
                #Attack is successful if the attacker's private blockchain becomes as long as the public blockchain
                # elif(self.attack_completion == 1 and len(self.privateblockchain) >= len(self.blockchain)):
                #     self.attack_completion = 0
                #     self.currentMode = "public"
                #     #print("Successful attack. Block ID: ", self.privateblockchain[len(self.privateblockchain)-1].id, "length of private blockchain: ",len(self.privateblockchain), "length of blockchain: ", len(self.blockchain))
                #     self.blockchain = self.privateblockchain.copy()
                #     self.privateblockchain = []

    ########################################################### reset the state of blockchains for all nodes in the network (before starting the next run) ###########################################################################################
    def resetState():
        from InputsConfig import InputsConfig as p
        for node in p.NODES:
            node.blockchain= [] # create an array for each miner to store chain state locally
            node.transactionsPool= []
            node.unclechain = []
            node.network_blocks = {}
            node.longest_branches = []
            node.longest_branch_length = 0
            node.blocks=0 # total number of blocks mined in the main chain
            node.uncles=0 # total number of uncle blocks included in the main chain
            node.balance= 0 # to count all reward that a miner made
            node.blocks_changed=0 # total number of blocks mined in the main chain
            node.uncles_changed=0 # total number of uncle blocks included in the main chain
            node.balance_changed= 0 # to count all reward that a miner made
            if(node.type != "honest"):
                # print("Successful Attacks: ", node.successfulAttacks)
                # print("Unsuccessful Attacks: ", node.unsuccessfulAttacks)
                # print("Blocks mined: ",node.mined_blocks)
                node.privateblockchain= [] # create an array for each attacker to store private chain state locally
                node.successfulAttacks = 0
                node.unsuccessfulAttacks = 0
            node.mined_blocks = 0

