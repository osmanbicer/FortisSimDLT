Simulation of Oracle and Bold Mining Attacks on FORTIS and Freshness Preferred Mining Algorihtms based on Blocksim  https://github.com/carlosfaria94/blocksim/tree/master/blocksim

-Nodes can be set from InputsConfig.py file along with their hashing powes. If a node is not honest, the types "oracle" or "bold" needs to be declared.

-Choice of Fortis or FP is also declared from the variable ConsensusType in InputsConfig.py. Moreover, if FORTIS is used search for alpha.csv in  InputsConfig.py and replace it  with alphaFortis.csv. Otherwise do not change it.

-To alter the block propagation delay search for the function receive_block_time.

