"""Pre-train the off-policy GReinSS set model used in Demo 2 of the tutorial notebook.

Uses the paper's real set-reconstruction data (|U|=1000, sigma=0.3, N=100 observations)
from data/GReinSS-UsedData/setSim, trains a GReinSS policy with an *observation-biased
off-policy proposal*, and saves everything the notebook needs into tutorial/assets/:

  setoff_obs.npz    - (100,1000) observed noisy vectors X
  setoff_truth.npz  - (100,1000) ground-truth sets S* (binary)
  setoff_model.pt   - trained off-policy policy model

This is the heavy step behind Demo 2 (dense ~177-element sets => minutes of training),
so the notebook loads the result rather than retraining live.  On-policy learning is left
to the notebook, where it visibly collapses, demonstrating why off-policy is essential.
"""
import os, sys, time
_here = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(_here, 'code')
if not os.path.isdir(CODE):
    CODE = os.path.abspath(os.path.join(_here, '..', 'code'))
sys.path.insert(0, CODE); os.chdir(CODE)

import numpy as np, torch
_orig = torch.load
torch.load = lambda *a, **k: _orig(*a, **{**k, 'weights_only': False})
from sharedGen import GraphGeneratorNet, gClass, train_model_off_policy

ASSETS = os.path.join(_here, 'assets'); os.makedirs(ASSETS, exist_ok=True)
DATA   = os.path.abspath(os.path.join(_here, '..', 'data', 'GReinSS-UsedData', 'setSim'))
TAG    = 'D100_N1000_P0.3_sim0'          # |U|=1000, sigma=0.3, N=100 (paper data)
sigma  = 0.3
EPOCHS = int(os.environ.get('EPOCHS', '1500'))

obs   = np.load(os.path.join(DATA, TAG + '_obs.npz'))['arr_0'].astype(np.float64)
truth = np.load(os.path.join(DATA, TAG + '_latent.npz'))['arr_0'].astype(np.float64)
N, U  = obs.shape
np.savez_compressed(os.path.join(ASSETS, 'setoff_obs.npz'), obs)
np.savez_compressed(os.path.join(ASSETS, 'setoff_truth.npz'), truth.astype(int))
print(f"|U|={U}  N={N}  sigma={sigma}  avg set size={truth.sum(1).mean():.1f}", flush=True)

# --- also stage the Demo 1 data (the paper's |U|=100, sigma=0.5 instance) into assets ---
D1TAG = 'D100_N100_P0.5_sim0'
o1 = np.load(os.path.join(DATA, D1TAG + '_obs.npz'))['arr_0']
l1 = np.load(os.path.join(DATA, D1TAG + '_latent.npz'))['arr_0']
np.savez_compressed(os.path.join(ASSETS, 'set100_obs.npz'), o1)
np.savez_compressed(os.path.join(ASSETS, 'set100_truth.npz'), l1)
print(f"staged Demo-1 data: set100_obs {o1.shape}, set100_truth {l1.shape}", flush=True)

# ---- memory-efficient log Pr(X|S) = -||s-o||^2 / 2sigma^2  (avoids an (S,N,U) tensor) ----
def multi_x_given_g(states, o):
    o = torch.as_tensor(o).float().to(states.device)
    s2 = states.sum(1, keepdim=True); o2 = (o*o).sum(1)[None, :]
    return -0.5*(s2 - 2.0*(states @ o.T) + o2)/(sigma**2)

CAP = int(min(U, 1.6*truth.sum(1).max()))          # cap generation length (true sets are <<)
def graphRules(g):
    x = torch.zeros((g.shape[0], U+1)); x[g.sum(1) >= CAP, :U] = -float('inf')
    return x, torch.zeros((g.shape[0], 1))

# ---- off-policy proposal: bias 'add element j' by the log-likelihood ratio (obs_j - 0.5)/sigma^2 ----
_obsT = torch.as_tensor(obs).float()
def offPolicyRule(g, arange1):
    idx = np.asarray(arange1) % N
    bias = torch.zeros((g.shape[0], U+1)); bias[:, :U] = (_obsT[idx]-0.5)/(sigma**2)
    return bias, torch.zeros((g.shape[0], 1))

np.random.seed(1); torch.manual_seed(1)
r = gClass(); r.graphSize=U; r.observations_batch=obs; r.batchSize=400; r.learning_rate=1e-3
r.model = GraphGeneratorNet(U, 1, 128, endingBias=0)
r.multi_x_given_g = multi_x_given_g; r.graphRules = graphRules; r.offPolicyRule = offPolicyRule

print(f"Training off-policy for {EPOCHS} epochs ...", flush=True)
t = time.time()
train_model_off_policy(r, r.learning_rate, r.batchSize, True, num_epochs=EPOCHS,
                       model_filename=os.path.join(ASSETS, 'setoff_model.pt'))
print(f"Done in {(time.time()-t)/60:.1f} min  ->  saved setoff_model.pt", flush=True)
