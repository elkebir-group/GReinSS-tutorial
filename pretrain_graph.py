"""Pre-train a GReinSS model on a small latent-graph simulation WITH ground truth,
so the tutorial notebook can show real reconstruction accuracy for the graph example.

Saves into tutorial/assets/:
  graph_obs.npz        - (D,10,10) observed (start,end) count matrices
  graph_truth.npz      - (D,90)    ground-truth adjacency (off-diagonal), for accuracy
  graph_model.pt       - trained policy model
  graph_loss.npz       - median log-likelihood per epoch (training curve)
"""
import os, sys, time
# code is a git submodule at tutorial/code (falls back to sibling ../code)
_here = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(_here, 'code')
if not os.path.isdir(CODE):
    CODE = os.path.abspath(os.path.join(_here, '..', 'code'))
os.chdir(CODE)
sys.path.insert(0, CODE)

import numpy as np
import torch
_orig = torch.load
torch.load = lambda *a, **k: _orig(*a, **{**k, 'weights_only': False})

from sharedGen import (GeneratorNet, gClass, train_model_off_policy,
                       sim1_log_calculate_pr_x_given_g, sim1_fast_multi)


# --- Graph simulator (inlined from simulator.py, which runs code at import) ---
def observationSampler(adjacency_matrix, num_paths_per_graph, num_nodes, doMatrix=True):
    observations = np.zeros((num_nodes, num_nodes), dtype=int)
    for _ in range(num_paths_per_graph):
        start_node = np.random.choice(num_nodes)
        current_node = start_node
        while True:
            out_edges = np.where(adjacency_matrix[current_node] == 1)[0]
            total_options = len(out_edges) + 1
            choice = np.random.choice(np.append(-1, out_edges),
                                      p=[1 / total_options] + [1 / total_options] * len(out_edges))
            if choice == -1:
                observations[start_node, current_node] += 1
                break
            else:
                current_node = choice
    return observations


def generate_simulation_instance(num_nodes, num_data_points, num_paths_per_graph):
    probNoEdge = 0.5
    NbaseGraph = 1
    thresholds = np.zeros((NbaseGraph, num_nodes, num_nodes))
    for gi in range(NbaseGraph):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:
                    delta = 0 if np.random.rand() < probNoEdge else np.random.uniform(0, 1)
                    if delta != 0:
                        delta = 0.25 + (0.75 * delta)
                    thresholds[gi, i, j] = delta
    adjacency_matrices = np.zeros((num_data_points, num_nodes, num_nodes))
    a_values = np.random.random(adjacency_matrices.shape[0])
    randomSelection = np.random.randint(NbaseGraph, size=adjacency_matrices.shape[0])
    a_values_mod = thresholds[randomSelection] - a_values.reshape((-1, 1, 1))
    adjacency_matrices[a_values_mod > 0] = 1
    observations_list = np.zeros((num_data_points, num_nodes, num_nodes))
    for d in range(num_data_points):
        observations_list[d] = observationSampler(adjacency_matrices[d], num_paths_per_graph, num_nodes)
    return np.array(adjacency_matrices), observations_list, thresholds

np.random.seed(7)
torch.manual_seed(7)

NUM_NODES = 10
NUM_GRAPHS = 300
NUM_PATHS = 100
NUM_EPOCHS = int(os.environ.get('EPOCHS', '3500'))

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(ASSETS, exist_ok=True)

print(f"Generating {NUM_GRAPHS} graphs, {NUM_NODES} nodes, {NUM_PATHS} walks each ...", flush=True)
adj, obs, thresholds = generate_simulation_instance(NUM_NODES, NUM_GRAPHS, NUM_PATHS)
# adj: (D,10,10) ground-truth adjacency; obs: (D,10,10) start-end count matrices
# state vector = off-diagonal entries in row-major order (length 90)
eye = np.eye(NUM_NODES)
offdiag = np.argwhere(eye == 0)
truth_vec = adj[:, offdiag[:, 0], offdiag[:, 1]].astype(int)  # (D,90)

np.savez_compressed(os.path.join(ASSETS, 'graph_obs.npz'), obs)
np.savez_compressed(os.path.join(ASSETS, 'graph_truth.npz'), truth_vec)
print("Saved observations and ground truth. obs", obs.shape, "truth", truth_vec.shape, flush=True)

stateSize = NUM_NODES * (NUM_NODES - 1)  # 90
model = GeneratorNet(stateSize, 50)
r = gClass()
r.graphSize = stateSize
r.observations_batch = obs
r.batchSize = 1000
r.learning_rate = 1e-3
r.model = model
r.log_calculate_pr_x_given_g = sim1_log_calculate_pr_x_given_g
r.multi_x_given_g = sim1_fast_multi

print(f"Training for {NUM_EPOCHS} epochs ...", flush=True)
t = time.time()
train_model_off_policy(r, r.learning_rate, r.batchSize, False,
                       num_epochs=NUM_EPOCHS,
                       model_filename=os.path.join(ASSETS, 'graph_model.pt'),
                       saveTrainingLoss=os.path.join(ASSETS, 'graph_loss.npz'))
print(f"Done in {(time.time()-t)/60:.1f} min", flush=True)
