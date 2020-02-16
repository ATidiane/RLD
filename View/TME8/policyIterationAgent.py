import argparse
import sys
import matplotlib
matplotlib.use("TkAgg")
import gym
import envs
#import gridworld_env
from gym import wrappers, logger
import numpy as np
import copy
import json


class policyIteration(object):
	def __init__(self, eps, action_space, MDP, gamma):
		self.eps = eps
		self.action_space = action_space
		self.state = [s for s in MDP[1]]
		self.all_states = [s for s in MDP[0]]
		self.P = MDP[1]
		self.gamma = gamma


		print("############## Debut apprentissage ##############")
		self.pi = {s: None for s in self.state} 
		pi_kplus = {s: self.action_space.sample() for s in self.state}

		while self.pi != pi_kplus:
			self.pi = dict(pi_kplus)
			Vpi_t = np.array([np.random.random(1)[0] for _ in range(len(self.all_states))]) #np.random.random(1)[0]
			Vpi_tplus = np.array([0. for i in range(len(self.all_states))])

			for s in self.state:
				Vpi_tplus[self.state.index(s)] = np.sum([proba * (reward + self.gamma * Vpi_t[self.all_states.index(s_prime)]) 
					for proba, s_prime, reward, boolean in self.P[s][self.pi[s]]])	

			while np.linalg.norm((Vpi_t - Vpi_tplus), ord=np.inf) > self.eps:
				Vpi_t = Vpi_tplus.copy()
				for s in self.state:
					Vpi_tplus[self.state.index(s)] = np.sum([proba * (reward + self.gamma * Vpi_t[self.all_states.index(s_prime)]) 
						for proba, s_prime, reward, boolean in self.P[s][self.pi[s]]])
		
			for s in self.state:
				pi_kplus[s] = np.argmax(
					[np.sum([proba * (reward + self.gamma * Vpi_t[self.all_states.index(s_prime)]) 
						for proba, s_prime, reward, boolean in self.P[s][a]]) for a in range(self.action_space.n)])
		
		self.pi = dict(pi_kplus)

		print("############### Fin apprentissage ###############")

	def act(self, observation, reward, done):
		return self.pi[observation.dumps()]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('env_id', nargs='?', default='gridworld-v0', help='Select the environment to run')
    args = parser.parse_args()

    # You can set the level to logger.DEBUG or logger.WARN if you
    # want to change the amount of output.
    logger.set_level(logger.INFO)
    
    envx = gym.make(args.env_id)
 

    outdir = 'gridworld-v0/random-agent-results'

    env = wrappers.Monitor(envx, directory=outdir, force=True, video_callable=False)

    env.seed(0)


    episode_count = 1000000
    reward = 0
    done = False
    envx.verbose = True

    envx.setPlan("gridworldPlans/plan7.txt",{0:-0.001,3:1,4:1,5:-1,6:-1})

    agent = policyIteration(0.00001, envx.action_space , envx.getMDP(), 0.9)

    rsum=0
    for i in range(episode_count):
        ob = env.reset()

        if i % 100 == 0 and i > 0:
            envx.verbose = True
        else:
            envx.verbose = False

        if envx.verbose:
            envx.render(1)
        j = 0
        #print(str(ob))
        while True:

            action = agent.act(ob, reward, done)
            ob, reward, done, _ = env.step(action)
            rsum+=reward
            j += 1
            if envx.verbose:
                envx.render()
            if done:
                print(str(i)+" rsum="+str(rsum)+", "+str(j)+" actions")
                rsum=0
                break

    print("done")
    env.close()