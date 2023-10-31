# %% [markdown]
# <a href="https://colab.research.google.com/github/JasonGross/neural-net-coq-interp/blob/main/October_2023_Monthly_Algorithmic_Challenge_Sorted_List_Jason%2C_Thomas%2C_Rajashree.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %% [markdown]
# # Monthly Algorithmic Challenge (October 2023): Sorted List
#
# This post is the fourth in the sequence of monthly mechanistic interpretability challenges. They are designed in the spirit of [Stephen Casper's challenges](https://www.lesswrong.com/posts/KSHqLzQscwJnv44T8/eis-vii-a-challenge-for-mechanists), but with the more specific aim of working well in the context of the rest of the ARENA material, and helping people put into practice all the things they've learned so far.
#
#
# If you prefer, you can access the Streamlit page [here](https://arena-ch1-transformers.streamlit.app/Monthly_Algorithmic_Problems).
#
# <img src="https://raw.githubusercontent.com/callummcdougall/computational-thread-art/master/example_images/misc/sorted-problem.png" width="350">

# %% [markdown]
# ## Setup

# %%
try:
    import google.colab # type: ignore
    IN_COLAB = True
except:
    IN_COLAB = False

import os; os.environ["ACCELERATE_DISABLE_RICH"] = "1"
import sys

if IN_COLAB:
    # Install packages
    %pip install einops
    %pip install jaxtyping
    %pip install transformer_lens
    %pip install git+https://github.com/callummcdougall/eindex.git
    %pip install git+https://github.com/callummcdougall/CircuitsVis.git#subdirectory=python

    # Code to download the necessary files (e.g. solutions, test funcs)
    import os, sys
    if not os.path.exists("chapter1_transformers"):
        !curl -o /content/main.zip https://codeload.github.com/callummcdougall/ARENA_2.0/zip/refs/heads/main
        !unzip /content/main.zip 'ARENA_2.0-main/chapter1_transformers/exercises/*'
        sys.path.append("/content/ARENA_2.0-main/chapter1_transformers/exercises")
        os.remove("/content/main.zip")
        os.rename("ARENA_2.0-main/chapter1_transformers", "chapter1_transformers")
        os.rmdir("ARENA_2.0-main")
        os.chdir("chapter1_transformers/exercises")
else:
    from IPython import get_ipython
    ipython = get_ipython()
    ipython.run_line_magic("load_ext", "autoreload")
    ipython.run_line_magic("autoreload", "2")
    import os, sys
    if not os.path.exists("chapter1_transformers"):
        !curl -o main.zip https://codeload.github.com/callummcdougall/ARENA_2.0/zip/refs/heads/main
        !unzip main.zip 'ARENA_2.0-main/chapter1_transformers/exercises/*'
        os.remove("main.zip")
        os.rename("ARENA_2.0-main/chapter1_transformers", "chapter1_transformers")
        sys.path.append(f"{os.getcwd()}/chapter1_transformers/exercises")
        os.rmdir("ARENA_2.0-main")

# %%
import torch as t
from pathlib import Path

# Make sure exercises are in the path
chapter = r"chapter1_transformers"
exercises_dir = Path(f"{os.getcwd().split(chapter)[0]}/{chapter}/exercises").resolve()
section_dir = exercises_dir / "monthly_algorithmic_problems" / "october23_sorted_list"
if str(exercises_dir) not in sys.path: sys.path.append(str(exercises_dir))

from monthly_algorithmic_problems.october23_sorted_list.dataset import SortedListDataset
from monthly_algorithmic_problems.october23_sorted_list.model import create_model
from plotly_utils import hist, bar, imshow

device = t.device("cuda" if t.cuda.is_available() else "cpu")

# %% [markdown]
#
#
# ## Prerequisites
#
# The following ARENA material should be considered essential:
#
# * **[1.1] Transformer from scratch** (sections 1-3)
# * **[1.2] Intro to Mech Interp** (sections 1-3)
#
# The following material isn't essential, but is recommended:
#
# * **[1.2] Intro to Mech Interp** (section 4)
# * **[1.4] Balanced Bracket Classifier** (all sections)
# * Previous algorithmic problems in the sequence
#

# %% [markdown]
# ## Difficulty
#
# **This problem is probably the easiest in the sequence so far**, so I expect solutions to have fully reverse-engineered it, as well as presenting adversarial examples and explaining how & why they work.**

# %% [markdown]
#
# ## Motivation
#
# Neel Nanda's post [200 COP in MI: Interpreting Algorithmic Problems](https://www.lesswrong.com/posts/ejtFsvyhRkMofKAFy/200-cop-in-mi-interpreting-algorithmic-problems) does a good job explaining the motivation behind solving algorithmic problems such as these. I'd strongly recommend reading the whole post, because it also gives some high-level advice for approaching such problems.
#
# The main purpose of these challenges isn't to break new ground in mech interp, rather they're designed to help you practice using & develop better understanding for standard MI tools (e.g. interpreting attention, direct logit attribution), and more generally working with libraries like TransformerLens.
#
# Also, they're hopefully pretty fun, because why shouldn't we have some fun while we're learning?

# %% [markdown]
# ## Logistics
#
# The solution to this problem will be published on this page at the start of November, at the same time as the next problem in the sequence. There will also be an associated LessWrong post.
#
# If you try to interpret this model, you can send your attempt in any of the following formats:
#
# * Colab notebook,
# * GitHub repo (e.g. with ipynb or markdown file explaining results),
# * Google Doc (with screenshots and explanations),
# * or any other sensible format.
#
# You can send your attempt to me (Callum McDougall) via any of the following methods:
#
# * The [Slack group](https://join.slack.com/t/arena-la82367/shared_invite/zt-1uvoagohe-JUv9xB7Vr143pdx1UBPrzQ), via a direct message to me
# * My personal email: `cal.s.mcdougall@gmail.com`
# * LessWrong message ([here](https://www.lesswrong.com/users/themcdouglas) is my user)
#
# **I'll feature the names of everyone who sends me a solution on this website, and also give a shout out to the best solutions.** It's possible that future challenges will also feature a monetary prize, but this is not guaranteed.
#
# Please don't discuss specific things you've found about this model until the challenge is over (although you can discuss general strategies and techniques, and you're also welcome to work in a group if you'd like). The deadline for this problem will be the end of this month, i.e. 31st August.

# %% [markdown]
# ## What counts as a solution?
#
# Going through the solutions for the previous problem in the sequence (July: Palindromes) as well as the exercises in **[1.4] Balanced Bracket Classifier** should give you a good idea of what I'm looking for. In particular, I'd expect you to:
#
# * Describe a mechanism for how the model solves the task, in the form of the QK and OV circuits of various attention heads (and possibly any other mechanisms the model uses, e.g. the direct path, or nonlinear effects from layernorm),
# * Provide evidence for your mechanism, e.g. with tools like attention plots, targeted ablation / patching, or direct logit attribution.
# * (Optional) Include additional detail, e.g. identifying the subspaces that the model uses for certain forms of information transmission, or using your understanding of the model's behaviour to construct adversarial examples.

# %% [markdown]
# ## Task & Dataset
#
# The problem for this month is interpreting a model which has been trained to sort a list. The model is fed sequences like:
#
# ```
# [11, 2, 5, 0, 3, 9, SEP, 0, 2, 3, 5, 9, 11]
# ```
#
# and has been trained to predict each element in the sorted list (in other words, the output at the `SEP` token should be a prediction of `0`, the output at `0` should be a prediction of `2`, etc).
#
# Here is an example of what this dataset looks like:

# %%
dataset = SortedListDataset(size=1, list_len=5, max_value=10, seed=42)

print(dataset[0].tolist())
print(dataset.str_toks[0])

# %% [markdown]
# The relevant files can be found at:
#
# ```
# chapter1_transformers/
# └── exercises/
#     └── monthly_algorithmic_problems/
#         └── october23_sorted_list/
#             ├── model.py               # code to create the model
#             ├── dataset.py             # code to define the dataset
#             ├── training.py            # code to training the model
#             └── training_model.ipynb   # actual training script
# ```
#

# %% [markdown]
# ## Model
#
# The model is attention-only, with 1 layer, and 2 attention heads per layer. It was trained with layernorm, weight decay, and an Adam optimizer with linearly decaying learning rate.
#
# You can load the model in as follows:
#

# %%
filename = section_dir / "sorted_list_model.pt"

model = create_model(
    list_len=10,
    max_value=50,
    seed=0,
    d_model=96,
    d_head=48,
    n_layers=1,
    n_heads=2,
    normalization_type="LN",
    d_mlp=None
)

state_dict = t.load(filename)

state_dict = model.center_writing_weights(t.load(filename))
state_dict = model.center_unembed(state_dict)
state_dict = model.fold_layer_norm(state_dict)
state_dict = model.fold_value_biases(state_dict)
model.load_state_dict(state_dict, strict=False);

# %% [markdown]
# The code to process the state dictionary is a bit messy, but it's necessary to make sure the model is easy to work with. For instance, if you inspect the model's parameters, you'll see that `model.ln_final.w` is a vector of 1s, and `model.ln_final.b` is a vector of 0s (because the weight and bias have been folded into the unembedding).

# %%
print("ln_final weight: ", model.ln_final.w)
print("\nln_final, bias: ", model.ln_final.b)

# %% [markdown]
# <details>
# <summary>Aside - the other weight processing parameters</summary>
#
# Here's some more code to verify that our weights processing worked, in other words:
#
# * The unembedding matrix has mean zero over both its input dimension (`d_model`) and output dimension (`d_vocab`)
# * All writing weights (i.e. `b_O`, `W_O`, and both embeddings) have mean zero over their output dimension (`d_model`)
# * The value biases `b_V` are zero (because these can just be folded into the output biases `b_O`)
#
# ```python
# W_U_mean_over_input = einops.reduce(model.W_U, "d_model d_vocab -> d_model", "mean")
# t.testing.assert_close(W_U_mean_over_input, t.zeros_like(W_U_mean_over_input))
#
# W_U_mean_over_output = einops.reduce(model.W_U, "d_model d_vocab -> d_vocab", "mean")
# t.testing.assert_close(W_U_mean_over_output, t.zeros_like(W_U_mean_over_output))
#
# W_O_mean_over_output = einops.reduce(model.W_O, "layer head d_head d_model -> layer head d_head", "mean")
# t.testing.assert_close(W_O_mean_over_output, t.zeros_like(W_O_mean_over_output))
#
# b_O_mean_over_output = einops.reduce(model.b_O, "layer d_model -> layer", "mean")
# t.testing.assert_close(b_O_mean_over_output, t.zeros_like(b_O_mean_over_output))
#
# W_E_mean_over_output = einops.reduce(model.W_E, "token d_model -> token", "mean")
# t.testing.assert_close(W_E_mean_over_output, t.zeros_like(W_E_mean_over_output))
#
# W_pos_mean_over_output = einops.reduce(model.W_pos, "position d_model -> position", "mean")
# t.testing.assert_close(W_pos_mean_over_output, t.zeros_like(W_pos_mean_over_output))
#
# b_V = model.b_V
# t.testing.assert_close(b_V, t.zeros_like(b_V))
# ```
#
# </details>

# %% [markdown]
#
# A demonstration of the model working:
#

# %%
from eindex import eindex

N = 500
dataset = SortedListDataset(size=N, list_len=10, max_value=50, seed=43)

logits, cache = model.run_with_cache(dataset.toks)
logits: t.Tensor = logits[:, dataset.list_len:-1, :]

targets = dataset.toks[:, dataset.list_len+1:]

logprobs = logits.log_softmax(-1) # [batch seq_len vocab_out]
probs = logprobs.softmax(-1)

batch_size, seq_len = dataset.toks.shape
logprobs_correct = eindex(logprobs, targets, "batch seq [batch seq]")
probs_correct = eindex(probs, targets, "batch seq [batch seq]")

avg_cross_entropy_loss = -logprobs_correct.mean().item()

print(f"Average cross entropy loss: {avg_cross_entropy_loss:.3f}")
print(f"Mean probability on correct label: {probs_correct.mean():.3f}")
print(f"Median probability on correct label: {probs_correct.median():.3f}")
print(f"Min probability on correct label: {probs_correct.min():.3f}")

# %% [markdown]
# And a visualisation of its probability output for a single sequence:

# %%
def show(i):

    imshow(
        probs[i].T,
        y=dataset.vocab,
        x=[f"{dataset.str_toks[i][j]}<br><sub>({j})</sub>" for j in range(dataset.list_len+1, dataset.seq_len)],
        labels={"x": "Token", "y": "Vocab"},
        xaxis_tickangle=0,
        title=f"Sample model probabilities:<br>Unsorted = ({','.join(dataset.str_toks[i][:dataset.list_len])})",
        text=[
            ["〇" if (str_tok == target) else "" for target in dataset.str_toks[i][dataset.list_len+1: dataset.seq_len]]
            for str_tok in dataset.vocab
        ],
        width=400,
        height=1000,
    )

show(0)

# %% [markdown]
# Best of luck! 🎈

# %% [markdown]
# The algorithm the transformer seems to run is roughly:
# **Find the smallest value not smaller than the current token, which hasn't been "cancelled" by an equivalent copy appearing already in the sorted list**
#
# Head 0 is mostly doing the cancelling, while head 1 is mostly doing the copying, except for token values around 28--37 where head 0 is doing copying and head 1 is doing nothing.
#
# Additional notes:
# - The skip connection (embed -> unembed) is a small bias against the current token, a smaller bias against numbers less than the current token, and a smaller bias in favor of numbers greater than the current token.
# - The layernorm scaling is fairly uniform at positions on the unsorted list but a bit less uniform on the sorted prefix (after the SEP token)
# - It seems like the cancelling doesn't work that well when there are tokens in the range where the head behavior is swapped, so most of the computation should work even in the absence of cancelling.  The cancelling presumably just tips the scales in marginal cases (and cases where there are duplicates), since most of the head's capacity is devoted to positive copying when such tokens are present.

# %% [markdown]
# To validate this hypothesis, we need to establish a couple of assertions:
#
# Let $S$ be the range of swapped tokens, $S = [28, 29, 30, 31, 32, 33, 34, 35, 36, 37]$.
#
# Let $h_{k}$ denote head 0 for tokens $k \in S$ and head 1 otherwise.
#
# 1. When the query token is SEP in position 10, we find the minimum of the sequence
# 2. When the query token is 50 in position 19, we emit 50
# 3. When the query token is anything other than 50 in position 19, we emit the maximum of the sequence
# 4. When the query is in positions between 11 and 18 inclusive, we follow the rough algorithm above.
#
# We can break down:
# 1. Breakdown:
#    1. Attention by head $h_{k}$ is mostly monotonic decreasing in the value of the token $k$
#    2. The OV circuit on head $h_{k}$ copies the value $k$ more than anything else
#    3. We pay enough more attention to the smallest token than to everything else combined and copy $k$ enough more than anything else that when we combine the effects of the two heads on other tokens, we still manage to copy the correct token.
# 2. Breakdown:
#    1. The copying effects from attending to 50 in position 19 and one additional 50 in some position before 10 gives enough difference between 50 and anything else that we don't care what happens elsewhere.
# 3. Breakdown (TODO: Check if this is right, it might not be)
#    1. Attention by head $h_{k}$ in position 19 is mostly monotonic increasing in the value of the token $k$
#    2. The OV circuit on head $h_{k}$ copies the value $k$ more than anything else
#    3. We pay enough more attention to the largest token than to everything else combined and copy $k$ enough more than anything else that when we combine the effects of the two heads on other tokens, we still manage to copy the correct token.
# 4. Breakdown:
#    1. For $k_1, k_2, q \not\in S$ with $k_1 < q \le k_2$, head 1 pays more attention to $k_2$ in positions before 10 than to $k_1$ in any position
#    2. For $k_1, k_2, q \not\in S$ with $k_1 = q \le k_2$, head 1 pays more attention to $k_2$ in positions before 10 than to $k_1$ in positions after 10
#    3. For $k_1, k_2, q \not\in S$ with $q \le k_1 < k_2$, head 1 pays more attention to $k_1$ in positions before 10 than to $k_2$ in positions before 10
#    4. For $k_2 \in S$ with $k_1 < q \le k_2$, head 0 pays more attention to $k_2$ in positions before 10 than to $k_1$ in any position
#    5. For $k_2 \in S$ with $k_1 = q \le k_2$, head 0 pays more attention to $k_2$ in positions before 10 than to $k_1$ in positions after 10
#    6. For $k_1 \in S$ with $q \le k_1 < k_2$, head 0 pays more attention to $k_1$ in positions before 10 than to $k_2$ in positions before 10
#    7. TODO more stuff

# %% [markdown]
# # Setup
#

# %% [markdown]
# ## Imports

# %%
from einops import einsum, rearrange, reduce
import torch
from matplotlib.widgets import Slider
from matplotlib import colors
from tqdm.auto import tqdm
from matplotlib.animation import FuncAnimation
import circuitsvis as cv
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import numpy as np
import transformer_lens.utils as utils
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from transformer_lens import HookedTransformer
import math

# %% [markdown]
# ## Utils

# %%
def imshow(tensor, renderer=None, xaxis="", yaxis="", color_continuous_scale="RdBu", **kwargs):
    px.imshow(utils.to_numpy(tensor), color_continuous_midpoint=0.0, color_continuous_scale=color_continuous_scale, labels={"x":xaxis, "y":yaxis}, **kwargs).show(renderer)


def line(tensor, renderer=None, xaxis="", yaxis="", line_labels=None, **kwargs):
    px.line(utils.to_numpy(tensor), labels={"x":xaxis, "y":yaxis}, y=line_labels, **kwargs).show(renderer)


def scatter(x, y, xaxis="", yaxis="", caxis="", renderer=None, **kwargs):
    x = utils.to_numpy(x)
    y = utils.to_numpy(y)
    px.scatter(y=y, x=x, labels={"x":xaxis, "y":yaxis, "color":caxis}, **kwargs).show(renderer)


def hist(tensor, renderer=None, xaxis="", yaxis="", **kwargs):
    px.histogram(utils.to_numpy(tensor), labels={"x":xaxis, "y":yaxis}, **kwargs).show(renderer)

def make_tickvals_text(step=10, include_lastn=1, skip_lastn=0, dataset=dataset):
    all_tickvals_text = list(enumerate(dataset.vocab))
    tickvals_indices = list(range(0, len(all_tickvals_text) - 1 - include_lastn - skip_lastn, step)) + list(range(len(all_tickvals_text) - 1 - include_lastn, len(all_tickvals_text)))
    tickvals = [all_tickvals_text[i][0] for i in tickvals_indices]
    ticktext = [all_tickvals_text[i][1] for i in tickvals_indices]
    return tickvals, ticktext

# %% [markdown]
# # Computation of Matrices (used in both visualization and as a cached computation in proofs)

# %%
@torch.no_grad()
def nanify_attn_sep_loc(attn_all, outdim='h qpos kpos qtok ktok', sep_loc=dataset.list_len, nanify_bad_self_attention=False):
    ref_outdim = 'h qpos kpos qtok ktok'
    attn_all = rearrange(attn_all, f'{outdim} -> {ref_outdim}')
    # attention paid from the SEP position always has query = SEP
    attn_all[:, sep_loc, :, :-1, :] = float('nan')
    # attention paid to the SEP position is always to SEP
    attn_all[:, :, sep_loc, :, :-1] = float('nan')
    # attention paid from non-SEP positions never has query = SEP
    attn_all[:, :sep_loc, :, -1, :], attn_all[:, sep_loc+1:, :, -1, :] = float('nan'), float('nan')
    # attention paid to non-SEP positions never has key = SEP
    attn_all[:, :, :sep_loc, :, -1], attn_all[:, :, sep_loc+1:, :, -1] = float('nan'), float('nan')
    # self-attention always has query token = key token
    if nanify_bad_self_attention:
        for h in range(attn_all.shape[0]):
            for pos in range(attn_all.shape[1]):
                for qtok in range(attn_all.shape[3]):
                    for ktok in range(attn_all.shape[4]):
                        if qtok != ktok:
                            attn_all[h, pos, pos, qtok, ktok] = float('nan')
    attn_all = rearrange(attn_all, f'{ref_outdim} -> {outdim}')
    return attn_all

@torch.no_grad()
def compute_attn_all(model, outdim='h qpos kpos qtok ktok', nanify_sep_loc=None, nanify_bad_self_attention=False):
    resid = model.blocks[0].ln1(model.W_pos[:,None,:] + model.W_E[None,:,:])
    outdimsorted = [i for i in sorted(outdim.split(' ')) if i != '']
    assert outdimsorted == list(sorted(['h', 'qpos', 'kpos', 'qtok', 'ktok'])), f"outdim must be 'h qpos kpos qtok ktok' in some order, got {outdim}"
    q_all = einsum(resid,
                   model.W_Q[0,:,:,:],
                   'qpos qtok d_model_q, h d_model_q d_head -> qpos qtok h d_head') + model.b_Q[0]
    k_all = einsum(resid,
                   model.W_K[0,:,:,:],
                   'kpos ktok d_model_k, h d_model_k d_head -> kpos ktok h d_head') + model.b_K[0]
    attn_all = einsum(q_all, k_all, f'qpos qtok h d_head, kpos ktok h d_head -> {outdim}') \
        / model.blocks[0].attn.attn_scale
    attn_all_max = reduce(attn_all, f"{outdim} -> {outdim.replace('kpos', '()').replace('ktok', '()')}", 'max')
    # print(attn_all_max.shape)
    # print(attn_all.shape)
    # #attn_all[:,dataset.list_len:-1,:,:-1,:]
    attn_all = attn_all - attn_all_max
    if nanify_sep_loc is not None: attn_all = nanify_attn_sep_loc(attn_all, outdim=outdim, sep_loc=nanify_sep_loc, nanify_bad_self_attention=nanify_bad_self_attention)
    return attn_all

# %%
@torch.no_grad()
def compute_attention_patterns(model, sep_pos=dataset.list_len, nanify_impossible_nonmin=True, num_min=1):
    '''
    returns post-softmax attention paid to the minimum token, the nonminimum token, and to the sep token
    in shape (head, 2, mintok, nonmintok, 3)

    The 2 is for computing both the min attention paid to the min tok and the max attention paid to the min tok
    The 3 is for mintok, nonmintok, and sep
    '''
    attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok', nanify_sep_loc=dataset.list_len)
    n_heads, _, _, d_vocab, _ = attn_all.shape
    d_vocab -= 1 # remove sep token
    num_nonmin = sep_pos - num_min
    attn_all = attn_all[:, sep_pos, :sep_pos+1, -1, :]
    # (h, kpos, ktok)
    # scores is presoftmax
    # print(attn_all[:, :, 22])
    # print(attn_all[:, -1:, -1])
    attn_scores = t.zeros((n_heads, 2, d_vocab, d_vocab, sep_pos+1), device=attn_all.device)
    # set attention paid to sep token
    attn_scores[:, :, :, :, -1] = attn_all[:, None, None, None, -1, -1]
    # remove sep token
    attn_all = attn_all[:, :-1, :-1]
    # sort attn_all along dim=1
    attn_all, _ = attn_all.sort(dim=1)
    # set min attention paid to min token across all positions
    attn_scores[:, 0, :, :, :num_min] = rearrange(attn_all[:, :num_min, :, None], 'h kpos ktokmin ktoknonmin -> h ktokmin ktoknonmin kpos')
    # set max attention paid to min token across all positions
    attn_scores[:, 1, :, :, :num_min] = rearrange(attn_all[:, -num_min:, :, None], 'h kpos ktokmin ktoknonmin -> h ktokmin ktoknonmin kpos')
    # set max attention paid to non-min-token across all positions (corresponds to min attention paid to min token)
    attn_scores[:, 0, :, :, num_min:-1] = rearrange(attn_all[:, -num_nonmin:, :, None], 'h kpos ktoknonmin ktokmin -> h ktokmin ktoknonmin kpos')
    # set min attention paid to non-min-token across all positions (corresponds to max attention paid to min token)
    attn_scores[:, 1, :, :, num_min:-1] = rearrange(attn_all[:, :num_nonmin, :, None], 'h kpos ktoknonmin ktokmin -> h ktokmin ktoknonmin kpos')

    # compute softmax
    attn_pattern_expanded = attn_scores.softmax(dim=-1)

    # remove rows corresponding to impossible non-min tokens
    if nanify_impossible_nonmin:
        for mintok in range(d_vocab):
            attn_pattern_expanded[:, :, mintok, :mintok, :] = float('nan')

    attn_pattern = t.zeros((n_heads, 2, d_vocab, d_vocab, 3), device=attn_all.device)
    attn_pattern[:, :, :, :, 0] = attn_pattern_expanded[:, :, :, :, :num_min].sum(dim=-1)
    attn_pattern[:, :, :, :, 1] = attn_pattern_expanded[:, :, :, :, num_min:-1].sum(dim=-1)
    attn_pattern[:, :, :, :, 2] = attn_pattern_expanded[:, :, :, :, -1]

    # for min = nonmin, move all attention to min
    for mintok in range(d_vocab):
        attn_pattern[:, :, mintok, mintok, 0] += attn_pattern[:, :, mintok, mintok, 1]
        attn_pattern[:, :, mintok, mintok, 1] = 0

    return attn_pattern
# %%
@torch.no_grad()
def compute_3way_attention_patterns(model, sep_pos=dataset.list_len, nanify_impossible_nonmin=True, num_min=1, num_nonmin1=1, attn_all=None, attn_all_outdim=None):
    '''
    returns post-softmax attention paid to the minimum token, two nonminimum tokens, and to the sep token
    in shape (head, 3, 2, mintok, nonmintok1, nonmintok2, 4)

    The 3, 2 is for the permutations of attention ordering by position, min vs nonmin1 vs nonmin2 in the lowest attention positions, and then which of the remaining two is in the highest attention position.
    The 4 is for mintok, nonmintok1, nonmintok2, and sep
    '''
    desired_attn_all_outdim = 'h qpos kpos qtok ktok'
    if attn_all is None:
        return compute_3way_attention_patterns(
            model, sep_pos=sep_pos, nanify_impossible_nonmin=nanify_impossible_nonmin, num_min=num_min, num_nonmin1=num_nonmin1,
            attn_all=compute_attn_all(model, outdim=desired_attn_all_outdim, nanify_sep_loc=sep_pos), attn_all_outdim=desired_attn_all_outdim)
    assert attn_all_outdim is not None
    attn_all = rearrange(attn_all, f'{attn_all_outdim} -> {desired_attn_all_outdim}')
    n_heads, _, _, d_vocab, _ = attn_all.shape
    d_vocab -= 1 # remove sep token
    num_nonmin2 = sep_pos - num_min
    attn_all = attn_all[:, sep_pos, :sep_pos+1, -1, :]
    # (h, kpos, ktok)
    # scores is presoftmax
    attn_scores = t.zeros((n_heads, 3, 2, d_vocab, d_vocab, d_vocab, sep_pos+1), device=attn_all.device)
    # set attention paid to sep token
    attn_scores[:, :, :, :, :, :, -1] = attn_all[:, None, None, None, None, None, -1, -1]
    # remove sep token
    attn_all = attn_all[:, :-1, :-1]
    # sort attn_all along dim=1
    attn_all, _ = attn_all.sort(dim=1)
    # set min attention paid to min token across all positions
    attn_scores[:, 0, :, :, :, :, :num_min] = rearrange(attn_all[:, :num_min, :, None, None, None], 'h kpos ktokmin ktoknonmin1 ktoknonmin2 minpos -> h minpos ktokmin ktoknonmin1 ktoknonmin2 kpos')
    # set max attention paid to min token across all positions
    attn_scores[:, 1:, 0, :, :, :, :num_min] = rearrange(attn_all[:, -num_min:, :, None, None, None], 'h kpos ktokmin ktoknonmin1 ktoknonmin2 minpos -> h minpos ktokmin ktoknonmin1 ktoknonmin2 kpos')
    # set middle attention paid to min token across all positions
    attn_scores[:, 1, 1, :, :, :, :num_min] = rearrange(attn_all[:, num_nonmin1:num_nonmin1+num_min, :, None, None], 'h kpos ktokmin ktoknonmin1 ktoknonmin2 -> h ktokmin ktoknonmin1 ktoknonmin2 kpos')
    attn_scores[:, 2, 1, :, :, :, :num_min] = rearrange(attn_all[:, -(num_nonmin1+num_min):-num_nonmin1, :, None, None], 'h kpos ktokmin ktoknonmin1 ktoknonmin2 -> h ktokmin ktoknonmin1 ktoknonmin2 kpos')

    # set min attention paid to nonmin2 token across all positions
    attn_scores[:, -1, :, :, :, :, -(num_nonmin2+1):-1] = rearrange(attn_all[:, :num_nonmin2, :, None, None, None], 'h kpos ktoknonmin2 ktokmin ktoknonmin1 minpos -> h minpos ktokmin ktoknonmin1 ktoknonmin2 kpos')
    # set max attention paid to nonmin2 token across all positions
    attn_scores[:, :-1, -1, :, :, :, -(num_nonmin2+1):-1] = rearrange(attn_all[:, -num_nonmin2:, :, None, None, None], 'h kpos ktoknonmin2 ktokmin ktoknonmin1 minpos -> h minpos ktokmin ktoknonmin1 ktoknonmin2 kpos')
    # set middle attention paid to nonmin2 token across all positions
    attn_scores[:, 0, 0, :, :, :, -(num_nonmin2+1):-1] = rearrange(attn_all[:, num_min:num_min+num_nonmin2, :, None, None], 'h kpos ktoknonmin2 ktokmin ktoknonmin1 -> h ktokmin ktoknonmin1 ktoknonmin2 kpos')
    attn_scores[:, 1, 0, :, :, :, -(num_nonmin2+1):-1] = rearrange(attn_all[:, -(num_min+num_nonmin2):-num_min, :, None, None], 'h kpos ktoknonmin2 ktokmin ktoknonmin1 -> h ktokmin ktoknonmin1 ktoknonmin2 kpos')

    # set min attention paid to nonmin1 token across all positions
    attn_scores[:, -1, :, :, :, :, num_min:num_min+num_nonmin1] = rearrange(attn_all[:, :num_nonmin1, :, None, None, None], 'h kpos ktoknonmin1 ktokmin ktoknonmin2 minpos -> h minpos ktokmin ktoknonmin1 ktoknonmin2 kpos')
    # set max attention paid to nonmin1 token across all positions
    attn_scores[:, :-1, -1, :, :, :, num_min:num_min+num_nonmin1] = rearrange(attn_all[:, -num_nonmin1:, :, None, None, None], 'h kpos ktoknonmin1 ktokmin ktoknonmin2 minpos -> h minpos ktokmin ktoknonmin1 ktoknonmin2 kpos')
    # set middle attention paid to nonmin1 token across all positions
    attn_scores[:, 0, 1, :, :, :, num_min:num_min+num_nonmin1] = rearrange(attn_all[:, num_min:num_min+num_nonmin1, :, None, None], 'h kpos ktoknonmin1 ktokmin ktoknonmin2 -> h ktokmin ktoknonmin1 ktoknonmin2 kpos')
    attn_scores[:, -1, 0, :, :, :, num_min:num_min+num_nonmin1] = rearrange(attn_all[:, -(num_min+num_nonmin1):-num_min, :, None, None], 'h kpos ktoknonmin1 ktokmin ktoknonmin2 -> h ktokmin ktoknonmin1 ktoknonmin2 kpos')

    # compute softmax
    attn_pattern_expanded = attn_scores.softmax(dim=-1)

    # remove rows corresponding to impossible non-min tokens
    if nanify_impossible_nonmin:
        for mintok in range(d_vocab):
            attn_pattern_expanded[:, :, :, mintok, :mintok, :, :] = float('nan')
            attn_pattern_expanded[:, :, :, mintok, :, :mintok, :] = float('nan')

    attn_pattern = t.zeros((n_heads, 3, 2, d_vocab, d_vocab, d_vocab, 4), device=attn_all.device)
    attn_pattern[:, :, :, :, :, :, 0] = attn_pattern_expanded[:, :, :, :, :, :, :num_min].sum(dim=-1)
    attn_pattern[:, :, :, :, :, :, 1] = attn_pattern_expanded[:, :, :, :, :, :, num_min:num_min+num_nonmin1].sum(dim=-1)
    attn_pattern[:, :, :, :, :, :, 2] = attn_pattern_expanded[:, :, :, :, :, :, num_min+num_nonmin1:-1].sum(dim=-1)
    attn_pattern[:, :, :, :, :, :, 3] = attn_pattern_expanded[:, :, :, :, :, :, -1]

    # remove rows corresponding to impossible non-min tokens
    if nanify_impossible_nonmin:
        for mintok in range(d_vocab):
            attn_pattern_expanded[:, :, :, mintok, :mintok, :, :] = float('nan')
            attn_pattern_expanded[:, :, :, mintok, :, :mintok, :] = float('nan')

    for mintok in range(d_vocab):
        # for min = nonmin1, move all attention to min
        attn_pattern[:, :, :, mintok, mintok, :, 0] += attn_pattern[:, :, :, mintok, mintok, :, 1]
        attn_pattern[:, :, :, mintok, mintok, :, 1] = 0
        # for min = nonmin2, move all attention to min
        attn_pattern[:, :, :, mintok, :, mintok, 0] += attn_pattern[:, :, :, mintok, :, mintok, 2]
        attn_pattern[:, :, :, mintok, :, mintok, 2] = 0
        # for nonmin1 = nonmin2, move all attention to nonmin1
        attn_pattern[:, :, :, :, mintok, mintok, 1] += attn_pattern[:, :, :, :, mintok, mintok, 2]
        attn_pattern[:, :, :, :, mintok, mintok, 2] = 0

    return attn_pattern

@torch.no_grad()
def compute_3way_attention_patterns_all_counts(model, sep_pos=dataset.list_len, nanify_impossible_nonmin=True, max_num_min=dataset.list_len-2, max_num_nonmin1=dataset.list_len-2, attn_all=None, attn_all_outdim='h qpos kpos qtok ktok'):
    '''
    returns post-softmax attention paid to the minimum token, two nonminimum tokens, and to the sep token
    in shape (num_min, num_nonmin1, head, 3, 2, mintok, nonmintok1, nonmintok2, 4)

    The 3, 2 is for the permutations of attention ordering by position, min vs nonmin1 vs nonmin2 in the lowest attention positions, and then which of the remaining two is in the highest attention position.
    The 4 is for mintok, nonmintok1, nonmintok2, and sep
    '''
    if attn_all is None:
        return compute_3way_attention_patterns_all_counts(
            model, sep_pos=sep_pos, nanify_impossible_nonmin=nanify_impossible_nonmin, max_num_min=max_num_min, max_num_nonmin1=max_num_nonmin1,
            attn_all=compute_attn_all(model, outdim=attn_all_outdim, nanify_sep_loc=sep_pos), attn_all_outdim=attn_all_outdim)

    n_heads, _, _, d_vocab, _ = attn_all.shape
    d_vocab -= 1 # remove sep token
    default = t.zeros((n_heads, 3, 2, d_vocab, d_vocab, d_vocab, 4), device=attn_all.device)
    default[...] = float('nan')

    return torch.stack([torch.stack([
        compute_3way_attention_patterns(model, sep_pos=sep_pos, nanify_impossible_nonmin=nanify_impossible_nonmin, num_min=num_min, num_nonmin1=num_nonmin1, attn_all=attn_all, attn_all_outdim=attn_all_outdim)
        if num_min + num_nonmin1 + 1 <= sep_pos else default
        for num_nonmin1 in range(1, max_num_nonmin1+1)
    ], dim=0)
    for num_min in range(1, max_num_min+1)], dim=0) # tqdm

# %%
@torch.no_grad()
def compute_EPVOU(model, nanify_sep_position=dataset.list_len):
    EPV = model.blocks[0].ln1(model.W_pos[:, None, :] + model.W_E[None, :, :])[None, :, :, :] @ model.W_V[0,:,None,:,:] + model.b_V[0, :, None, None, :]
    # (head, pos, input, d_head)
    # b_O is not split amongst the heads, so we distribute it evenly amongst heads
    EPVO = EPV @ model.W_O[0,:,None,:,:] + model.b_O[0, None, None, None, :] / model.cfg.n_heads
    # (head, pos, input, d_model)
    EPVOU = layernorm_noscale(EPVO) @ model.W_U
    # (head, pos, input, output)
    EPVOU = EPVOU - EPVOU.mean(dim=-1, keepdim=True)
    if nanify_sep_position is not None:
        # SEP is the token in the SEP position
        EPVOU[:, nanify_sep_position, :-1, :] = float('nan')
        # SEP never occurs in positions other than the SEP position
        EPVOU[:, :nanify_sep_position, -1, :], EPVOU[:, nanify_sep_position+1:, -1, :] = float('nan'), float('nan')
    return EPVOU
# %%
@torch.no_grad()
def compute_EUPU(model, nanify_sep_position=dataset.list_len):
    EUPU = layernorm_noscale(model.W_pos[:, None, :] + model.W_E[None, :, :]) @ model.W_U + model.b_U[None, None, :]
    EUPU = EUPU - EUPU.mean(dim=-1, keepdim=True)
    if nanify_sep_position is not None:
        # SEP is the token in the SEP position
        EUPU[nanify_sep_position, :-1, :] = float('nan')
        # SEP never occurs in positions other than the SEP position
        EUPU[:nanify_sep_position, -1, :], EUPU[nanify_sep_position+1:, -1, :] = float('nan'), float('nan')
    return EUPU

# %%
@torch.no_grad()
def compute_EPVOU_EUPU(model, nanify_sep_position=dataset.list_len, qtok=-1, qpos=dataset.list_len):
    '''
    return indexed by (head, n_ctx_k, d_vocab_k, d_vocab_out)
    '''
    EPVOU = compute_EPVOU(model, nanify_sep_position=nanify_sep_position)
    # (head, pos, input, output)
    EUPU = compute_EUPU(model, nanify_sep_position=nanify_sep_position)
    # (pos, input, output)
    return EPVOU + EUPU[qpos, qtok, None, None, None, :] / EPVOU.shape[0]

# %%
@torch.no_grad()
def layernorm_noscale(x: torch.Tensor) -> torch.Tensor:
    return x - x.mean(axis=-1, keepdim=True)

@torch.no_grad()
def layernorm_scales(x: torch.Tensor, eps: float = 1e-5, recip: bool = True) -> torch.Tensor:
    x = layernorm_noscale(x)
    scale = (x.pow(2).mean(axis=-1, keepdim=True) + eps).sqrt()
    if recip: scale = 1 / scale
    return scale

# %% [markdown]
# # Exploratory Plots
#
# Before diving into the proof, we provide some plots that may help with understanding the above claims.  These are purely exploratory (aimed at hypothesis generation) and are not required for hypothesis validation.

# %% [markdown]
# ## Initial Layernorm Scaling


# %%
s = layernorm_scales(model.W_pos[:,None,:] + model.W_E[None,:,:])[...,0]
# the only token in position 10 is SEP
s[dataset.list_len, :-1] = float('nan')
# SEP never occurs in positions other than 10
s[:dataset.list_len, -1:], s[dataset.list_len+1:, -1:] = float('nan'), float('nan')
# we don't actually care about the prediction in the last position
s = s[:-1, :]
smin = s[~s.isnan()].min()
# s = s / smin
px.imshow(utils.to_numpy(s), color_continuous_scale='Sunsetdark', labels={"x":"Token Value", "y":"Position"}, title=f"Layer Norm Scaling", x=dataset.vocab).show(None)

# %% [markdown]
# ## Attention Plots

# %%
# Attention
attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok', nanify_sep_loc=dataset.list_len)
attn_subset = attn_all[:, dataset.list_len, :dataset.list_len+1, -1, :]
zmin, zmax = attn_subset[~attn_subset.isnan()].min().item(), attn_subset[~attn_subset.isnan()].max().item()

fig = make_subplots(rows=1, cols=model.cfg.n_heads, subplot_titles=("Head 0", "Head 1"))
fig.update_layout(title="Attention (pre-softmax) from SEP to other tokens and positions")
tickvals, ticktext = make_tickvals_text(step=10, include_lastn=0, skip_lastn=1, dataset=dataset)
for h in range(model.cfg.n_heads):
    fig.add_trace(go.Heatmap(z=utils.to_numpy(attn_subset[h]), colorscale='Plasma', zmin=zmin, zmax=zmax, hovertemplate="Token: %{x}<br>Position: %{y}<br>Attention: %{z}<extra>Head " + str(h) + "</extra>"), row=1, col=h+1)
    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, title_text="Key Token", row=1, col=h+1)
    fig.update_yaxes(title_text="Position of Key", row=1, col=h+1)
fig.show()

# %%
# Attention Across Positions
attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok', nanify_sep_loc=dataset.list_len)
zmax = attn_all[~attn_all.isnan()].max().item()
zmin = attn_all[~attn_all.isnan()].min().item()

default_attn = t.zeros_like(attn_all[0, 0, 0])
default_attn[:, :] = float('nan')
default_attn = utils.to_numpy(default_attn)

n_cols = 10
n_rows_per_head = (dataset.seq_len - 1 - 1) // n_cols + 1
n_rows = n_rows_per_head * model.cfg.n_heads

tickvals, ticktext = make_tickvals_text(step=20, include_lastn=0, skip_lastn=0, dataset=dataset)

subplot_titles = []
for h in range(model.cfg.n_heads):
    subplot_titles += [f"{h}:{kpos}" for kpos in range(dataset.seq_len - 1)]
    subplot_titles += ["" for _ in range(dataset.seq_len - 1, n_cols * n_rows_per_head)]
fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=subplot_titles)
fig.update_annotations(font_size=5)
fig.update_layout(title="Attention head:key_position, x=key token, y=query token")

def make_update(qpos, h=None, kpos=None, showscale=False, include_tickvals_ticktext=False):
    if h is None or kpos is None:
        return [make_update(qpos, h, kpos, include_tickvals_ticktext=include_tickvals_ticktext) for h in range(model.cfg.n_heads) for kpos in range(n_cols * n_rows_per_head)]
    cur_attn = attn_all[h, qpos, kpos] if kpos <= qpos else default_attn
    x = dataset.vocab
    cur_tickvals, cur_ticktext = tickvals, ticktext
    if kpos == dataset.list_len:
        cur_attn = cur_attn[:, -1:]
        # nan_column = torch.full((cur_attn.shape[0], 1), float('nan'), device=cur_attn.device, dtype=cur_attn.dtype)
        # cur_attn = torch.cat([nan_column, cur_attn, nan_column], dim=1)
        # x, cur_tickvals, cur_ticktext = [float('nan'), x[-1], float('nan')], [float('nan'), cur_tickvals[-1], float('nan')], ['', cur_ticktext[-1], '']
        x, cur_tickvals, cur_ticktext = x[-1:], cur_tickvals[-1:], cur_ticktext[-1:]
    trace = go.Heatmap(z=utils.to_numpy(cur_attn), colorscale='Plasma', zmin=zmin, zmax=zmax, showscale=showscale, x=x, y=dataset.vocab, hovertemplate="Key: %{x}<br>Query: %{y}<br>Attention: %{z}<extra>" + f"Head {h}<br>Key Pos {kpos}<br>Query Pos {qpos}" + "</extra>")
    if include_tickvals_ticktext: return trace, cur_tickvals, cur_ticktext
    return trace

def update(qpos):
    fig.data = []
    for i, (trace, cur_tickvals, cur_ticktext) in enumerate(make_update(qpos, include_tickvals_ticktext=True)):
        row, col = i // n_cols + 1, i % n_cols + 1
        fig.add_trace(trace, row=row, col=col)
        fig.update_xaxes(tickvals=cur_tickvals, ticktext=cur_ticktext, constrain='domain', row=row, col=col, tickfont=dict(size=5), title_font=dict(size=5))
        fig.update_yaxes(autorange='reversed', scaleanchor="x", scaleratio=1, row=row, col=col, tickvals=tickvals, ticktext=ticktext, tickfont=dict(size=5), title_font=dict(size=5))

# Create the initial heatmap
update(dataset.seq_len-2)

# Create frames for each position
frames = [go.Frame(
    data=make_update(qpos),
    name=str(qpos)
) for qpos in range(dataset.list_len+1, dataset.seq_len - 1)]

fig.frames = frames

# # Add animation controls
# animation_settings = dict(
#     frame=dict(duration=1000, redraw=True),
#     fromcurrent=True,
#     transition=dict(duration=0)
# )

# Create slider
sliders = [dict(
    active=len(fig.frames) - 1,
    yanchor='top',
    xanchor='left',
    currentvalue=dict(font=dict(size=20), prefix='Query Position:', visible=True, xanchor='right'),
    transition=dict(duration=0),
    pad=dict(b=10, t=50),
    len=0.9,
    x=0.1,
    y=0,
    steps=[dict(args=[[frame.name], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                method='animate',
                label=frame.name) for frame in fig.frames]
)]

fig.update_layout(
    sliders=sliders
)

# fig.update_layout(
#     updatemenus=[dict(
#         type='buttons',
#         showactive=False,
#         buttons=[dict(label='Play',
#                       method='animate',
#                       args=[None, animation_settings])]
#     )]
# )

fig.show()

# %% [markdown]
# ## OV Attention Head Plots

# %%
EPVOU = compute_EPVOU(model, nanify_sep_position=dataset.list_len)
zmax = EPVOU[~EPVOU.isnan()].abs().max().item()
EPVOU = utils.to_numpy(EPVOU)

fig = make_subplots(rows=1, cols=model.cfg.n_heads, subplot_titles=[f"head {h}" for h in range(model.cfg.n_heads)])
# fig.update_annotations(font_size=12)
fig.update_layout(title="OV Logit Impact: x=Ouput Logit Token, y=Input Token<br>LN_noscale(LN1(W_pos[pos,:] + W_E) @ W_V[0,h] @ W_O[0, h]) @ W_U")

tickvals, ticktext = make_tickvals_text(step=10, include_lastn=0, skip_lastn=1, dataset=dataset)

def make_update(pos, h, adjust_sep=True):
    cur_EPVOU = EPVOU[h, pos]
    y = dataset.vocab
    if adjust_sep and pos == dataset.list_len:
        cur_EPVOU = cur_EPVOU[-1:, :]
        y = y[-1:]
    elif pos != dataset.list_len:
        cur_EPVOU = cur_EPVOU[:-1, :]
        y = y[:-1]
    return go.Heatmap(z=utils.to_numpy(cur_EPVOU), colorscale='Picnic_r', x=dataset.vocab, y=y, zmin=-zmax, zmax=zmax, showscale=(h == 0), hovertemplate="Input Token: %{y}<br>Output Token: %{x}<br>Logit: %{z}<extra>" + f"Head {h}<br>Pos {pos}" + "</extra>")

def update(pos):
    fig.data = []
    for h in range(model.cfg.n_heads):
        fig.add_trace(make_update(pos, h), row=1, col=h+1)
        fig.update_xaxes(constrain='domain', row=1, col=h+1) #, title_text="Output Logit Token"
        if pos == dataset.list_len:
            fig.update_yaxes(range=[-1,1], row=1, col=h+1)
        else:
            fig.update_yaxes(autorange='reversed', row=1, col=h+1)

# Create the initial heatmap
update(0)

# Create frames for each position
frames = [go.Frame(
    data=[make_update(pos, h, adjust_sep=True) for h in range(model.cfg.n_heads)],
    name=str(pos),
    layout={'yaxis': {'range': ([-1, 1] if pos == dataset.list_len else [len(dataset.vocab)-2, 0])},
        'yaxis2': {'range': ([-1, 1] if pos == dataset.list_len else [len(dataset.vocab)-2, 0])}},
) for pos in range(dataset.seq_len-1)]

fig.frames = frames

# # Add animation controls
# animation_settings = dict(
#     frame=dict(duration=1000, redraw=True),
#     fromcurrent=True,
#     transition=dict(duration=0)
# )

# Create slider
sliders = [dict(
    active=0,
    yanchor='top',
    xanchor='left',
    currentvalue=dict(font=dict(size=20), prefix='Position:', visible=True, xanchor='right'),
    transition=dict(duration=0),
    pad=dict(b=10, t=50),
    len=0.9,
    x=0.1,
    y=0,
    steps=[dict(args=[[frame.name], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                method='animate',
                label=str(pos)) for pos, frame in enumerate(fig.frames)]
)]

fig.update_layout(
    sliders=sliders
)

# fig.update_layout(
#     updatemenus=[dict(
#         type='buttons',
#         showactive=False,
#         buttons=[dict(label='Play',
#                       method='animate',
#                       args=[None, animation_settings])]
#     )]
# )

fig.show()

# %% [markdown]
# ## Skip Connection / Residual Stream Plots

# %%
n_rows = 2
n_cols = 1 + (dataset.list_len - 1) // n_rows
fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=[f"pos={pos}" for pos in range(dataset.list_len, dataset.seq_len - 1)])
fig.update_layout(title="Logit Impact from the embedding (without layernorm scaling)<br>LN_noscale(W_pos[pos,:] + W_E) @ W_U, y=Input, x=Ouput Logit Token")

EUPU = compute_EUPU(model, nanify_sep_position=dataset.list_len)
zmax = EUPU[~EUPU.isnan()].abs().max().item()
EUPU = utils.to_numpy(EUPU)
for i, pos in enumerate(range(dataset.list_len, dataset.seq_len-1)):
    r, c = i // n_cols, i % n_cols
    cur_EUPU = EUPU[pos]
    y = dataset.vocab
    if pos == dataset.list_len:
        cur_EUPU = cur_EUPU[-1:, :]
        y = y[-1:]
    else:
        cur_EUPU = cur_EUPU[:-1, :]
        y = y[:-1]
    fig.add_trace(go.Heatmap(z=utils.to_numpy(cur_EUPU), x=dataset.vocab, y=y, colorscale='Picnic_r', zmin=-zmax, zmax=zmax, showscale=(i==0), hovertemplate="Input Token: %{y}<br>Output Token: %{x}<br>Logit: %{z}<extra>" + f"Pos {pos}" + "</extra>"), row=r+1, col=c+1)
    fig.update_xaxes(constrain='domain', row=r+1, col=c+1) #, title_text="Output Logit Token"
    if pos == dataset.list_len:
        fig.update_yaxes(range=[-1,1], row=r+1, col=c+1)
    else:
        fig.update_yaxes(autorange='reversed', scaleanchor="x", scaleratio=1, row=r+1, col=c+1)
fig.show()

# %% [markdown]
# # Finding the Minimum with query SEP in Position 10

# %% [markdown]
# ## State Space Reduction
#
# **Lemma**: For a single attention head, it suffices to consider sequences with at most two distinct tokens.
#
# Note that we are comparing sequences by pre-final-layernorm-scaling gap between the logit of the minimum token and the logit of any other fixed token.
# Layernorm scaling is non-linear, but if we only care about accuracy and not log-loss, then we can ignore it (neither scaling nor softmax changes which logit is the largest).
#
# **Proof sketch**:
# We show that any sequence with three token values, $x < y < z$, is strictly dominated either by a sequence with just $x$ and $y$ or a sequence with just $x$ and $z$.
#
# Suppose we have $k$ copies of $x$, $n$ copies of $y$, and $\ell - k - n$ copies of $z$, the attention scores are $s_x$, $s_y$, and $s_z$, and the differences between the logit of $x$ and our chosen comparison logit (as computed by the OV circuit for each token) are $v_x$, $v_y$, and $v_z$.
# Then the difference in logit between $x$ and the comparison token is
# $$\left(k e^{s_x} v_x + n e^{s_y} v_y + (\ell - k - n)e^{s_z}v_z \right)\left(k e^{s_x} + n e^{s_y} + (\ell - k - n)e^{s_z}\right)^{-1}$$
# Rearrangement gives
# $$\left(\left(k e^{s_x} v_x + (\ell - k) e^{s_z} v_z\right) + n \left(e^{s_y} v_y - e^{s_z}v_z\right) \right)\left(\left(k e^{s_x} + (\ell - k) e^{s_z}\right) + n \left(e^{s_y} - e^{s_z}\right)\right)^{-1}$$
# This is a fraction of the form $\frac{a + bn}{c + dn}$.  Taking the derivative with respect to $n$ gives $\frac{bc - ad}{(c + dn)^2}$.  Noting that $c + dn$ cannot equal zero for any valid $n$, we get the the derivative never changes sign.  Hence our logit difference is maximized either at $n = 0$ or at $n = \ell - k$, and the sequence with just two values dominates the one with three.
#
# This proof generalizes straightforwardly to sequences with more than three values.
#
# Similarly, this proof shows that, when considering only a single attention head, it suffices to consider sequences of $\ell$ copies of the minimum token and sequences with one copy of the minimum token and $\ell - 1$ copies of the non-minimum token, as intermediate values are dominated by the extremes.
#

# %% [markdown]
# Let's bound how much attention is paid to the minimum token, non-minimum tokens (in aggregate), and the SEP token.
#
# First a plot.  We use green for "paying attention to the minimum token", red for "paying attention to the non-minimum token", and blue for "paying attention to the SEP token".

# %%
# swap the axes so that we have red for nonmin, green for min, and blue for sep
attn_patterns = torch.stack([compute_attention_patterns(model, num_min=num_min)[:, :, :, :, (1, 0, 2)] for num_min in range(1, dataset.list_len)], dim=0)
# (num_min, head, 2, mintok, nonmintok, 3)
attn_patterns[attn_patterns.isnan()] = 1
attn_patterns = utils.to_numpy(attn_patterns * 256)

fig = make_subplots(rows=1, cols=model.cfg.n_heads, subplot_titles=[f"head {h}" for h in range(model.cfg.n_heads)])# {minmax} attn on mintok" for h in range(model.cfg.n_heads) for minmax in ('min', 'max')])
# fig.update_annotations(font_size=12)
minmaxi_g = 0 # min attention, but it doesn't matter much
fig.update_layout(title=f"Attention ({('min', 'max')[minmaxi_g]} on min tok)")

all_tickvals_text = list(enumerate(dataset.vocab[:-1]))
tickvals_indices = list(range(0, len(all_tickvals_text) - 1, 10)) + [len(all_tickvals_text) - 1]
tickvals = [all_tickvals_text[i][0] for i in tickvals_indices]
tickvals_text = [all_tickvals_text[i][1] for i in tickvals_indices]

# # Generate custom hovertext
# all_hovertext = []
# kinds = ['Non-min', 'Min', 'SEP']
# for num_min in range(1, dataset.list_len):
#     hovertext_num_min = []
#     for h in range(model.cfg.n_heads):
#         hovertext_h = []
#         for minmaxi, minmax in enumerate(('min', 'max')):
#             hovertext_minmax = []
#             for mintok in range(attn_patterns.shape[-3]):
#                 for nonmintok in range(attn_patterns.shape[-2]):
#                     value = attn_patterns[num_min - 1, h, minmaxi, mintok, nonmintok]
#                     label = f"Non-min token: {all_tickvals_text[nonmintok][1]}<br>Min token: {all_tickvals_text[mintok][1]}<br>{kinds[value.argmax().item()]} attn: {value.max().item() / 256 * 100}%<br>{kinds[value.argmin().item()]} attn: {value.min().item() / 256 * 100}%"
#                     hovertext_minmax.append(label)
#             hovertext_h.append(hovertext_minmax)
#         hovertext_num_min.append(hovertext_h)
#     all_hovertext.append(hovertext_num_min)

#     # fig.data[0].customdata = np.array(hovertext, dtype=object)
#     # fig.data[0].hovertemplate = '<b>%{customdata}</b>'


def make_update(h, minmaxi, num_min):
    cur_attn_pattern = attn_patterns[num_min - 1, h, minmaxi]
    # cur_hovertext = all_hovertext[num_min - 1][h][minmaxi]
    return go.Image(z=cur_attn_pattern, customdata=cur_attn_pattern / 256 * 100) #, customdata=cur_hovertext, hoverinfo="text", hovertext=cur_hovertext)

def update(num_min, update_title=True):
    fig.data = []
    for h in range(model.cfg.n_heads):
        for minmaxi, minmax in list(enumerate(('min', 'max')))[:1]:
            col, row = h+1, minmaxi+1
            fig.add_trace(make_update(h, minmaxi, num_min), col=col, row=row)
            fig.update_xaxes(tickvals=tickvals, ticktext=tickvals_text, constrain='domain', col=col, row=row, title_text="non-min tok") #, title_text="Output Logit Token"
            fig.update_yaxes(autorange='reversed', scaleanchor="x", scaleratio=1, col=col, row=row, title_text="min tok")
    if update_title: fig.update_layout(title=f"Attention distribution range ({num_min} copies of min tok)")
    fig.update_traces(hovertemplate="Non-min token: %{x}<br>Min token: %{y}<br>Min token attn: %{customdata[1]:.1f}%<br>Nonmin tok attn: %{customdata[0]:.1f}%<br>Sep attn: %{customdata[0]:.1f}%<extra>head %{fullData.name}</extra>")
    # %{color}

# Create the initial heatmap
update(1, update_title=True)

# Create frames for each position
frames = [go.Frame(
    data=[make_update(h, minmaxi, num_min) for h in range(model.cfg.n_heads) for minmaxi in (minmaxi_g, )],
    name=str(num_min)
) for num_min in range(1, dataset.list_len)]

fig.frames = frames

# Create slider
sliders = [dict(
    active=0,
    yanchor='top',
    xanchor='left',
    currentvalue=dict(font=dict(size=20), prefix='# copies of min token:', visible=True, xanchor='right'),
    transition=dict(duration=0),
    pad=dict(b=10, t=50),
    len=0.9,
    x=0.1,
    y=0,
    steps=[dict(args=[[frame.name], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                method='animate',
                label=str(num_min+1)) for num_min, frame in enumerate(fig.frames)]
)]

fig.update_layout(
    sliders=sliders
)


fig.show()

# %% [markdown]
#
# There are some remarkable things about this plot.
#
# 1. For sequences where the minimum token is 19 or larger, the model should basically never get the first token correct, because it's paying too much attention to either the SEP token or the wrong non-min token.
# 2. Even for sequences with 9 or 10 copies of the same number, if that number is 25--39, so much attention is paid to the SEP token (by both heads) that we predict that the model probably gets the wrong answer, even before analyzing OV.
# 3. The plot probably overestimates the incorrect behavior when the non-min token is relatively close to the min token, because the OV matrices do (small) positive copying of numbers below the current one.  We don't analyze this behavior in enough depth here to put hard bounds on when it's enough to compensate for paying attention to the wrong token, but a more thorough analysis would.
#
# Before using the above distributions to place concrete bounds on what fraction of outputs the network gets correct, let's compute cutoffs for the OV behavior.
#
# But first, is this actually right?  Which uniform sequences does the model get wrong?  What fraction of sequences starting at 19 get the wrong minimum?

# %%
uniform_predictions = [model(t.tensor([i] * dataset.list_len + [len(dataset.vocab) - 1] + [i] * dataset.list_len))[0, dataset.list_len].argmax(dim=-1).item() for i in range(len(dataset.vocab) - 1)]
wrong_uniform_predictions = [(i, p) for i, p in enumerate(uniform_predictions) if p != i]
print(f"The model incorrectly predicts the minimum for {len(wrong_uniform_predictions)} sequences ({', '.join(str(i) for i, p in wrong_uniform_predictions)}):\n{' '.join([f'{i} (model: {p})' for i, p in wrong_uniform_predictions])}")

# %% [markdown]
# Interestingly, the model manages to get 35, 36, 37 right, despite paying most attention to SEP.

# %%
n_total_datapoints = 10000
datapoints_per_batch = 1000
# Set a random seed, then generate n_datapoints sequences of length dataset.list_len of numbers between 19 and len(dataset.vocab) - 2, inclusive
# Set random seed for reproducibility
torch.manual_seed(42)
all_predictions = t.zeros((0,), dtype=torch.long)
all_minima = t.zeros((0,), dtype=torch.long)
low = 19
# true minimum, predicted minimum, # copies of minimum
results = t.zeros((len(dataset.vocab) - 1, len(dataset.vocab) - 1, dataset.list_len + 1))
with torch.no_grad():
    for _ in tqdm(range(n_total_datapoints // datapoints_per_batch)):
        for real_low in range(low, len(dataset.vocab) - 1):
            sequences = torch.randint(real_low, len(dataset.vocab) - 1, (datapoints_per_batch, dataset.list_len))
            sorted_sequences = sequences.sort(dim=-1).values
            minima = sorted_sequences[:, 0]
            n_copies = (sequences == minima.unsqueeze(-1)).sum(dim=-1)
            sequences = torch.cat([sequences, torch.full((datapoints_per_batch, 1), len(dataset.vocab) - 1, dtype=torch.long), sorted_sequences], dim=-1)
            # Compute the model's predictions for the minimum
            predictions = model(sequences)[:, dataset.list_len, :].argmax(dim=-1)
            # Compute the actual minimums
            all_predictions = torch.cat([all_predictions, predictions.cpu()])
            all_minima = torch.cat([all_minima, minima.cpu()])
            # count the number of copies of the minimum
            results[minima.cpu(), predictions.cpu(), n_copies.cpu()] += 1
            # if real_low == 45:
            #     good_sequences = sequences
            #     print(set(sequences.cpu()[(minima.cpu() == 45) & (predictions.cpu() == minima.cpu())]))
    # Compute the fraction of correct predictions
    correct = (predictions.cpu() == minima).float().mean().item()
# (true minimum, # copies of minimum)
fraction_correct = (results / results.sum(dim=1, keepdim=True)).diagonal(dim1=0, dim2=1)
# print(f"The model correctly predicts the minimum for {correct * 100}% of sequences of length {dataset.list_len} with numbers between {low} and {len(dataset.vocab) - 2} inclusive")
# # plot predictions - minima against minima
# scatter(all_minima, all_predictions - all_minima, title="Predicted - Actual Minimum vs Actual Minimum", xaxis="Actual Minimum", yaxis="Predicted - Actual Minimum")
# scatter(all_minima, all_predictions, title="Actual Minimum vs Predicted Minimum", xaxis="Actual Minimum", yaxis="Predicted - Actual Minimum")
# scatter(list(range(low, len(dataset.vocab) - 1)), [(all_predictions[all_minima == i] == i).float().mean().item() for i in range(low, len(dataset.vocab) - 1)], title="Fraction Correct vs Actual Minimum", xaxis="Actual Minimum", yaxis="Fraction Correct")
imshow(fraction_correct, title="Fraction Correct vs Actual Minimum and # Copies of Minimum", xaxis="Actual Minimum", yaxis="# Copies of Minimum")
# print(sequences)

# %% [markdown]
# So we see that with enough copies of the minimum, we can get things correct, but with only one or two copies, we tend not to.
#
# This makes sense, though.  Consider what fraction of sequences start at 19 or higher.

# %%
total_sequences = (len(dataset.vocab) - 1) ** dataset.list_len
# (minimum, n copies of minimum)
count_of_sequences = torch.zeros((len(dataset.vocab) - 1, dataset.list_len + 1), dtype=torch.long)
count_of_sequences[:, dataset.list_len] = 1 # one sequence for each min tok when everything is the same
for mintok in range(len(dataset.vocab) - 1):
    for n_copies in range(1, dataset.list_len):
        count_of_sequences[mintok, n_copies] = math.comb(dataset.list_len, n_copies) * (len(dataset.vocab) - 1 - mintok - 1)**(dataset.list_len - n_copies)
assert count_of_sequences.sum().item() == total_sequences, f"{np.abs(count_of_sequences.sum().item() - total_sequences)} != 0"
fraction_of_sequences = count_of_sequences.float() / total_sequences
imshow(fraction_of_sequences, title="Fraction of Sequences vs Actual Minimum and # Copies of Minimum", yaxis="Actual Minimum", xaxis="# Copies of Minimum")
fraction_of_sequences_all_counts = fraction_of_sequences.sum(dim=-1)
cumulative_fraction_of_sequences_all_counts = fraction_of_sequences_all_counts.cumsum(dim=0)
significant = cumulative_fraction_of_sequences_all_counts[cumulative_fraction_of_sequences_all_counts <= 0.99]
print(f"{cumulative_fraction_of_sequences_all_counts[significant.shape[0]+1] * 100:.1f}% of sequences start at or below {significant.shape[0] + 1}")

# %% [markdown]
#
# So since more than 99% of cases have their minimum at or below 19, it seem fine to only explain the behavior on sequences with minimum at or below 19.


# %% [markdown]
# ## OV Cutoffs
#
# For each pair of minimum and non-minimum tokens, we can ask: how much attention needs to be paid to the minimum token to ensure that the correct output logit is highest?
# We ask this question separately for when the remainder of the attention is paid to the non-min token vs paid to the SEP token.
# Note that to make use of the proof above about considering only sequences with at most two distinct tokens, we need to consider the behavior of the two heads independently.

# %% [markdown]
# Let's first find the worst-case OV behavior for head 0, indexed by (minimum token, output logit)
# %%
@torch.no_grad()
def compute_worst_OV(model, sep_pos=dataset.list_len, num_min=1):
    '''
    returns (n_heads, d_vocab_min, d_vocab_nonmin, d_vocab_out)
    '''
    EPVOU_EUPU = compute_EPVOU_EUPU(model, nanify_sep_position=sep_pos, qtok=-1, qpos=sep_pos)
    # (head, pos, input, output)
    EPVOU_EUPU_sep = EPVOU_EUPU[:, sep_pos, -1, :]
    EPVOU_EUPU = EPVOU_EUPU[:, :sep_pos, :-1, :]
    attn_patterns = compute_attention_patterns(model, sep_pos=sep_pos, num_min=num_min)
    # (head, 2, mintok, nonmintok, 3)
    # 2 is for max attn on min vs nonmin, 3 is for min, nonmin, sep
    results = t.zeros(tuple(list(attn_patterns.shape[:-1]) + [model.cfg.d_vocab_out]), device=attn_patterns.device)
    for mintok in range(model.cfg.d_vocab - 1):
        # center on the logit for the minimum token
        cur_EPVOU_EUPU = EPVOU_EUPU - EPVOU_EUPU[:, :, :, mintok].unsqueeze(dim=-1)
        # (head, pos, input, output)
        # reduce along position, since they're all nearly identical
        cur_EPVOU_EUPU = cur_EPVOU_EUPU.max(dim=1).values
        # (head, input, output)

        cur_EPVOU_EUPU_sep = EPVOU_EUPU_sep - EPVOU_EUPU_sep[:, mintok].unsqueeze(dim=-1)
        # (head, output)

        cur_attn_patterns = attn_patterns[:, :, mintok, :, :]
        # (head, 2, nonmintok, 3)

        results[:, :, mintok, :, :] = \
            einsum(cur_attn_patterns[..., 0], cur_EPVOU_EUPU[:, mintok, :],
                    "head minmax nonmintok, head output -> head minmax nonmintok output") \
            + einsum(cur_attn_patterns[..., 1], cur_EPVOU_EUPU,
                    "head minmax nonmintok, head nonmintok output -> head minmax nonmintok output") \
            + einsum(cur_attn_patterns[..., 2], cur_EPVOU_EUPU_sep,
                    "head minmax nonmintok, head output -> head minmax nonmintok output")
        # re-center on output logit for minimum token
        results[:, :, mintok, :, :] -= results[:, :, mintok, :, mintok].unsqueeze(dim=-1)

    return results.max(dim=1).values

@torch.no_grad()
def reduce_worst_OV(worst_OV):
    '''
    returns (n_heads, d_vocab_min)
    '''
    worst_OV = worst_OV.clone()
    results = torch.zeros_like(worst_OV[:, :, 0, 0])
    assert len(results.shape) == 2
    for mintok in range(worst_OV.shape[1]):
        # set diagonal to min to avoid including the logit of the min in the worst non-min logit
        worst_OV[:, mintok, :, mintok] = worst_OV[:, mintok, :, :].min(dim=-1).values
        # reduce for worst logit
        results[:, mintok] = worst_OV[:, mintok, mintok:, :].max(dim=-1).values.max(dim=-1).values
    return results

@torch.no_grad()
def compute_worst_OV_reduced(model, **kwargs):
    '''
    returns (n_heads, d_vocab_min)
    '''
    return reduce_worst_OV(compute_worst_OV(model, **kwargs))


# %%
line(compute_worst_OV_reduced(model).T, title="Worst OV behavior per head, Value vs Min Token")

# %% [markdown]
#
# Now let's compute, for each minimum and non-minimum token, whether or not the attention from head 1 is enough to overcome the worst behavior from head 0

# %%
@torch.no_grad()
def compute_slack(model, good_head_num_min=1, **kwargs):
    '''
    returns (n_heads, d_vocab_min, d_vocab_nonmin, d_vocab_out)
    '''
    # we consider the worst behavior of the bad heads with only one copy of the minimum (except for the diagonal, which has the maximum number of copies)
    worst_OV = compute_worst_OV(model, num_min=1, **kwargs)
    # for the good head, we pass in the number of copies of the minimum token
    worst_OV_good = compute_worst_OV(model, num_min=good_head_num_min, **kwargs)
    # (n_heads, d_vocab_min, d_vocab_nonmin, d_vocab_out)
    results = worst_OV_good.clone()
    for good_head in range(worst_OV.shape[0]):
        # reduce along nonmin tokens in other heads and add them in
        other_worst_OV = torch.cat((worst_OV[:good_head], worst_OV[good_head+1:]), dim=0)
        # (n_heads, d_vocab_min, d_vocab_nonmin, d_vocab_out)
        for mintok in range(worst_OV.shape[1]):
            results[good_head, mintok] += \
                reduce(other_worst_OV[:, mintok, mintok:, :],
                       "head nonmintok output -> head () output", reduction="max").sum(dim=0)
    return results

@torch.no_grad()
def compute_slack_reduced(model, good_head_num_min=1, **kwargs):
    '''
    returns (n_heads, d_vocab_min, d_vocab_nonmin)
    '''
    slack = compute_slack(model, good_head_num_min=good_head_num_min, **kwargs)
    # (n_heads, d_vocab_min, d_vocab_nonmin, d_vocab_out)
    for mintok in range(slack.shape[1]):
        # assert centered
        test_slack = slack[:, mintok, :, mintok]
        test_slack = test_slack[~test_slack.isnan()]
        assert (test_slack == 0).all(), test_slack.max().item()
        # set diagonal to min to avoid including the logit of the min in the worst non-min logit
        slack[:, mintok, :, mintok] = slack[:, mintok, :, :].min(dim=-1).values
    return slack.max(dim=-1).values

# %%
slacks = torch.stack([compute_slack_reduced(model, good_head_num_min=num_min) for num_min in range(1, dataset.list_len)], dim=0)
# (num_min, head, mintok, nonmintok)
zmax = slacks[~slacks.isnan()].abs().max().item()
# negate for coloring
slacks_sign = slacks.sign()
slacks_full = -utils.to_numpy(slacks)
slacks_sign = -utils.to_numpy(slacks_sign)

for slacks in (slacks_full, slacks_sign):
    fig = make_subplots(rows=1, cols=model.cfg.n_heads, subplot_titles=[f"slack on head {h}" for h in range(model.cfg.n_heads)])# {minmax} attn on mintok" for h in range(model.cfg.n_heads) for minmax in ('min', 'max')])
    fig.update_layout(title=f"Slack (positive for either head ⇒ model is correct)")

    all_tickvals_text = list(enumerate(dataset.vocab[:-1]))
    tickvals_indices = list(range(0, len(all_tickvals_text) - 1, 10)) + [len(all_tickvals_text) - 1]
    tickvals = [all_tickvals_text[i][0] for i in tickvals_indices]
    tickvals_text = [all_tickvals_text[i][1] for i in tickvals_indices]


    def make_update(h, num_min, showscale=True):
        cur_slack = slacks[num_min - 1, h]
        return go.Heatmap(z=cur_slack,  colorscale='RdBu', zmin=-zmax, zmax=zmax, showscale=showscale)

    def update(num_min):
        fig.data = []
        for h in range(model.cfg.n_heads):
            col, row = h+1, 1
            fig.add_trace(make_update(h, num_min), col=col, row=row)
            fig.update_xaxes(tickvals=tickvals, ticktext=tickvals_text, constrain='domain', col=col, row=row, title_text="non-min tok") #, title_text="Output Logit Token"
            fig.update_yaxes(autorange='reversed', scaleanchor="x", scaleratio=1, col=col, row=row, title_text="min tok")
        fig.update_traces(hovertemplate="Non-min token: %{x}<br>Min token: %{y}<br>Slack: %{z}<extra>head %{fullData.name}</extra>")

    # Create the initial heatmap
    update(1)

    # Create frames for each position
    frames = [go.Frame(
        data=[make_update(h, num_min) for h in range(model.cfg.n_heads)],
        name=str(num_min)
    ) for num_min in range(1, dataset.list_len)]

    fig.frames = frames

    # Create slider
    sliders = [dict(
        active=0,
        yanchor='top',
        xanchor='left',
        currentvalue=dict(font=dict(size=20), prefix='# copies of min token:', visible=True, xanchor='right'),
        transition=dict(duration=0),
        pad=dict(b=10, t=50),
        len=0.9,
        x=0.1,
        y=0,
        steps=[dict(args=[[frame.name], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                    method='animate',
                    label=str(num_min+1)) for num_min, frame in enumerate(fig.frames)]
    )]

    fig.update_layout(
        sliders=sliders
    )


    fig.show()

# %% [markdown]
# Let's count what fraction of sequences we can now explain the computation of the minimum on.

# %%
@torch.no_grad()
def calculate_correct_minimum_lower_bound(model, sep_pos=dataset.list_len):
    count = 0
    for min_token_copies in range(1, sep_pos):
        slack = compute_slack_reduced(model, good_head_num_min=min_token_copies, sep_pos=sep_pos)
        # (n_heads, d_vocab_min, d_vocab_nonmin)
        # find where we have slack
        slack = (slack < 0)
        for mintok in range(slack.shape[1]):
            # count the number of sequences with the specified number of copies of mintok and with other tokens drawn from the values where we have slack
            # we reduce along heads to find out which head permits us the most values with slack;
            # since the proof of convexity only works when we fix which head we're analyzing, we can't union permissible values across heads
            n_allowed_values = slack[:, mintok, mintok+1:].sum(dim=-1).max().item()
            if n_allowed_values > 0:
                count += math.comb(sep_pos, min_token_copies) * n_allowed_values ** (sep_pos - min_token_copies)
        if min_token_copies == sep_pos - 1:
            # add in the diagonal on this last round
            count += slack.any(dim=0).diagonal(dim1=-2, dim2=-1).sum().item()

    return count

@torch.no_grad()
def calculate_correct_minimum_lower_bound_fraction(model, sep_pos=dataset.list_len, **kwargs):
    total_sequences = (model.cfg.d_vocab - 1) ** sep_pos
    return calculate_correct_minimum_lower_bound(model, sep_pos=sep_pos, **kwargs) / total_sequences

# %%
print(f"Assuming no errors in our argument, we can prove that the model computes the correct minimum of the sequence in at least {calculate_correct_minimum_lower_bound(model)} cases ({100 * calculate_correct_minimum_lower_bound_fraction(model):.1f}% of the sequences).")

# %% [markdown]
# ## Summary of Results for First Sequence Token Predictions
#
# We've managed to prove a lower bound on correctness of the first token at 32%.  While this isn't great (the model in fact seems to do much better than this), this is only a preliminary analysis of the behavior.
#
# Recaping: We found that head 1 does positive copying on numbers outside of 25--39.  For numbers below 20, head 1 frequently manages to pay most attention to the smallest number.  Since fewer than 1% of sequences have a minimum above 19, we largely neglect the behavior on sequences with large minima.  We compute for each head the largest logit gap between the actual minima and any other logit, separately for each number of copies of the minimum token.  We then compute the worst-case behavior of the other heads.  We pessimize over position, which mostly does not matter.  We folded the computation of skip connection into the computation of the attention head.  We made a convexity argument that, as long as we consider each head's behavior independently, we can restrict our attention to sequences with at most two distinct tokens and still bound the behavior of other sequences.
#
# Although we don't do a more in-depth analysis of the prediction of the first token for the October challenge, we (Jason Gross and Rajashree Agrwal, and Thomas Kwa) are working on a project involving more deeply anlyzing the behavior of even smaller models (1 attention head, no layer norm, only computing the maximum of a list) in more detail, with proofs formalized in the proof assistant Coq.  We're in the process of writing up preliminary results, including connections with heuristic arguments, and hope to post on LessWrong and/or the Alignment Forum soon.  Keep an eye out!

# %% [markdown]
# ## More fine-grained analysis of first token prediction
#
# We currently are making very loose approximations when the model outputs the wrong minimum on $n$ copies of the minimum and $10 - n$ copies of some non-minimum token; we throw away all sequences that contain any copies of that token.  For example, the model outputs the wrong minimum for `[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]`:

# %%
print(f"The model predicts {model(t.tensor([0] + [1] * (dataset.list_len - 1) + [len(dataset.vocab) - 1] + [0] + [1] * (dataset.list_len - 1))).argmax(dim=-1)[0, dataset.list_len].item()} instead of 0.")

# %% [markdown]
# But then we throw away all sequences that contain a 0, any number of 1s, and any other non-zero numbers!  But the model predicts the minimum correctly for many of these!

# %%
n_samples = 10000
sequences = torch.randint(2, len(dataset.vocab) - 2, (n_samples, dataset.list_len))
zero_idxs = torch.randint(0, dataset.list_len - 1, (n_samples,))
one_idxs = (zero_idxs + torch.randint(1, dataset.list_len - 1, (n_samples,))) % dataset.list_len
sequences[torch.arange(n_samples), zero_idxs], sequences[torch.arange(n_samples), one_idxs] = 0, 1
sorted_sequences, _ = sequences.sort(dim=-1)
# add sep
sequences = torch.cat([sequences, torch.full((n_samples, 1), len(dataset.vocab) - 1, dtype=torch.long), sorted_sequences], dim=-1)
# compute predictions
predictions = model(sequences)[:, dataset.list_len, :].argmax(dim=-1)
print(f"The model gets a {(predictions == 0).float().mean().item() * 100}% correct predictions of the minimum from a random sample of {n_samples} sequences with one 0, one 1, and the remainder of numbers above 2.")

# %% [markdown]
# So we can do much better.
#
# For each count of copies of the minimum, for each minimum token, we can divide the remaining token values into ones that are okay to have all copies of, and ones that are not.  Then we can consider each number of copies of each token that is not okay to have all copies of, and compute which other tokens it's okay to to fill the remainder of the sequence with.  We can then attempt to use this to compute the fraction of sequences that the model gets correct.

# %%
@torch.no_grad()
def compute_worst_OV_3way_shared_data(model, sep_pos=dataset.list_len, max_num_min=dataset.list_len-2, max_num_nonmin1=dataset.list_len-2):
    EPVOU_EUPU = compute_EPVOU_EUPU(model, nanify_sep_position=sep_pos, qtok=-1, qpos=sep_pos)
    # (head, pos, input, output)
    EPVOU_EUPU_sep = EPVOU_EUPU[:, sep_pos, -1, :]
    EPVOU_EUPU = EPVOU_EUPU[:, :sep_pos, :-1, :]
    attn_patterns = compute_3way_attention_patterns_all_counts(model, sep_pos=sep_pos, max_num_min=max_num_min, max_num_nonmin1=max_num_nonmin1)
    # (num_min, num_nonmin1, head, 3, 2, mintok, nonmintok1, nonmintok2, 4)
    # The 3, 2 is for the permutations of attention ordering by position, min vs nonmin1 vs nonmin2 in the lowest attention positions, and then which of the remaining two is in the highest attention position.
    # The 4 is for mintok, nonmintok1, nonmintok2, and sep
    return EPVOU_EUPU, EPVOU_EUPU_sep, attn_patterns

@torch.no_grad()
def compute_worst_OV_3way(model, mintok, sep_pos=dataset.list_len, max_num_min=dataset.list_len-2, max_num_nonmin1=dataset.list_len-2, EPVOU_EUPU=None, EPVOU_EUPU_sep=None, attn_patterns=None):
    '''
    returns (num_min, num_nonmin1, n_heads, d_vocab_nonmin1, d_vocab_nonmin2, d_vocab_out)
    '''
    if EPVOU_EUPU is None or EPVOU_EUPU_sep is None or attn_patterns is None:
        EPVOU_EUPU, EPVOU_EUPU_sep, attn_patterns = compute_worst_OV_3way_shared_data(model, sep_pos=sep_pos, max_num_min=max_num_min, max_num_nonmin1=max_num_nonmin1)
        return compute_worst_OV_3way(model, mintok, sep_pos=sep_pos, max_num_min=max_num_min, max_num_nonmin1=max_num_nonmin1, EPVOU_EUPU=EPVOU_EUPU, EPVOU_EUPU_sep=EPVOU_EUPU_sep, attn_patterns=attn_patterns)

    results = t.zeros(tuple(list(attn_patterns.shape[:-4]) + list(attn_patterns.shape[-3:-1]) + [model.cfg.d_vocab_out]), device=attn_patterns.device)
    # center on the logit for the minimum token
    cur_EPVOU_EUPU = EPVOU_EUPU - EPVOU_EUPU[:, :, :, mintok].unsqueeze(dim=-1)
    # (head, pos, input, output)
    # reduce along position, since they're all nearly identical
    cur_EPVOU_EUPU = cur_EPVOU_EUPU.max(dim=1).values
    # (head, input, output)

    cur_EPVOU_EUPU_sep = EPVOU_EUPU_sep - EPVOU_EUPU_sep[:, mintok].unsqueeze(dim=-1)
    # (head, output)

    cur_attn_patterns = attn_patterns[:, :, :, :, :, mintok, :, :, :]
    # (num_min, num_nommin, head, 3, 2, nonmintok1, nonmintok2, 4)

    results = \
        einsum(cur_attn_patterns[..., 0], cur_EPVOU_EUPU[:, mintok, :],
                "num_min num_nonmin head mini maxi nonmintok1 nonmintok2, head output -> num_min num_nonmin head mini maxi nonmintok1 nonmintok2 output") \
        + einsum(cur_attn_patterns[..., 1], cur_EPVOU_EUPU,
                "num_min num_nonmin head mini maxi nonmintok1 nonmintok2, head nonmintok1 output -> num_min num_nonmin head mini maxi nonmintok1 nonmintok2 output") \
        + einsum(cur_attn_patterns[..., 2], cur_EPVOU_EUPU,
                "num_min num_nonmin head mini maxi nonmintok1 nonmintok2, head nonmintok2 output -> num_min num_nonmin head mini maxi nonmintok1 nonmintok2 output") \
        + einsum(cur_attn_patterns[..., -1], cur_EPVOU_EUPU_sep,
                "num_min num_nonmin head mini maxi nonmintok1 nonmintok2, head output -> num_min num_nonmin head mini maxi nonmintok1 nonmintok2 output")
    # re-center on output logit for minimum token
    results -= results[:, :, :, :, :, :, :, mintok].unsqueeze(dim=-1)

    return reduce(results, "num_min num_nonmin head mini maxi nonmintok1 nonmintok2 output -> num_min num_nonmin head nonmintok1 nonmintok2 output", reduction="max")

@torch.no_grad()
def compute_slack_3way_reduced(model, good_head_max_num_min=dataset.list_len-2, good_head_max_num_nonmin1=dataset.list_len-2, **kwargs):
    '''
    returns (num_min, num_nonmin1, n_heads, d_vocab_min, d_vocab_nonmin1, d_vocab_nonmin2)
    '''
    # we consider the worst behavior of the bad heads with only one copy of the minimum (except for the diagonal, which has the maximum number of copies)
    worst_OV = compute_worst_OV(model, num_min=1, **kwargs)
    # (n_heads, d_vocab_min, d_vocab_nonmin, d_vocab_out)

    results = []
    EPVOU_EUPU, EPVOU_EUPU_sep, attn_patterns = compute_worst_OV_3way_shared_data(model, max_num_min=good_head_max_num_min, max_num_nonmin1=good_head_max_num_nonmin1, **kwargs)

    for mintok in tqdm(range(worst_OV.shape[1])):
        # for the good head, we pass in the number of copies of the minimum token
        worst_OV_good = compute_worst_OV_3way(model, mintok, max_num_min=good_head_max_num_min, max_num_nonmin1=good_head_max_num_nonmin1, EPVOU_EUPU=EPVOU_EUPU, EPVOU_EUPU_sep=EPVOU_EUPU_sep, **kwargs)

        # (num_min, num_nonmin1, n_heads, d_vocab_nonmin1, d_vocab_nonmin2, d_vocab_out)
        cur_results = worst_OV_good.clone()
        for good_head in range(worst_OV.shape[0]):
            # reduce along nonmin tokens in other heads and add them in
            other_worst_OV = torch.cat((worst_OV[:good_head], worst_OV[good_head+1:]), dim=0)
            # (n_heads, d_vocab_min, d_vocab_nonmin, d_vocab_out)

            # # assert centered 1
            # test_slack = cur_results[:, :, good_head, :, :, mintok]
            # test_slack = test_slack[~test_slack.isnan()]
            # assert (test_slack == 0).all(), f"cur_results 1 (good_head={good_head}): {test_slack.max().item()}"

            # # assert centered other
            # test_slack = other_worst_OV[:, mintok, mintok:, mintok]
            # test_slack = test_slack[~test_slack.isnan()]
            # assert (test_slack == 0).all(), f"other_worst_OV: {test_slack.max().item()}"

            cur_results[:, :, good_head] += \
                reduce(other_worst_OV[:, mintok, mintok:, :],
                    "head nonmintok output -> head () () () () output", reduction="max").sum(dim=0)

        # assert centered
        test_slack = cur_results[:, :, :, :, :, mintok]
        test_slack = test_slack[~test_slack.isnan()]
        assert (test_slack == 0).all(), f"cur_results: {test_slack.max().item()}"

        # set diagonal to min to avoid including the logit of the min in the worst non-min logit
        cur_results[:, :, :, :, :, mintok] = cur_results[:, :, :, :, :, :].min(dim=-1).values

        results.append(cur_results.max(dim=-1).values)
    return torch.stack(results, dim=3)

# %%
slacks_3way = compute_slack_3way_reduced(model)
# (num_min, num_nonmin1, n_heads, d_vocab_min, d_vocab_nonmin1, d_vocab_nonmin2)
# %%
# XXX TODO Figure out visualization https://stackoverflow.com/questions/77392813/how-do-i-make-interacting-updates-in-plotly
# zmax = slacks_3way[~slacks_3way.isnan()].abs().max().item()
# # negate for coloring
# slacks_3way_sign = slacks_3way.sign()
# slacks_3way_full = -utils.to_numpy(slacks_3way)
# slacks_3way_sign = -utils.to_numpy(slacks_3way_sign)

# all_tickvals_text = list(enumerate(dataset.vocab[:-1]))
# tickvals_indices = list(range(0, len(all_tickvals_text) - 1, 10)) + [len(all_tickvals_text) - 1]
# tickvals = [all_tickvals_text[i][0] for i in tickvals_indices]
# tickvals_text = [all_tickvals_text[i][1] for i in tickvals_indices]

# for slacks_kind in (slacks_3way_full, slacks_3way_sign):
#     fig = make_subplots(rows=1, cols=model.cfg.n_heads, subplot_titles=[f"slack on head {h}" for h in range(model.cfg.n_heads)])
#     fig.update_layout(title=f"Slack (positive for either head ⇒ model is correct)")

#     def make_update(h, num_min, num_nonmin1, mintok, showscale=True):
#         cur_slack = slacks_kind[num_min - 1, num_nonmin1 - 1, h, mintok]
#         return go.Heatmap(z=cur_slack, colorscale='RdBu', zmin=-zmax, zmax=zmax, showscale=showscale)

#     def update(num_min, num_nonmin1, mintok):
#         fig.data = []
#         for h in range(model.cfg.n_heads):
#             col, row = h+1, 1
#             fig.add_trace(make_update(h, num_min, num_nonmin1, mintok), col=col, row=row)
#             fig.update_xaxes(tickvals=tickvals, ticktext=tickvals_text, constrain='domain', col=col, row=row, title_text="non-min tok 2") #, title_text="Output Logit Token"
#             fig.update_yaxes(autorange='reversed', scaleanchor="x", scaleratio=1, col=col, row=row, title_text="non min tok 1")
#         fig.update_traces(hovertemplate="Non-min token 1: %{y}<br>Non-min token 2: %{x}<br>Slack: %{z}<extra>head %{fullData.name}</extra>")

#     # Create the initial heatmap
#     update(1, 1, 0)

#     # Create frames for each combination of mintok, num_min, and num_nonmin1
#     frames = [go.Frame(
#         data=[make_update(h, num_min, num_nonmin1, mintok) for h in range(model.cfg.n_heads)],
#         name=f"{num_min}-{num_nonmin1}-{mintok}"
#     ) for num_min in range(1, dataset.list_len - 1) for num_nonmin1 in range(1, dataset.list_len - 1) for mintok in range(len(dataset.vocab[:-1]))]

#     fig.frames = frames

#     # Create three sliders
#     sliders = [
#         # Slider for num_min
#         dict(
#             active=0,
#             yanchor='top',
#             xanchor='left',
#             currentvalue=dict(font=dict(size=20), prefix='# copies of min token:', visible=True, xanchor='right'),
#             transition=dict(duration=0),
#             pad=dict(b=10, t=50),
#             len=0.3,
#             x=0.1,
#             y=0,
#             steps=[dict(args=[[f"{num_min}-{num_nonmin1}-{mintok}"], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
#                         method='animate',
#                         label=str(num_min)) for num_min, num_nonmin1, mintok, frame in enumerate(fig.frames) if num_min == mintok]
#         ),
#         # Slider for num_nonmin1
#         dict(
#             active=0,
#             yanchor='top',
#             xanchor='left',
#             currentvalue=dict(font=dict(size=20), prefix='Num nonmin1:', visible=True, xanchor='right'),
#             transition=dict(duration=0),
#             pad=dict(b=10, t=150),
#             len=0.3,
#             x=0.1,
#             y=0.4,
#             steps=[dict(args=[[f"{num_min}-{num_nonmin1}-{mintok}"], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
#                         method='animate',
#                         label=str(num_nonmin1)) for num_min, num_nonmin1, mintok, frame in enumerate(fig.frames) if num_nonmin1 == mintok]
#         ),
#         # Slider for mintok
#         dict(
#             active=0,
#             yanchor='top',
#             xanchor='left',
#             currentvalue=dict(font=dict(size=20), prefix='Mintok:', visible=True, xanchor='right'),
#             transition=dict(duration=0),
#             pad=dict(b=10, t=250),
#             len=0.3,
#             x=0.1,
#             y=0.8,
#             steps=[dict(args=[[f"{num_min}-{num_nonmin1}-{mintok}"], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
#                         method='animate',
#                         label=str(mintok)) for num_min, num_nonmin1, mintok, frame in enumerate(fig.frames)]
#         )
#     ]

#     fig.update_layout(
#         sliders=sliders
#     )

#     fig.show()

# %%
@torch.no_grad()
def calculate_correct_minimum_lower_bound_3way(model, sep_pos=dataset.list_len, slacks_3way=None):
    count = 0
    if slacks_3way is None: slacks_3way = compute_slack_3way_reduced(model, sep_pos=sep_pos, good_head_max_num_min=sep_pos-2, good_head_max_num_nonmin1=sep_pos-2)
    # (num_min, num_nonmin1, n_heads, d_vocab_min, d_vocab_nonmin1, d_vocab_nonmin2)
    slacks_3way = (slacks_3way < 0)
    for min_token_copies in tqdm(range(1, sep_pos)):
        slack = compute_slack_reduced(model, good_head_num_min=min_token_copies, sep_pos=sep_pos)
        # (n_heads, d_vocab_min, d_vocab_nonmin)
        # find where we have slack
        slack = (slack < 0)
        for mintok in range(slack.shape[1]):
            # count the number of sequences with the specified number of copies of mintok and with other tokens drawn from the values where we have slack
            # we reduce along heads to find out which head permits us the most values with slack;
            # since the proof of convexity only works when we fix which head we're analyzing, we can't union permissible values across heads
            n_allowed_values, maxhead = slack[:, mintok, mintok+1:].sum(dim=-1).max(dim=0)
            n_allowed_values = n_allowed_values.item()
            if n_allowed_values > 0:
                count += math.comb(sep_pos, min_token_copies) * n_allowed_values ** (sep_pos - min_token_copies)
                for nonmin_token1_copies in range(1, sep_pos - min_token_copies):
                    # find all disallowed values which have enough slack on all allowed values as the nonmintok2
                    cur_3way_slack = slacks_3way[min_token_copies - 1, nonmin_token1_copies - 1, :, mintok, mintok+1:, mintok+1:]
                    # (head, d_vocab_nonmin1, d_vocab_nonmin2)
                    # subset the 3-way slack values to the ones where mintok1 is a token without enough (2-way) slack, and consider the cases where it does have enough (3-way) slack on all tokens with enough 2-way slack
                    # pytorch slicing is arcane; we want cur_3way_slack[:, ~slack[maxhead, mintok, mintok+1:], slack[maxhead, mintok, mintok+1:]], but this is not how pytorch does boolean slicing (which can only produce flat tensors), and we need to broadcast tensor int indices
                    cur_3way_slack = cur_3way_slack[torch.arange(0, cur_3way_slack.shape[0], device=cur_3way_slack.device)[:, None, None],
                                                    torch.arange(0, cur_3way_slack.shape[1], device=cur_3way_slack.device)[~slack[maxhead, mintok, mintok+1:]][None, :, None],
                                                    torch.arange(0, cur_3way_slack.shape[2], device=cur_3way_slack.device)[slack[maxhead, mintok, mintok+1:]][None, None, :]].all(dim=-1)
                    # (head, d_vocab_nonmin1)
                    # count how many tokens for nonmintok1 have enough slack in this way
                    n_allowed_nonmintok1_values = cur_3way_slack.sum(dim=-1).max().item()
                    if n_allowed_nonmintok1_values > 0:
                        count += math.comb(sep_pos, min_token_copies) * math.comb(sep_pos - min_token_copies, nonmin_token1_copies) * n_allowed_nonmintok1_values ** nonmin_token1_copies * n_allowed_values ** (sep_pos - min_token_copies - nonmin_token1_copies)
        if min_token_copies == sep_pos - 1:
            # add in the diagonal on this last round
            count += slack.any(dim=0).diagonal(dim1=-2, dim2=-1).sum().item()

    return count

@torch.no_grad()
def calculate_correct_minimum_lower_bound_fraction_3way(model, sep_pos=dataset.list_len, **kwargs):
    total_sequences = (model.cfg.d_vocab - 1) ** sep_pos
    return calculate_correct_minimum_lower_bound_3way(model, sep_pos=sep_pos, **kwargs) / total_sequences

# # %%
# slacks_3way = compute_slack_3way_reduced(model)
# # %%
# print(f"Assuming no errors in our argument, we can now prove that the model computes the correct minimum of the sequence in at least {calculate_correct_minimum_lower_bound(model)} cases ({100 * calculate_correct_minimum_lower_bound_fraction_3way(model, slacks_3way=slacks_3way):.1f}% of the sequences).")
# %%
print(f"Assuming no errors in our argument, we can now prove that the model computes the correct minimum of the sequence in at least {calculate_correct_minimum_lower_bound(model)} cases ({100 * calculate_correct_minimum_lower_bound_fraction_3way(model):.1f}% of the sequences).")


# # %%
# import sys
# def sizeof_fmt(num, suffix='B'):
#     ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
#     for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
#         if abs(num) < 1024.0:
#             return "%3.1f %s%s" % (num, unit, suffix)
#         num /= 1024.0
#     return "%.1f %s%s" % (num, 'Yi', suffix)

# for name, size in sorted(((name, sys.getsizeof(value)) for name, value in list(
#                           locals().items())), key= lambda x: -x[1])[:100]:
#     print("{:>30}: {:>8}".format(name, sizeof_fmt(size)))
# # %%
# import torch
# import gc
# def torch_objs():
#     for obj in gc.get_objects():
#         try:
#             if torch.is_tensor(obj) or (hasattr(obj, 'data') and torch.is_tensor(obj.data)):
#                 yield (obj, type(obj), obj.size(), np.prod(obj.size()), obj.device)
#         except:
#             pass

# for obj, obj_type, obj_size, obj_prod, obj_device in sorted([i for i in torch_objs() if 'cuda' in str(i[-1])], key=lambda x: (str(x[-1]), -x[3]))[:100]:
#     print(obj.name, obj_type, obj_size, obj_prod, obj_device)

# %% [markdown]
# # OLD STUFF

# %% [markdown]
# # Analysis of first token prediction with different independence assumptions
#
# Currently our analysis treats head 0 and head 1 completely independently.  This likely leads to loss of tightness in the bounds we're able to prove, since head 0 does negative copying on the tokens it pays attention to, plausibly giving head 1 more slack.
#
# In fact it looks like head 0 pays mostly uniform attention (except for 1, 2, and numbers around 27--37), so we we may get a better result if we can keep the OV behavior of head 0 coupled to the OV behavior (& attention) of head 1, but allow the attention behavior to vary independently.
#
# To do this, we need to prove that it still suffices to consider only sequences with at most two distinct tokens.
#
# **Lemma**: With two attention heads, any sequences with three token values $x < y < z$ is strictly dominated by a sequence just with $x$ and $y$ or a sequence just with $x$ and $z$, when we allow head 0 the option to pay attention to $y$ as if it were $z$ and vice versa.
#
# **Proof**: Suppose we have $k$ copies of $x$, $n$ copies of $y$, and $\ell - k - n$ copies of $z$, the attention scores are $s_{h,x}$, $s_{h,y}$, and $s_{h,z}$, and the differences between the logit of $x$ and our chosen comparison logit (as computed by the OV circuit for each token) are $v_{h,x}$, $v_{h,y}$, and $v_{h,z}$, where $h$ is the head index.
# Let $s_{0,b,y}$ be $s_{0,y}$ when $b$ is true (i.e. when head 0 is paying attention to $y$ as if it were $y$) and $s_{0,z}$ when $b$ is false (i.e. when head 0 is paying attention to $y$ as if it were $z$), and similarly for $s_{0,b,z}$.
#
# Then the difference in logit between $x$ and the comparison token is
# $$\left(k e^{s_{0,x}} v_{0,x} + n e^{s_{0,b,y}} v_{0,y} + (\ell - k - n)e^{s_{0,b,z}}v_{0,z} \right)\left(k e^{s_{0,x}} + n e^{s_{0,b,y}} + (\ell - k - n)e^{s_{0,b,z}}\right)^{-1}$$
# $${} + \left(k e^{s_{1,x}} v_{1,x} + n e^{s_{1,y}} v_{1,y} + (\ell - k - n)e^{s_{1,z}}v_{1,z} \right)\left(k e^{s_{1,x}} + n e^{s_{1,y}} + (\ell - k - n)e^{s_{1,z}}\right)^{-1}$$
#
# We want to show that the minimum and maximum of this expression occur at $n = 0$ and $n = \ell - k$ (with $b$ allowed to be either true or false on each of these).
#
# Rearrangement gives
# $$\frac{\left(k e^{s_{0,x}} v_{0,x} + (\ell - k) e^{s_{0,b,z}} v_{0,z}\right) + n \left(e^{s_{0,b,y}} v_{0,y} - e^{s_{0,b,z}}v_{0,z}\right)}{\left(k e^{s_{0,x}} + (\ell - k) e^{s_{0,b,z}}\right) + n \left(e^{s_{0,b,y}} - e^{s_{0,b,z}}\right)}$$
# $${}+ \frac{\left(k e^{s_{1,x}} v_{1,x} + (\ell - k) e^{s_{1,z}} v_{1,z}\right) + n \left(e^{s_{1,y}} v_{1,y} - e^{s_{1,z}}v_{1,z}\right)}{\left(k e^{s_{1,x}} + (\ell - k) e^{s_{1,z}}\right) + n \left(e^{s_{1,y}} - e^{s_{1,z}}\right)}$$

# %% [markdown]
# OLD
#
# For a single attention head, it suffices to consider sequences with at most two distinct tokens.
#
# Note that we are comparing sequences by pre-final-layernorm-scaling gap between the logit of the minimum token and the logit of any other fixed token.
# Layernorm scaling is non-linear, but if we only care about accuracy and not log-loss, then we can ignore it (neither scaling nor softmax changes which logit is the largest).
#
# **Proof sketch**:
# We show that any sequence with three token values, $x < y < z$, is strictly dominated either by a sequence with just $x$ and $y$ or a sequence with just $x$ and $z$.
#
# Suppose we have $k$ copies of $x$, $n$ copies of $y$, and $\ell - k - n$ copies of $z$, the attention scores are $s_x$, $s_y$, and $s_z$, and the differences between the logit of $x$ and our chosen comparison logit (as computed by the OV circuit for each token) are $v_x$, $v_y$, and $v_z$.
# Then the difference in logit between $x$ and the comparison token is
# $$\left(k e^{s_x} v_x + n e^{s_y} v_y + (\ell - k - n)e^{s_z}v_z \right)\left(k e^{s_x} + n e^{s_y} + (\ell - k - n)e^{s_z}\right)^{-1}$$
# Rearrangement gives
# $$\left(\left(k e^{s_x} v_x + (\ell - k) e^{s_z} v_z\right) + n \left(e^{s_y} v_y - e^{s_z}v_z\right) \right)\left(\left(k e^{s_x} + (\ell - k) e^{s_z}\right) + n \left(e^{s_y} - e^{s_z}\right)\right)^{-1}$$
# This is a fraction of the form $\frac{a + bn}{c + dn}$.  Taking the derivative with respect to $n$ gives $\frac{bc - ad}{(c + dn)^2}$.  Noting that $c + dn$ cannot equal zero for any valid $n$, we get the the derivative never changes sign.  Hence our logit difference is maximized either at $n = 0$ or at $n = \ell - k$, and the sequence with just two values dominates the one with three.
#
# This proof generalizes straightforwardly to sequences with more than three values.
#
# Similarly, this proof shows that, when considering only a single attention head, it suffices to consider sequences of $\ell$ copies of the minimum token and sequences with one copy of the minimum token and $\ell - 1$ copies of the non-minimum token, as intermediate values are dominated by the extremes.
#




# %% [markdown]
# # Analysis of the middle token predictions


# # %% [markdown]
# # ## When the sequence contains nothing in $S$
# # %%
# _, cachev = model.run_with_cache(t.tensor([22] * 10 + [51] + [22] * 10))
# # %% [markdown]
# # ### More attention is paid to the minimum by head 1 than to anything else
# #
# # Operationalization:
# #
# # Simplest version:
# # Independence relaxations:
# # - Attention to token is independent of key position
# # - Off-diagonal OV behavior is independent of which wrong answer we're considering
# # - Attention to non-min tokens is independent of OV behavior
# # - The EUPU behavior is irrelevant (independent of everything else)
# # - Attention paid to non-min tokens is independent between the two heads
# #
# # Operationalization:
# # - For each possible minimum sequence value ktokmin:
# # - The sum of the two OV matrices on input key ktokmin makes the logit for ktokmin larger than any other logit by more than the largest logit gap in EUPU
# # - The attention correction that comes from either head paying more attention to anything else is small enough that the logit gap is still large enough
# #

# # %% [markdown]
# #
# # We first compute the skip connection / EUPU (Embed @ Unembed + PosEmbed @ Unembed) behavior.

# # %%
# @torch.no_grad()
# def skip_connection_impacts(model: HookedTransformer, pos=dataset.list_len, tok=-1) -> t.Tensor:
#     EUPU = compute_EUPU(model)
#     # (pos, input, output)
#     EUPU = EUPU[pos, tok]
#     return t.cat([EUPU[i+1:] - EUPU[i] for i in range(EUPU.shape[0] - 1)])

# @torch.no_grad()
# def worst_skip_connection_impact(model: HookedTransformer, **kwargs) -> float:
#     return skip_connection_impacts(model, **kwargs).max().item()


# hist(skip_connection_impacts(model), title="Skip Connection ((W_E + W_pos) @ W_U) Impact on Logits", xaxis="Logit diff (nonmin - min)")
# print(worst_skip_connection_impact(model))

# # %% [markdown]
# #
# # Now we compute the distribution of behaviors of OV

# # %%
# @torch.no_grad()
# def ov_impacts(model: HookedTransformer, sep_pos=dataset.list_len) -> t.Tensor:
#     EPVOU = compute_EPVOU(model)
#     # (head, pos, input, output)
#     EPVOU = EPVOU[:, :sep_pos, :-1, :]
#     return t.cat([EPVOU[:, :, :, i+1:] - EPVOU[:, :, :, i:i+1] for i in range(EPVOU.shape[-1] - 1)], dim=-1)

# @torch.no_grad()
# def worst_ov_impact(model: HookedTransformer, **kwargs) -> float:
#     return ov_impacts(model, **kwargs).max().item()

# for h, ov in enumerate(ov_impacts(model)):
#     hist(ov.flatten(), title=f"OV Impact on Logits (head {h})", xaxis="Logit diff (nonmin - min)", renderer='png')
# print(worst_ov_impact(model))

# # %% [markdown]
# #
# # Now we compute the copying behavior of OV, which handles the uniform sequences (all 0s, all 1s, all 2s, etc) and gives us a starting point for other sequences
# #
# # Let's first compute the sum of the OV matrices, as if 100% of the attention were paid to the minimum token, by both heads.

# # %%
# @torch.no_grad()
# def ov_copying_impacts_full_attention(model: HookedTransformer, sep_pos=dataset.list_len) -> t.Tensor:
#     EPVOU = compute_EPVOU(model)
#     # (head, pos, input, output)
#     EPVOU = EPVOU[:, :sep_pos, :-1, :]
#     EPVOU = EPVOU.sum(dim=0)
#     # (pos, input, output)
#     EPVOU = EPVOU - EPVOU.diagonal(dim1=-2, dim2=-1)[:, :, None]
#     # remove the diagonal
#     diag_mask = torch.zeros_like(EPVOU) + torch.eye(EPVOU.size(-2), EPVOU.size(-1)).to(EPVOU.device)
#     return EPVOU[diag_mask == 0]

# hist(ov_copying_impacts_full_attention(model))

# # %% [markdown]
# # How much attention gets paid to non-minimum tokens?


# # %%
# attn_pattern = compute_attention_patterns(model)

# # %%
# for h in range(attn_pattern.shape[0]):
#     for min_max, min_max_str in enumerate(('min', 'max')):
#         imshow(attn_pattern[h, min_max, :, :, 0], title=f"{min_max_str} attention paid to min token (head {h})", xaxis="Non-minimum Token", x=dataset.vocab[:-1], yaxis="Minimum Token", y=dataset.vocab[:-1])

# # %%
# for h in range(attn_pattern.shape[0]):
#     for min_max, min_max_str in enumerate(('min', 'max')):
#         imshow(attn_pattern[h, min_max, :, :, 2], title=f"{min_max_str} attention paid to sep token (head {h})", xaxis="Non-minimum Token", x=dataset.vocab[:-1], yaxis="Minimum Token", y=dataset.vocab[:-1])


# # %%
# attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok', nanify_sep_loc=dataset.list_len)
# attn_all = attn_all[:, dataset.list_len, :dataset.list_len+1, -1, :]
# attn_by_head_distances = [[] for _ in range(attn_all.shape[0])]
# attn_by_head_attns = [[] for _ in range(attn_all.shape[0])]
# for h in range(attn_all.shape[0]):
#     for pos in range(dataset.list_len):
#         for mintok in range(model.cfg.)
# print(attn_all.shape)

# # %%
# dataset.str_toks[0]
# list(enumerate(i.item() for i in model(torch.tensor([21, 48, 48, 48, 48, 48, 48, 48, 48, 48, 51, 21, 48, 48, 48, 48, 48, 48, 48, 48, 48])).argmax(dim=-1)[0]))
# # %%
# min_min_tok, max_min_tok = 20, 50
# # get 100 samples of numbers between min_min_tok and max_min_tok
# min_toks = torch.randint(min_min_tok, max_min_tok, (100,))
# # for each sample, get 100 samples of dataset.list_len - 1 numbers between mintok+1 and dataset.vocab_size-1 inclusive, then shuffle
# # Initialize a list to store the results
# samples = []
# # For each value in min_toks
# for min_tok in min_toks:
#     for _ in range(100):
#         # Generate dataset.list_len - 1 numbers between min_tok+1 and dataset.vocab_size-1
#         sample = torch.randint(min_tok + 1, len(dataset.vocab) - 1, (dataset.list_len - 1,))
#         # Append the min_tok to the sample
#         sample = torch.cat((sample, torch.tensor([min_tok])))
#         # Shuffle the sample
#         sample = sample[torch.randperm(sample.size(0))]
#         # sort sample
#         sorted_sample = torch.sort(sample).values
#         sample = torch.cat((sample, torch.tensor([len(dataset.vocab) - 1]), sorted_sample))
#         samples.append(sample)
# # Convert samples list to a PyTorch tensor
# samples = torch.stack(samples)
# # %%
# results = model(samples)
# # %%
# print(samples.shape, results.shape)
# # %%
# predictions = results[:, dataset.list_len].argmax(dim=-1)
# expecteds = samples[:, :dataset.list_len].max(dim=-1).values
# print((predictions.cpu() == expecteds.cpu()).float().mean())
# # %%
# EPVOU = compute_EPVOU(model)
# EUPU = compute_EUPU(model)
# print(EUPU.shape)
# # for h in range(2):
# line(EPVOU[:, dataset.list_len, -1].sum(dim=0) + EUPU[dataset.list_len, -1])
# # %%
# print(EPVOU.shape)
# line(EPVOU[:, 0, 25].T)
# # %%
# EPVOU = compute_EPVOU(model, nanify_sep_position=dataset.list_len)
# test = EPVOU[:, :dataset.list_len, :-1]
# test = test - test.max(dim=-1, keepdim=True).values
# result = torch.zeros(test.shape[:-1], device=test.device)
# for h in range(test.shape[0]):
#     for pos in range(test.shape[1]):
#         for tok in range(test.shape[2]):
#             result[h, pos, tok] = test[h, pos, tok, tok]
# for h in range(result.shape[0]):
#     imshow(result[h], title=f"logit of input - max logit (head {h})", xaxis="Input Token", x=dataset.vocab[:-1], yaxis="Position", y=list(range(dataset.list_len)))

# # %% [markdown]

# #
# # - Show that network correctly computes the min for the 50 sequences that are uniform (10 0s, 10 1s, 10 2s, etc)
# # - For each possible minimum sequence value ktokmin, each possible "worst case" alternate sequence token ktoknonmin, and each possible wrong answer outtok:
# # - For each head h:
# # - If OV outputting ktokmin is greater than OV outputting outtok, then we want to consider the minimal attention paid to this token across all positions and have as few copies as possible
# # - If OV outputting ktokmin is less than OV outputting outtok, then we want to consider the maximal attention paid to this token across all positions and have as many copies as possible
# # - Find minimal/maximal attention paid to ktokmin and ktoknonmin across all positions
# # - Softmax the attention according to which token should show up most
# # - Find the worst-case OVs across all positions, and take the weighted average of the OVs according to the softmaxed attention
# # - Validate that the
# #
# # - Find the minumum attention paid to this token across positions 0--9
# # - For each possible non-minimum token ktok:
# # - Find the ma

# # %%
# attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok')# , nanify_sep_loc=dataset.list_len)

# # %%
# print(f"Self attention with SEP: {attn_all[:, dataset.list_len, dataset.list_len, -1, -1]}")
# other_attn = attn_all[:, dataset.list_len, :dataset.list_len, -1, :-1]
# # (head, kpos, ktok)
# other_attn_min, other_attn_max = other_attn.min(dim=1).values, other_attn.max(dim=1).values
# other_attn_min_max = t.stack([other_attn_min, other_attn_max], dim=1)
# line(utils.to_numpy(other_attn_min_max[1].T))
# line(utils.to_numpy(other_attn_min_max[0].T))

# # %%

# # model([])

# # # %% [markdown]
# # # ## Exploratory Plots

# # # %%
# # from training.analysis_utils import imshow, line, analyze_svd, layernorm_noscale, layernorm_scales

# # # %%
# # print(dataset[0])
# # print(', '.join(dataset.str_toks[0]))
# # print(model(dataset[0]))
# # print(model(dataset[0]).argmax(dim=-1))
# # print([(i, v.item()) for i, v in enumerate(model(dataset[0]).argmax(dim=-1)[0])])

# # # %%


# # # %%
# # imshow(EPVOU)

# # # %%
# # attention_pattern = cache['blocks.0.attn.hook_pattern'].shape
# # cv.attention.attention_patterns(
# #     tokens=dataset.str_toks,
# #     attention=attention_pattern)

# # # %%
# # print(dataset.str_toks[0])
# # for p in cache['blocks.0.attn.hook_pattern'][0]:
# #     lbls = [f'{i}:{s}' for i, s in enumerate(dataset.str_toks[0])]
# #     imshow(p, x=lbls, y=lbls)

# # # %%
# # cache.keys()

# # # %%
# # model.blocks[0].ln1.b

# # # %%
# # print(model.W_E.shape)

# # # %%


# # # %%


# # # %%
# # dataset[0]
# # model(t.tensor([10, 15, 30, 15, 15, 40, 41, 42, 43, 44, 51, 10, 15, 15, 15, 30, 40, 41, 42, 43, 44])).argmax(dim=-1)

# # # %%
# # dataset.list_len

# # # %%
# # dataset.seq_len

# # # %%


# # # %%
# # plt.imshow([[1,2,3],[4,5,6]])

# # # %%
# # model.W_E.shape

# # # %%


# # # %%


# # # %%


# # # %%


# # # %%
# # # Here you may want to determine an appropriate grid size based on the number of plots
# # # For example, if you have a total of 12 plots, you might choose a 3x4 grid
# # n_rows = 3  # Example value, adjust as needed
# # n_cols = 4  # Example value, adjust as needed

# # plot_idx = 0

# # # Create a figure and a grid of subplots
# # fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 10))

# # # Flatten the 2D axis array to easily iterate over it in a single loop
# # ax = ax.flatten()


# # # Counter for the subplot index
# # # plot_idx = 0
# # attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok')

# # for qpos in range(dataset.list_len, dataset.seq_len-1):
# #     for kpos in range(qpos+1):
# #         for h in range(2):
# #             attn = attn_all[h, qpos, kpos].detach().cpu().numpy()
# #             # Check if the counter exceeds the available subplots and create new figure if needed
# #             if plot_idx >= n_rows * n_cols:
# #                 fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))
# #                 ax = ax.flatten()
# #                 plot_idx = 0

# #             # Plot heatmap
# #             cax = ax[plot_idx].imshow(attn, cmap='viridis')

# #             # Set title and axis labels if desired

# #             ax[plot_idx].set_title(f"{h}: {qpos} -> {kpos}")
# #             ax[plot_idx].set_xlabel("key tok")
# #             ax[plot_idx].set_ylabel("query tok")

# #             # Optionally add a colorbar
# #             plt.colorbar(cax, ax=ax[plot_idx])

# #             # Increment the counter
# #             plot_idx += 1

# #             # You might want to save or display the plot here if you're iterating over many subplots
# #             if plot_idx == 0:
# #                 plt.tight_layout()
# #                 plt.show()

# # # %%
# # # Here you may want to determine an appropriate grid size based on the number of plots
# # # For example, if you have a total of 12 plots, you might choose a 3x4 grid
# # n_rows = 4  # Example value, adjust as needed
# # n_cols = 10  # Example value, adjust as needed

# # # Create a figure and a grid of subplots
# # fig, ax = plt.subplots(n_rows, n_cols, figsize=(20, 10))

# # # Flatten the 2D axis array to easily iterate over it in a single loop
# # ax = ax.flatten()

# # attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok')

# # def compute_attn_maps(qpos):
# #     attn_maps = []
# #     for kpos in range(qpos+1):
# #         for h in range(2):
# #             attn = attn_all[h, qpos, kpos, :, :]
# #             attn = attn.detach().cpu().numpy()

# #             attn_maps.append((h, kpos, attn))
# #     return attn_maps

# # def update(qpos):
# #     # Clear previous plots
# #     for a in ax:
# #         a.clear()

# #     attn_maps = compute_attn_maps(qpos)

# #     for plot_idx, (h, kpos, attn) in enumerate(attn_maps):
# #         plot_idx = h * n_cols * 2 + kpos
# #             # break

# #         # Plot heatmap
# #         cax = ax[plot_idx].imshow(attn, cmap='viridis')

# #         # Set title and axis labels if desired
# #         ax[plot_idx].set_title(f"{h}:{kpos}")
# #         # ax[plot_idx].set_xlabel("key tok")
# #         # ax[plot_idx].set_ylabel("query tok")

# #         # Optionally add a colorbar
# #         # plt.colorbar(cax, ax=ax[plot_idx])

# #     plt.tight_layout()

# # # Create animation
# # ani = FuncAnimation(fig, update, frames=tqdm(range(dataset.list_len, dataset.seq_len-1)), interval=1000)

# # plt.show()

# # from IPython.display import HTML
# # HTML(ani.to_jshtml())

# # # # Counter for the subplot index
# # # # plot_idx = 0

# # # for qpos in range(dataset.list_len, dataset.seq_len-1):
# # #     for kpos in range(qpos+1):
# # #         for h in range(2):
# # #             attn = model.blocks[0].ln1(model.W_pos[qpos,:] + model.W_E) @ model.W_Q[0,h,:,:] @ model.W_K[0,h,:,:].T @ model.blocks[0].ln1(model.W_pos[kpos,:] + model.W_E).T
# # #             attn = attn - attn.max(dim=-1, keepdim=True).values
# # #             attn = attn.detach().cpu().numpy()
# # #             # Check if the counter exceeds the available subplots and create new figure if needed
# # #             if plot_idx >= n_rows * n_cols:
# # #                 fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))
# # #                 ax = ax.flatten()
# # #                 plot_idx = 0

# # #             # Plot heatmap
# # #             cax = ax[plot_idx].imshow(attn, cmap='viridis')

# # #             # Set title and axis labels if desired

# # #             ax[plot_idx].set_title(f"{h}: {qpos} -> {kpos}")
# # #             ax[plot_idx].set_xlabel("key tok")
# # #             ax[plot_idx].set_ylabel("query tok")

# # #             # Optionally add a colorbar
# # #             plt.colorbar(cax, ax=ax[plot_idx])

# # #             # Increment the counter
# # #             plot_idx += 1

# # #             # You might want to save or display the plot here if you're iterating over many subplots
# # #             if plot_idx == 0:
# # #                 plt.tight_layout()
# # #                 plt.show()

# # # %%
# # model.ln_final

# # # %%
# # def ln_final_noscale(x):
# #     return x - x.mean(axis=-1, keepdim=True)

# # # %%
# # # Here you may want to determine an appropriate grid size based on the number of plots
# # # For example, if you have a total of 12 plots, you might choose a 3x4 grid
# # n_rows = 3  # Example value, adjust as needed
# # n_cols = 4  # Example value, adjust as needed

# # # Create a figure and a grid of subplots
# # fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))

# # # Flatten the 2D axis array to easily iterate over it in a single loop
# # ax = ax.flatten()

# # # Counter for the subplot index
# # plot_idx = 0

# # for pos in range(dataset.seq_len-1):
# #     for h in range(2):
# #         EPVOU = ln_final_noscale(model.blocks[0].ln1(model.W_pos[pos,:] + model.W_E) @ model.W_V[0,h,:,:] @ model.W_O[0,h,:,:]) @ model.W_U
# #         EPVOU = EPVOU - EPVOU.mean(dim=-1, keepdim=True)
# #         EPVOU = EPVOU.detach().cpu().numpy()
# #         # Check if the counter exceeds the available subplots and create new figure if needed
# #         if plot_idx >= n_rows * n_cols:
# #             fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))
# #             ax = ax.flatten()
# #             plot_idx = 0

# #         # Plot heatmap
# #         cax = ax[plot_idx].imshow(EPVOU, cmap='RdBu', norm=colors.CenteredNorm())

# #         # Set title and axis labels if desired

# #         ax[plot_idx].set_title(f"h{h} P{pos}: EVOU+PVOU ln_final_noscale")
# #         ax[plot_idx].set_xlabel("output tok")
# #         ax[plot_idx].set_ylabel("key tok")

# #         # Optionally add a colorbar
# #         plt.colorbar(cax, ax=ax[plot_idx])

# #         # Increment the counter
# #         plot_idx += 1

# #         # You might want to save or display the plot here if you're iterating over many subplots
# #         if plot_idx == 0:
# #             plt.tight_layout()
# #             plt.show()

# # # %%


# # # %%
# # # Here you may want to determine an appropriate grid size based on the number of plots
# # # For example, if you have a total of 12 plots, you might choose a 3x4 grid
# # n_rows = 3  # Example value, adjust as needed
# # n_cols = 4  # Example value, adjust as needed

# # # Create a figure and a grid of subplots
# # fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))

# # # Flatten the 2D axis array to easily iterate over it in a single loop
# # ax = ax.flatten()

# # # Counter for the subplot index
# # plot_idx = 0

# # for pos in range(dataset.list_len, dataset.seq_len-1):
# #     EUPU = ln_final_noscale(model.W_pos[pos,:] + model.W_E) @ model.W_U
# #     EUPU = EUPU.detach().cpu().numpy()
# #     # Check if the counter exceeds the available subplots and create new figure if needed
# #     if plot_idx >= n_rows * n_cols:
# #         fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))
# #         ax = ax.flatten()
# #         plot_idx = 0

# #     # Plot heatmap
# #     cax = ax[plot_idx].imshow(EUPU, cmap='RdBu')

# #     # Set title and axis labels if desired

# #     ax[plot_idx].set_title(f"{pos}")
# #     ax[plot_idx].set_xlabel("output tok")
# #     ax[plot_idx].set_ylabel("key tok")

# #     # Optionally add a colorbar
# #     plt.colorbar(cax, ax=ax[plot_idx])

# #     # Increment the counter
# #     plot_idx += 1

# #     # You might want to save or display the plot here if you're iterating over many subplots
# #     if plot_idx == 0:
# #         plt.tight_layout()
# #         plt.show()

# # # %%
# # attn_all = compute_attn_all(model, outdim='h qpos kpos qtok ktok')

# # # %%
# # analyze_svd(attn_all[1,10,0])

# # # %%
# # s = layernorm_scales(model.W_pos[:,None,:] + model.W_E[None,:,:])[...,0]
# # s = s / s.min()
# # imshow(s)
# # # resid = model.blocks[0].ln1(model.W_pos[:,None,:] + model.W_E[None,:,:])
# # # q_all = einsum(resid,
# # #                    model.W_Q[0,:,:,:],
# # #                    'qpos qtok d_model_q, h d_model_q d_head -> qpos qtok h d_head') + model.b_Q[0]
# # #     k_all = einsum(resid,
# # #                    model.W_K[0,:,:,:],
# # #                    'kpos ktok d_model_k, h d_model_k d_head -> kpos ktok h d_head') + model.b_K[0]
# # #     attn_all = einsum(q_all, k_all, f'qpos qtok h d_head, kpos ktok h d_head -> {outdim}')
# # #     attn_all_max = reduce(attn_all, f"{outdim} -> {outdim.replace('kpos', '()').replace('ktok', '()')}", 'max')


# # # %%



# # x = x - x.mean(axis=-1, keepdim=True)  # [batch, pos, length]
# #         scale: Float[torch.Tensor, "batch pos 1"] = self.hook_scale(
# #             (x.pow(2).mean(-1, keepdim=True) + self.eps).sqrt()
# #         )
# #         x = x / scale  # [batch, pos, length]

# # # %%
# # model.blocks[0].ln1

# # # %%
# # sys.path.append(f"{os.getcwd()}/training")
# # import visualization
# # from visualization import visualize_on_input

# # # %%
# # dataset.toks[0]

# # # %%
# # visualize_on_input(model, dataset.toks[0])

# # # %%
# # targets[326]

# # # %%
# # ' '.join(dataset.str_toks[326])

# # # %%

# # imshow(logits[326])

# # # %%
# # ls = [5,6,33,40,41,42,43,44,45,46]
# # # ls = [1, 1, 1, 1, 40, 40, 40, 40, 40]
# # unsorted_list = t.tensor(ls)
# # sorted_list = t.sort(unsorted_list).values
# # toks = t.concat([unsorted_list, t.tensor([dataset.vocab.index("SEP")]), sorted_list], dim=-1)
# # str_toks = [dataset.vocab[i] for i in toks]
# # print(' '.join(str_toks))
# # imshow(model(toks.unsqueeze(0))[0, dataset.list_len:-1, :])

# # # %%
# # probs_correct.min(dim=0,keepdim=True)


# # # %%
# # logits, cache = model.run_with_cache(dataset.toks)
# # logits: t.Tensor = logits[:, dataset.list_len:-1, :]

# # targets = dataset.toks[:, dataset.list_len+1:]

# # logprobs = logits.log_softmax(-1) # [batch seq_len vocab_out]
# # probs = logprobs.softmax(-1)


# # # %%
# # model.W_pos.shape

# # # %%
# # model.W_E.shape

# # # %%
# # from einops import reduce

# # # %%


# # # %%
# # W_pos_reduced = model.W_pos[dataset.list_len+1:-1]
# # W_pos_mean = W_pos_reduced.mean(dim=0)
# # W_pos_centered = W_pos_reduced - W_pos_mean[None,:]
# # line(W_pos_mean)
# # imshow(W_pos_centered)

# # # %%
# # U, S, Vh = t.svd(model.W_pos.detach().cpu()[:10])
# # imshow(U)
# # imshow(Vh)
# # line(S)
# # U, S, Vh = t.svd(model.W_pos.detach().cpu()[11:])
# # imshow(U)
# # imshow(Vh)
# # line(S)

# # # %%
# # with t.no_grad():
# #     # print((model.blocks[0].ln1(model.W_pos[dataset.list_len:-1,None,:] + model.W_E[None,:,:])).shape)
# #     # print(model.W_Q[0,:,:,:].shape)
# #     # print(model.W_K[0,:,:,:].shape)
# #     attn_all = einsum(model.blocks[0].ln1(model.W_pos[dataset.list_len:-1,None,:] + model.W_E[None,:,:]),
# #                       model.W_Q[0,:,:,:],
# #                       model.W_K[0,:,:,:],
# #                       model.blocks[0].ln1(model.W_pos[:-1,None,:] + model.W_E[None,:,:]),
# #                    'qpos qtok d_model_q, h d_model_q d_head, h d_model_k d_head, kpos ktok d_model_k -> h qpos kpos qtok ktok')
# #     # for h in range(2):
# #     #     for qpos in range(attn_all.shape[1]):
# #     #         for qtok in range(attn_all.shape[3]):
# #     #             attn_all[h,qpos,:,qtok,:] = attn_all[h,qpos,:,qtok,:] - attn_all[h,qpos,:,qtok,:].max()
# #     # attn_all = attn_all - attn_all.max(dim=2, keepdim=True).values
# #     print(attn_all.shape)
# #     attn_all_reduced = attn_all.clone()
# #     for qpos in range(attn_all.shape[1]):
# #         attn_all_reduced[:,qpos,:,:] = attn_all[:,qpos,:qpos+11,:].mean(dim=1, keepdim=True)
# #     attn_all_reduced = attn_all_reduced.mean(dim=2)[:,1:-1].mean(dim=1)
# #     print(attn_all_reduced.shape)
# #     # subtract off diagonal
# #     for h in range(attn_all_reduced.shape[0]):
# #         attn_all_reduced[h] = attn_all_reduced[h] - attn_all_reduced[h].diag()[:, None]
# #     attn_all_reduced = attn_all_reduced - attn_all_reduced.max(dim=-1,keepdim=True).values
# #     # attn_all_reduced = attn_all_reduced - attn_all_reduced.max(dim=-1, keepdim=True).values
# #     for h, attn in enumerate(attn_all_reduced):
# #         imshow(attn, title=f"h{h} attn_all_reduced")
# #     for h, attn in enumerate(attn_all_reduced):
# #         U, S, Vh = t.svd(attn)
# #         imshow(U, title=f"h{h} U attn_all_reduced")
# #         imshow(Vh, title=f"h{h} Vh attn_all_reduced")
# #         line(S, title=f"h{h} S attn_all_reduced")

# #     # print(attn_all_reduced.shape)

# #     # attn_all_reduced = attn_all[:,].mean(dim=1)
# #     # attn_all_reduced = reduce(attn_all[:,], 'h qpos kpos qtok ktok -> h qpos kpos qtok', 'sum')
# #     # all_attn_by_gap = []
# #     # #t.zeros(list(attn_all.shape[:-1]) + [attn_all.shape[-1], attn_all.shape[-1]])
# #     # for h in range(2):
# #     #     for qpos in range(attn_all.shape[1]):
# #     #         for kpos in range(qpos+1):
# #     #             for qtok in range(attn_all.shape[3]):
# #     #                 for ktok1 in range(attn_all.shape[4]):
# #     #                     for ktok2 in range(attn_all.shape[4]):
# #     #                         all_attn_by_gap.append(attn_all[h,qpos,kpos,qtok,ktok])

# # # %%


# # # %%
# # model.blocks[0].ln1(model.W_pos[qpos,:] + model.W_E) @ model.W_Q[0,h,:,:] @ model.W_K[0,h,:,:].T @ model.blocks[0].ln1(model.W_pos[kpos,:] + model.W_E).T

# # # %%
# # attn = model.blocks[0].ln1(model.W_pos[qpos,:] + model.W_E) @ model.W_Q[0,h,:,:] @ model.W_K[0,h,:,:].T @ model.blocks[0].ln1(model.W_pos[kpos,:] + model.W_E).T
# #             attn = attn - attn.max(dim=-1, keepdim=True).values
# #             attn = attn.detach().cpu().numpy()


# # # %%
# # # with t.no_grad():
# # #     attn_all = einsum(model.blocks[0].ln1(model.W_pos[dataset.list_len:-1,None,:] + model.W_E[None,:,:]),
# # #                       model.W_Q[0,:,:,:],
# # #                       model.W_K[0,:,:,:],
# # #                       model.blocks[0].ln1(model.W_pos[:-1,None,:] + model.W_E[None,:,:]),
# # #                    'qpos qtok d_model_q, h d_model_q d_head, h d_model_k d_head, kpos ktok d_model_k -> h qpos kpos qtok ktok')


# # # %%
# # model.W_O.shape

# # # %%
# # with t.no_grad():
# #     EP = model.W_pos[:-1,None,:] + model.W_E[None,:,:]
# #     EP = model.blocks[0].ln1(EP)
# #     EPVO =  einsum(EP,
# #                    model.W_V[0,:,:,:],
# #                    model.W_O[0,:,:,:],
# #                    '''pos vocab_in d_model_v,
# #                     h d_model_v d_head,
# #                     h d_head d_model_o
# #                       -> h pos vocab_in d_model_o'''.replace('\n', ' '))
# #     EPVO = ln_final_noscale(EPVO)
# #     EPVOU = einsum(EPVO,
# #                      model.W_U,
# #                      '''h pos vocab_in d_model_o,
# #                      d_model_o vocab_out
# #                      -> h pos vocab_in vocab_out'''.replace('\n', ' '))
# #     EPVOU_mean = t.cat([EPVOU[:,:dataset.list_len,:,:], EPVOU[:,dataset.list_len+1:-1,:,:]], dim=1).mean(dim=1,keepdim=True)
# #     EPVOU = EPVOU - EPVOU_mean
# #     # EPVOU_mean = EPVOU_mean - EPVOU_mean.max(dim=-1, keepdim=True).values
# #     for h in range(2):
# #         imshow(EPVOU_mean[h, 0], title=f"h{h} EPVOU.mean(dim=pos)")

# #     for h in range(2):
# #         line(EPVOU_mean[h, 0].diag(), title=f"h{h} EPVOU.mean(dim=pos).diag()")
# #     line(EPVOU_mean[:, 0].sum(dim=0).diag(), title=f"h{h} EPVOU.mean(dim=pos).sum(dim=head).diag()")
# #     # Here you may want to determine an appropriate grid size based on the number of plots
# #     # For example, if you have a total of 12 plots, you might choose a 3x4 grid
# #     n_rows = 3  # Example value, adjust as needed
# #     n_cols = 4  # Example value, adjust as needed

# #     # Create a figure and a grid of subplots
# #     fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))

# #     # Flatten the 2D axis array to easily iterate over it in a single loop
# #     ax = ax.flatten()

# #     # Counter for the subplot index
# #     plot_idx = 0

# #     for pos in range(EPVOU.shape[1]):
# #         for h in range(2):
# #             # Check if the counter exceeds the available subplots and create new figure if needed
# #             if plot_idx >= n_rows * n_cols:
# #                 fig, ax = plt.subplots(n_rows, n_cols, figsize=(15, 15))
# #                 ax = ax.flatten()
# #                 plot_idx = 0

# #             # Plot heatmap
# #             cax = ax[plot_idx].imshow(EPVOU[h, pos].detach().cpu().numpy(), cmap='RdBu')

# #             # Set title and axis labels if desired

# #             ax[plot_idx].set_title(f"h{h} P{pos}: EVOU+PVOU ln_final_noscale")
# #             ax[plot_idx].set_xlabel("output tok")
# #             ax[plot_idx].set_ylabel("key tok")

# #             # Optionally add a colorbar
# #             plt.colorbar(cax, ax=ax[plot_idx])

# #             # Increment the counter
# #             plot_idx += 1

# #             # You might want to save or display the plot here if you're iterating over many subplots
# #             if plot_idx == 0:
# #                 plt.tight_layout()
# #                 plt.show()
# #     # for pos in range(EPVOU.shape[1]):
# #     #     for h in range(2):
# #     #         imshow(EPVOU[h, pos], title=f"h{h} pos{pos} EPVOU")
# #     #     break
# #     # EPVOU_all = einsum()
# # # for pos in range(dataset.seq_len-1):
# # #     for h in range(2):
# # #         EPVOU = ln_final_noscale(model.blocks[0].ln1(model.W_pos[qpos,:] + model.W_E) @ model.W_V[0,h,:,:] @ model.W_O[0,h,:,:]) @ model.W_U
# # #         EPVOU = EPVOU.detach().cpu().numpy()


# # # %%
# # model.b_K

# # # %%

# %%
