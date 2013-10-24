from gromacs.fileformats import MDP
from MDAnalysis import Universe
from collections import Counter
import numpy as np

def main(mdp_file="grompp.mdp", conf_file="conf.gro", traj_file="workdir/traj.xtc"):
    mdp = MDP(mdp_file)
    
    target_time = int(mdp["nsteps"].split()[0]) * mdp["dt"]  # target chemical time in ps
    u = Universe(conf_file, traj_file)
    times = [f.time for f in u.trajectory]
    
    # Check if there are no double frames
    c = Counter(times)
    c.most_common(3)
    assert(c.most_common(1)[0][1]  == 1)
    
    # Check if no frames are missing
    desired_times = list(np.arange(0.0, max(times)+mdp["dt"]*mdp["nstxtcout"], mdp["dt"]*mdp["nstxtcout"]))
    assert(len(times) == len(desired_times))
    
    return max(times), target_time
if __name__ == "__main__":
    print main()  