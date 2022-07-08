---
title: "Bayesian Quantile and Expectile Optimisation"
collection: publications
date: 2021-07-01
venue: 'Conference on Uncertainty in Artificial Intelligence'
---
Bayesian optimisation (BO) is widely used to optimise stochastic black box functions. While most BO approaches focus on optimising conditional expectations, many applications require risk-averse strategies and alternative criteria accounting for the distribution tails need to be considered. In this paper, we propose new variational models for Bayesian quantile and expectile regression that are well-suited for heteroscedastic noise settings. Our models consist of two latent Gaussian processes accounting respectively for the conditional quantile (or expectile) and the scale parameter of an asymmetric likelihood functions. Furthermore, we propose two BO strategies based on entropy search and Thompson sampling, that are tailored to such models and that can accommodate large batches of points. Contrary to existing BO approaches for risk-averse optimisation, our strategies can directly optimise for the quantile and expectile, without requiring replicating observations or assuming a parametric form for the noise. As illustrated in the experimental section, the proposed approach clearly outperforms the state of the art in the heteroscedastic, non-Gaussian case.

[Download paper here](http://henrymoss.github.io/files/quantile.pdf)

