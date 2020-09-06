import time

import numpy as np
import gym

from rllab.baselines.linear_feature_baseline import LinearFeatureBaseline


from pytorchrl.algos.irl_trpo import IRLTRPO
from pytorchrl.envs.gym_env import GymEnv
from pytorchrl.irl.gail import GAIL
from pytorchrl.policies.gaussian_mlp_policy import GaussianMLPPolicy
from pytorchrl.misc.log_utils import load_latest_experts

import torch.nn as nn

def main():
    env = GymEnv('Pendulum-v0', record_video=False, record_log=False)

    experts = load_latest_experts('data/irl/pendulum2', n=5)

    irl_model = GAIL(env_spec=env.spec, expert_trajs=experts)
    observation_dim = np.prod(env.observation_space.shape)
    action_dim = np.prod(env.action_space.shape)

    policy = GaussianMLPPolicy(
        observation_dim=observation_dim,
        action_dim=action_dim,
        # The neural network policy should have two hidden layers, each with 32 hidden units.
        hidden_sizes=(32, 32))

    algo = IRLTRPO(
        env=env,
        policy=policy,
        irl_model=irl_model,
        n_itr=1,
        batch_size=4000,
        max_path_length=100,
        discount=0.99,
        store_paths=True,
        discrim_train_itrs=50,
        irl_model_wt=1.0,
        entropy_weight=0.0, # GAIL should not use entropy unless for exploration
        zero_environment_reward=True,
        baseline=LinearFeatureBaseline(env_spec=env.spec),
    )


    algo.train()

if __name__ == '__main__':
    main()
