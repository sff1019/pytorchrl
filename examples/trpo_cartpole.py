import numpy as np
import gym

from rllab.baselines.linear_feature_baseline import LinearFeatureBaseline
from rllab.envs.normalized_env import normalize

from pytorchrl.algos.trpo import TRPO
from pytorchrl.envs.gym_env import GymEnv
from pytorchrl.policies.categorical_mlp_policy import CategoricalMLPPolicy
from pytorchrl.misc.instrument import run_experiment_lite, VariantGenerator, variant


class VG(VariantGenerator):
    @variant
    def seed(self):
        return [1]

    @variant
    def name(self):
        return ['pytorch-finite']

def run_task(*_):
    env = GymEnv("CartPole-v0", record_video=False, force_reset=True)

    observation_dim = np.prod(env.observation_space.shape)
    num_actions = env.action_space.n

    policy = CategoricalMLPPolicy(
        observation_dim=observation_dim,
        num_actions=num_actions,
        # The neural network policy should have two hidden layers, each with 32 hidden units.
        hidden_sizes=(32, 32)
    )

    baseline = LinearFeatureBaseline(env_spec=env.spec)

    algo = TRPO(
        env=env,
        policy=policy,
        baseline=baseline,
        batch_size=4000,
        max_path_length=env.horizon,
        n_itr=1,
        discount=0.99,
        step_size=0.01,
        use_finite_diff_hvp=True,
        symmetric_finite_diff=False,
        # Uncomment both lines (this and the plot parameter below) to enable plotting
        plot=True,
    )
    algo.train()

# if __name__ == '__main__':
#     run_task()

variants = VG().variants()

for v in variants:
    run_experiment_lite(
        run_task,
        exp_prefix='trpo_cartpole_comparison',
        # Number of parallel workers for sampling
        n_parallel=1,
        # Only keep the snapshot parameters for the last iteration
        snapshot_mode="last",
        # Specifies the seed for the experiment. If this is not provided, a random seed
        # will be used
        seed=v['seed'],
        variant=v,
        # dry=True,
        plot=True,
    )
