---
title: "A penalisation method for batch multi-objective Bayesian optimisation with application in heat exchanger design"
collection: publications
date: 2022-07-01
venue: 'ICML 2nd RealML Workshop'
---
We present HIghly Parallelisable Pareto Optimisation (HIPPO) -- a batch acquisition function that enables multi-objective Bayesian optimisation methods to efficiently exploit parallel processing resources. Multi-Objective Bayesian Optimisation (MOBO) is a very efficient tool for tackling expensive black-box problems. However, most MOBO algorithms are designed as purely sequential strategies, and existing batch approaches are prohibitively expensive for all but the smallest of batch sizes. We show that by encouraging batch diversity through penalising evaluations with similar predicted objective values, HIPPO is able to cheaply build large batches of informative points. Our extensive experimental validation demonstrates that HIPPO is at least as efficient as existing alternatives whilst incurring an order of magnitude lower computational overhead and scaling easily to batch sizes considerably higher than currently supported in the literature. Additionally, we demonstrate the application of HIPPO to a challenging heat exchanger design problem, stressing the real-world utility of our highly parallelisable approach to MOBO.

[Download paper here](http://henrymoss.github.io/files/penal.pdf)

