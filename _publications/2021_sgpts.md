---
title: "Scalable Thompson Sampling using Sparse Gaussian Process Models"
collection: publications
date: 2021-10-01
venue: 'Advances in Nerual Information Processing (NeurIPS) 2021'
---
Thompson Sampling (TS) from Gaussian Process (GP) models is a powerful toolfor the optimization of black-box functions. Although TS enjoys strong theoreticalguarantees and convincing empirical performance, it incurs a large computationaloverhead that scales polynomially with the optimization budget. Recently, scalableTS methods based on sparse GP models have been proposed to increase the scopeof TS, enabling its application to problems that are sufficiently multi-modal, noisyor combinatorial to require more than a few hundred evaluations to be solved.However, the approximation error introduced by sparse GPs invalidates all existingregret bounds.  In this work, we perform a theoretical and empirical analysis ofscalable TS. We provide theoretical guarantees and show that the drastic reductionin computational complexity of scalable TS can be enjoyed without loss in theregret performance over the standard TS. These conceptual claims are validated forpractical implementations of scalable TS on synthetic benchmarks and as part of areal-world high-throughput molecular design task.

[Download paper here](http://henrymoss.github.io/files/S_GP_TS.pdf)

