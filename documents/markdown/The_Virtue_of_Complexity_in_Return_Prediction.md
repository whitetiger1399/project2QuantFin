# The Virtue of Complexity in Return Prediction

**Bryan Kelly, Semyon Malamud, and Kangying Zhou**

*The Journal of Finance*, Vol. LXXIX, No. 1, February 2024. DOI: 10.1111/jofi.13298

> Converted from the original PDF. Mathematical expressions, multi-column tables, and figure content may not preserve their original formatting. Refer to the PDF for exact notation.


<!-- PDF page 1 -->

THE JOURNAL OF FINANCE • VOL. LXXIX, NO. 1 • FEBRUARY 2024




BRYAN KELLY, SEMYON MALAMUD, and KANGYING ZHOU*


## Abstract

Much of the extant literature predicts market returns with “simple” models that use
only a few parameters. Contrary to conventional wisdom, we theoretically prove that
simple models severely understate return predictability compared to “complex” models in which the number of parameters exceeds the number of observations. We empirically document the virtue of complexity in U.S. equity market return prediction.
Our ﬁndings establish the rationale for modeling expected returns through machine
learning.



THE FINANCE LITERATURE HAS RECENTLY seen rapid advances in return
prediction methods borrowing from the machine learning canon. The primary economic-use case of these predictions has been portfolio construction.
While a number of papers document signiﬁcant empirical gains in portfolio
performance through the use of machine learning, there is little theoretical

*Bryan Kelly is at Yale School of Management, AQR Capital Management, and NBER. Semyon
Malamud is at Swiss Finance Institute, EPFL, and CEPR, and is a consultant to AQR. Kangying Zhou is at Yale School of Management. We are grateful for helpful comments from Cliff Asness; Kobi Boudoukh; Daniel Buncic; James Choi; Frank Diebold; Egemen Eren; Paul Goldsmith-
Pinkham; Amit Goyal; Ron Kaniel (discussant); Stefan Nagel (Editor); Andreas Neuhierl (discussant); Matthias Pelster (discussant); Olivier Scaillet (discussant); Christian Schlag (discussant);
Akos Toeroek; Hui Wang (discussant); Guofu Zhou (discussant); seminar participants at AQR,
Yale, Vienna University of Economics and Business, Philadelphia Fed, Bank for International
Settlements, NYU Courant, and EPFL; and conference participants at the Macro Finance Society, Adam Smith Asset Pricing Conference, SFS Cavalcade North America Conference, Hong
Kong Conference for Fintech, AI, and Big Data in Business, Wharton Jacobs-Levy Conference,
Research Symposium on Finance and Economics, China International Risk Forum, Stanford SITE
New Frontiers in Asset Pricing, and XXI Symposium. We are especially grateful to Mohammad
Pourmohammadi for suggesting several essential improvements to our proofs and technical conditions. AQR Capital Management is a global investment management ﬁrm, which may or may
not apply similar investment techniques or methods of analysis as described herein. The views
expressed here are those of the authors and not necessarily those of AQR. Semyon Malamud
gratefully acknowledges support from the Swiss Finance Institute and the Swiss National Science
Foundation, Grant 100018_192692. We have read The Journal of Finance’s disclosure policy and
have no conﬂicts of interest to disclose.
Correspondence: Bryan Kelly, Yale School of Management, AQR Capital Management, and
NBER; 165 Whitney Ave., New Haven, CT 06511; e-mail: bryan.kelly@yale.edu.


This  is an open access article under the terms of the Creative Commons Attribution-Non
Commercial-NoDerivs License, which permits use and distribution in any medium, provided the
original work is properly cited, the use is non-commercial and no modiﬁcations or adaptations are
made.

DOI: 10.1111/joﬁ.13298

© 2023 The Authors. The Journal of Finance published by Wiley Periodicals LLC on behalf of
American Finance Association.



<!-- PDF page 2 -->

15406261,
2024,
460                   The Journal of Finance®                                                        1,
Downloadedunderstanding of return forecasts and portfolios formed from heavily paramefrom
terized models.
We provide a theoretical analysis of such “machine learning portfolios.” Our
analysis can be summarized by the following thought experiment. Imagine
there is a true predictive model of the form

Rt+1 = f (Gt) + ϵt+1,                              (1)

where R is an asset return, G is a ﬁxed set of predictive signals, and  f is
a smooth function. The predictors G may be known to the analyst, but the                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
prediction function f is unknown. Rather than futile guess the functional form,                by
the analyst relies on the universal approximation rationale (see, for example,                                                                 National
Hornik, Stinchcombe, and White (1990)), that  f can be approximated with a
sufﬁciently wide neural network,                                                                                                                                                                                                                                                                                                                                                                                                                              University
Of
P
f (Gt) ≈     Si,tβi,                                                                                                                                                                                                                                                                                                                  Singapore,
i=1                                                                                                                                                                                Wiley
Onlinewhere Si,t =  ˜f (w′iGt) is a known nonlinear activation function with known
weights wi and P is sufﬁciently large.1 As a result, (1) takes the form                                                                                                        Library
on

P
Rt+1 =     Si,tβi + ˜ϵt+1.                            (2)                                                                                                         [18/10/2026].
i=1                                                                                                                  See
the
The training sample for this regression has a ﬁxed number of data points, T,                                        Terms
and the analyst must decide on the “complexity,” or the number of features P, to                        and
use in their approximating model. A simple model, one with P << T, will have                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Conditions
low variance thanks to parsimonious parameterization but will be a coarse
approximator of f, while a high-complexity model (P > T) has better approximation potential but may be poorly behaved and will require shrinkage/bias.
Our central research question therefore is, what level of model complexity (i.e.,
which P) should the analyst opt for? Does the approximation improvement
from large P justify the statistical costs (higher variance and/or higher bias)?
Answer: We prove that expected out-of-sample forecast accuracy and portfolio performance are strictly increasing in model complexity when appropri-ate shrinkage is applied (indeed, we derive the optimal degree of shrinkage                                                                                                                                                                                                                                                                                                                                                                                                                                                    (https://onlinelibrary.wiley.com/terms-and-conditions)
to maximize expected out-of-sample model performance). The analyst should                on
Wiley
always use the largest approximating model that she can compute. In other
Onlinewords, when the true data-generating process (DGP) is unknown, the approximation gains achieved through model complexity dominate the statistical costs                                                        Library
of heavy parameterization. The interpretation is not necessarily that asset re-                        for                                                                                                                                                                                                                                                                                                                                         rules
turns are subject to a large number of fundamental driving forces. Rather,                of
use;
even when the driving variables (Gt) have low dimension, complex models                OA
1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              articles
Assuming known weights wi is innocuous, as the universal approximation result applies even                        are
if weights are randomly generated Rahimi and Recht (2007). Our empirical analysis uses the
random Fourier feature (RFF) method of Rahimi and Recht (2007) to generate features as in (2).                                                                       governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 3 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          461               1,
Downloadedbetter leverage the information content of Gt by more accurately approximatfrom
ing the unknown and likely nonlinear prediction function.
To provide intuitive characterizations of forecast and portfolio behavior
in complex models, our theoretical environment has two simplifying aspects.
First, the machine learning models we study are restricted to high-dimensional
linear models. As suggested by equation (2), this sacriﬁces little generality as
a number of recent papers establish an equivalence between high-dimensional
linear models and more sophisticated models such as deep neural networks
(Jacot, Gabriel, and Hongler (2018), Allen-Zhu, Li, and Song (2019), Hastieet al. (2022)). In fact, equation (2) is a neural network with one hidden layer                                                                                                                                                                                                                                                                                                                                                                                                               https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
with P neurons and ﬁxed input weights. Second, we focus on a single risky               by
asset. Prediction is therefore isolated to the time-series dimension, and the                                                           National
These                                                         two sim-portfolio optimization                    problem                              reduces                                           to                                    market timing.2
pliﬁcations         make our key                       ﬁndings                            more                                            accessible,                                                   yet neither                                                                             is critical                                                                                  for                                                                          University
Of
our conclusions.
To provide a baseline for our ﬁndings, consider the well-known deﬁciency                                                                          Singapore,
of ordinary least squares (OLS) prediction in high dimensions. As the num-                                     Wiley
ber of regressors, P, approaches the number of data points, T, the expected                                            Online
out-of-sample R2 tends to negative inﬁnity. An immediate implication is that                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Library
a portfolio strategy attempting to use OLS return forecasts in such a setting               on
will have divergent variance. In turn, its expected out-of-sample Sharpe ratio collapses to zero. The intuition behind this is simple: When the number of                                                                                                [18/10/2026].
regressors is similar to the number of data points, the regressor covariance                      See
matrix is unstable, and its inversion induces wild variation in coefﬁcient esti-                      the
Terms
mates and forecasts. This is commonly interpreted as overﬁtting: With P = T,                      and
the regression exactly ﬁts the training data and performs poorly out-of-sample.
We are particularly interested in the behavior of portfolios in the high model                                                                          Conditions
complexity regime, where the number of predictors exceeds the number of observations (P > T).3 In this case, standard regression logic no longer holds
because the regressor inverse covariance matrix is not deﬁned. However, the
pseudo-inverse is deﬁned and it corresponds to a limiting ridge regression with
inﬁnitesimal shrinkage, or the “ridgeless” limit. An emerging statistics and
machine learning literature shows that, in the high-complexity regime, ridgeless regression can achieve accurate out-of-sample forecasts despite ﬁtting the
training data perfectly.4                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
on
2 The single-asset time-series case is economically important in its own right. It coincides with                                     Wiley
predictive regression for the market return, which has been the primary method for investigating                                            Online
a central organizing question of asset pricing: How much do discount rates vary over time? While
our analysis can be applied to a panel of many assets, the roles of covariances in asset returns and                                                    Library
signals across stocks complicate the theory.                                                                                                                       for
3 The statistics and machine learning community often refer to P > T as the “high-dimensional”                                     rulesof
or “overparameterized” regime. We avoid terminology like “overparameterized” and “overﬁt” as it                              use;
suggests the model uses too many parameters, which is not necessarily the case. For example, the               OA
true DGP may be highly complex (i.e., P is large relative to T) and thus a correctly speciﬁed model                                                           articles
would require P > T. When an empirical model has the same speciﬁcation as the true model, we                      are
prefer to call it correctly parameterized as opposed to overparameterized.
4 This seemingly counterintuitive phenomenon is sometimes called “benign overﬁt” (Bartlett                                                           governed
et al. (2020), Tsigler and Bartlett (2023)).                                                                                 bythe
applicable
Creative
Commons
License


<!-- PDF page 4 -->

15406261,
2024,
462                   The Journal of Finance®                                                        1,
Downloaded We analyze related phenomena in the context of return prediction and portfrom
folio optimization. We establish the striking theoretical result that market
timing strategies based on ridgeless least-squares predictions generate positive Sharpe ratio improvements for arbitrarily high levels of model complexity. Stated more plainly, when the true DGP is highly complex (i.e., has many
more parameters than there are training data observations), one might think
that a timing strategy based on ridgeless regression is bound to fail. After all,
it exactly ﬁts the training data with zero error. Surprisingly, this intuition is
wrong. We prove that strategies based on extremely high-dimensional modelscan thrive out-of-sample and outperform strategies based on simpler models                                                                                                                                                                                                                                                                                                                                                                                                                                                   https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
under fairly general conditions.                                                                                     by
Our theoretical analysis delivers a number of additional conclusions. First, it                                                                National
from a                                       prediction                                         model is                                              an incompleteshows      that          the out-of-sample                        R2                                                           mea-                                                                                 Universitysure of         its economic                     value. A                        market                                  timer                                      can generate                                                       signiﬁcant                                                             economic
Of
proﬁts even when the predictive R2 is negative. The reason is that the R2 is
heavily inﬂuenced by the variance of forecasts.5 A very low out-of-sample R2                                                                                 Singapore,
indicates a highly volatile timing strategy. But the properties of least squares                                        Wiley
imply that the expected out-of-sample return of a timing strategy is always                                                Online
positive. So, as long as the timing variance is not too high (R2 is not too nega-                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Library
tive), the timing Sharpe ratio can be substantial.                                                           on
Second, we study two theoretical cases, one for correctly speciﬁed models and
one for misspeciﬁed models. The correctly speciﬁed case develops the behavior                                                                                                         [18/10/2026].
of timing portfolios when the true DGP varies from simple to complex, holding                        See
the data size ﬁxed. This is valuable for developing a general understanding                        the
Terms
of machine learning portfolios for various DGPs. But the correct model spec-                        and
iﬁcation is unrealistic—it is unlikely that we ever have a predictor data set
that nests all relevant conditioning information, and it is also unlikely that                                                                                 Conditions
we use information in the proper functional form. Our main theoretical results
pertain to misspeciﬁed models, and this analysis coincides with the thought
experiment above. In practice, when we vary the empirical model speciﬁcation
from simple to complex, we change how accurately the model approximates a
ﬁxed DGP.
Third, while the results discussed so far refer primarily to the case of
ridgeless regression, we show that machine learning portfolios tend to incrementally beneﬁt from moving away from the ridgeless limit by introducing                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
nontrivial shrinkage. The bias induced by heavier ridge shrinkage lowers the                on
expected returns to market timing, but the associated variance reduction reins                                        Wiley
Online
5 That is, R2 is not just about predictive correlation. Consider a simple model with a single                                                        Library
predictor and a coefﬁcient estimate many times larger than the true value. This scale error will                        for
tend to drive the R2 negative, but it will not affect the correlation between the model ﬁts and the                                        rules
true conditional expectation. The R2 is negative only because the variance of the ﬁts is off. Related,                of                                                                                                                                                                                                                                                                        use;
Rapach, Strauss, and Zhou (2010) show that mean square forecast error (MSE) decomposes into a                OA
scale-free (correlation) component and a scale-dependent component. It is the scale-free component                                                                 articles
that is important for trading strategy performance. Leitch and Tanner (1991), Cenesizoglu and                        are
Timmermann (2012), and Rapach and Zhou (2013) also emphasize the importance of evaluating
return prediction models based on their economic value in terms of trading strategy performance.                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 5 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          463               1,
Downloadedin the volatility of the strategy. The Sharpe ratio tends to beneﬁt from higher
from
shrinkage because the variance reduction overwhelms the deterioration in expected timing returns. This is especially true when P ≈T, where the behavior
of ridgeless regression is most vulnerable.
From a technical standpoint, we characterize the behavior of portfolios in the
high-complexity regime using asymptotic analysis, as the model’s size grows
with the number of observations at a ﬁxed rate (T →∞and P/T →c > 0).
When P →∞, the regular asymptotic results, such as laws of large numbers
and central limit theorems, do not hold. Such analysis requires the apparatusof random matrix theory, on which we draw heavily to derive our results. Con-                                                                                                                                                                                                                                                                                                                                                                                                               https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
ceptually, this delivers an approximation of how a machine learning model be-               by
haves as we gradually increase the number of parameters holding the amount                                                           National
of  data       ﬁxed.
We     conduct           an extensive empirical analysis that demonstrates the virtues of                                                                          University
Of
model complexity in a canonical asset pricing problem: predicting the aggregate U.S. equity market return.6 In particular, we study market timing strate-                                                                          Singapore,
gies based on predictions from very simple models with a single parameter to                                     Wiley
extremely complex models with over 10,000 parameters (applied to training                                            Online
samples with as few as 12 monthly observations). The data inputs to our mod-                                                    Library
els are 15 standard predictor variables from the ﬁnance literature compiled by               on
Goyal and Welch (2008). To map our data analysis to the theory, we require a
method that smoothly transitions from low- to high-complexity models while                                                                                                [18/10/2026].
holding the underlying information set ﬁxed. The random feature method of                      See
Rahimi and Recht (2007) is ideal for this. We use it to construct expanding                      the
Terms
neural network architectures that take the Goyal and Welch (2008) predictors                      and
as inputs and maintain the core ridge regression structure of our theory.
We ﬁnd extraordinary agreement between empirical patterns and our theo-                                                                          Conditions
retical predictions. Over the standard Center for Research in Security Prices
(CRSP) sample from 1926 to 2020, out-of-sample market timing Sharpe ratio
improvements (relative to market buy-and-hold) reach roughly 0.47 per annum
with t-statistics near 3.0. This is despite the fact that the out-of-sample predictive R2 is substantially negative for the vast majority of models, consistent
with the theoretical argument that predictive R2 is inappropriate for judging
the economic beneﬁt of a machine learning model.
Timing positions from high-complexity models are remarkable. They behave                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
similarly to long-only strategies, following the Campbell and Thompson (2008)               on
recommendation to impose a nonnegativity constraint on expected market re-                                     Wiley
turns. But our models learn this behavior as opposed to being handed a con-                                            Online
straint. Moreover, machine learning strategies learn to divest leading up to                                                    Library
National Bureau of Economic Research (NBER) recessions, successfully doing                      for
so in 14 out of 15 recessions in our test sample on a purely out-of-sample basis.                                     rules
of
use;
OA
6                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         articles
Surveys of this large literature include Koijen and Van Nieuwerburgh (2011), Cochrane (2011),                      are
and Rapach and Zhou (2022). For early machine learning approaches to market return prediction,
see Rapach, Strauss, and Zhou (2010) and Kelly and Pruitt (2013).                                                                                                                                                                                                              governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 6 -->

15406261,
2024,
464                   The Journal of Finance®                                                        1,
Downloaded  This paper relates most closely to emerging literature that studies the theofrom
retical properties of machine learning models. A number of recent papers show
that linear models combined with random matrix theory help characterize the
behavior of neural networks trained by gradient descent.7 In particular, wide
neural networks (many nodes in each layer) are effectively kernel regressions,
and “early stopping” in neural network training is closely related to ridge regularization (Ali, Kolter, and Tibshirani (2019)). Recent research also emphasizes
the phenomenon of benign overﬁt and “double descent,” in which expected forecast error drops in the high-complexity regime.8  In this literature, the paper closest to ours is Hastie et al. (2022), who de-                                                                                                                                                                                                                                                                                                                                                                                                                                                    https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
rive nearly optimal error bounds in ﬁnite samples for bias and risk in the                by
ridge(less) regression under very general conditions.9 They are also the ﬁrst                                                                 National
to   introduce            misspeciﬁed                      models                                  in                               which                                  some of                                                the signals                                             may be                                                                unobservable.         In this                 paper, we                            focus                             on                                   the (easier)                                              asymptotic                                                          regime.                                              We                                                                  use                                                                                 University
Of
a different method of proof and relax some of the technical conditions on the
distributions of signals, using recent results of Yaskov (2016). In particular,                                                                                 Singapore,
we allow for nonuniformly positive-deﬁnite covariance matrices. Most impor-                                        Wiley
tantly, instead of focusing on the prediction model forecast error variance, we                                                Online
characterize expected out-of-sample expected returns, volatility, and Sharpe                                                        Library
ratios of market timing strategies based on machine learning predictions. As                on
in Hastie et al. (2022), our key interest is in the misspeciﬁed model. While
Hastie et al. (2022) focus on a speciﬁc form of misspeciﬁcation and its ridge-                                                                                                         [18/10/2026].
less limit, we derive general expressions for asymptotic expected returns and                        See
volatility in terms of signal correlations.                                                                                                            the
Terms
Our paper also relates closely to a growing empirical literature that uses ma-                        and
chine learning methods to analyze stock returns. The state-of-the-art market
return prediction uses high-dimensional models with shrinkage and demon-                                                                                 Conditions
strates robust out-of-sample predictive power. Rapach, Strauss, and Zhou
(2010) use predictors from Goyal and Welch (2008) and forecast combination
methods (which they show exert a strong shrinkage effect). Ludvigson and Ng
(2007) and Kelly and Pruitt (2013) use principal components regression and
partial least squares, respectively, to leverage large predictor sets for market
return prediction and achieve shrinkage through dimension reduction. Dong
et al. (2022) use 100 long-short “anomaly” portfolios to forecast the market return using a variety of forecasting strategies to implement shrinkage (more                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
generally, see the recent survey by Rapach and Zhou (2022)). An emerging lit-                on
erature uses machine learning methods to forecast large panels of individual                                        Wiley
stock returns or portfolios, including Rapach and Zhou (2020), Kozak, Nagel,                                                Online
and Santosh (2020), Freyberger, Neuhierl, and Weber (2020), Gu, Kelly, and                                                        Library
Xiu (2020), and Chen, Pelger, and Zhu (2023) (also see the survey by Kelly                        for
rules
7 See, for example, Jacot, Gabriel, and Hongler (2018), Hastie et al. (2022), Du et al. (2018), Du                of                                                                                                                                                                                                                                                                        use;
et al. (2019), and Allen-Zhu, Li, and Song (2019).                                                                          OA
8 See, for example, Spigler et al. (2019), Belkin et al. (2019), Belkin, Rakhlin, and Tsybakov                                                                 articles(2019), Belkin, Hsu, and Xu (2020), and Bartlett et al. (2020).
are
9 See also Richards, Mourtada, and Rosasco (2021), who obtain less general results in an asymptotic setting (as in our paper).                                                                                                                                                                                                                                                                                                                                                                                                  governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 7 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          465               1,
Downloadedand Xiu (2022)). Our paper offers theoretical justiﬁcation for the successes of
from
machine learning prediction documented in the asset pricing literature. Our
theoretical results call for researchers to consider even larger information sets
and higher dimensional approximations to further improve return forecasts (a
rationale justiﬁed by our empirical analysis). Finally, our paper is related to
Martin and Nagel (2022) and Da, Nagel, and Xiu (2022), who examine market
efﬁciency implications of the high-dimensional prediction problem faced by investors, to Fan et al. (2022) who touch upon the “double descent” phenomenon
in their analysis of structural machine learning models, and to ﬁnancial econo-metrics applications of random matrix theory such as Fan, Fan, and Lv (2008),                                                                                                                                                                                                                                                                                                                                                                                                               https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
Ledoit and Wolf (2020), and Fan, Guo, and Zheng (2022).                                              by
The paper is organized as follows. In Section I, we lay out the theoretical                                                           National
environment.             Section                         II                       presents                               the                                   foundational                                                   results                                                 from                                                 random                                                               matrix                                                                          Universitytheory from which              we                      derive                          our                          main                                         theoretical                                                       results.                                                         Section                                                                            III charac-
Of
terizes the behavior of machine learning portfolios in the correctly speciﬁed
setting and emphasizes the intuition behind the portfolio beneﬁts of high-                                                                          Singapore,
complexity prediction models. Section IV extends these results to the more                                     Wiley
practically relevant setting of misspeciﬁed models. We present our main em-                                            Online
pirical results in Section V. Section VI concludes. The Internet Appendix con-                                                    Library
tains a variety of supplementary theoretical results and empirical robustness               on
analyses.10 We invite readers that are primarily interested in the qualitative
theoretical points and the empirical analysis to skip the technical material of                                                                                                [18/10/2026].
Sections I and II.                                                                                                                                                             See
the
Terms
I. Environment                                                                                          and
This section describes our modeling assumptions and outlines the criteria                                                                          Conditions
we use to evaluate machine learning portfolios.


### A. Asset Dynamics

ASSUMPTION 1: There is a single asset whose excess return behaves according
to

Rt+1 = S′tβ + εt+1,                               (3)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
with εt+1 independent and identically distributed (i.i.d.), E[εt+1] = E[ε3t+1] =               on                                                                                                                                                                                                                                                                                                                                      Wiley
0, E[ε2t+1] = σ 2, E[ε4t+1] < ∞,11 and St a P-vector of predictor variables. Without                                                                     2                                                                                                                                 Onlineloss of generality, everywhere in the sequel, we normalize σ = 1.
Library
Assumption 1 establishes the basic return-generating process. Most notably,                      for
conditional expected returns depend on a potentially high-dimensional infor-                                     rulesof
use;
OA
10 The Internet Appendix is available in the online version of the article on The Journal of                                                           articlesFinance website.
are
11 The assumption of zero skewness simpliﬁes the analytical expressions but does not affect
our results.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 8 -->

15406261,
2024,
466                   The Journal of Finance®                                                        1,
Downloadedmation set embodied by the predictors, S. The interpretation of this assumpfrom
tion is not necessarily that asset returns are subject to many fundamental
driving forces. Instead, it espouses the machine learning perspective discussed
in the introduction: The DGP’s functional form is unknown but may be approximated with richly parameterized models using a high-dimensional nonlinear
expansion S of some underlying feature set.
The covariance structure of S plays a central role in the behavior of machine
learning predictions and portfolios. Assumption 2 imposes basic regularity conditions on this covariance.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298ASSUMPTION 2: There exist independent random vectors Xt ∈RP with four ﬁ-                by
nite ﬁrst moments, and a symmetric, P-dimensional positive semideﬁnite matrix                                                                 National  such that
University                                  St =   1/2Xt.                                                                 Of
Furthermore,  E[Xi,t] = E[Xi,t]3 = E[Xi1Xi2Xi3] = 0  and  E[Xi,t]2 = 1,  for  all                                                                                 Singapore,
i, i1, i2, i3 = 1, . . . , P and E[Xi1Xi2Xi3Xi4] = 0 whenever at least three indices                                                                                     4                                                            Wiley
among i1, i2, i3, i4 are different. Furthermore, the fourth moments E[Xi,t] are                                                                                                                                                                                                                                                                                                                                                                                                           Online
uniformly bounded.
Library
As we show below, the theoretical properties of machine learning portfolios                on
depend heavily on the distribution of eigenvalues of    . We are interested in
limiting behavior in the high model complexity regime, that is, as P, T →∞,                                                                                                         [18/10/2026].
with P/T →c > 0. Assumption 3 ensures that estimates of   are well behaved                        See
the
in this limit.                                                                                                                                                                                                                                                                                                                                         Terms
ASSUMPTION 3: We use λk(  ), k = 1, . . . , P, to denote the eigenvalues of an                        and
arbitrary matrix    . In the limit as P →∞, the spectral distribution F  of the                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Conditions
eigenvalues of

P
1
F  (x) =        1λk(  )≤x,                             (4)
P
k=1

converges to a nonrandom probability distribution H supported on [0, +∞).12
Furthermore,    is uniformly bounded as P →∞. We use                           ψ∗,k = P→∞P−1tr(lim          k) k ≥1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              (https://onlinelibrary.wiley.com/terms-and-conditions)
on
to denote asymptotic moments of the eigenvalues of    .                                                                                                                                    Wiley
Online  Our last assumption governs the behavior of the true predictive coefﬁcient,
β.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Library
for
ASSUMPTION 4: We assume that β = βP is random, β = (βi)Pi=1 ∈RP, with i.i.d.                                        rulesof
coordinates βi that are independent13 of S and R, and such that E[β] = 0,                                use;
OA
12 If zero is in the support of H, then   is strictly degenerate, meaning that some signals are re-                                                                 articlesdundant.
are
13 The assumption of a random coefﬁcient vector β is related to that in Gagliardini, Ossola, and
Scaillet (2016).                                                                                                                                                                                                                                                                                                                                                                                                                                                                        governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 9 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          467               1,
Downloaded
E[ββ′] = P−1b∗,PI for some constant b∗,P = E[∥β∥2],14 and satisﬁes b∗,P →b∗in                                                                                                                                                                                                                                                                     from
probability for some b∗> 0. Furthermore, E[β4i ] ≤KP−2 for some K > 0.

The randomness of β in Assumption 4 allows us to characterize the prediction and portfolio problem for generic predictive coefﬁcients. The assumption
that β is mean zero is inconsequential; we could allow for a nonzero mean
and restate our analysis in terms of variances rather than second moments.
The assumption E[ββ′] = P−1b∗,PI imposes that the predictive content of signals is rotationally symmetric, that is, predictability is uniformly distributed
across signals. This may seem restrictive, as commonly used return predictors                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
would not satisfy Assumption 4. But it is closely aligned with the structure               by
of feed-forward neural networks, in which raw features are mixed and non-                                                           National
linearly       propagated                     into ﬁnal generated                                       features                                        whose                                                     ordering                                                                             is essentially
randomized           by the initialization                                step of                                   network                                                    training.                                                                 Intuitively,                                                    we ex-                                                                          University
pect (and later conﬁrm empirically) that the random-feature methodology that               Of
we use in our empirical analysis satisﬁes Assumption 4.15                                                                                                                                                                                                                                Singapore,
When β is random and rotationally symmetric, we can focus on average port-                                     Wiley
folio behavior across signals, which implies that only the traces of the relevant                                            Online
matrices matter, as opposed to entire matrices (which are the source of techni-
Librarycal intractability). The proportionality of E[ββ′] to P−1, and likewise the ﬁnite               on
limiting ℓ2 norm of β, controls the “true” Sharpe ratio. It ensures that Sharpe
ratios of timing strategies remain bounded as the number of predictors grows.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].
In other words, our setting is one with many signals, each contributing a little                      See
bit of predictability.                                                                                                                                                        the
Terms A key aspect of our paper, and one rooted in Assumptions 2 and 4, is that
and
realized out-of-sample expected returns are independent of the speciﬁc realization of β. This is due to a law of large numbers in the P →∞limit and is                                                                          Conditions
guaranteed by the following lemma.16

LEMMA 1: As P →∞, we have

β′APβ −P−1b∗tr(AP) →0

in probability for any bounded sequence of matrices AP. In particular, β′  β →
b∗ψ∗,1.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
14 This identity follows because b∗= tr E[ββ′] = E[tr(ββ′)] = E[b∗].                                                                                                                                               Online
15 From a technical standpoint, it is possible to derive explicit expressions for portfolio per-                                                    Library
formance without this assumption, but the expressions become more complex. In this case, the                      for
asymptotic behavior depends on the distribution of projections of β on the eigenvectors of   (the                                     rules
signals’ principal components). See Hastie et al. (2022). In particular, when β is concentrated on               of                                                                                                                                                                                                                                                                     use;
the top principal components, the phenomenon of benign overﬁt emerges (Bartlett et al. (2020),               OA
Tsigler and Bartlett (2023)) and the optimal ridge regularization is zero. We leave this generaliza-                                                           articlestion for future research.
are
16 It is possible to use the results in Hastie et al. (2022) to extend our analysis to generic β
distributions. We leave this important direction for future research.                                                                                                                                                                                                         governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 10 -->

15406261,
2024,
468                   The Journal of Finance®                                                        1,
DownloadedB. Timing Strategies and Performance Evaluation
from
We study timing-strategy returns, deﬁned as

Rπt+1 = πtRt+1,

where πt is a timing weight that scales the position in the asset up and down
to exploit time variation in the asset’s expected returns.
We are interested in timing strategies that optimize the unconditional
Sharpe ratio,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
E[Rπt+1]                                                                by
SR =                      .                               (5)                                                                 National
E[(Rπt+1)2]
University
While there are other possible performance criteria, we focus on this one for                Of
its simplicity and ubiquity. It is implied by the quadratic utility function at                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Singapore,
the foundation of mean-variance portfolio theory. Academics and real-world                                        Wiley
investors rely nearly universally on the unconditional Sharpe ratio when eval-                                                Online
uating empirical trading strategies. The use of centered versus uncentered sec-
Libraryond moment in the denominator is without loss of generality.17                                       on
Our analysis centers on the following timing-strategy functional form:                                                                                                                                                                [18/10/2026].
πt(β) = S′tβ.                                  (6)                        See
the
This strategy takes positions equal to the asset’s conditional expected re-                                        Terms
turn. Note that this timing strategy optimizes the conditional Sharpe ra-                        and
tio. It achieves the same Sharpe ratio as the conditional Markowitz solution,     MV                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    ConditionsπCond.t    = Et[Rt+1]/Vart[Rt+1] = S′tβ, according to equation (3). While strategy
πt is conditionally mean-variance efﬁcient, it is not the optimizer of the unconditional objective in (5), which takes the form πUncond.t     MV = S′tβ/(1 + (S′tβ)2).18
In the proof of Proposition 1 in the Internet Appendix, we show that πt in equation (6) and πUncond.t     MV are equal up to third-order terms.19 We study πt = S′tβ
for the simplicity of its linearity in both β and St, but note that our conclusions
are identical for πUncond.t     MV because, in the limit as P →∞, the normalization
factor 1 + (S′tβ)2 converges to a constant.20  Proposition 1 states the behavior of timing strategy πt = S′tβ when T →∞                                                                                                                                                                                                                                                                                                                                                                                                                                                    (https://onlinelibrary.wiley.com/terms-and-conditions)
and P/T →0 (i.e., when the predictive parameter β is known).                                       on
Wiley
Online
Library
17                 E[Rπt+1]                                          1                                                                                 for    Deﬁne SR =                   . Direct calculation yields SR =               .
Var[(Rπt+1)]                               1+SR−2                                                                                                                              rules
18 See Hansen and Richard (1987), Ferson and Siegel (2001), Abhyankar, Basu, and Stremme                of                                                                                                                                                                                                                                                                        use;
(2012).                                                                                                                            OA
19 In particular, the Sharpe ratio in equation (5) is less than one due to the                                                                    Cauchy-Schwarz                                                                 articles                                                         MV
inequality. We show that the difference in Sharpe ratios for πt versus πUncond.t            is on the order of                        are
the Sharpe ratio cubed.
20 By a version of Lemma 1, 1 + (S′tβ)2 →1 + b∗ψ∗,1.                                                                                                                                                                                                                                                                         governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 11 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          469               1,
DownloadedPROPOSITION 1 (Inﬁnite Sample): The unconditional ﬁrst and second moments
from
of returns to the infeasible market timing strategy πt = S′tβ are

E[πtRt+1] →b∗ψ∗,1 > 0  and E (πtRt+1)2 →  3(b∗ψ∗,1)2 + b∗ψ∗,1  .

The infeasible market-timing Sharpe ratio is

1          1  1/2
SR →          <             .                      (7)
3 + (b∗ψ∗,1)−1    3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
For comparison, under Assumptions 1 to 4, the unconditional ﬁrst and sec-                                                           Nationalond moments of the untimed asset return are (see Lemma 1)
University                E[Rt+1] = 0,  and  E[R2t+1] →1 + b∗ψ∗,1 .                                         Of
That is, our assumptions imply that the untimed asset has a Sharpe ratio of                                                                          Singapore,
zero. This is just a normalization so that any positive market timing Sharpe                                     Wiley
ratio can be interpreted as pure excess performance arising from timing ability.                                            Online
Library
C. Relating Predictive Accuracy to Portfolio Performance                                               on

We are ultimately interested in understanding the portfolio properties of a                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].
feasible timing strategy, ˆπt = ˆβ′St. This is, of course, intimately tied to the pre-                      See
diction accuracy of the estimator ˆβ, summarized by its expected MSE on an                      the
Termsindependent test sample. This is the fundamental notion of estimator “risk”
and
from statistical theory, although we use the term “MSE” here to avoid confusion with portfolio riskiness. We can write MSE as                                                                                                                                                                                                                                                                                      Conditions

MSE( ˆβ) = E  Rt+1 −S′t ˆβ 2| ˆβ = E[R2t+1] −2 E[ ˆπtRt+1| ˆβ] + E[ ˆπ2t | ˆβ] .   (8)

Timing        Timing
Expected Return    Leverage

In other words, the higher the strategy’s expected return, the lower the MSE.
And the larger the positions—or “leverage”—of the strategy, the larger the
MSE. A timing strategy with a higher expected return corresponds to morepredictive power, while higher leverage gives the strategy higher variance. In-                                                                                                                                                                                                                                                                                                                                                                                                               (https://onlinelibrary.wiley.com/terms-and-conditions)
terestingly, these two objects, expected return and leverage of the timing strat-               on
Wileyegy, appear repeatedly throughout our analysis. The expected return/leverage
trade-off in (8) is a ﬁnancial decomposition of MSE analogous to its statistical                                            Online
decomposition into a bias/variance trade-off.                                                                                                                                                                                                                                   Library
Note that a strategy πt = β′St based on the infeasible true β satisﬁes                      for                                                                                                                                                                                                                                                                                                                                      rules
ofE[πtRt+1] = E[β′  β] = E[π2t ].21 In this case, the MSE collapses to E[R2t+1] −
E[πtRt+1] and is minimized, meaning that the leverage taken is exactly justi-                              use;OA
ﬁed by the predictive beneﬁts of the strategy. This can also be stated in terms                                                           articles
are
21 Indeed, E[(β′St)2] = E[β′StS′tβ] = β′  β.                                                                                                                                                                                                                                                                                                                   governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 12 -->

15406261,
2024,
470                   The Journal of Finance®                                                        1,
Downloadedof the infeasible R2 based on equation (3) and Lemma 1:
from
β′  β        b∗ψ∗,1
R2 =    →                                  β′  β + 1    b∗ψ∗,1 + 1.

Thus, there is a monotonic mapping from the infeasible timing-strategy expected return to the true R2, and from the infeasible Sharpe ratio to the true
R2 (see equation (7)).                 II. Machine Learning and Random Matrices                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
The central premise of machine learning is that large data sets can be used                                                                 Nationalin ﬂexible model speciﬁcations to improve prediction. This can be understood in
the environment above by considering the regime in which the number of pre-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   University
dictors, P, is large, perhaps even larger than T. Our main objective is thus to                Of
understand the behavior of optimal timing portfolios as the prediction model                                                                                 Singapore,becomes increasingly complex, that is, as P →∞. Because this involves es-
Wileytimating inﬁnite-dimensional parameters, traditional large-T asymptotics do
not apply, and hence we instead resort to random matrix theory. In this sec-                                                Online
tion, we discuss the ridge estimator and present random matrix theory results                                                        Library
at the foundation of our theoretical characterization of high-complexity tim-                on
ing strategies.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        [18/10/2026].
See
A. Least Squares Estimation                                                                                                                                     the
Terms
Throughout, we analyze (regularized) least-squares estimators taking the                        and
form                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Conditions
−1
1
ˆβ(z) =  zI + T−1    StS′t         StRt+1
T
t                         t

for a given ridge shrinkage parameter, z. The ridge-regularized form is necessary for characterizing ˆβ(z) in the high-complexity regime, P/T →c > 1, although we will see that it also has important implications for the behavior of
ˆβ(z) when P/T < 1.22
Consider ﬁrst the OLS estimator, ˆβ(0). As P approaches T from below, the                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
denominator of the least-squares estimator approaches the singularity. This                on
produces explosive variance of ˆβ(0) and, in turn, explosive forecast error vari-                                        Wiley
ance. As P →T, the model begins to ﬁt the data with zero error, so a common                                                Online
Library
22 One could alternatively analyze “sparse” least-squares models that combine shrinkage with                        for
variable selection (e.g., based on LASSO). First, recent evidence of Giannone, Lenza, and Primiceri                                        rules
(2021) suggests that sparsity of predictive relationships in economics and ﬁnance is likely an illu-                of                                                                                                                                                                                                                                                                        use;
sion. Second, our empirical focus is on nonparametric models that seek to approximate a generic                OA
nonlinear function as a linear combination of generated features, and sparsity in the generated                                                                 articles
feature space is difﬁcult to identify (see, for example, Ghorbani et al. (2020)). Third, analysis with                        are
ℓ1 shrinkage is signiﬁcantly more taxing from a theoretical standpoint. We thus leave sparse leastsquares models to future research.                                                                                                                                                                                                                                                                                                                                                                           governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 13 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          471               1,
Downloaded
interpretation of the explosive variance of ˆβ(0) is an insidious overﬁt that does                                                                                                                                                                                                                                                                     from
not generalize out-of-sample.
When P moves beyond  T,  there  are more parameters than  observations and  the  least-squares problem has  multiple  solutions. A  particularly  interesting  solution invokes the Moore-Penrose pseudo-inverse,
(T−1     t StS′t)+ T1      t StRt+1.23 This solution is equivalent to the ridge estimator as the shrinkage parameter approaches zero:

−1
1
ˆβ(0+) =                      lim   zI + T−1                                          StS′t                                                        StRt+1.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298                     z→0+                                  T                                                                                                                                  by                                                                          t                                                                                                    t
National
The solution ˆβ(0+) is often referred to as the “ridgeless” regression estimator. When P < T, OLS is the ridgeless estimator. At P = T, there is still a                                                                          University
unique least-squares solution, but the model can exactly ﬁt the training data               Of
(for this reason, P = T is called the “interpolation boundary”). When P > T, the                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Singapore,
ridgeless estimator is one of many solutions that exactly ﬁt the training data,
Wiley
but among these, it is the only solution that achieves the minimum ℓ2 norm
Onlineˆβ(z) (Hastie et al. (2022)). The machine learning literature has recently devoted substantial attention to understanding ridgeless regression in the high-                                                    Library
complexity regime. The counterintuitive insight from this literature is that,               on
beyond the interpolation boundary, allowing the model to become more com-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].plex in fact regularizes the behavior of least-squares regression despite using
See
inﬁnitesimal shrinkage. We explore the implications of this idea for market                      the
timing in the subsequent sections.                                                                                                                                                                                                       Terms
and
B. The Role of Random Matrix Theory                                                                                                                                                                                                                                                                                                                                                                                  Conditions

We analyze the ˆβ(z) behavior and associated market-timing strategies in the
limit as P →∞. This is possible due to a remarkable connection between ridge
regression and random matrix theory.
In regression analysis, the sample covariance matrix  of signals,   ˆ :=
T−1     t StS′t, naturally plays a central role. But no general characterization
exists for the behavior of  ˆ in the limit as P, T →∞. However, the tools of
random matrix theory characterize one aspect of  ˆ —the distribution of itseigenvalues. Fortunately, as we show, the prediction and portfolio performance                                                                                                                                                                                                                                                                                                                                                                                                                (https://onlinelibrary.wiley.com/terms-and-conditions)
properties of least-squares estimators rely only on the eigenvalue distribution               on
Wileyof  ˆ . Thus, random matrix theory facilitates a rich understanding of machine
Onlinelearning portfolios. Here, we elaborate on the core results from the random
matrix theory that we build upon.                                                                                                                                                                                                                                                                                        Library
First, to understand the central role of  ˆ ’s eigenvalue distribution in deter-                      for
rules
mining the limiting behavior of the least-squares estimator, suppose for the               of
moment that we could replace  ˆ with its true unobservable signal covariance,                              use;OA
articles
are
23 Recall that the Moore-Penrose pseudo-inverse A+  of a matrix A  is deﬁned as A+ =
limz→0+(zI + A′A)−1A′ = limz→0+ A′(zI + AA′)−1.                                                                                                                                                                                                                                                                                                   governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 14 -->

15406261,
2024,
472                   The Journal of Finance®                                                        1,
Downloaded   . For any symmetric matrix    , a convenient matrix identity states that
from

P
1              1
Ptr (  −zI)−1 = P     (λi(  ) −z)−1 ,
i=1

where λi(  ) are the eigenvalues of    . Using formula (4), we can rewrite this
identity as

1                  1                Ptr (  −zI)−1 =   x −zdF  (x) z < 0 .                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
From this identity, we immediately see the fundamental connection between                                                                National
ridge regularization and the distribution of eigenvalues for    . The right-hand
side quantity is the Stieltjes transform of the eigenvalue distribution of     ,                                                                                 University
denoted F   . By Assumption 3, this distribution is well behaved when P →∞                Of
and converges to a nonrandom distribution H. We therefore have                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Singapore,
Wiley                        1             1
m  (z) :=                          x −zdH(x) = P→∞lim Ptr (  −zI)−1  .               (9)                                                Online
Library
The function m  (z) is the limiting Stieltjes transform of the eigenvalue distri-                on
bution of    . Equation (9) is a powerful step toward understanding the least-squares estimator in the machine learning regime (and hence machine learn-                                                                                                         [18/10/2026].
ing predictions and portfolios). It states that key properties of the limiting                        See
the
inverse of the ridge-regularized signal covariance matrix can be characterized                                        Terms
entirely if we know   ’s eigenvalue distribution.                                                                                            and
The      problem,                  of course,                               is                           that                               the true                                                     is unobservable.                                        We                                                              only observe
ˆits   sample           counterpart,                                             , and                                 thus,                            we only                                         have empirical                                                              access                                                                           to the                                                                                 Conditions
Stieltjes transform of  ˆ ’s eigenvalues. The empirical counterpart to the unobservable m  (z) is

1
m(z; c) := lim        ( ˆ −zI)−1  .                        P→∞ Ptr

In traditional ﬁnite P statistics, we would have a convergence between the
sample covariance  ˆ and the true covariance   as T →∞. One might betempted to think that limP→∞1Ptr(( ˆ −zI)−1) and limP→∞1Ptr((  −zI)−1) also                                                                                                                                                                                                                                                                                                                                                                                                                                                    (https://onlinelibrary.wiley.com/terms-and-conditions)
converge as T →∞. But this is not the case. The limiting eigenvalue distri-                on
Wileybutions of  ˆ and   remain divergent in the limit as T →∞if P/T →c > 0.
OnlineHere, we see a ﬁrst glimpse of the complexity of machine learning and how random matrix theory can help us understand it. In the Internet Appendix (see                                                        Library
Theorem 2), we show how m(−z; c) can be computed from m (−z) using re-                        for
rules
sults of Silverstein and Bai (1995) and Bai and Zhou (2008). In particular,                of
m(−z; c) > m(−z; 0) = m (−z) for all c > 0.24 The next result shows that,                                use;OA
articles
are
24 Theorem 2 in the Internet Appendix is a generalized version of the Marˇcenko and Pastur
(1967) theorem that accommodates non-i.i.d. St. When signals are i.i.d. with  = I and m  (z) =                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 15 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          473               1,
Downloadedremarkably, if we constrain ourselves to linear ridge regression estimators, all
from
asymptotic expressions depend only on m(z; c) and do not require m  .25

PROPOSITION 2: We have

1
lim    tr((zI + ˆ )−1   ) →ξ(z; c)                    (10)
T→∞ T

almost surely, where

1 −zm(−z; c)
ξ(z; c) =                                  c−1 −1 + zm(−z; c).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
The quantity tr E[(zI + ˆ )−1  ] appears in virtually every expression we an-                                                           National
alyze      to        describe                   portfolio                          behavior.                                          It depends                                       on the                                                      interaction                                                       between
the                                                                          Universitysample      and           true signal                      covariance                              matrix                                 and arises                                                    in                                                  the computation                                                                               of both
the expected return and leverage of the timing strategy (see equation (8)). One               Of
might imagine, therefore, that we need to know the limiting eigenvalue distri-                                                                          Singapore,
bution of both matrices (or their Stieltjes transforms, m and m  ) to describe                                     Wiley
tr E[(zI + ˆ )−1   ]. Proposition 2 shows that this is not the case—we only need                                                                                                                                                                                                                                                                                                                                                                                                       Online
to know the empirical version, m(−z; c). This is a powerful result. It will allow
Library
us to quantify the expected out-of-sample behavior of machine learning portfo-               on
lios based only on the eigenvalue distribution of the sample signal covariance
ˆ (which is observable) without requiring that we know the eigenvalues of   .26                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].
We refer to the constant c as “model complexity,” which (as the preceding                      See
results show) plays a critical role in understanding model behavior. It describes                      the
Termsthe limiting ratio of predictors to data points: P/T →c. When T grows at a
and
faster rate than the number of predictors (i.e., c →0), the limiting eigenvalue
distributions of  ˆ and   converge: m(−z; 0) = m (−z). As c becomes positive,                                                                          Conditions
these distributions fail to converge, and their divergence is wider for larger c.
It is, therefore, clear that the behavior of the least-squares estimator in the
machine learning regime will differ from the true coefﬁcient, even when T →
∞, as long as c > 0. As a result, machine learning portfolios will suffer relative
to the infeasible performance in Proposition 1 despite abundant data. However,
while machine learning portfolios underperform the infeasible strategy, they


(1 −z)−1, Marˇcenko and Pastur (1967) show that                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
−((1 −c) + z) +   ((1 −c) + z)2 + 4cz                                             on
m(−z; c) =                                                                                                                          .                                                                                                             Wiley                                                  2cz
By direct calculation, the expression above is indeed the unique positive solution to (IA4) when                                            Online
m  (z) = (1 −z)−1. While the eigenvalue distributions of the sample and true covariance matri-                                                    Library
ces do not coincide, Theorem 2 describes the precise nonlinear way they relate to each other. In                      for
particular, when P > T, the matrix  ˆ has P −T zero eigenvalues and therefore, P−1tr((zI + ˆ )−1)                                     rules
contains a singular part, P−1(P −T)z−1 = (1 −c−1)z−1.                                                                 of
25                                                                                                                                                                                                                                                          use;
It is possible to develop nonlinear shrinkage estimators analogous to those developed by               OA
Ledoit and Wolf (2020) for covariance matrices. Such estimators would require knowledge of the                                                           articlestrue eigenvalue distribution of    , which can be recovered from m(z; c) using equation (IA4).
are
26 Heuristically, E[ ˆ ] =  and hence tr E[(zI + ˆ )−1  ] ≈tr E[(zI + ˆ )−1 ˆ ]. However, random
matrix corrections make the true relationship nonlinear.                                                                                                                                                                                                                                                              governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 16 -->

15406261,
2024,
474                   The Journal of Finance®                                                        1,
Downloadedcan continue to generate substantial trading gains. This is true even in the
from
ridgeless case. Additional ridge shrinkage can boost performance even further.
We precisely characterize these behaviors in the following sections.


## III. Prediction and Performance in the Machine Learning Regime

In this section, we analyze correctly speciﬁed models. We present the theoretical characterizations of machine learning models in terms of prediction
accuracy and portfolio performance. We then illustrate their behavior in a cal-ibrated theoretical setting.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
NationalA. Expected Out-of-Sample R2
To understand a model’s prediction accuracy in the high-complexity regime,                                                                                 University
Of
we study its limiting MSE, deﬁned as                                                                                                                                                                                                                                                                                                                                                                                            Singapore,
MSE(z; c) =     lim   E  Rt+1 −S′t ˆβ(z) 2| ˆβ(z)  .           (11)                                        Wiley                          T,P→∞, P/T→c
Online
Notably, while ˆβ(z) is random and depends on the sample realization, we show                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Library
below that the limit in (11) is nonrandom. The arguments z and c are central                on
to understanding the limiting predictive ability of least squares. Respectively,
they describe the extent of ridge shrinkage and the complexity of the DGP (and                                                                                                         [18/10/2026].
thus of the correctly speciﬁed model).                                                                                                                   See
the
In ﬁnance and economics, it is common to state predictive performance in                                                                                                                                                                                                                                                                                                                                         Terms
terms of R2 rather than MSE. We denote the limiting out-of-sample R2 as                                  and

MSE(z, c)                      R2(z; c) = 1 −                          ,                                                                                                                                                                                                                                                         Conditions
limT,P→∞E[R2t+1]

where E[R2t+1] is the null MSE when β = 0.
In Section I.C above, we discuss the infeasible maximum R2, or

b∗ψ∗,1
R2(0; 0) =                    .
1 + b∗ψ∗,1

This corresponds to a data-rich environment (c = 0, so observations vastly out-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)number parameters) and OLS regression (z = 0). The R2(0; 0) is the bench-                on
mark for evaluating the loss of predictive accuracy due to high model com-                                        Wiley
plexity, even when data are abundant. Speciﬁcally, the R2 of the least-squares                                                Online
estimator in the machine learning regime behaves as follows.
Library
PROPOSITION 3: In the limit as T, P →∞, and P/T →c, we have                                                   for
rules
E(z; c) = lim E[ ˆπtRt+1| ˆβ(z)] = b∗ν(z; c),                                                  ofuse;
OA
L(z; c) = lim E[ ˆπ2t | ˆβ(z)] = b∗ˆν(z; c) −cν′(z; c),             (12)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               articles
2E(z; c) −L(z; c)                                                                                                    are
R2(z; c) =                                                              ,                                                                                                                                                                                                                                                                     governed                          1 + b∗ψ∗,1
by
the
applicable
Creative
Commons
License


<!-- PDF page 17 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          475               1,
Downloadedwhere
from
ν(z; c) = ψ∗,1 −c−1zξ(z; c)    = lim P−1tr( ˆ (zI + ˆ )−1   )  > 0,

ν′(z; c) = −c−1(ξ(z; c) + zξ ′(z; c)) = −lim P−1tr( ˆ (zI + ˆ )−2   ) < 0,

ˆν(z; c) = ν(z; c) + zν′(z; c)     = lim P−1tr( ˆ 2(zI + ˆ )−2   ) > 0.

As we show in the Internet Appendix, these limits exist in probability.
Furthermore, R2(z; c) is monotone increasing in z for z < z∗= c/b∗, and decreasing in z for z > z∗. The R2(z; c) attains its maximum at z∗= c/b∗, where it                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
is positive and given by                                                                                                by
ξ(z∗; c)       b∗ν(z∗; c)                                                                                                                                                                                 National
R2(z∗; c) = R2(0; 0) −       =        > 0 .
1 + b∗ψ∗,1   1 + b∗ψ∗,1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            University
In the ridgeless limit, assuming H(0+) = 0, we have                                                      Of
Singapore,
(c−1 −1)−1,  c < 1
R2(0; c) = R2(0; 0) −(1 + b∗ψ∗,1)−1                            (13)                                     Wiley
μ(c),         c > 1                                                                                            Online
for some μ(c) > 0, μ(1+) = +∞. Lastly, we have                                                                                                                                                                                                                Library
on
c→∞R2(0;lim       c) = 0 > limc→1 R2(0; c) = −∞.                (14)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].
See
the
When the prediction model is complex (c > 0), the limiting eigenvalues of                                     Terms
ˆ and   diverge, and this unambiguously reduces the predictive R2 relative                      and
to the infeasible best, R2(0; 0). Intuitively, because the frictionless R2(0; 0) is                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Conditions
ﬁxed, as c increases, the investor must learn the same amount of predictability but spread across many sources, and this dimensionality expansion hinders
statistical inference. The degradation in predictive accuracy due to complexity
can be so severe that expected out-of-sample R2 becomes extremely negative,
particularly in the ridgeless case. Shrinkage can mitigate this and help preserve accuracy amid complexity. Shrinkage controls variance but introduces
bias. Proposition 3 points out that the amount of shrinkage that optimizes
the bias-variance trade-off is z∗= c/b∗.27 More complex settings beneﬁt fromheavier shrinkage, while settings with a higher signal-to-noise ratio (higher                                                                                                                                                                                                                                                                                                                                                                                                               (https://onlinelibrary.wiley.com/terms-and-conditions)
b∗) beneﬁt from lighter shrinkage (see, for example, Hastie et al. (2022)). The               on
WileyE and L are the limiting out-of-sample expected return and leverage of the
timing strategy. Proposition 3 shows that these are the main determinants of                                            Online
out-of-sample R2.                                                                                                                                                                                                                                                                                                                                                                              Library
Figure 1 illustrates the theoretical behavior of the least-squares estimator                      for
rules
derived in Proposition 3. The plots set   to the identity matrix and ﬁx b∗= 0.2               of
use;
OA
27 Note that the optimal shrinkage must be inferred from an estimate of b∗. Our theoretical and                                                           articles
empirical results indicate a general insensitivity of prediction and timing-strategy performance to                      are
the choice of z in the high-complexity regime. As a result, simple shrinkage selection methods like
cross-validation tend to perform well.                                                                                                                                                                                                                                                                                                                                                        governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 18 -->

15406261,
2024,
476                   The Journal of Finance®                                                        1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Figure  1. Expected out-of-sample R2 and norm of least-squares coefﬁcient. This                Of
ﬁgure shows the limiting out-of-sample R2 and ˆβ norm as a function of c and z from Proposition 3 assuming   is the identity matrix and b∗= 0.2. (Color ﬁgure can be viewed at wileyonlineli-                                                                                 Singapore,
brary.com)                                                                                                                                                                                                                                                                                                          Wiley
Online
(recall that σ 2 is normalized to one). The left panel draws the expected out-                                                        Library
onof-sample R2 as a function of model complexity c (shown on the x-axis) and
ridge penalty z (different curves). In this calibration, the infeasible maximumpredictive R2 (that uses the true parameter values) is the dotted red line and                                                                                                         [18/10/2026].
provides a reference point. Throughout the paper, we refer to plots like these,                        Seethe
which describe the model’s performance as a function of model complexity, as                                        Terms
“VoC curves.”                                                                                                                                                                        and
The black line shows the R2 in the ridgeless limit. When c ≤1, the ridgeless                                                                                 Conditionslimit corresponds to exactly z = 0 (i.e., OLS). On this side of c = 1, predictive
accuracy deteriorates rapidly as model complexity increases. This captures the
well-known property that OLS suffers when the number of predictors is large
relative to the number of data points. As c →1, the denominator of the OLS
estimator approaches the singularity, and the expected out-of-sample R2 dives.
To the right of c = 1, the number of predictors exceeds the sample size, and
the “ridgeless” case is deﬁned as the limit as z →0 (i.e., when the least-squares
denominator is calculated via the pseudo-inverse of  ˆ ). Counterintuitively, the
R2 begins to rise as model complexity increases.28                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
The reason is that, while there are many equivalent β solutions that exactly                on
ﬁt29 the training data when c > 1, ridgeless regression selects the solution with                                        Wiley
the smallest norm. As complexity increases, there are more solutions for ridge-                                                Online
less regression to search over, and thus it can ﬁnd smaller and smaller betas                                                        Library
that still exactly ﬁt the training data. This acts as shrinkage, biasing the beta                        for
rulesestimate toward zero. Due to this bias, the forecast variance drops, improv-                of
ing the R2. In other words, despite z →0, the ridgeless solution still regular-                                use;
OA
izes the least-squares estimator, and more so, the larger is c. This property of
articles
are
28 This is an illustration of what the statistics literature refers to as benign overﬁtting.
29 That is, β′St = Rt+1 for all t ∈[1, . . . , T].                                                                                                                                                                                                                                                                                                                        governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 19 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          477               1,
Downloadedridgeless least squares is a newly documented phenomenon in the statistics litfrom
erature and an emerging topic of research.30 It shows that even in very simple
DGPs, one may be able to improve the accuracy of return forecasts by pushing
model dimensionality well beyond sample size.
The remaining curves in Figure 1 show how the out-of-sample R2 is affected
by nontrivial ridge shrinkage. Allowing z > 0 improves R2 except at very low
levels of complexity. This is again a manifestation of the bias-variance tradeoff. When z > 0, the norm of ˆβ is controlled, and the associated variance reduction outweighs the effects of bias when the model is complex.   It is useful to place our analysis thus far in the context of the literature. Some                                                                                                                                                                                                                                                                                                                                                                                                               https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
formulas of Propositions 2 and 3 have been established in papers on random               by
matrix theory (e.g., Ledoit and Péché (2011)). Hastie et al. (2022) prove an                                                           National
analog        of         Proposition                  3 allowing                                   for arbitrary                                     β and                                                expressing                                                                         all                                                                quantities                                                                            in                                                                          Universityterms       of        the             distribution                            of projections                                           of β onto                                            the                                                  eigenvectors                                                                        of                                                                        (see also
Of
Wu and Xu (2020)). Furthermore, they establish nonasymptotic bounds on the
rate of convergence. However, both Hastie et al. (2022) and Wu and Xu (2020)                                                                          Singapore,
require that    is strictly positive deﬁnite. By contrast, in our data analysis,                                     Wiley
we ﬁnd that    is nearly degenerate. Richards, Mourtada, and Rosasco (2021)                                            Online
also allow for more general β structures and   matrices, but require that Xt                                                     Library
be i.i.d. Gaussian and Dobriban and Wager (2018) require Xt be i.i.d. This is               on
clearly not applicable to the RFFs used in our empirical analysis (or any other
nonlinear signal transformations). In contrast to these papers, we establish                                                                                                [18/10/2026].
our results under much weaker conditions on the distribution of Xi,t across i.                      See
This is important for practical applications, where neither the independence of                      the
Terms
Xt nor equality (or boundedness) of their higher moments can be guaranteed.                      and
Lastly, the novel techniques that we develop allow us to characterize the outof-sample performance of misspeciﬁed models. While Hastie et al. (2022) study                                                                          Conditions
misspeciﬁcation in certain stylized examples, we derive more general results
allowing for generic covariance structures. To the best of our knowledge, our
characterization is new in the literature (see Section IV).
Our main theoretical contribution is in the following sections, where we derive portfolio performance properties.


B. Expected Out-of-Sample Market Timing Performance                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
We analyze the behavior of market timing based on the least-squares esti-               on
mate,                                                                                                                                                                                                                                                                                                                 Wiley
Online                                         ˆπt(z) = ˆβ(z)′St.
Library
Formula (12) derives the expected return of this strategy. The following propo-                      for
rules
sition characterizes the expected out-of-sample risk-return trade-off of market               of
timing in the high-complexity regime.                                                                                                                                                     use;
OA
articles
are
30 See Spigler et al. (2019), Belkin et al. (2019), Belkin, Rakhlin, and Tsybakov (2019), Belkin,
Hsu, and Xu (2020), and Hastie et al. (2022).                                                                                                                                                                                                                                                                                                                      governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 20 -->

15406261,
2024,
478                   The Journal of Finance®                                                        1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
Figure 2. Expected out-of-sample risk and return of market timing. This ﬁgure shows the                                                                                 University
limiting out-of-sample expected return and volatility of the market timing strategy as a function                Of
of c and z from Proposition 3 assuming    is the identity matrix and b∗= 0.2. (Color ﬁgure can be                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Singapore,viewed at wileyonlinelibrary.com)
Wiley
Online
PROPOSITION 4: In the limit when P, T →∞, and P/T →c, the limiting sec-
Libraryond moment of the market timing strategy is                                                                   on

V(z; c) := lim E ( ˆπt(z)Rt+1)2| ˆβ = 2(E(z; c))2 + 1 + b∗ψ∗,1 L(z; c)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        [18/10/2026].
in probability, with E and L given in (12). As a result, the Sharpe ratio satisﬁes                        Seethe
Terms
and
E(z; c)             1
SR(z; c) = √    =                                          .            (15)                             V(z; c)                                L(z;c)                                                                                                                                                                                                                     Conditions                                 2 + 1 + b∗ψ∗,1  (E(z;c))2

Furthermore, we have
(i) E(z; c)  is monotone decreasing in z and hence 0 < E(z; c) < E(0, c) <
E(0, 0), and
(ii) SR(z; c) is monotone increasing in z for z < z∗= c/b∗and monotone decreasing in z for z > z∗= c/b∗. Thus, the maximal Sharpe ratio is given by

1              SR(z∗; c) =               < SR(0; 0) ,            (16)                                                                                                                                                                                                                                                                                                                                                                                                                                                    (https://onlinelibrary.wiley.com/terms-and-conditions)
2 + 1 + b∗ψ∗,1  b∗ν(z∗;c)1                                                             on                                                                                                                                                                                                                                                                                                                                         Wiley
where E(0, 0) and SR(0, 0) are the infeasible market-timing expected return and                                                Online
Sharpe ratio from Proposition 1.                                                                                                                                                                                                                                                                                                      Library
for
The left panel of Figure 2 plots the expected out-of-sample return and the                                        rules
right panel plots the expected out-of-sample volatility based on Propositions 3                ofuse;
and 4 using the same calibration as Figure 1. Again, the ridgeless case is in                OA
black. The expected returns of least-squares timing strategies are always posi-                                                                 articles
tive because they are quadratic in beta. When c < 1 (i.e., in the OLS case), the                        are
ridgeless timing strategy achieves the true expected return even though the                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 21 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          479               1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Figure 3. Expected out-of-sample Sharpe ratio of market timing. This ﬁgure shows the               Of
limiting        out-of-sample                   Sharpe                                 ratio                                         of the                                    market                                               timing                                                         strategy                                                              as                                                           a function                                                                                           of                                                                                        c and z                                                                               from
Proposition          3 assuming                                is the                                  identity                                     matrix                                       and                                                                 0.2. (Color                                                            ﬁgure                                                                  can be                                                                         viewed                                                                                          at                                                                                            wi-                                                                          Singapore,                                    b∗=
leyonlinelibrary.com)                                                                                                                                                                                                                                                                        Wiley
Online
corresponding R2 is signiﬁcantly negative in much of this range. The fact that                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Library
the out-of-sample expected return is unimpaired reﬂects the unbiasedness of               on
OLS, while the declining R2 reﬂects the increasing forecast variance as c rises
toward one. The return volatility of the timing strategy is likewise increasing                                                                                                [18/10/2026].
in c for c ∈[0, 1] due to the rising forecast variance and maxes out at c = 1.                             See
When c > 1, the ridgeless expected return begins to deteriorate. This is more                      the
Terms
subtle and is related to the rising R2 discussed above. When model complexity                      and
is  high,        the            multiplicity                           of                           least-squares                                         solutions                                                allows                                                           ridgeless                                                                 regression
to  ﬁnd a        low-norm                  beta                        that                              exactly ﬁts                                       the training                                                      data.                                                             So, even                                                            though                                                                          Conditions
z →0, the ridgeless beta is biased, and the expected return of the strategy
falls. At the same time, the volatility of the strategy falls.
The other expected return and volatility curves show that the bias induced
by a nontrivial ridge penalty eats into the timing strategy even for c < 1. But
the bright side of this attenuation is a reduction in the strategy’s riskiness. For
relatively high shrinkage levels like z = 1, the volatility of the timing strategy drops even below that of the infeasible best strategy while maintaining a
meaningfully positive expected return.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
The net effect of these expected return and volatility behaviors is summa-               on
rized by the market timing strategy’s expected out-of-sample Sharpe ratio,                                     Wiley
given in Proposition 4. The calibrated Sharpe ratio is shown in Figure 3. Recall                                            Online
that the buy-and-hold Sharpe ratio is normalized to zero. The key implication                                                    Library
of Proposition 4 is that despite the sometimes massively negative predictive                      for
R2, the ridgeless Sharpe ratio is everywhere positive, even for extreme levels                                     rules
of model complexity. At c = 1, the Sharpe ratio drops to near zero, not because               ofuse;
the strategy is unproﬁtable (it remains maximally proﬁtable in an expected               OA
return sense) but because its volatility explodes.                                                                                                                                                                                                                                            articles
Another interesting aspect of Figure 3 is that the Sharpe ratio beneﬁts from                      are
nontrivial ridge shrinkage regardless of model complexity. Shrinkage is most                                                           governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 22 -->

15406261,
2024,
480                   The Journal of Finance®                                                        1,
Downloadedvaluable near c = 1, where it reins in volatility substantially more than it refrom
duces expected return. At both low levels of complexity (c ≈0) and high levels
of complexity (c >> 1), the Sharpe ratio is relatively insensitive to z.
Proposition 4 also implies that when the model is correctly speciﬁed, the
shrinkage that optimizes the expected out-of-sample R2 also optimizes the
Sharpe ratio. This is convenient because it means that one can focus on tuning
the prediction model and be conﬁdent that the tuned z will optimize timing
performance. Two caveats, however, are in order. The ﬁrst is that this statement applies to the Sharpe ratio, so if investors judge their performance withother criteria, then other levels of shrinkage may be optimal. For example,                                                                                                                                                                                                                                                                                                                                                                                                                                                    https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
a risk-neutral investor prefers ridgeless regression despite its comparatively                by
poor performance in R2. Second, this statement requires correct speciﬁcation.                                                                 National
If  the      empirical model                            is misspeciﬁed,                                     the                                        optimal                                         amount                                                                    of shrinkage                                                                can
or                                                                                 Universitydiffer     depending              on whether                           the objective                                                   is                                               to maximize                                                        out-of-sample                                                           R2
Of
the Sharpe ratio.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     Singapore,
WileyC. A Note on R2
Online
At this point, we already see that a timing strategy with negative R2                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Library
can have high average out-of-sample returns and thus positive out-of-sample                on
Sharpe ratios.31 More plainly, the positivity of out-of-sample R2 is not a necessary condition for an economically valuable timing strategy. The least-squares                                                                                                         [18/10/2026].
timing strategies in our framework all have strictly positive out-of-sample ex-                        See
pected return and Sharpe ratio regardless of shrinkage or model complexity                        the
Terms
(despite having enormously negative R2 in many cases).                                                                         and
This is        an            important                        contrast                               versus                                      the mapping                                               from                                                  R2 to                                                              the                                                                 timing
Sharpe        ratio            proposed                    by                      Campbell                             and Thompson                                                     (2008),                                                  which                                                                               is                                                       an                                                                           often-                                                                                 Conditions
used heuristic for interpreting the economic beneﬁts of a predictive R2. Their
mapping is population mapping, meaning that it corresponds to the special
case of an analyst using a correctly speciﬁed model with c = 0 (i.e., inﬁnitely
more data than parameters). In contrast, our analysis characterizes expected
out-of-sample R2 and Sharpe ratios for generic c, even with misspeciﬁed models (see Section IV).
Out-of-sample R2 and Sharpe ratio measurements serve different purposes.
The R2 helps evaluate forecast accuracy, while the Sharpe ratio is appropri-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
ate for evaluating the economic value of forecasts in asset allocation contexts.                on
Much of the empirical literature on return prediction and market timing fo-                                        Wiley
cuses its evaluations on out-of-sample predictive R2 (see, for example, Goyal                                                Online
and Welch (2008)). Proposition 4 ensures that we can worry less about the                                                        Library
for
rules
31 To see this in a simple example, consider a model with one predictor and imagine estimating                of                                                                                                                                                                                                                                                                        use;
a predictive coefﬁcient that happens to be a large scalar multiple of the truth. In this case, the                OA
R2 will be pushed negative, but the predictions will be perfectly correlated with the true expected                                                                 articles
return. Thus, the expected return of the timing strategy will be positive. Furthermore, because the                        are
Sharpe ratio is independent of scale effects, this timing strategy will equal the actual Sharpe ratio
of the DGP.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 23 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          481               1,
Downloadedpositivity of out-of-sample R2 from a prediction model and focus more on the
from
out-of-sample performance of timing strategies based on those predictions.


## IV. Machine Learning and Model Misspeciﬁcation

So far we have studied the behavior of machine learning portfolios as a function of the complexity of the true DGP while assuming we have the correctly
speciﬁed model. Under correct speciﬁcation, the complexity comparative statics in Figures 1 to 3 change both the empirical and the true model as we varyc, and thus, these theoretical comparative statics cannot be taken to the data.                                                                                                                                                                                                                                                                                                                                                                                                               https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
Nevertheless, theory grounded on correct model speciﬁcation is powerful for               by
developing a conceptual understanding of machine learning portfolios.                                                                                                         National
A more empirically relevant theoretical setting would consider a single true                                                                          University
DGP. It would then consider empirical models that are always a misspeciﬁed               Of
approximation                to this                  DGP.                               Finally,                                                 it would                                  make                                               comparisons                                                        by
increas-                                                                          Singapore,ing the complexity                     of the                         empirical                              model                                            to achieve                                          an                                                       increasingly                                                                 accurate
approximation of the true DGP. We develop this theory now.                                                                                                        Wiley
We consider a true DGP with P predictors. We consider an expanding                                            Online
set of empirical models to approximate the DGP. Each model is indexed by                                                    Library
P1 = 1, . . . , P and corresponds to an economic agent observing only a subset of               on
the signals, S(1)t = (Si,t)P1i=1. We use S(2)t = (Si,t)Pi=P1+1 to denote the remainingunobserved signals. The signal covariance matrix corresponding to this parti-                                                                                                [18/10/2026].
tion is                                                                                                                                                                                      See
the
Terms
=     1,1′      1,2   .                                                                                          and
1,2   2,2                                                                                                                                                                                                                                                                                                                               Conditions
Naturally, misspeciﬁed estimator behavior depends on the correlation structure of observed and unobserved signals captured by the off-diagonal blocks of
.
We make the following technical assumption, which ensures that estimators
in the machine learning regime have well-behaved limits.

ASSUMPTION 5: For any sequence P1 →∞such that P1/P = q > 0, the eigenvalue distribution of the matrix   1,1 converges to a nonrandom probability dis-tribution H(x; q). We say that signals are sufﬁciently mixed if H(x; q) is inde-                                                                                                                                                                                                                                                                                                                                                                                                               (https://onlinelibrary.wiley.com/terms-and-conditions)
pendent of q. We also use                                                                                              on                                                                                                                                                                                                                                                                                                                                      Wiley
k                                                                                                                                                                                          Online
1  tr(  1,1) k ≥1,                        ψ∗,k(q) = P1→∞P−1lim                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Library
for
to denote asymptotic moments of the eigenvalues of   1,1.                                                                                                                        rulesof
use;
In a misspeciﬁed model, the (regularized) least-squares estimator is                           OA
articles
−1 1                                                                                                          are
ˆβ(z; q) =  zI + ˆ 1,1           S(1)t  Rt+1 ∈RP1 ,
T                                                                               t                                                                                                                                                                                                                                                                           governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 24 -->

15406261,
2024,
482                   The Journal of Finance®                                                        1,
Downloadedwhere
from
ˆ 1,1 = T−1     S(1)t  (S(1)t   )′ ∈RP1×P1 .
t

We also introduce the following auxiliary objects:

1,2  1,2]′  ≥0,        (17)              ξ2,1(z; cq; q) = T→∞T−1trlim       E[(zI + ˆ 1,1)−1

1,2  1,2]′  ≥0 .    ξ2,1(z; cq; q) = T→∞T−1trlim       E[(zI + ˆ 1,1)−1  1,1(zI + ˆ 1,1)−1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
The quantities in (17) account for covariances between observed and unob-                                                                 National
served signals. While the existence of the limits in (17) cannot be guaranteed
in general, the expectations are uniformly bounded for z > 0 (as the   matrices                                                                                 University
are uniformly bounded for z > 0). Hence, by passing to a subsequence of T, P,                Of
we can always assume that the limits in (17) exist. In the Internet Appendix,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Singapore,
we show that these limits actually exist for a class of correlation structures.                                                                                                                                                                                                                                                                                                                                         Wiley
With the additional assumptions for the misspeciﬁed setting in place, we
Online
have the following analog of Propositions 2, 3, and 4.
Library
onPROPOSITION 5: In the limit T, P, P1 →∞, P/T →c, and P1/P →q ∈(0, 1],

1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        [18/10/2026].                 lim    tr((zI + ˆ 1,1)−1  1,1) →ξ(z; cq; q)
T→∞ T                                                                                                                                              See
the
in probability, where                                                                                                                                                                                                                                                             Terms
and

1 −zm(−z; cq; q)                     ξ(z; cq; q) =                                                                                                                                                                                                                                                                                                                                                                                                                                        Conditions
(cq)−1 −1 + zm(−z; cq; q)

and

m(−z; cq; q) = lim P−11  tr((zI + ˆ 1,1)−1) .

Furthermore,

ν(z; cq; q) = ψ∗,1(q) −(qc)−1zξ(z; cq; q) > 0,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
ν′(z; cq; q) = −(qc)−1(ξ(z; cq; q) + zξ ′(z; cq; q)) < 0,                                   on                                                                                                                                                                                                                                                                                                                                         Wiley
ˆν(z; cq; q) = ν(z; cq; q) + zν′(z; cq; q) > 0 .                                                                                                                                                      Online
Library
In addition, we have                                                                                                                                                        for
rules
(i) The expected return on the market timing strategy converges in proba-                ofuse;
bility to                                                                                                              OA
articles
(cq)−1ξ2,1(z; cq; q)                                   are
E(z; cq; q) := lim E[ ˆπt(z)Rt+1|ˆβ] = b∗q  ν(z; cq; q) +                                  .                                                      1 + ξ(z; cq; q)                                                                                                          governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 25 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          483               1,
Downloaded    (ii) Expected leverage converges in probability to
from
L(z; cq; q) : = lim E[ ˆπt(z)2| ˆβ] = q b∗ˆν(z; cq; q)
−c(1 + b∗[ψ∗,1(1) −qψ∗,1(q)])ν′(z; cq; q) +   (z; cq; q),

where

(qc)−1 ξ2,1(z; cq; q) + 2(1 + ξ(z; cq; q))ν′(z; cq; q)ξ2,1(z; cq; q)
(z; cq; q) = b∗                                                                                                      .
(1 + ξ(z; cq; q))2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
(iii) R2 converges in probability to                                                                             by
National                                      2E(z; cq; q) −L(z; cq; q)
R2(z; cq; q) =                                         .             (18)                                   1 + b∗ψ∗,1(1)                                                                                                                                                                                                                                                    University
Of
(iv) The second moment of the market timing strategy converges in probabil-                                                                          Singapore,
ity to                                                                                                                                                                                                                                                                                          Wiley
Online
V(z; cq; q) := lim E  ( ˆπt(z)Rt+1)2 = 2(E(z; cq; q))2 + 1 + b∗ψ∗,1 L(z; cq; q) .
Library
on
(v) And, as a result, the Sharpe ratio satisﬁes                                                                                                                                                                                                                                                                                                                                                                                            [18/10/2026].                                E(z; cq; q)              1
SR(z; cq; q) =        =                                             .                                       See
V(z; cq; q)    2 + 1 + b∗ψ∗,1  (E(z;cq;q))2L(z;cq;q)                                            theTerms
and
In     general,             the                 behavior                              of the                                 quantities                                             in Proposition                                                  5 depends
in com-                                                                          Conditionsplex     fashion           on              the                    correlations                           between                                      observable                                         and unobservable                                                                          signals,
as captured by the quantities (17). When both quantities (17) are zero, the expressions simplify signiﬁcantly. It is straightforward to show that both quantities in (17) are zero if the matrices   1,2,   2,1 have uniformly bounded traces.
For example, this is when    1,2 has a ﬁnite, uniformly bounded rank when
P, P1 →∞(due to, say, a ﬁnite-dimensional factor structure in the signals).
We thus obtain the following result.

PROPOSITION 6: Suppose that tr(  1,2  2,1) = o(P).32 Then, ξ2,1 = ξ2,1 = 0. Fur-thermore,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       (https://onlinelibrary.wiley.com/terms-and-conditions)
(i)  E(z; cq; q)  is monotone decreasing  in  z and hence 0 < E(z; cq; q) <               on
Wiley
E(0; cq; q) < E(0, 0; 0).
Online   (ii) Both R2(z; cq; q) and SR(z; cq; q) are monotone increasing in z for z < z∗=
c(1 + b∗(ψ∗,1(1) −qψ∗,1(q)))/b∗and monotone decreasing in z for z > z∗.                                                                                          Library
(iii) And in the ridgeless limit as z →0, we have                                                                                     for                                                                                                                                                                                                                                                                                                                                      rules
of
use;
32 This is the case, for example, when  P = DP + QP, where lim supP→∞rankQP < ∞, while DP               OA
are diagonal matrices and DP, QP are uniformly bounded. In this case, we can replace  P with DP                                                            articles
in all expressions. Perhaps more tangibly, this condition obtains when the signals satisfy a ﬁnite-                      are
dimensional factor structure. Furthermore, if the signals have similar idiosyncratic variance, they
satisfy the necessary mixing condition.                                                                                                                                                                                                                                                                                                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 26 -->

15406261,
2024,
484                   The Journal of Finance®                                                        1,
Downloaded
from
E(0; cq; q) = b∗q (ψ∗,1(q) −(cq)−2m∗(cq; q)−1 1q>1/c),

((cq)−1 −1)−1,  q < 1/c
L(0; cq; q) = E(0; cq; q) + (1 + b∗(ψ∗,1(1) −qψ∗,1(q)))
˜μ(cq; q),       q > 1/c,

V(0; cq; q) = 2(E(0; cq; q))2 + 1 + b∗ψ∗,1 L(0; cq; q),

E(0; cq; q)                      SR(0; cq; q) =                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
V(0; cq; q)                                                       by
National
for some m∗(cq; q) > 0 and some ˜μ(cq; q) < 0 with ˜μ(1+; c) = −∞. In particular, if    is proportional to the identity matrix,  = ψ∗,1 I, then                                                                                                                                                                                                              University
Of
E(0; cq; q) = b∗ψ∗,1 min{q, c−1}                     (19)                                                                                 Singapore,
Wileyis constant for q > 1/c.
Online
The comparative statics of Section III.B highlight how, even when the empir-                                                        Library
ical model is correctly speciﬁed, complexity hinders the model’s ability to hone                on
in on the true DGP because there is not enough data to support the model’s
heavy parameterization. That analysis shows that when models are correctly                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        [18/10/2026].
speciﬁed, the best performance (in terms of R2 and Sharpe ratio) comes from                        See
simple models. Naturally, a small correctly speciﬁed model will converge on                        the
Termsthe truth faster than a large correctly speciﬁed model. But this is not a very                                                                                                                                                                                                      and
helpful comparison.
The fundamental difference in this section is that while raising cq brings the                                                                                 Conditions
usual statistical challenges of heavy parameterization without much data, the
added complexity also brings the beneﬁt of improving the empirical model’s
approximation of the true DGP. A simple model will tend to suffer from poor
approximation and thus fare poorly in terms of both statistical metrics like
R2 and portfolio metrics like the expected return and Sharpe ratio. Thus, our
misspeciﬁcation analysis tackles the most important question about high complexity: Does the improvement in approximation justify the statistical cost of
heavy parameterization when it comes to out-of-sample forecast and portfolio                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)performance? The answer is yes, as established by the following theorem.                       on
WileyTHEOREM 1 (Virtue of Complexity): Suppose that signals are sufﬁciently mixed
Online(so that H(x; q) does not depend on q) and tr(  1,2  2,1) = o(P). Then, with
the optimal amount of shrinkage z∗, the Sharpe ratio SR(z∗(q; c); cq; q) and                                                        Library
R2(z∗(q; c); cq; q) are strictly monotone increasing and concave in q ∈[0, 1].                                for
rules
Figures 4, 5, and 6 illustrate the behavior of misspeciﬁed machine learn-                ofuse;
ing predictions and portfolios derived in Proposition 5. In this calibration, the                OA
true unknown DGP is assumed to have a complexity of c = 10. We continue to                                                                articles
calibrate   as identity and b∗= 0.2. We analyze the behavior of approximat-                        are
ing empirical models that range in complexity from very simple (cq ≈0 and                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 27 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          485               1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Figure 4. Expected out-of-sample prediction accuracy from misspeciﬁed models. This               Of
ﬁgure shows the limiting out-of-sample R2 and ˆβ norm as a function of c and z from Proposition 6
assuming    is the identity matrix, b∗= 0.2, and the complexity of the true model is c = 10. (Color                                                                          Singapore,
ﬁgure can be viewed at wileyonlinelibrary.com)                                                                                                                                                                                           Wiley
Online
Library
on
[18/10/2026].
See
the
Terms
and
Conditions





Figure  5. Expected out-of-sample risk and return from misspeciﬁed models. This
ﬁgure shows the limiting out-of-sample expected return and volatility of the market timing strategy as a function of c and z from Proposition 6 assuming    is the identity matrix, b∗= 0.2, and
the complexity of the true model is c = 10. (Color ﬁgure can be viewed at wileyonlinelibrary.com)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
on
Wiley
thus severely misspeciﬁed) to highly complex (q = 1, cq = 10 and thus cor-                                            Online
rectly speciﬁed). The left panel of Figure 4 shows the expected out-of-sample                                                    Library
R2. The cost of misspeciﬁcation for low c is seen as a shift downward in the R2                      for
relative to Figure 1. The challenges of model complexity highlighted in previ-                                     rules
ous sections play an important role here as well. Intermediate levels of com-               ofuse;
plexity (cq ≈1) dilate the size of beta estimates (Figure 4, right panel), driving               OA
down the R2 and inﬂating portfolio volatility (Figure 5, right panel). These                                                           articles
effects abate once again for cq > 1 due to the implicit regularization of high-                      are
complexity ridgeless regression, just as in the earlier analysis. More generally,                                                           governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 28 -->

15406261,
2024,
486                   The Journal of Finance®                                                        1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
Figure  6. Expected  out-of-sample Sharpe  ratio from  misspeciﬁed  models.  This                                                                                 University
ﬁgure shows the limiting out-of-sample Sharpe ratio of the market timing strategy as a func-                Of
tion of c and z from Proposition 6 assuming    is the identity matrix, b∗= 0.2, and the complexity                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Singapore,
of the true model is c = 10. (Color ﬁgure can be viewed at wileyonlinelibrary.com)
Wiley
Online
the patterns for R2, ˆβ norm, and portfolio volatility share similar qualitative                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Library
patterns as those in Figure 1.                                                                                        on
The most important difference compared to Figure 1 is the pattern for the
out-of-sample expected return of the market timing strategy (Figure 5, left                                                                                                         [18/10/2026].
panel). Expected returns are now low for simple strategies due to their poor ap-                        See
proximation of the DGP. Increasing model complexity monotonically increases                        the
Terms
expected timing returns. In the ridgeless case, the beneﬁt of added complexity                        and
when                                                  cq                                 = 1. A surprisingreaches          its        maximum                         of E(0; 1;                                c−1) =                                       b∗ψ∗,1c−1
fact                                                                                 Conditionsis that the           ridgeless                   expected                            return                                            is                                       exactly ﬂat                                              as                                                  complexity                                                                     rises beyond
cq = 1, in which case the beneﬁts of incremental improvements in DGP approximation are exactly offset by the gradually rising bias of ridgeless shrinkage;
see formula (19).
This new fact that the expected return rises monotonically with model complexity in the misspeciﬁed setting induces a similar pattern in the out-ofsample Sharpe ratio, shown in Figure 6. Rather than decreasing in complexity
as we saw in the correctly speciﬁed setting, the expected return improvement
from additional complexity leads the Sharpe ratio to also increase with com-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
plexity. Consistent with Theorem 1, this is particularly true with nontrivial                on
ridge shrinkage but is even true in the ridgeless case as long as cq is sufﬁ-                                        Wiley
ciently far from unity. In summary, in the realistic case of misspeciﬁed em-                                                Online
pirical models, complexity is a virtue. It improves the expected out-of-sample                                                        Library
market timing performance in terms of both expected return and Sharpe ratio.                        for
It is instructive to compare our ﬁndings with the phenomenon of double de-                                        rules
scent, where by absent regularization, out-of-sample MSE has a nonmonotonic                ofuse;
pattern in model complexity (Belkin et al. (2019), Hastie et al. (2022)). The mir-                OA
ror image of double descent in MSE is the “double ascent” behavior of the ridge-                                                                 articles
less Sharpe ratio (Figure 6). As Theorem 1 shows, Sharpe ratio double ascent                        are
is an artifact of insufﬁcient shrinkage. With the right amount of shrinkage,                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 29 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          487               1,
Downloadedcomplexity becomes a virtue even in the low-complexity regime (when cq < 1):
from
The hump disappears, and “double ascent” turns into “permanent ascent.”


## V. Virtue of Complexity: Empirical Evidence From Market Timing

In this section, we present empirical analyses that are direct empirical
analogs to the theoretical comparative statics for misspeciﬁed models in Section IV.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
A. Data                                                                                                                       by
Our empirical investigation centers on a cornerstone of empirical asset pric-                                                           National
ing   research—forecasting                        the                           aggregate                                       stock                                      market                                                     return.                                                   To make                                                                 the                                                                        con-                                                                          Universityclusions       from this analysis                         as                           easy to digest                                         as                                                  possible,                                         we perform                                                             our                                                                       anal-
Of
ysis in a conventional setting with conventional data. Our forecast target is
the monthly excess return of the CRSP value-weighted index. The information                                                                          Singapore,
set we use for prediction consists of the 15 predictor variables from Goyal and                                     Wiley
Welch (2008) available monthly over the sample from 1926 to 2020.33                                                                                    Online
We volatility-standardize returns and predictors using backward-looking                                                    Library
standard deviations that preserve the out-of-sample nature of our forecasts.               on
Returns are standardized by their trailing 12-month return standard deviation
(to capture their comparatively fast-moving conditional volatility).34 In con-                                                                                                [18/10/2026].
trast, predictors are standardized using an expanding window historical stan-                      See
dard deviation (given the much higher persistence of most predictors). We re-                      the
Terms
quire 36 months of data to ensure enough stability in our initial predictor stan-                      and
dardization, so the ﬁnal sample we bring to our analysis began in 1930. We perform this standardization to align the empirical analysis with our homoskedas-                                                                          Conditions
tic theoretical setting. Our results are insensitive to this step—none of our
ﬁndings are sensitive to variations in how standardizations are implemented.


### B. Random Fourier Features

We seek models that take the form of equation (3).35 To evaluate our theory,
we also seek a framework that will allow us to smoothly transition from low-   33                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 (https://onlinelibrary.wiley.com/terms-and-conditions)
This list includes (using mnemonics from their paper): dfy, inﬂ, svar, de, lty, tms, tbl, dfr, dp,               on
dy, ltr, ep, b/m, and ntis, as well as one lag of the market return. Most of these variables are based                                     Wiley
on market prices and are available at month end. Our date convention for inﬂation is that used by
Goyal, Welch, and Zaﬁrov (2023) and the data set graciously provided by Amit Goyal. Note that                                            Online
while inﬂation for month t is typically reported two weeks into month t + 1, the Goyal, Welch, and                                                    Library
Zaﬁrov (2023) date convention views the price data upon which the ofﬁcial inﬂation statistic is                      for
based as part of the time t information set. We show in Internet Appendix Figure IA12 and Table                                     rules
IA2 that our results are essentially unchanged if we exclude inﬂation from our analysis.                          of                                                                                                                                                                                                                                                                     use;
34 For returns, we calculate standard deviation from the uncentered second moment due to the               OA
noisiness           of estimating mean monthly returns in short windows.                                                                                                                                                                                                                        articles   35
As in equation (3), we exclude the intercept from our regressions. If we include a constant as                      are
an additional regressor in our high complexity regressions, the associated intercept is shrunken
so heavily that it has no effect on the results reported in Table I.                                                                                                                                                                                                                        governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 30 -->

15406261,
2024,
488                   The Journal of Finance®                                                        1,
Downloadedcomplexity models to high-complexity models. To do so, we adopt an inﬂuential
from
methodology from the machine learning literature known as RFF (Rahimi and
Recht (2007), Rahimi and Recht (2008)).36 Let Gt denote our 15 × 1 vector of
predictors. The RFF methodology converts Gt into a pair of new signals,

Si,t = sin(γ ω′iGt), cos(γ ω′iGt) ′,   ωi ∼i.i.d.N(0, I),          (20)

where  Si,t uses the vector ωi to form a random linear combination of Gt,
which is then fed through the trigonometric functions.37 The advantage ofRFF is that for a ﬁxed set of input data, Gt, we can create an arbitrar-                                                                                                                                                                                                                                                                                                                                                                                                                                                    https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
ily large (or small) set of features based on the information in Gt through                by
the nonlinear transformation in (20). If one desires a very low-dimensional                                                                 National
model in (3), say P = 2, one can generate a single pair of RFFs. For a very                                                                                 University
high-dimensional model, say P = 10,000, one can instead draw many random                Of
The                                       larger the                                      number                                                                 of random                                                                       features,weight       vectors                 ωi, i = 1, . . . , 5,000.
the    richer          the approximation                             that (3)                                    provides                                                 to                                              the general                                                              functional                                                               form                                                                                 Singapore,
E[Rt+1|Gt] = f (Gt), where  f is some smooth nonlinear function. Indeed, the                                        Wiley
RFF approach is a wide two-layer neural network with ﬁxed weights in the                                                Online
ﬁrst layer (in the form of ωi) and optimized weights in the second layer (in the                                                        Library
form of the regression estimates for β).                                                                          on
[18/10/2026].
C. Out-of-Sample Performance                                                                                                                                  See
the
To conduct the empirical analogue of the theoretical analysis in Figures 4,                                        Terms
5, and 6, we consider one-year, ﬁve-year, and 10-year rolling training windows                        and
(T  = 12,         60,             or 120)                 and                     a                           large set                                          of RFFs (as                                             high                                                  as                                         P                                    = 12,000).                                                             These                                                                                 Conditionschoices       are           guided                 by                    our                           desire                                   to investigate                                             the                                                       role                                                                of                                                  model                                                                  complexity,
deﬁned in the empirical analysis as c = P/T. The advantages of short training
samples like T = 12 are (i) we can reach extreme levels of model complexity
with smaller P and thus less computing burden and (ii) it shows that the virtue
of complexity can be enjoyed in small samples. But none of our conclusions are
sensitive to this choice as we document all of the same patterns for training
windows of T = 60 and 120.   36                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     (https://onlinelibrary.wiley.com/terms-and-conditions)
Rahimi and Recht (2007) describe how RFF approximation accuracy improves as one in-                on
creases the level of model complexity. In the limit of zero complexity (P, T →∞, P/T →0), RFF                                        Wiley
regression approximates any sufﬁciently smooth nonlinear function arbitrarily well. Subsequent
papers (see, for example, Rudi and Rosasco (2017)) further characterize rates of convergence. The                                                Online
case of nonzero complexity is less well understood. Recent results (Mei and Montanari (2022),                                                        Library
Mei, Misiakiewicz, and Montanari (2022), Ghorbani et al. (2020)) show that, for nonzero complex-                        for
ity, random features methods cannot learn the true function and only learn its projection on a                                        rules
speciﬁc functional subspace.                                                                                                  of                                                                                                                                                                                                                                                                        use;
37 The parameter γ controls the Gaussian kernel bandwidth in the generation of RFFs. Ran-                OA
dom features can be generated in several ways (for a survey, see Liu et al. (2021)). Our choice of                                                                 articles
functional form in (20) is guided by Sutherland and Schneider (2015), who document tighter error                        are
bounds for this functional approximation relative to some alternative random feature formulations. We ﬁnd, however, that our results are insensitive to using other random feature schemes.                                                                          governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 31 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          489               1,
Downloaded  To draw “VoC curves” along the lines of Figures 4, 5, and 6, we estimate a sefrom
quence of out-of-sample predictions and trading strategies for various degrees
of model complexity, ranging from P = 2 to P = 12,000, and various degrees of
ridge shrinkage, ranging from log10(z) = −3, . . . , 3. One repetition of our analysis proceeds as follows:

(i) Generate 12,000 RFFs according to (20) with bandwidth parameter γ .38
(ii) Fix a model deﬁned by the number of features P ∈{2, . . . , 12,000} and
ridge shrinkage parameter log10(z) ∈{−3, . . . , 3}. The set of predictors       St for regression (3) corresponds to the ﬁrst P RFFs from (i).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
(iii) Given the model in (ii), and ﬁxing a training window T ∈{12, 60, 120},               by
conduct a recursive out-of-sample prediction and market timing strat-                                                           National
egy. For              each                            t ∈{T,                                                . . . , 1,091},                                     estimate                                                         (3)                                                 using                                                           training                                                                  observa-
)}.39 Then,                                            from                                                    the                                                       estimated                                                                       regres-                                                                          University       tions             {(Rt,                  St−1),                                       . . . , (Rt−T+1,                                  St−T
sion coefﬁcient, construct out-of-sample return forecast ˆβ′St and timing               Of
strategy return ˆβ′StRt+1.                                                                                                                                                                                                                                                                                                                                                                                                                                 Singapore,
(iv) From the sequence of out-of-sample predictions and strategy returns                                     Wiley
in (iii), calculate the average ∥ˆβ∥2 across training samples, the out-of-                                                                                                                                                                                                                                                                                                                                                                                                       Online
sample R2, and the out-of-sample average return, volatility, and Sharpe
Library       ratio of the timing strategy.40                                                                             on

The inherent randomness of RFFs means that estimates of out-of-sample per-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].formance tend to be noisy for models with low P. We therefore repeat the anal-
See
ysis steps from (i) to (iv) 1,000 times with independent draws of the RFFs, and                      the
then average the performance statistics across repetitions.                                                                                                             Terms
The VoC curves in Figures 7 and 8 plot out-of-sample prediction and market                      and
timing performance as a function of model complexity and ridge shrinkage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Conditions
for the case T = 12. The wide range of complexity that we consider (e.g., c ∈
[0, 1000] when T = 12) can make it difﬁcult to read plots. To better visualize
the results while emphasizing both behaviors near the interpolation boundary
and behavior for extreme complexity, we break the x-axis at an intermediate
value of c.
The ﬁrst conclusion from these ﬁgures is that the out-of-sample empirical
behavior of machine learning predictions is a strikingly close match to the VoC
curves predicted by our theory. In particular, compare the empirical results ofFigure 7 to the theoretical results under model misspeciﬁcation from Figure 4.                                                                                                                                                                                                                                                                                                                                                                                                               (https://onlinelibrary.wiley.com/terms-and-conditions)
The beta estimates and out-of-sample R2 demonstrate explosiveness at the in-               on
Wiley
terpolation boundary and recovery in the high-complexity regime. Figures IA1
Onlineand IA2 (reported in the Internet Appendix in the interest of space) document
identical patterns for training windows of 60 and 120 months.                                                                                                                                       Library
for
rules
38 We set γ = 2. Our results are generally insensitive to γ , as discussed in Section V.F.                         of                                                                                                                                                                                                                                                                     use;
39 Prior to estimation, we volatility-standardize the training sample RFFs {St−1, . . . , St−T} and               OA
out-of-sample          RFFs St by their standard deviations in the training sample.                                                                                                                                                                      articles   40
Our empirical R2 calculation is one minus the ratio of out-of-sample forecast error variance to                      are
out-of-sample realized return variance. Our empirical Sharpe ratio calculation uses the centered
standard deviation in the denominator.                                                                                                                                                                                                                                                                                                                                                governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 32 -->

15406261,
2024,
490                   The Journal of Finance®                                                        1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Of
Singapore,
Wiley
Online
Library
on
[18/10/2026].
See
the
Terms
and

Figure 7. Out-of-sample market timing performance (T = 12). This ﬁgure shows the out-of-sample prediction accuracy and portfolio performance estimates for the empirical analysis de-                                                                                 Conditions
scribed in Section V.C. The training window is T = 12 months and RFF count P (or cT) ranges
from 2 to 12,000 with γ = 2. (Color ﬁgure can be viewed at wileyonlinelibrary.com)



Extreme behavior at the interpolation boundary makes it difﬁcult to fully appreciate the patterns in R2. Figure IA3 in the Internet Appendix provides more
detail by plotting the out-of-sample R2 zooming-in on the range [−10%, 1%].
Here, we see more clearly that high complexity and regularization together                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)produce a positive out-of-sample R2. In this plot, regularization comes in two                on
forms, both directly through higher z and more subtly through higher c (which                                        Wiley
allows ridgeless regression to ﬁnd solutions with small ˆβ norm). For large z,                                                Online
the R2 is almost everywhere positive for all training windows.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Library
The most intriguing aspect of Figure 7 is the clear increasing pattern in                        for
out-of-sample expected returns as model complexity rises. For z = 10−3, which                                        rules
roughly approximates the ridgeless case, we see a nearly linear upward trend                ofuse;
in average returns as c rises from zero to one. Beyond c = 1, the ridgeless                OA
expected return is nearly ﬂat, just as predicted by equation (19) in Propo-                                                                 articles
sition 6. For higher levels of ridge shrinkage, the rise in expected return                        are
is more gradual and continues into the range of extreme model complexity.                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 33 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          491               1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Of
Singapore,
Wiley
Online
Library
on
[18/10/2026].
See
the
Terms
and
Figure 8. Out-of-sample market timing performance (T = 12). This ﬁgure shows the outof-sample prediction accuracy and portfolio performance estimates for the empirical analysis de-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Conditions
scribed in Section V.C. The training window is T = 12 months and RFF count P (or cT) ranges from
2 to 12,000 with γ = 2. Alphas are versus a static position in the volatility-standardized market
portfolio. (Color ﬁgure can be viewed at wileyonlinelibrary.com)



Internet Appendix Figures IA1 and IA2 again document an identical expected
return pattern for longer training windows.
The increasing pattern in out-of-sample expected return and the decreasing
pattern in volatility above c = 1 translate into a generally increasing pattern                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
in the out-of-sample market-timing Sharpe ratio, shown in Figure 8. The ex-               on
ception is a brief dip near c = 1 at low levels of regularization as the spike in                                     Wiley
variance compresses the Sharpe ratio. For high complexity, the Sharpe ratio                                            Online
generally exceeds 0.4.                                                                                                                                                                                                                                                                                                                                                       Library
In our theoretical setting, we normalize the expected return of the untimed                      for
asset to zero. This is not the case of course for the U.S. market return. There-                                     rules
fore, to adjust for buy-and-hold market exposure, we calculate the out-of-               ofuse;
sample alpha, alpha t-statistic, and information ratio (IR) of the timing strat-               OA
egy return via time-series regression on the untimed market. Figure 8 shows                                                           articles
that the market timing alpha and IR inherit the same patterns as the average                      are
return and Sharpe ratio. In the high-complexity regime, we ﬁnd IRs around                                                           governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 34 -->

15406261,
2024,
492                   The Journal of Finance®                                                        1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Of
Singapore,
Wiley
Online
Library
on
[18/10/2026].
See
the
Terms
and
Figure 9. Out-of-sample market timing performance (T = 60, 120). This ﬁgure shows the
out-of-sample prediction accuracy and portfolio performance estimates for the empirical analy-                                                                                 Conditions
sis described in Section V.C. The training window is T = 60 or 120 months and RFF count P
(or cT) ranges from 2 to 12,000 with γ = 2. Alphas are versus a static position in the volatilitystandardized market portfolio. (Color ﬁgure can be viewed at wileyonlinelibrary.com)


0.3 and signiﬁcant alpha t-statistics ranging from 2.6 to 2.9 depending on the
amount of ridge shrinkage. Figure 9 repeats this analysis for training windows of 60 and 120 months, where we ﬁnd similar IRs of roughly 0.25 with
t-statistics above 2.0 for high-complexity models.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        (https://onlinelibrary.wiley.com/terms-and-conditions)  What do market timing strategies look like in the high-complexity regime?                on
Figure 10 plots ˆπ(z, c) for the highest complexity and shrinkage conﬁgurations                                        Wiley
of our empirical model (P = 12,000 and z = 103, averaged across 1,000 sets of                                                                                                                                                                                                                                                                                                                                                                                                            Online
random feature weights). The three lines correspond to training windows of 12,
Library
60, and 120 months. Positions show the same patterns for all training windows;                        for
their time-series correlations are 90% (T = 12 with T = 60), 87% (T = 12 with                                        rules
T = 120), and 97% (T = 60 with T = 120).41 The plot shows six-month moving                ofuse;
OA
41                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          articles
While the time-series patterns in positions are the same for all training windows, the scale                        are
of positions is smaller for longer training windows. This is because the “leverage” of a strategy is
driven by the norm of beta, and this is typically smaller for larger T.                                                                                                                                                                                                          governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 35 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          493               1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Of
Singapore,
Wiley
Online
Figure 10. Market timing positions. This ﬁgure shows the out-of-sample prediction accuracy
and portfolio performance estimates for the empirical analysis described in Section V.C. The train-                                                    Library
ing window is T = 12, 60, or 120 months with P = 12,000, z = 103, and γ = 2. Positions are av-               on
eraged across 1,000 sets of random feature weights. Plots show the six-month moving average of
positions to improve readability. (Color ﬁgure can be viewed at wileyonlinelibrary.com)                                                                                                                                                                                      [18/10/2026].
See
the
averages of raw positions for better readability (our trading results are based                                     Terms
on the raw positions and not the moving averages).                                                                                  and
The timing positions in Figure 10 are remarkable. First, they show that the                                                                          Conditionshigh-complexity strategy is long-only at heart. Negative bets are infrequent
and small relative to positive bets. The machine learning model thus heeds
the guidance of Campbell and Thompson (2008) “that many predictive regressions beat the historical average return, once weak restrictions are imposed on
the signs of coefﬁcients and return forecasts.” However, unlike Campbell and
Thompson (2008), the machine seems to learn this rule without being given an
explicit constraint.42
Second, the machine learning strategy learns to divest leading up to recessions. NBER recession dates are shown in the gray-shaded regions. For 14 out                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
of 15 recessions in our test sample, the timing strategy substantially reduces               on
its position in the market before the recession (the exception is the eight-month                                     Wiley
recession of 1945). And it does this on a purely out-of-sample basis.                                                                                             Online
Library
for
D. Comparison with Goyal and Welch (2008)                                                                                                                                                                 rules
of
Our results seem at odds with the primary conclusion of Goyal and Welch                              use;
OA
(2008). These authors argue that the enterprise of market return prediction,
articles
are
42 Strictly imposing the Campbell and Thompson (2008) constraint boosts the Sharpe ratio from
0.47 to 0.54 in the T = 12 case, from 0.42 to 0.50 for T = 60, and from 0.41 to 0.49 for T = 120.                                                                         governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 36 -->

15406261,
2024,
494                   The Journal of Finance®                                                        1,
Downloadedwhich has occupied a large amount of attention in the asset pricing literature
from
for decades, is by and large a failed endeavor: “these models seem unstable,
as diagnosed by their out-of-sample predictions and other statistics; and these
models would not have helped an investor with access only to available information to proﬁtably time the market.” But we use the same predictive information as in that paper. What is the source of the discrepancy?
The conclusions of Goyal and Welch (2008) are based on their ﬁndings of consistently negative out-of-sample prediction R2. They do not analyze the performance of timing strategies based on expected returns or Sharpe ratios.43 Werevisit their analysis with a focus on timing strategy performance using the                                                                                                                                                                                                                                                                                                                                                                                                                                                   https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
same recursive out-of-sample prediction scheme as in the analysis of Figures 7                by
and 8. We use rolling 12-, 60-, and 120-month training windows (Panels A,                                                                National
B,  and       C, respectively),                    and we                                focus on                                   a version                                                          of what Goyal                                                      and                                                            Welch                                                                                 University(2008)        call          the “kitchen sink”                             regression.                               Our                                        implementation                                                        uses 15                                                          monthly
Of
predictors in a linear ridgeless regression.44
The ﬁrst ﬁnding of Table I is that we conﬁrm the conclusions of Goyal and                                                                                 Singapore,
Welch (2008). Note that with monthly data, a model with 15 regressors already                                        Wiley
has nontrivial complexity even for long training windows, and for the 12-month                                                Online
training window, its complexity even exceeds one. Monthly return forecasts us-                                                        Library
ing linear ridgeless regression behave egregiously. The monthly out-of-sample                on
R2 from ridgeless regression (z = 0+) is large and negative at less than −100%
(−9764% to be precise!). The timing strategy based on these predictions is also                                                                                                         [18/10/2026].
poor. The Sharpe ratio is −0.11 and is insigniﬁcantly different from zero. This                        See
seems perhaps not so terrible given the wildness of the forecasts, but it is due                        the
Terms
to the fact that the strategy’s volatility is so high. Its maximum loss is 98 stan-                        and
dard deviations. In light of our theoretical analysis, this agreement with the
conclusions of Goyal and Welch (2008) is perhaps unsurprising. With P = 15                                                                                 Conditions
and T = 12, this analysis takes place near the interpolation boundary. Thus,
forecasts and timing-strategy returns are expected to be highly volatile, as
our estimates conﬁrm. In Panels B and C, we repeat the analysis with longer
training windows (T = 60 and 120). Longer training windows lead to less variable ridgeless regression estimates, producing higher (though still negative)
R2, and improving the Sharpe ratio.
Our theoretical analysis suggests that, in circumstances like the linear
kitchen sink where the regression takes place near the interpolation boundary,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
the beneﬁts from additional ridge shrinkage are potentially large. We, there-                on
fore, reestimate the Goyal and Welch (2008) kitchen sink regression with the                                        Wiley
same range of ridge parameters that we used in our machine learning mod-                                                Online
els. The R2 from even heavily regularized regressions can remain negative,                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Library
for
43 Updating the original Goyal and Welch (2008) analysis, Goyal, Welch, and Zaﬁrov (2023)                                        rules
provide some evidence of timing-strategy performance for market return predictors.                                of                                                                                                                                                                                                                                                                        use;
44 To remain consistent with our other analyses, the forecast target is the monthly market                OA
return standardized by its rolling 12-month volatility standardization. We continue to refer to this                                                                 articles
as “the market” throughout. As discussed in the robustness section, our results across the board                        are
are generally insensitive to, and our conclusions entirely unaffected by, whether we work with the
raw or volatility-standardized market return.                                                                                                                                                                                                                                                                                                                       governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 37 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          495               1,
Table I                                                                                                                                                                                                                                                                                                                                                    Downloaded
from            Comparison with Goyal and Welch (2008)

This table report the out-of-sample prediction accuracy and portfolio performance estimates for
high-complexity timing-strategy returns with c = 1,000 and z = 103 in Section V.C (“Nonlinear”)
averaged across 1,000 sets of random feature weights, compared with the linear kitchen sink
model of Goyal and Welch (2008) (“Linear”) with shrinkage of z = 0+ (ridgeless) and z = 103. The
forecast target is the monthly market return standardized by its rolling 12-month volatility standardization. We report strategy Sharpe ratios (with average return t-statistics), information ratios
versus the market and versus the linear model with z = 103 (with alpha t-statistics). The panels
correspond to training windows of 12, 60, or 120 months. “Max Loss” is in standard deviation units.                                              IR v.         IR v.      Max                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
Model     Shrinkage      R2      SR       t    Mkt       t    Linear    t   Loss  Skew
National
Panel A: 12-month training window                                                                                                                                                                                                                                                                                                                                                                                                                                                        UniversityLinear        z = 0+   <−100%     −0.11  −1.0  −0.16  −1.6   –     –    98.5   −0.9               Of
z = 103        −3.8%    0.46    4.4    0.33    3.1   –     –     2.4   −0.1
Nonlinear    z = 103          0.6%    0.47    4.5    0.31    2.9   0.26    2.5    1.2     2.5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Singapore,
Panel B: 60-month training window                                                                                                                                                                                                                            Wiley
OnlineLinear        z = 0+       −96.6%    0.00    0.0  −0.07  −0.6   –     –    35.8  −11.1
z = 103        −0.5%    0.44    4.1    0.10    0.9   –     –     1.4   −0.3                                                    Library
Nonlinear    z = 103          0.5%    0.42    3.9    0.25    2.3   0.27    2.5    0.5     1.7               on

Panel C: 120-month training window                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].
Linear        z = 0+       −26.6%    0.20    1.8    0.14    1.2   –     –    15.4   −6.5                      See
the
z = 103          0.1%    0.49    4.4    0.13    1.2   –     –     0.8   −0.9
TermsNonlinear    z = 103          0.3%    0.41    3.7    0.24    2.2   0.24    2.2    0.3     0.9
and
Conditions
as seen in the out-of-sample R2 of −3.8% when z = 103. However, with this
much shrinkage, the beneﬁts of market timing become large. The annualized
out-of-sample Sharpe ratio of the strategy is 0.46 with a t-statistic of 4.4. This
performance is not due to static market exposure. In the column “IR v. Mkt,”
we report performance after regressing on the volatility-standardized market
return. The linear model with z = 103 has an IR of 0.33 (t = 3.1) versus the
market. Shrinkage also produces more attractive maximum loss and skewness.
These patterns align with the behavior predicted by our theoretical analysis.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)Near the interpolation boundary, models can seem defective in terms of R2, yet               on
they can nonetheless confer large economic beneﬁts to investors. In Panels B                                     Wiley
and C, we see that shrinkage also beneﬁts performance amid longer training                                            Online
windows. For T = 120, the linear strategy Sharpe ratio is 0.49 for z = 103 (the                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Library
alpha versus the market is insigniﬁcant, however).                                                                                   for
The “Nonlinear” model in Table I refers to the machine learning timing strat-                                     rules
egy with c = 1,000 and z = 103 (averaged across 1,000 sets of random weight               ofuse;
draws). In Panel A, the out-of-sample R2 is 1% per month, with a Sharpe ratio               OA
of 0.46 and an IR of 0.31 versus the market. It also has a signiﬁcant IR of 0.26                                                           articles
(t = 2.5) versus the best linear strategy (z = 103). One of the most attractive as-                      are
pects of the machine learning strategy is its low downside risk. Its worst month                                                           governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 38 -->

15406261,
2024,
496                   The Journal of Finance®                                                        1,
Downloaded
from
https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
by
National
University
Of
Figure 11. Variable importance. This ﬁgure shows the variable importance (VI) for the ith
predictor that is the change in performance, deﬁned as out-of-sample R2 or Sharpe ratio, moving                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Singapore,
from the full model with 15 variables to the reestimated model using 14 variables (excluding
Wileyvariable i). (Color ﬁgure can be viewed at wileyonlinelibrary.com)
Online
Library
on
was a loss of 1.23 standard deviations, and its skewness is positive, 2.48. These
attractive tail risk properties of the machine learning model are not reﬂected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        [18/10/2026].
in the Sharpe ratio. Still, they would be an important utility boost for investors                        See
who care about non-Gaussian risks. Note that the machine learning strategy                        the
Termsaccomplishes this using the identical information set as the linear strategy; it
and
exploits this information in a high-dimensional, nonlinear way. Using longer
training windows (Panels B and C) leads to the same conclusions.                                                                                                                                                                             Conditions


### E. Variable Importance

These results above beg the question: how can such large models learn predictive patterns in training windows as short as 12 months, particularly when
several raw predictors are highly persistent (e.g., dividend yield and T-bill
rate)? The short answer is that a number of the 15 raw predictors are, in fact,
highly variable over short horizons, and these variables are the most impor-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
tant contributors to the performance of the high-complexity model. To shed                on
more detailed light on this answer, we analyze the contribution of each vari-                                        Wiley
able to overall model performance. We reestimate the machine learning model                                                Online
omitting each of the 15 predictor variables one by one. We calculate “variable                                                        Library
importance” (VI) for the ith predictor as the change in performance (deﬁned as                        for
out-of-sample R2 or Sharpe ratio) moving from the full model with 15 variables                                        rules
to the reestimated model using 14 variables (excluding variable i).                                  ofuse;
Figure 11 plots the results for the 12-month training window (with P =                OA
12,000, z = 103, and averaged across 1,000 sets of random feature weights).                                                                 articles
The three most important variables are also the three predictors with the                        are
highest average variation in 12-month windows  (i.e., the least persistent                                                                 governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 39 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          497               1,
Downloadedpredictors).45 Excluding the lagged market return (“lag mkt”), long-term bond
from
return (“ltr”), or default return (“dfr”) from the random features model reduces
the out-of-sample monthly prediction R2 by 1.9%, 1.3%, and 0.8%, respectively.
In other words, the complex model is particularly adept at leveraging information in short-horizon ﬂuctuations among predictors. The VI calculations tell
the same story when we measure it in terms of R2 (bars) or Sharpe ratio (line).
VI helps us identify which of the 15 predictors are the most dominant information sources. But our results further show that the key differentiator of the
high-complexity model is its ability to extract nonlinear prediction effects. Theﬁrst evidence of this is its alpha versus the linear model shown in Table I. The                                                                                                                                                                                                                                                                                                                                                                                                               https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
linear model has access to the same predictors, but incorporating nonlineari-               by
ties generates signiﬁcant alpha over the linear model.                                                                                                                                                                                                          National
The VI results show that some linear predictors have impressive individ-                                                                          University
ual performance. To show that machine learning performance is not driven               Of
by   these        simple linear                          effects,                             Internet                                 Appendix                                             Table                                              IA1                                                           reports                                                           IRs                                                                                of
the                                                                          Singapore,machine         learning                 strategy                      on the                                  linear                                      univariate                                              timing                                                        strategy                                                                          of                                                             each                                                                          predictor (the univariate timing strategy is deﬁned as the product of a predictor                                     Wiley
at time t with the market return at t + 1).                                                                                                                                                                                                             Online
The machine learning model has a large and highly signiﬁcant IR over ev-                                                    Library
ery linear strategy. We also calculate its IR versus all 15 univariate strategies               on
simultaneously (“All”).46 In this case, we ﬁnd an IR of 0.32 (t = 2.9), providing
further direct evidence for the nonlinear beneﬁts of complexity.                                                                                                                                                                                                                                                 [18/10/2026].
Naturally, interpretation is a challenge for complex nonlinear models. In-                      See
the
ternet Appendix Figure IA5 makes progress in this direction by illustrating                                                                                                                                                                                                                                                                                                                                      Terms
the nonlinear prediction patterns associated with each of the 15 predictors. To                      and
trace     the impact                   of                   predictor                                        i on                               expected                                          returns,                                     we ﬁx the                                                             prediction                                                            model
estimated         from a                given                       training                           sample                                and                                   ﬁx the values                                                                of all                                                              variables                                                                     other                                                                          Conditions
than i at their values at the time of the forecast. Next, we vary the value of the
ith predictor from its full-sample min (corresponding to −1 in the plots) to its
full-sample max (corresponding to +1) and record how the return prediction
varies. We then average this prediction response function across all training
windows and plot the result.
The ﬁgure illustrates a few interesting patterns. First, we see that when certain indicators of macroeconomic risk are at their lowest (in particular, stock
market variance “svar” and credit spreads on risky corporate debt “dfy”), the                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
machine learning model forecasts positive returns. However, once these vari-               on
ables reach even moderate levels, the return prediction drops to zero. This is                                     Wiley
Online
45 Figure IA4 in the Internet Appendix reports the average variation of each predictor in 12-                                                    Library
month training windows.                                                                                                                                                       for
46 We cannot run in-sample versus all 15 univariate strategies simultaneously because this                                     rules
would be equivalent to using the in-sample tangency portfolio of the 15 timing strategies as a               of                                                                                                                                                                                                                                                                     use;
benchmark. This is not an apples-to-apples comparison because the machine learning strategy is               OA
out-of-sample, so it should be benchmarked to a similarly out-of-sample strategy. To this end, we                                                           articles
build the out-of-sample tangency portfolio of the 15 timing strategies (scaled to have an expected                      are
volatility of 20%) using an expanding window. We use this combined strategy as the regressor
when calculating alpha for the “all” case.                                                                                                                                                                                                                                                                                                                                        governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 40 -->

15406261,
2024,
498                   The Journal of Finance®                                                        1,
Downloadedconsistent with the time-series pattern in Figure 10, which shows that timfrom
ing positions (i.e., expected returns) drop to zero heading into recessions. In
fact, all predictors demonstrate a similar “risk on/risk off” predictive pattern
in which certain values trigger positive market bets; otherwise, they advocate
positions near zero.


### F. The Extent of Nonlinearity and Other Robustness

It is interesting to note that the linear strategy and the nonlinear machinelearning strategy each have beneﬁcial performance relative to buy-and-hold.                                                                                                                                                                                                                                                                                                                                                                                                                                                    https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
Yet, they are distinct from each other (e.g., the nonlinear strategy has signif-                by
icant alpha versus the linear strategy). The parameter γ controls the degree                                                                 National
of  nonlinearity               in                 the               RFF approximation.                                                  It turns                                               out                                                    that                                                       the linear                                                                  kitchen
sink     regression                   is                 equivalent                              to an RFF model                                              in the                                                       limit                                           when                                                           γ ≈0.                                                                 In par-                                                                                 University
Of
ticular, note that                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      Singapore,
sin(γ ω′iGt) = γ ω′iGt + O(γ 2), cos(γ ω′iGt) = 1 −γ ω′iGt + O(γ 2).    (21)                                        Wiley
OnlineSuppose for simplicity that we only have the sin features. Then, deﬁning
Library  =   1         P1/2 (ωi)Pi=1 ∈R15×P, we have that the model is equivalent to a model with                                                                                                                                    on
random linear features, St =   ′Gt.47
This begs the question: is there an optimal degree of nonlinearity? In gen-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        [18/10/2026].
eral, the answer is no. In the high-complexity regime, different choices of γ                         See
deliver different approximations of the true DGP, with none strictly domi-                        the
nating the others. Mei, Misiakiewicz, and Montanari (2022) show that high                                        Terms
and
model complexity poses an insurmountable obstacle for any random feature
regression—it is impossible to learn the “true” dependency Rt+1 = f (Gt) + εt+1                                                                                 Conditions
when the model is complex. In this case, different random feature generators
recover different aspects (projections) of the truth on different subspaces. As a
result, we would expect linear and nonlinear random features to contain complementary information. This is clearly reﬂected in the results of Table I.48
We assess robustness of our results to various degrees of nonlinearity (γ =
0.5 or 1, versus γ = 2 in our main analysis) in Section VI of the Internet Appendix. We also investigate the effect of excluding volatility standardization of
the market return. The brief summary of these analyses is that our conclusionsare robust to each variation in empirical design.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
Next, we analyze the robustness of our main ﬁndings in subsamples. We                on                                                                                                                                                                                                                                                                                                                                         Wiley
report model performance splitting the test sample into halves, as shown in
Online
Internet Appendix Figures IA9, IA10, and IA11 for training windows T = 12,
60, and 120, respectively. The left side of each ﬁgure reports machine learning                                                        Library
for
timing-strategy out-of-sample performance from 1930 to 1974, and the right                                        rules
of
use;
47 See Proposition IA1 in Section V of the Internet Appendix.                                                        OA
48 Related, the machine learning model and the linear kitchen sink (with z = 103) have alpha                                                                 articles
versus each other, suggesting that there are beneﬁts to model averaging. For example, an equal-                        are
weighted average of the two strategies (after they are rescaled to have the same volatility) produces a Sharpe ratio of 0.53 and a signiﬁcant IR versus the market of 0.37.                                                                                                                                                                            governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 41 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          499               1,
Downloadedside from 1975 to 2020. The ﬁgures show that the patterns of out-of-sample
from
timing- strategy performance with respect to complexity and shrinkage do not
depend on the subsample. Average out-of-sample returns rise monotonically
with complexity and decrease with ridge shrinkage; volatility abates when we
move past the interpolation boundary and is further dampened by shrinkage.
IRs rise with complexity and are fairly insensitive to shrinkage. In the interest
of space, we do not plot the out-of-sample R2 or ˆβ norm, but these also follow
identical patterns to those for the full sample.
While the patterns are the same across subsamples, the magnitudes differ.Average returns in the second sample are about half as large as in the ﬁrst                                                                                                                                                                                                                                                                                                                                                                                                               https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
sample. But volatilities are roughly the same, so IRs are about half as large               by
in the second sample. This is consistent with the machine’s trading patterns                                                           National
plotted        in Figure 10. Starting                          around                                    1968,                                          the                                         machine                                                ﬁnds notably                                                                 fewer
buying        opportunities                    and, when                                            it does,                                       takes                                             smaller                                                         positions                                                         than in                                                                     the                                                                          University
Of
earlier sample.
Finally, we compare the performance of the machine learning model with                                                                          Singapore,
a 12-month training window to a 12-month time-series momentum strategy                                     Wiley
(Moskowitz, Ooi, and Pedersen (2012)). If regressors are highly persistent, they                                            Online
will appear roughly static in a typical 12-month window. In this case, forecasts                                                    Library
from a high-complexity regression will behave very similarly to time-series               on
momentum.49 In Section VII of the Internet Appendix, we explain this issue
in more detail. We also show that our results are not driven by this “short                                                                                                [18/10/2026].
window and persistent regressor” mechanism. Instead, as emphasized in Sec-                      See
tion V.E, our machine learning model performance is driven by relatively high-                      the
Terms
frequency ﬂuctuations among the predictors. We also show that the machine                      and
learning timing strategy has economically large and statistically signiﬁcant
alpha over time-series momentum.                                                                                                                                                                                                                                                                                                                                                                                                          Conditions


## VI. Conclusion

The ﬁeld of asset pricing is in the midst of a boom in research applications using machine learning. The asset management industry is experiencing a parallel boom in adopting machine learning to improve portfolio construction. However, the properties of portfolios based on such richly parameterized models
are not well understood.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
In this paper, we offer new theoretical insights into the expected out-of-               on
sample behavior of machine learning portfolios. Building on recent advances                                     Wiley
in the theory of high-complexity models from the machine learning literature,                                            Online
we demonstrate a theoretical “virtue of complexity” for investment strategies                                                    Library
derived from machine learning models. Contrary to conventional wisdom, we                      for
prove that market timing strategies based on ridgeless least squares generate                                     rules
positive Sharpe ratio improvements for arbitrarily high levels of model com-               ofuse;
plexity. In other words, the performance of machine learning portfolios can               OA
be theoretically improved by pushing model parameterization far beyond the                                                           articles
are
49 We are grateful to the editor for pointing this out.                                                                                                                                                                                                                                                                       governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 42 -->

15406261,
2024,
500                   The Journal of Finance®                                                        1,
Downloadednumber of training observations, even when minimal regularization is applied.
from
We provide a rigorous foundation for this behavior rooted in techniques from
random matrix theory. We complement these technical developments with intuitive descriptions of the key statistical mechanisms.
In addition to establishing the virtue of complexity, we demonstrate that
out-of-sample R2 from a prediction model is generally a poor measure of its
economic value. We prove that a market timing model can earn large economic
proﬁts when R2 is large and negative. This naturally recommends that the ﬁnance profession focus less on evaluating models in terms of forecast accuracyand more on evaluating in economic terms, for example, based on the Sharpe                                                                                                                                                                                                                                                                                                                                                                                                                                                    https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
ratio of the associated strategy. We compare and contrast the implications of                by
model complexity for machine learning portfolio performance in correctly spec-                                                                National
iﬁed     versus           misspeciﬁed                       models.
Finally,        we            compare theoretically                                    predicted behavior to the empirical be-                                                                                 University
Of
havior of machine learning–based trading strategies. The theoretical virtue
of complexity aligns remarkably closely with patterns in real-world data. In                                                                                 Singapore,
a canonical empirical ﬁnance application—market return prediction and con-                                        Wiley
comitant market timing strategies—we ﬁnd out-of-sample IRs on the order                                                Online
of 0.3 relative to a market buy-and-hold strategy, and these improvements are                                                        Library
highly statistically signiﬁcant. The emerging strategies have some remarkable                on
attributes, behaving as long-only strategies that divest the market leading up
to recessions. Our high-complexity models learn this behavior without guid-                                                                                                         [18/10/2026].
ance from researcher priors or modeling constraints.                                                                                 See
Our results are not a license to add arbitrary predictors to a model. Instead,                        the
Terms
we recommend (i) including all plausibly relevant predictors and (ii) using rich                        and
nonlinear models rather than simple linear speciﬁcations. Doing so confers
prediction and portfolio beneﬁts, even when training data are scarce, particu-                                                                                 Conditions
larly when accompanied by prudent shrinkage. Even when the number of raw
predictors is small, gains are achieved using those predictors in highly parameterized nonlinear prediction models.
This recommendation clashes with the philosophy of parsimony frequently
espoused by economists and famously articulated by the statistician George
Box:

Since all models are wrong, the scientist cannot obtain a ‘correct’ one by                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
excessive elaboration. On the contrary, following William of Occam he                    on
should seek an economical description of natural phenomena. Just as the                                                  Wiley
ability to devise simple but evocative models is the signature of the great                                                            Online
scientist so overelaboration and overparameterization is often the mark of                                                                      Library
mediocrity. (Box (1976))                                                                                                                                           for
rules
Our theoretical analysis (along with that of Belkin et al. (2019), Hastie et al.                ofuse;
(2022), and Bartlett et al. (2020), among others) shows the ﬂaw in this view—                OA
Occam’s razor may instead be Occam’s blunder. Theoretically, we show that a                                                                articles
small model is preferable only if it is correctly speciﬁed. But as Box (1976)                        are
emphasizes, models are never correctly speciﬁed. The logical conclusion is                                                                governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 43 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          501               1,
Downloadedthat large models are preferable under fairly general conditions. The machine
from
learning literature demonstrates the preferability of large models in a wide
range of real-world prediction tasks. Our results indicate that the same is
likely true in ﬁnance and economics.
Our ﬁndings point to a number of interesting directions for future work,
such as studying the theoretical behavior of high-complexity models in crosssectional trading strategies and more extensive empirical investigation into
the virtue of complexity across different asset markets.                      Initial submission: June 21, 2022; Accepted: December 16, 2022                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
Editors: Stefan Nagel, Philip Bond, Amit Seru, and Wei Xiong                                      by
National
REFERENCES                                                                                                                                                                                                                                                                                                             University
Of
Abhyankar, Abhay, Devraj Basu, and Alexander Stremme, 2012, The optimal use of return predictability: An empirical study, Journal of Financial and Quantitative Analysis 47, 973–1001.                                                                          Singapore,
Ali, Alnur, J. Zico Kolter, and Ryan J. Tibshirani, 2019, A continuous-time view of early stopping                                     Wiley
for least squares regression, in Kamalika Chaudhuri and Masashi Sugiyama, eds., Proceedings of the 22nd International Conference on Artiﬁcial Intelligence and Statistics (AISTATS),                                            Online
volume 89, 1370–1378 (Naha, Okinawa, Japan), PMLR.                                                                                                                                                                                                               Library
Allen-Zhu, Zeyuan, Yuanzhi Li, and Zhao Song, 2019, A convergence theory for deep learning via               on
over-parameterization, in Kamalika Chaudhuri and Ruslan Salakhutdinov, eds., Proceedings
of the 36th International Conference on Machine Learning, 242–252 (Long Beach, California),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].   PMLR 97.
See
Bai, Zhidong, and Wang Zhou, 2008, Large sample covariance matrices without independence                      the
structures in columns, Statistica Sinica 18, 425–442.                                                                                                                                                            Terms
Bartlett, Peter L., Philip M. Long, Gábor Lugosi, and Alexander Tsigler, 2020, Benign overﬁtting                      and
in linear regression, Proceedings of the National Academy of Sciences 117, 30063–30070.
Belkin, Mikhail, Daniel Hsu, Siyuan Ma, and Soumik Mandal, 2019, Reconciling modern machine-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Conditions
learning practice and the classical bias–variance trade-off, Proceedings of the National
Academy of Sciences 116, 15849–15854.
Belkin, Mikhail, Daniel Hsu, and Ji Xu, 2020, Two models of double descent for weak features,
SIAM Journal on Mathematics of Data Science 2, 1167–1180.
Belkin, Mikhail, Alexander Rakhlin, and Alexandre B. Tsybakov, 2019, Does data interpolation
contradict statistical optimality? In Kamalika Chaudhuri and Masashi Sugiyama, eds., Proceedings of the 22nd International Conference on Artiﬁcial Intelligence and Statistics (AIS-
TATS), volume 89, 1611–1619 (Naha, Okinawa, Japan), PMLR.
Box, George EP, 1976, Science and statistics, Journal of the American Statistical Association 71,
791–799.Campbell, John Y., and Samuel B. Thompson, 2008, Predicting excess stock returns out of sample:                                                                                                                                                                                                                                                                                                                                                                                                               (https://onlinelibrary.wiley.com/terms-and-conditions)
on
Can anything beat the historical average? Review of Financial Studies 21, 1509–1531.                                                          Wiley
Cenesizoglu, Tolga, and Allan Timmermann, 2012, Do return prediction models add economic
value? Journal of Banking & Finance 36, 2974–2987.                                                                                                                                                                                           Online
Chen, Luyang, Markus Pelger, and Jason Zhu, 2023, Deep learning in asset pricing, Management                                                    Library
Science, Articles in Advance, 1–37.                                                                                                                              for
Cochrane, John H., 2011, Presidential address: Discount rates, Journal of Finance 66, 1047–1108.                                     rules
Da, Rui, Stefan Nagel, and Dacheng Xiu, 2022, The statistical limit of arbitrage, Working paper,               of
use;
Chicago Booth.
OA
Dobriban,         Edgar,              and Stefan Wager,                                  2018, High-dimensional
asymptotics of prediction: Ridge re-                                                           articles    gression           and classiﬁcation,                          The Annals                                                 of Statistics 46, 247–279.
Dong, Xi, Yan Li, David E. Rapach, and Guofu Zhou, 2022, Anomalies and the expected market                      are
return, Journal of Finance 77, 639–681.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          governed
Du, Simon, Jason Lee, Haochuan Li, Liwei Wang, and Xiyu Zhai, 2019, Gradient descent ﬁnds               by
global minima of deep neural networks, in Kamalika Chaudhuri and Ruslan Salakhutdinov,                      the
applicable
Creative
Commons
License


<!-- PDF page 44 -->

15406261,
2024,
502                   The Journal of Finance®                                                        1,
Downloaded     eds., Proceedings of the 36th International Conference on Machine Learning, 1675–1685 (Long
from    Beach, California), PMLR.
Du, Simon S., Xiyu Zhai, Barnabas Poczos, and Aarti Singh, 2018, Gradient descent provably
optimizes over-parameterized neural networks, Working paper, arXiv, Cornell University.
Fan, Jianqing, Yingying Fan, and Jinchi Lv, 2008, High dimensional covariance matrix estimation
using a factor model, Journal of Econometrics 147, 186–197.
Fan, Jianqing, Jianhua Guo, and Shurong Zheng, 2022, Estimating number of factors by adjusted
eigenvalues thresholding, Journal of the American Statistical Association 117, 852–861.
Fan, Jianqing, Zheng Tracy Ke, Yuan Liao, and Andreas Neuhierl, 2022, Structural deep learning
in conditional asset pricing, Working paper, SSRN.
Ferson, Wayne E., and Andrew F. Siegel, 2001, The efﬁcient use of conditioning information in     portfolios, Journal of Finance 56, 967–982.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
Freyberger, Joachim, Andreas Neuhierl, and Michael Weber, 2020, Dissecting characteristics non-                by
parametrically, Review of Financial Studies 33, 2326–2377.                                                                                                                                                                                                                                 National
Gagliardini, Patrick, Elisa Ossola, and Olivier Scaillet, 2016, Time-varying risk premium in large
cross-sectional equity data sets, Econometrica 84, 985–1046.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   University
Ghorbani, Behrooz, Song Mei, Theodor Misiakiewicz, and Andrea Montanari, 2020, When do neu-                Of
ral networks outperform kernel methods? Advances in Neural Information Processing Systems
33, 14820–14830.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  Singapore,
Giannone, Domenico, Michele Lenza, and Giorgio E. Primiceri, 2021, Economic predictions with                                        Wiley
big        data:           The                   illusion                             of sparsity,                                  Econometrica 89,                                                 2409–2437.
Goyal,      Amit,           and                 Ivo                    Welch,                           2008, A comprehensive                                                    look                                                         at the empirical performance of equity                                                Online
premium prediction, Review of Financial Studies 21, 1455–1508.                                                                                                                                                                               Library
Goyal, Amit, Ivo Welch, and Athanasse Zaﬁrov, 2023, A comprehensive 2021 look at the empirical                on
performance of equity premium prediction II, Working paper, Swiss Finance Institute.
Gu, Shihao, Bryan Kelly, and Dacheng Xiu, 2020, Empirical asset pricing via machine learning,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        [18/10/2026].
Review of Financial Studies 33, 2223–2273.                                                                                                                                                                                                      See
Hansen, Lars Peter, and Scott F. Richard, 1987, The role of conditioning information in deducing                        the
testable restrictions implied by dynamic asset pricing models, Econometrica 55, 587–613.                                                    Terms
Hastie, Trevor, Andrea Montanari, Saharon Rosset, and Ryan J. Tibshirani, 2022, Surprises in                        and
high-dimensional ridgeless least squares interpolation, The Annals of Statistics 50, 949–986.
Hornik, Kurt, Maxwell Stinchcombe, and Halbert White, 1990, Universal approximation of an un-                                                                                 Conditions
known mapping and its derivatives using multilayer feedforward networks, Neural Networks
3, 551–560.
Jacot, Arthur, Franck Gabriel, and Clément Hongler, 2018, Neural tangent kernel: Convergence
and generalization in neural networks, Advances in Neural Information Processing Systems
31.
Kelly, Bryan, and Seth Pruitt, 2013, Market expectations in the cross-section of present values,
Journal of Finance 68, 1721–1756.
Kelly, Bryan, and Dacheng Xiu, 2022, Financial machine learning, Working paper, Yale.
Koijen, Ralph, and Stijn Van Nieuwerburgh, 2011, Predictability of returns and cash ﬂows, Annual
Review of Financial Economics 3, 467–491.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      (https://onlinelibrary.wiley.com/terms-and-conditions)
Kozak, Serhiy, Stefan Nagel, and Shrihari Santosh, 2020, Shrinking the cross-section, Journal of                on
Financial Economics 135, 271–292.                                                                                                                                                                                                                    Wiley
Ledoit, Olivier, and Sandrine Péché, 2011, Eigenvectors of some large sample covariance matrix
ensembles, Probability Theory and Related Fields 151, 233–264.                                                                                                                                                        Online
Ledoit, Olivier, and Michael Wolf, 2020, Analytical nonlinear shrinkage of large-dimensional co-                                                        Library
variance matrices, The Annals of Statistics 48, 3043–3065.                                                                                      for
Leitch, Gordon, and J. Ernest Tanner, 1991, Economic forecast evaluation: Proﬁts versus the con-                                        rules
ventional error measures, American Economic Review 580–590.                                                   of
use;
Liu, Fanghui, Xiaolin Huang, Yudong Chen, and Johan A. K. Suykens, 2021, Random features                OA
for kernel approximation: A survey on algorithms, theory, and beyond, IEEE Transactions on                                                                 articles    Pattern Analysis and Machine Intelligence 44, 7128–7148.
are
Ludvigson, Sydney C., and Serena Ng, 2007, The empirical risk–return relation: A factor analysis
approach, Journal of Financial Economics 83, 171–222.                                                                                                                                                                                                                                                   governed
by
the
applicable
Creative
Commons
License


<!-- PDF page 45 -->

15406261,
2024,
The Virtue of Complexity in Return Prediction          503               1,
DownloadedMarˇcenko, Vladimir A., and Leonid Andreevich Pastur, 1967, Distribution of eigenvalues for some
from    sets of random matrices, Mathematics of the USSR-Sbornik 1, 457.
Martin, Ian W. R., and Stefan Nagel, 2022, Market efﬁciency in the age of big data, Journal of
Financial Economics 145, 154–177.
Mei, Song, Theodor Misiakiewicz, and Andrea Montanari, 2022, Generalization error of random
feature and kernel methods: Hypercontractivity and kernel matrix concentration, Applied and
Computational Harmonic Analysis 59, 3–84.
Mei, Song, and Andrea Montanari, 2022, The generalization error of random features regression: Precise asymptotics and the double descent curve, Communications on Pure and Applied
Mathematics 75, 667–766.
Moskowitz, Tobias J., Yao Hua Ooi, and Lasse Heje Pedersen, 2012, Time series momentum,    Journal of Financial Economics 104, 228–250.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              https://onlinelibrary.wiley.com/doi/10.1111/jofi.13298
Rahimi, Ali, and Benjamin Recht, 2007, Random features for large-scale kernel machines, Ad-               by
vances in Neural Information Processing Systems 20.                                                                                                                                                                                                                                                          National
Rahimi, Ali, and Benjamin Recht, 2008, Weighted sums of random kitchen sinks: Replacing minimization with randomization in learning, Advances in Neural Information Processing Systems                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            University
21.                                                                                                                          Of
Rapach, David, and Guofu Zhou, 2013, Forecasting stock returns, in Graham Elliott and Allan
Timmermann, eds., Handbook of Economic Forecasting, volume 2, 328–383 (Elsevier).                                                                                                                     Singapore,
Rapach, David, and Guofu Zhou, 2022, Asset pricing: Time-series predictability, Oxford Research                                     Wiley
Encyclopedia                    of                 Economics                        and Finance.
Rapach,       David E.,                 Jack                      K. Strauss,                             and Guofu Zhou, 2010, Out-of-sample equity premium pre-                                            Online
diction: Combination forecasts and links to the real economy, Review of Financial Studies 23,                                                    Library
821–862.                                                                                                                   on
Rapach, David E., and Guofu Zhou, 2020, Time-series and cross-sectional stock return forecasting:
New machine learning methods, Machine Learning for Asset Management: New Developments                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                [18/10/2026].
and Financial Applications 1–33.                                                                                                                                                                                                    See
Richards, Dominic, Jaouad Mourtada, and Lorenzo Rosasco, 2021, Asymptotics of ridge (less) re-                      the
gression under general source condition, in Arindam Banerjee and Kenji Fukumizu, eds., Pro-                                     Terms
ceedings of the 24th International Conference on Artiﬁcial Intelligence and Statistics (AIS-                      and
TATS), 3889–3897 (SanDiego, California, USA), PMLR.
Rudi, Alessandro, and Lorenzo Rosasco, 2017, Generalization properties of learning with random                                                                          Conditions
features, Advances in Neural Information Processing Systems 30.
Silverstein, Jack W., and Z. D. Bai, 1995, On the empirical distribution of eigenvalues of a class of
large dimensional random matrices, Journal of Multivariate Analysis 54, 175–192.
Spigler, Stefano, Mario Geiger, Stéphane d’Ascoli, Levent Sagun, Giulio Biroli, and Matthieu
Wyart, 2019, A jamming transition from under-to over-parametrization affects generalization
in deep learning, Journal of Physics A: Mathematical and Theoretical 52, 474001.
Sutherland, Danica J., and Jeff Schneider, 2015, On the error of random fourier features, Proceedings of the Thirty-First Conference on Uncertainty in Artiﬁcial Intelligence 862–871.
Tsigler, Alexander, and Peter L. Bartlett, 2023, Benign overﬁtting in ridge regression, Journal of
Machine Learning Research 24, 123–131.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (https://onlinelibrary.wiley.com/terms-and-conditions)
Wu, Denny, and Ji Xu, 2020, On the optimal weighted ℓ2 regularization in overparameterized               on
linear regression, Advances in Neural Information Processing Systems 33, 10112–10123.                                                   Wiley
Yaskov, Pavel, 2016, A short proof of the Marchenko–Pastur theorem, Comptes Rendus Mathematique 354, 319–322.                                                                                                                                                                                                                                                                                                                   Online
Library
for
Supporting Information                                                                                                                                   rules
of
Additional Supporting Information may be found in the online version of this                              use;                                                                                                                                  OA
article at the publisher’s website:                                                                                                                                                                                                                                                                                                                                     articles
Appendix S1: Internet Appendix.                                                                                                                       are
Replication Code.                                                                                                                                                                                                                                                                                                                                                                                                                   governed
by
the
applicable
Creative
Commons
License
