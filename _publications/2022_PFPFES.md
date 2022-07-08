---
title: "{PF}^2ES: Parallel Feasible Pareto Frontier Entropy Search for Multi-Objective Bayesian Optimization Under Unknown Constraints"
collection: publications
date: 2022-03-01
venue: 'Preprint'
---
We present Parallel Feasible Pareto Frontier Entropy Search {PF}^2ES -- a novel information-theoretic acquisition function for multi-objective Bayesian optimization. Although information-theoretic approaches regularly provide state-of-the-art optimization, they are not yet widely used in the context of constrained multi-objective optimization. Due to the complexity of characterizing mutual information between candidate evaluations and (feasible) Pareto frontiers, existing approaches must employ severe approximations that significantly hamper their performance. By instead using a variational lower bound, {PF}^2ES provides a low cost and accurate estimate of the mutual information for the parallel setting (where multiple evaluations must be chosen for each optimization step). Moreover, we are able to interpret our proposed acquisition function by exploring direct links with other popular multi-objective acquisition functions. We benchmark {PF}^2ES across synthetic and real-life problems, demonstrating its competitive performance for batch optimization across synthetic and real-world problems including vehicle and electronic filter design.

[Download paper here](http://henrymoss.github.io/files/pfpfes.pdf)

