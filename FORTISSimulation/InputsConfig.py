from Node import Node
#from Attacker import Attacker
import random
import csv
import sys
class InputsConfig(object):
    #################################################################### simulation parameters that needs to be set up #####################################################################

    ##### Blocks parameters #####
    Binterval = 600 # Average time (in seconds)for creating a block in the blockchain
    Bsize = 2000000 # the block limit in byte, currently 2MB
    Bdelay = 15.7 #average 1MB block propogation delay in seconds, source: On Scaling Decentralized Blockchains
    Breward = 6.25 # Reward for mining a block, currently 6.25

    ##### Transactions parameters #####
    hasTrans = False  # True/False to enable/disable transactions in the simulator
    Ttechnique = "Light" # Full/Light to specify the way of modelling transactions
    Tn=3.4 # rate of the number of transactions added per second, 2031 is the average number of transactions in a block, source: https://bitinfocharts.com/bitcoin/
    Tdelay = 5.1 # average transaction propagation delay in seconds (Only if Full technique is used)
    Tfee = 0.00032 # average transaction fee in Bitcoin per size unit, source: https://ycharts.com/indicators/bitcoin_average_transaction_fee
    Tsize = 615 # average transaction size  in byte, source: https://bitcoinvisuals.com/chain-tx-size
    ## note: the transaction fee (the submitter of the transaction has to pay) is Tfee * Tsize

    ##### Uncles parameters #####
    hasUncles = False # boolean variable to indicate use of uncle mechansim or not
    Buncles=0 # maximum number of uncle blocks allowed per block
    Ugenerations = 0 # the depth in which an uncle can be included in a block
    Ureward =0
    UIreward = 0 # Reward for including an uncle

    ##### Nodes parameters #####
    Nn = 4 # the total number of nodes in the network
    # the id & hash power for each node in the network -> id should be strat from 0
    # NODES = []
    # for i in range(Nn-1):
    #     hashPower =  random.uniform(0,30) # generate a random hash power for node i between 0% and 30%
    #     NODES += [Node(i,hashPower)]bold
    # NODES += [Node(Nn-1,20,"bold")]
    alpha_attacker=25 #10% for example
    ######### if you want to configure the hash power of each node as you prefer use this instead of randomly assign hash powers to nodes ############
    NODES = [
    Node(0,alpha_attacker,"bold"),
        Node(1,(100-alpha_attacker)*0.21),
        Node(2,(100-alpha_attacker)*0.18),
        Node(3,(100-alpha_attacker)*0.15),
        Node(4,(100-alpha_attacker)*0.13),
        Node(5,(100-alpha_attacker)*0.12),
        Node(6,(100-alpha_attacker)*0.11),
        Node(7,(100-alpha_attacker)*0.10),
#    Node(1,25),
#     Node(2,25), Node(3,25),
#        Node(2,(100-alpha_attacker)*0.18),
#        Node(3,(100-alpha_attacker)*0.15),
#        Node(4,(100-alpha_attacker)*0.13),
#        Node(5,(100-alpha_attacker)*0.12),
#        Node(6,(100-alpha_attacker)*0.11),
#        Node(7,(100-alpha_attacker)*0.10),
    ] 

    ##### Simulation parameters ####
    simTime= 60000 # the simulation length (in seconds)
    Runs=5000# Number of simulation runs

    ##### Consensus parameters #####
    ConsensusType = "FP" #FP/FORTIS/None to specify the type of consensus protocol to be followed by a miner in case of competing branches
    fortis_prob = 0.630

    ##### Results #######
    attacker_blocks = 0

    ##### Oracle Mining Table #####
    with open('oracle_mining/alpha.csv', newline='') as f:
        reader = csv.reader(f)
        oracle_file = list(reader)

    alpha = [float(i) for i in oracle_file[0]]
    tmax = [float(i) for i in oracle_file[1]]
    #oracle_time = {self.alpha[i]: self.tmax[i]*Binterval for i in range(len(self.alpha))}
    oracle_time = dict(zip(alpha, tmax))
    TOTAL_HASHPOWER = sum([miner.hashPower for miner in NODES])
    for node in NODES:
        if(node.type == "oracle"):
            hashrate = float(node.hashPower)/TOTAL_HASHPOWER
            minimum = abs(alpha[0]-hashrate)
            key = alpha[0]
            for i in alpha[1:]:
                if(abs(i-hashrate) < minimum):
                    key = i
                    minimum = abs(i-hashrate)
            node.t = oracle_time[key]*Binterval
            print(node.t)

    ########################################################### The distribution for transactions' attributes in the Ethereum network (gathered from real Ethereum)  ###########################################################################################
    def random_Gaslimit():
        global glimit
        rand = random.uniform(0,1)
        if rand <= 0.15:
            glimit = 21000
        elif rand <= 0.32:
            glimit = random.randint(21001,50000)
        elif rand <= 0.71:
            glimit = random.randint(50001,100000)
        elif rand <= 0.93:
            glimit = random.randint(100001,250000)
        elif rand <= 0.98:
            glimit = random.randint(250001,1000000)
        elif rand <= 1:
            glimit = random.randint(1000001,7919992)
        return glimit

    def random_Usedgas():
        global ugas
        rand = random.uniform(0,1)
        if rand <= 0.14:
            ugas = random.uniform(0.0,0.25)
        elif rand <= 0.38:
            ugas = random.uniform(0.26,0.50)
        elif rand <= 0.65:
            ugas = random.uniform(0.51,0.75)
        elif rand <= 1:
            ugas = random.uniform(0.76,1)
        return ugas

    def random_GasPrice():
        global gprice
        rand = random.uniform(0,1)
        if rand <= 0.13:
            gprice = random.uniform(0.000000000,0.000000004)
        elif rand <= 0.46:
            gprice = random.uniform(0.000000005,0.00000001)
        elif rand <= 0.72:
            gprice = random.uniform(0.000000011,0.00000002)
        elif rand <= 0.89:
            gprice = random.uniform(0.000000021,0.00000004)
        elif rand <= 1:
            gprice = random.uniform(0.000000041,0.000000134)
        return gprice
