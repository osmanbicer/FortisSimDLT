
from InputsConfig import InputsConfig as p
import random
from Transaction import Transaction
from Block import Block
from Event import Event
from Queue import Queue
from Node import Node
import numpy.random
#from Attacker import Attacker
from Consensus import Consensus as c
###################################### A class to schedule future events ########################################
class Scheduler:

    # ##### Time methods #####
    # def PoW_completion_time(hashPower):
    #     return random.expovariate(hashPower * 1/p.Binterval)
    def receive_block_time(blocksize):
        delayAve=((blocksize+1)/float(1000000))*p.Bdelay
        #return 0
        #return delayAve
        #return numpy.random.normal(delayAve,1,1)
        return random.expovariate(1/delayAve)
    # ##### Start solving a fresh PoW on top of last block appended #####
    # def solve_PoW(miner):
    #     TOTAL_HASHPOWER = sum([miner.hashPower for miner in p.NODES])
    #     hashPower = miner.hashPower/TOTAL_HASHPOWER
    #     return Scheduler.PoW_completion_time(hashPower)
    ##### Schedule initial events and add them to the event list #####
    def initial_events():
        currentTime = 0 # at the start of the simualtion, time will be zero
        for node in p.NODES:
            if node.hashPower >0: # only if hashPower >0, the node will be eligiable for mining
                Scheduler.create_block_event(node,currentTime)

    ##### Schedule a block creation event and add it to the event list #####
    def create_block_event(miner,currentTime):
        if miner.hashPower > 0:
            # blockTime = currentTime + Scheduler.solve_PoW(miner)
            if (currentTime >= miner.last_block().timestamp)
                blockTime = currentTime + c.PoW(miner)
            else 
                blockTime= 2*miner.last_block().timestamp-currentTime + c.PoW(miner)
            eventTime = blockTime
            if(miner.type == "oracle"):
                blockTime += miner.t;
            eventType = "create_block"

            if eventTime <= p.simTime: ##### create the event + add it to the event list #####
                # prepare attributes for the event
                minerId= miner.id
                blockId= random.randrange(100000000000)
                blockPrev= miner.last_block().id
                blockDepth = len(miner.blockchain)
                blockSize=int((eventTime-currentTime)*p.Tn*p.Tsize)
                if blockSize>p.Bsize: blockSize=p.Bsize
                block = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],blockSize,[]) # event content: transctions, uncles and blockSize is not set yet -> they will be set once the event is created
                event = Event(eventType,minerId,eventTime,block) # create the event
                Queue.add_event(event) # add the event to the queue

                # if(miner.type == "oracle"):
                #     event = Event("oracle_attack_end",minerId,blockTime,block)
                #     Queue.add_event(event)

                ######
                # if(miner.type!="honest"):
                #     print("Started mining block ", blockId, " at ",currentTime, " finishing at: ", eventTime)
            # else:
            #     if(miner.type!="honest"):
            #         print("Started mining block at ",currentTime, " finishing at: ", blockTime)

    ##### Schedule a private block creation event and add it to the event list #####
    def create_private_block_event(miner,currentTime):
        if miner.hashPower > 0:
            # blockTime = currentTime + Scheduler.solve_PoW(miner)
            blockTime = currentTime + c.PoW(miner)
            eventTime = blockTime

            eventType = "create_private_block"
            if(miner.type == "oracle"):
                if(blockTime < miner.last_private_block().timestamp):
                    blockTime = miner.last_private_block().timestamp;
                else:
                    eventType = "create_block"

            if eventTime <= p.simTime: ##### create the event + add it to the event list #####
                # prepare attributes for the event
                minerId= miner.id
                blockDepth = len(miner.privateblockchain)
                blockId= random.randrange(100000000000)
                blockPrev= miner.last_private_block().id
                blockSize=int((eventTime-currentTime)*p.Tn*p.Tsize)
                if blockSize>p.Bsize: blockSize=p.Bsize
                block = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],blockSize,[]) # event content: transctions, uncles and blockSize is not set yet -> they will be set once the event is created
                event = Event(eventType,minerId,eventTime,block) # create the event
                Queue.add_event(event) # add the event to the queue


                #######
            #     if(miner.type!="honest"):
            #         print("Started mining private block ", blockId, " at ",currentTime, " finishing at: ", eventTime)

            # else:
            #     if(miner.type!="honest"):
            #         print("Started mining private block at ",currentTime, " finishing at: ", blockTime)

    ##### Schedule block receiving events for all other nodes and add those events to the event list #####
    def receive_block_event(event):
        miner= event.node
        blockDepth = event.block.depth
        blockId = event.block.id
        blockTrans = event.block.transactions
        blockPrev= event.block.previous
        bockSize = event.block.size
        blockTimestamp = event.time
        blockUncles= event.block.uncles

        for recipient in p.NODES:
            if recipient.id != miner:
                # draw time for node i to receive the block
                if recipient.type=="honest" and p.NODES[miner].type=="honest":
                    receive_block_time = event.time + Scheduler.receive_block_time(bockSize) # draw time for node i to receive the block
                    
                elif recipient.type=="honest" and (p.NODES[miner].type=="oracle" or p.NODES[miner].type=="bold"):
                    receive_block_time = event.time #+ Scheduler.receive_block_time(bockSize)
                 
                elif (recipient.type=="oracle" or recipient.type=="bold") and p.NODES[miner].type=="honest":
                    receive_block_time = event.time #+ Scheduler.receive_block_time(bockSize)
                
                if receive_block_time <= p.simTime:
                    block = Block(blockDepth,blockId,blockPrev,blockTimestamp,miner,blockTrans,bockSize,blockUncles)
                    e = Event("receive_block", recipient.id, receive_block_time, block)
                    Queue.add_event(e)
        # if(p.NODES[miner].type != "honest"):
        #     print("Published block ", blockId, " at ", blockTimestamp, " depth ", blockDepth)

    def receive_private_blocks_event(event):
        miner= p.NODES[event.node]
        block = event.block
        while(block.id != miner.attack_start):
            blockDepth = block.depth
            blockId = block.id
            blockTrans = block.transactions
            blockPrev= block.previous
            bockSize = block.size
            blockTimestamp = block.timestamp
            blockUncles= block.uncles

            for recipient in p.NODES:
                if recipient.id != miner.id:
                    #receive_block_time = block.timestamp + Scheduler.receive_block_time() # draw time for node i to receive the block
                    receive_block_time = block.timestamp   #+ Scheduler.receive_block_time(bockSize)                 
                    if receive_block_time <= p.simTime:
                        block = Block(blockDepth,blockId,blockPrev,blockTimestamp,miner.id,blockTrans,bockSize,[])
                        e = Event("receive_block", recipient.id, receive_block_time, block)
                        Queue.add_event(e)
            # print("Pubished private block ", blockId, " at ", blockTimestamp, " depth ", blockDepth)

            block = miner.network_blocks[block.previous]
            

    def oracle_attack_end_event(minerId, attack_end_time, block):
        event = Event("oracle_attack_end",minerId,attack_end_time,block)
        Queue.add_event(event)

