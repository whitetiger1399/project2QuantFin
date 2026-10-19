# Sparse Signals in the Cross-Section of Returns

**Authors:** Alex Chinco, Adam D. Clark-Joseph, Mao Ye  
**Journal:** The Journal of Finance, Vol. LXXIV, No. 1 (February 2019)  
**DOI:** 10.1111/jofi.12733

> Converted from the supplied PDF. Equations with complex mathematical layouts and figures should be checked against the original PDF.

---

<!-- PDF page 1 -->

THE JOURNAL OF FINANCE • VOL. LXXIV, NO. 1 • FEBRUARY 2019

ALEX CHINCO, ADAM D. CLARK-JOSEPH, and MAO YE∗

## Abstract

This paper applies the Least Absolute Shrinkage and Selection Operator (LASSO) to make rolling one-minute-ahead return forecasts using the entire cross-section of lagged returns as candidate predictors. The LASSO increases both out-of-sample ﬁt and forecast-implied Sharpe ratios. This out-of-sample success comes from identifying predictors that are unexpected, short-lived, and sparse. Although the LASSO uses a statistical rule rather than economic intuition to identify predictors, the predictors it identiﬁes are nevertheless associated with economically meaningful events: the LASSO tends to identify as predictors stocks with news about fundamentals.

FINANCIAL ECONOMISTS HAVE BEEN LOOKING for variables that predict future stock returns for as long as there have been ﬁnancial economists. For example, Banz (1981) uses market cap to predict future returns, Jegadeesh and Titman (1993) use lagged returns, and Cohen and Frazzini (2008) use customer earnings surprises. To ﬁnd these sorts of variables, researchers have to solve two distinct problems: identiﬁcation and estimation. First, they have to identify a subset of candidate predictors; then, they have to estimate the quality of these predictors.

In the past, researchers typically reached for a different set of tools when working on each of these problems, using their intuition to identify predictors and statistics to estimate quality. This two-pronged approach works well when you are only looking for steady long-lived predictors. For example, Cabot Oil & Gas’s lagged return predicted its future return at the one-minute horizon throughout October 2010. Because it formed such a steady long-lived predictive

∗Alex Chinco, Adam D. Clark-Joseph, and Mao Ye are all at Gies College of Business, University of Illinois at Urbana–Champaign. Mao Ye is also with the NBER. We have received many helpful comments and suggestions from John Campbell; Victor DeMiguel; Xavier Gabaix; Andrew Karolyi; Bryan Kelly; Maureen O’Hara; Vassilis Papavassiliou; Ioanid Rosu; Thomas Ruchti; Gideon Saar; Allan Timmermann; Heather Tookes; Sunil Wahal; and Brian Weller; as well as from seminar participants at the University of Illinois Urbana-Champaign, the 11th Annual Central Bank Conference on the Microstructure of Financial Markets, the 2016 AFA Annual Meetings, and the NBER EFFE SI. Hao Xu, Ruixuan Zhou, and Rukai Lou provided excellent research assistance. This research is supported by National Science Foundation grant #1352936, which is joint with the Ofﬁce of Financial Research at the U.S. Department of the Treasury. This work also uses the Extreme Science and Engineering Discovery Environment (XSEDE), which is supported by National Science Foundation grant #OCI-1053575. We thank David O’Neal of the Pittsburgh Supercomputer Center for his assistance with supercomputing, which was made possible through the XSEDE Extended Collaborative Support Service (ECSS) program. We have read the Journal of Finance’s disclosure policy and have no conﬂicts of interest to disclose.

DOI: 10.1111/joﬁ.12733


---

<!-- PDF page 2 -->

450 The Journal of Finance R ⃝

relationship, a researcher could intuit this variable and then estimate its quality with an ordinary least squares (OLS) regression

rt−ℓ= ˆα + ˆβ · xt−(ℓ+1) + εt−ℓ ℓ∈{0, . . . , L −1}, (1)

where rt is Cabot’s minute-t return, ˆα is its mean return, L is the length of the estimation window, xt−1 is Cabot’s lagged return standardized to have zero mean and unit variance during the estimation window, and ˆβ is the associated OLS coefﬁcient.

But, modern ﬁnancial markets are big, fast, and complex. Predictability now exists at scales that are not easy for a researcher to intuit. For instance, the lagged returns of Family Dollar Corp. were a signiﬁcant predictor for 20% of the oil-and-gas industry—including Cabot Oil & Gas—during a 50-minute stretch on October 6, 2010. Can a researcher really ﬁsh this particular variable out of the sea of spurious predictors using only his intuition? Of course not.

And, without a clear idea of which candidate predictors to test, a researcher cannot use the OLS regression in equation (1) to estimate the amount of crossstock predictability. There were 2,191 NYSE-listed stocks in October 2010. So, using an OLS regression to estimate the relationship between Cabot’s current return and the lagged returns of every one of these candidate predictors would require at least 2,191 observations—or, nearly six trading days! A researcher cannot wait six days to identify a signal that lasts less than an hour.

With this type of problem in mind, we apply the Least Absolute Shrinkage and Selection Operator (LASSO) rather than intuition to identify unexpected short-lived predictors such as the lagged returns of Family Dollar Corp. We ﬁnd that using the LASSO increases both out-of-sample ﬁt and forecastimplied Sharpe ratios, and we show that this out-of-sample success comes from identifying predictors that are unexpected, short-lived, and sparse. Finally, we document that these predictors are often the lagged returns of stocks with news about fundamentals. In other words, although the unexpected short-lived predictors that the LASSO identiﬁes are not easy to intuit, they are still economically meaningful.

The LASSO. We begin our analysis by describing both how the LASSO works and why we use it. We are motivated by a simple observation about the limit of human intuition. As researchers, we cannot use our intuition to identify predictors that are sufﬁciently unexpected and short-lived—at some point, our brains just do not work fast enough. So, to incorporate these sorts of signals into our return forecasts, we need some other way to solve the identiﬁcation problem described above. And, bringing an additional assumption to bear on the data-generating process for returns is one way to do this.

Our approach is to assume that there are only a handful of important predictors at any one point in time—that is, to bet on sparsity. Morally speaking, if only S ≪2,191 predictors are important for forecasting Cabot’s returns, then you should need only a few more than S observations to identify and estimate this sparse set of predictors. A researcher can leverage this assumption by using the LASSO. This is a penalized-regression procedure that sets all


---

<!-- PDF page 3 -->

Sparse Signals in the Cross-Section of Returns 451

OLS coefﬁcients weaker than its penalty parameter, λ, to be exactly 0. Because it does not have to worry about estimating these weak coefﬁcients, the LASSO can estimate the remaining strong coefﬁcients using far fewer observations. So, if there are only a handful of important predictors at any one point in time, then we can use the LASSO to incorporate unexpected shortlived signals, such as the lagged return of Family Dollar Corp., into our return forecasts in a way that would not be possible using an unpenalized OLS regression.

Out-of-Sample Performance. After describing how and why we use the LASSO to bet on sparsity, we next investigate whether this bet pays off. To do this, we evaluate one-minute-ahead return forecasts for a randomly chosen subset of 250 NYSE-listed stocks on each trading day from January 2005 to December 2012. As a benchmark, we start with forecasts made via OLS regressions that include only steady long-lived predictors, such as a stock’s own lagged returns or the lagged returns on the market. In our main speciﬁcations, we study one-minute-ahead return forecasts created using three lags of various steady long-lived predictors, but the exact number of lags does not qualitatively affect our results.

We then apply the LASSO to make these same one-minute-ahead return forecasts using the lagged returns of all 2,000+ NYSE-listed stocks during the previous three minutes as candidate predictors. We ﬁnd that using the LASSO in addition to a standard benchmark model increases out-of-sample ﬁt by at least  ¯R2

n = 1.2 percentage points relative to just using the benchmark model by itself. A 1.2-percentage-point increase might seem small, but remember that we are making one-minute-ahead return forecasts. And, at short horizons, small increases in “R2 statistics can generate large beneﬁts for investors” (Campbell and Thompson (2008, p. 1526)). To highlight this point, we convert the LASSO’s one-minute-ahead return forecasts into a forecast-implied trading strategy and document that this forecast-implied strategy generates an annualized Sharpe ratio of 1.8 net of trading costs.

It is important to emphasize two things about these results. The ﬁrst is that we are running out-of-sample tests. It should not be surprising that the LASSO has better in-sample ﬁt than an OLS regression. The LASSO can choose from over 3 · N ≈6,000 candidate predictors; in a 30-minute estimation window, an OLS regression is restricted to fewer than 30. But, there is no guarantee that the LASSO’s better in-sample ﬁt will translate into better out-of-sample ﬁt. This will only happen if the cross-section of returns actually contains a sparse collection of S < 30 signals. If there are no signals to be found or if there are more than 30 signals, then using the LASSO will not help.

The second is that our results do not imply that researchers should use the LASSO instead of the standard two-pronged approach—that is, instead of their intuition. As a researcher, if you can use your economic intuition to identify a steady long-lived predictor, such as a stock’s own lagged returns, then an OLS regression is the right way to incorporate this predictor into your return forecast (Abadie and Kasy (2017)). But, the Bible does not say that all sources


---

<!-- PDF page 4 -->

452 The Journal of Finance R ⃝

of return predictability should make intuitive sense.1 And, the fact that using the LASSO and a benchmark model increases out-of-sample ﬁt relative to just using the benchmark model suggests that if researchers restrict their attention to steady long-lived predictors that they can suss out using nothing more than their intuition, then they will be ignoring important sources of predictability at the one-minute horizon.

Predictor Analysis. After seeing that the LASSO increases out-of-sample ﬁt, a natural next question is: What do the predictors selected by the LASSO look like? Consistent with our original motivation, we ﬁnd that the predictors selected by the LASSO are unexpected, short-lived, and sparse.

We begin by looking at why the predictors are unexpected. When we examine the LASSO’s cross-validated penalty parameter, we ﬁnd that it has an average value of 2.5% per month. In other words, the LASSO ignores any predictor weaker than 2.5% per month when making its one-minute-ahead return forecasts. This lower bound is twice as large as well-known predictors at the weekly and monthly horizon documented in the academic literature (McLean and Pontiff (2016), Harvey, Liu, and Zhu (2016), Linnainmaa and Roberts (2017)). As a result, there is little relation between the predictors identiﬁed by the LASSO each minute and existing predictors documented in the academic literature, which makes the LASSO’s choice of predictors seem unexpected. In addition, the predictors selected by the LASSO are also short-lived and sparse. Less than 5% of the predictors selected by the LASSO are used for more than 15 minutes in a row. And, on average the LASSO uses the lagged returns of only 12.7 other stocks as predictors when making its return forecast for each stock.

Economic Origins. We conclude our analysis by investigating the economic, rather than statistical, origins of the LASSO’s success. This is important because the LASSO uses a purely statistical rule to identify candidate predictors that are too unexpected and short-lived to be pinned down by economic intuition alone. And, because it does not rely on a researcher’s intuition, the LASSO’s increase in out-of-sample ﬁt could in principle have nothing to do with economic fundamentals. For example, it could be the case that the LASSO’s increase in out-of-sample ﬁt comes from identifying statistical artifacts. But this is not what we ﬁnd in the data. We document that the LASSO tends to identify as predictors the lagged returns of stocks with news about fundamentals. In other words, although the unexpected short-lived predictors that the LASSO identiﬁes are not easy to intuit, they are still economically meaningful.

Related Literature. This paper builds on several strands of the asset-pricing and statistics literature. To start with, our paper relates to work on return predictability (McLean and Pontiff (2016), Harvey, Liu, and Zhu (2016), Linnainmaa and Roberts (2017)). Campbell and Thompson (2008) show that many of the predictors documented in the academic literature work much better insample. And, DeMiguel, Garlappi, and Uppal (2009) document that simpler

1 Original quote by Enrico Fermi: “The Bible does not say that all laws of nature are expressible linearly” (Ulam (1976, p. xxiii)).


---

<!-- PDF page 5 -->

Sparse Signals in the Cross-Section of Returns 453

predictive regressions perform better out-of-sample due to overﬁtting. The LASSO avoids this overﬁtting problem by using a penalty function that removes all but the strongest predictors.

Our paper also relates to work on the role of sparsity in ﬁnancial economics. For example, Gabaix (2014) takes a top-down approach, proposing that traders prune away the least important predictors when forming mental models by having a preference for sparsity and internally imposing an ℓ1 penalty. By contrast, Chinco (2017) takes a bottom-up approach, showing that, if traders want to uncover sparse signals in market data, then there are informationtheoretic limits to how quickly they can interpret these signals regardless of what mental model they are using. Either way, this paper gives evidence that there are sparse signals for traders to ﬁnd in the cross-section of minute-byminute returns.

In addition, this paper builds on a large body of work looking at the performance of penalized regressions, such as the LASSO. The LASSO was ﬁrst introduced in Tibshirani (1996). See Hastie, Tibshirani, and Friedman (2001) for a general introduction. Meinshausen and Yu (2009) show how LASSO-type estimators extend to settings with correlated right-hand-side variables.

There are several excellent papers applying these ideas to topics in ﬁnancial economics. For example, DeMiguel et al. (2009) explain why norm-constrained estimators will perform better out-of-sample in the presence of estimation error. Both Freyberger, Neuhierl, and Weber (2017) and Feng, Giglio, and Xiu (2017) use the LASSO to identify characteristics related to the cross-section of expected returns at the monthly horizon. Bryzgalova (2017) develops a new model-speciﬁcation test by imposing an ℓ1-penalty function. And, Kozak, Nagel, and Santosh (2017) show that using ℓ1and ℓ2-penalized regressions to forecast returns can increase forecast-implied Sharpe ratios using monthly data.

Our paper differs from these other ﬁnancial applications of the LASSO in an important way. These papers are using the LASSO to choose between various predictors that have already been identiﬁed by other researchers using the standard two-pronged approach. By contrast, we are studying a situation where the standard two-pronged approach simply does not apply. A researcher cannot use his intuition to identify candidate predictors that are sufﬁciently unexpected and short-lived. And, without a clear idea of which candidate predictors to test, a researcher cannot use an OLS regression to incorporate these cross-stock signals into his return forecasts. So, we are suggesting the LASSO should be used as a complement to existing methods—that is, as a way for researchers to analyze unexpected short-lived predictors that they would not otherwise have access to using existing methods.

Finally, our paper relates to the literature looking at the relationship between news and asset prices. Brogaard, Hendershott, and Riordan (2014) show that algorithmic traders’ orders predict price changes over very short horizons and are correlated with macroeconomic news announcements. And, Manela and Moreira (2017) use news to form an uncertainty index and show that it is related to expected returns. Theoretical models of algorithmic trading (e.g., Hoffman (2014), Foucault, Hombert, and Rosu (2016), Du and Zhu (2017)) focus on this


---

<!-- PDF page 6 -->

454 The Journal of Finance R ⃝

ability to react to news announcements faster for individual ﬁrms. By contrast, our results suggest that the LASSO’s success comes from quickly identifying the unexpected consequences of news announcements for other ﬁrms.

Notation. Below, we use greek letters to denote in-sample parameter values, a superscript star⋆to denote a parameter value from the true data-generating process, a  hat to denote an in-sample OLS estimate of the true parameter value during a particular 30-minute estimation window, and a  tilde to denote the corresponding in-sample LASSO estimate; although these in-sample estimates are functions of the particular 30-minute estimation window they are estimated in, we do not include an estimation window subscript to avoid clutter. We use boldface characters to denote vectors. Finally, we use a bar to denote out-ofsample parameter estimates.

## I. The LASSO

We now outline both how the LASSO works and why we use it.

### A. Motivation

To see why we use the LASSO to make one-minute-ahead return forecasts, consider the following data-generating process for the nth stock’s return in minute t.

Data-Generating Process. Suppose that the nth stock’s return in minute t could be related to the lagged returns of any of the other N stocks in the market during the previous three minutes:

3·N 

β⋆

rn,t = α⋆

n,n′ · xn′,t−1 + ε⋆

n,t. (2)

n +

n′=1

In the equation above, α⋆

n is the mean return of the nth stock, and ε⋆

n,t is a noise term with E[ε⋆

n,t] = 0 and Var[ε⋆

n,t] = σ 2

ε . Since we are considering as predictors the lagged return of each NYSE-listed stock during the previous three minutes, we now use xn′,t−1 to denote the value of 1 of these 3 · N predictors standardized to have zero mean and unit variance during the estimation window. The parameter β⋆

n,n′ is then the predictive power of the n′th predictor for the nth stock’s returns. In our empirical analysis, we will be making one-minute-ahead return forecasts for many different stocks, not just for Cabot Oil & Gas. So, from now on, we include an n subscript to denote which stock we are interested in forecasting.

Unexpected and Short-Lived. If the predictive relationship embodied by β⋆

n,n′ is steady and long-lived, then it is reasonable to think that a ﬁnancial economist could intuit this connection. After all, researchers have used their intuition to uncover hundreds if not thousands of cross-sectional return predictors (McLean and Pontiff (2016), Harvey, Liu, and Zhu (2016), Linnainmaa and Roberts (2017)). And, if a researcher can intuit a candidate predictor, then he can use


---

<!-- PDF page 7 -->

Sparse Signals in the Cross-Section of Returns 455

an OLS regression to estimate the quality of this predictor. This is the standard two-pronged approach to ﬁnding predictors mentioned in the introduction.

But, if a researcher cannot use his intuition to narrow down the list of candidate predictors, then an OLS regression is no longer a viable option. For example, to estimate all 3 · N of the cross-stock predictive relationships in equation (2) using an OLS regression, you would have to solve the optimization problem



2⎫

⎧ ⎨

⎬

L−1 

3·N 

def= arg min

βn,n′ · xn′,t−(ℓ+1)

rn,t−ℓ−αn −

ˆαn, ˆβn

⎩

⎭, (3)

1 L ·

αn,βn

ℓ=0

n′=1

where ˆβn = [ ˆβn,1 · · · ˆβn,3·N]⊤is the (3 · N × 1)-dimensional vector of slope coefﬁcients used to forecast the returns of the nth stock.

This multivariate analogue to equation (1) is ill-posed when there are more parameters to estimate than observations to estimate them with (3 · N + 1) >

L. There are roughly N = 2,000 NYSE-listed stocks at any point in time, and 2,000 minutes is roughly six trading days. So, if the cross-stock signal represented by β⋆

n,n′ does not stick around for at least 18 trading days, then there is no way for a researcher to estimate it using an OLS regression without making some sort of intuitive leap. If a researcher wants to use such an unexpected short-lived predictor, then he needs to ﬁnd some other way of solving his identiﬁcation problem that shortens the required estimation window.

Betting on Sparsity. One popular approach is to assume that there are only a handful of strong predictors at any point in time—that is, to bet on sparsity (Hastie, Tibshirani, and Friedman (2001)). Intuitively, it should not require all 3 · N observations to estimate a coefﬁcient vector containing mostly zeros. If

Sn,λ denotes the number of predictors for stock n that are more extreme than λn,

3·N 

def=

1{|β⋆

Sn,λ

n,n′|>λn}, (4)

n′=1

then betting on sparsity with an L-minute estimation window means assuming that

Sn,λ ∈{1, 2, . . . , L −1}. (5)

It is important to note that this bet is not guaranteed to succeed. There are two ways for the data to be nonsparse. First, if Sn,λ = 0, then there are no predictors to ﬁnd. Second, if Sn,λ ≥L, then the predictors are dense, meaning that there is no way to consistently estimate the relationship between all these predictors and the nth stock’s returns in an L-minute estimation window no matter what approach you take. Either way, if the predictors are not sparse, then a researcher’s bet on sparsity will not pay off.

Why Sparsity Helps. Before getting to any more math, let us pause for a moment and build some intuition about why betting on sparsity might help.


---

<!-- PDF page 8 -->

456 The Journal of Finance R ⃝

Suppose you are standing on a beach, and you are trying to ﬁgure out whether a dark spot you see on the horizon is a sailboat or a cloud. A natural human reaction in this situation is to squint. But, why are our brains wired this way? After all, by squinting and slightly closing your eyes, you are removing information and making it harder to see colors and quick movements.

The key insight is that colors and quick movements are not going to tell you much about the nature of the mysterious blob on the horizon. Sailboats and clouds are both going to be dark and slow-moving at this distance. So, in essence, squinting penalizes these weak predictors. When you squint, the only things left for you to see are the most relevant details for the question you are trying to answer: Is the blob triangular? Does it have a mast? And, by ignoring extraneous details, you will be able identify the nature of the object on the horizon at a much greater distance.

But this approach will only work if you can answer your question using only a handful of strong predictors. For instance, squinting will do you no good when trying to ﬁgure out whether the sailboat is ﬂying a British or American ﬂag. Both of these ﬂags use the same colors. Distinguishing between these two possibilities will require many subtle cues about how the colors are organized. No amount of squinting will help you resolve these subtle differences. You will just have to wait until the sailboat gets closer and get a better look.

Subset Selection. Most economists are familiar with the Akaike information criterion (AIC; Akaike (1974)) and the Bayesian information criterion (BIC; Schwarz (1978)). These criteria are examples of a particular way of solving the selection problem known as best-subset selection. They both impose a penalty that eliminates weak predictors—just like in the example above—by solving the following optimization problem for different choices of λn:



2

⎧ ⎨

⎫ ⎬

L−1 

3·N 

3·N 

βn,n′ · xn′,t−(ℓ+1)

rn,t−ℓ−αn −

+ λn ·

1{βn,n′̸=0}

⎩

⎭. (6)

1 L ·

min αn,βn

ℓ=0

n′=1

n′=1

If λn = 2 · σε, then solving equation (6) is equivalent to using the AIC; whereas, if λn = 2 · σε · log(L), then it is equivalent to using the BIC (Foster and George (1994)).

So, why not use the AIC or the BIC to identify unexpected short-lived predictors in the cross-section of returns? The problem with these criteria is that they “are highly impractical” (Candes and Plan (2009, p. 2146)) when choosing among many variables. When solving the optimization problem in equation (6), there is a ﬁxed λn penalty for moving βn,n′ any distance away from zero, no matter whether it is an inch or a mile. And, this hard threshold implies that the optimization problem in equation (6) is nonconvex and thus NP (nondeterministic polynomial-time) hard (Natarajan (1995)), requiring an exhaustive search over all possible subsets of 23·N predictors.

To give a sense of the difﬁculty of this combinatorial search problem, note that most WiFi networks are deemed secure because cracking a 128-bit pass code would involve a brute-force search over 2128 parameter values. Such a


---

<!-- PDF page 9 -->

Sparse Signals in the Cross-Section of Returns 457

search would take 1 quintillion years (Arora (2012)). So, running more than 26,000 separate regressions is out of the question.

Convex Relaxation. The difﬁculty of this combinatorial-search problem is what brings us to the LASSO. The LASSO offers a way to solve this subsetselection problem that gets around the computational roadblock associated with AIC and BIC. The LASSO does this by changing the penalty function in equation (6) slightly:



2

⎫ ⎬

⎧ ⎨

L−1 

3·N 

3·N 

def= arg min

|βn,n′|

βn,n′ · xn′,t−(ℓ+1)

rn,t−ℓ−αn −

+ λn ·

˜αn, ˜βn

⎭.

⎩

1 L ·

αn,βn

ℓ=0

n′=1

n′=1

(7)

The optimization problem in equation (6) uses the penalty 1{βn,n′̸=0} while the problem in equation (7) uses the penalty |βn,n′|. This is the only difference between the two optimization problems. But, this difference convexiﬁes the problem (Efron and Hastie (2016, p. 308)). And, “if we can formulate a problem as a convex optimization problem, then we can solve it efﬁciently . . . with only a bit of exaggeration, we can say that, if you formulate a practical problem as a convex optimization problem, then you have solved the original problem” (Boyd and Vandenberghe (2004, p. 9)).

### B. Implementation

With this motivation in mind, let us now examine the details of how we use the LASSO to make one-minute-ahead return forecasts in rolling 30-minute estimation windows using the entire cross-section of lagged returns as candidate predictors.

LASSO Forecasts. Prior to the start of each trading day, we choose 250 stocks at random. Then, for each stock n in this collection of 250, we solve the optimization problem in equation (7) in R using the glmnet package (Friedman, Hastie, and Tibshirani (2010)) in rolling (L = 30)-minute estimation windows. As predictors, we consider the lagged returns of all NYSE-listed stocks during the previous three minutes, including the lagged returns of stock n itself. This means solving an estimation problem with 3 · N ≈6, 000 right-hand-side variables using only 30 observations, something that would clearly be impossible within an OLS-regression framework. We generate a one-minute-ahead return forecast, f LASSO

n,t , for the nth stock’s return in minute (t + 1) by applying the LASSO-coefﬁcient estimates from the previous 30 minutes to the most recent three minutes of data:

3·N 

f LASSO

˜βn,n′ · xn′,t. (8)

def= ˜αn +

n,t

n′=1

**Figure 1 summarizes this procedure for creating one-minute-ahead return forecasts.**


---

<!-- PDF page 10 -->

458 The Journal of Finance R ⃝

**Figure 1. Estimation and forecast timing. To make our one-minute-ahead forecast for the nth**

stock’s return in minute (t + 1) = 12:00, we ﬁrst estimate a model using data from the previous 30 minutes, {11:30, . . . , 11:59}. Then, we apply the estimated coefﬁcients to the most recent three minutes of data, {11:57, 11:58, 11:59}. We use f LASSO

11:59 to denote this forecast for the nth stock’s return in minute 12:00 because it only uses information up to minute 11:59.

Penalty Parameter. There is a clear choice for λn in best-subset selection procedures like the AIC and the BIC. The LASSO convexiﬁes these problems, making them computationally tractable in settings with thousands of predictors. But outside of special cases, there is no theoretically optimal value for λn when using the LASSO. So, we follow the standard procedure (Hastie, Tibshirani, and Friedman (2001)) and choose λn on a stock-by-stock basis in each 30-minute estimation window via K-fold cross-validation with K = 10 folds. This is the default setting for the cv.glmnet function.

Alternative Penalties. The LASSO is not the only way to convexify the bestsubset selection problem in equation (6). Researchers have proposed alternative procedures, such as the adaptive LASSO (Zou (2006)) or the elastic net (Zou and Hastie (2005)). These procedures represent interesting variations on the LASSO, but we focus on the LASSO for a simple reason: we want to show that it is possible for researchers to incorporate unexpected short-lived signals into their existing return forecasts using a statistical selection rule rather than their intuition. To accomplish this goal, it is best to use the simplest possible version of one of these rules—namely, the LASSO.

Benchmark Forecasts. Finally, in Section II, we show that using one-minuteahead return forecasts from both the LASSO and a standard benchmark model increases out-of-sample ﬁt relative to just using the return forecast from the benchmark model. To construct these benchmark forecasts, we run OLS regressions that include a wide range of steady long-lived predictors. We estimate each of these regressions using the exact same rolling 30-minute estimation windows described above. We then compute our benchmark one-minute-ahead return forecasts, f Bmk

n,t , by applying the resulting OLS estimates to the most recent three minutes of data. In our main speciﬁcations, we use benchmark models with three lags of each predictor, but we show that the exact number of lags does not qualitatively affect the results.

## II. Out-of-Sample Performance

This section investigates whether it pays to bet on sparsity with the LASSO. This means testing whether using both the LASSO and a benchmark model to


---

<!-- PDF page 11 -->

Sparse Signals in the Cross-Section of Returns 459

forecast returns increases out-of-sample ﬁt relative to just using the benchmark model.

### A. Data Description

Our tests incorporate data from several different sources. One-Minute Returns. We obtain data on the one-minute returns of NYSElisted stocks from the Trade and Quote (TAQ) database. Our sample includes every trading day from January 2005 to December 2012. We remove stocks with prices below $5 at the previous day’s close. While we consider the entire cross-section of NYSE-listed stocks as candidate predictors, we only make oneminute-ahead return forecasts for a randomly selected subset of 250 stocks each day for computational reasons.

Because we use a 30-minute estimation window and three lags, the ﬁrst oneminute-ahead return forecast each day is at t = 10:04 am. To avoid distortions due to the NYSE closing auction, we also drop the last minute of each trading day from our sample. This means that we make 356 separate one-minuteahead return forecasts, t ∈{10:04 am, . . . , 3:59 pm}, for each of the randomly selected 250 stocks during each day. In other words, each stock-day contains 356 · 250 = 64,000 forecasts.

Benchmark Predictors. We consider multiple steady long-lived predictors when making our benchmark one-minute-ahead return forecasts. In autoregressive speciﬁcations, a stock’s lagged returns come from the TAQ data described above. When a speciﬁcation involves the lagged returns on a portfolio (market, size, or value), we use the one-minute returns of exchange-traded funds (ETFs). The market return corresponds to the return on the iShares market ETF. And, size and value returns correspond to the returns on the iShares Russell 1000 and 2000 value and growth ETFs. When a speciﬁcation involves lagged industry returns, we construct a value-weighted return for the corresponding three-digit SIC industry.

Control Variables. We look at how the LASSO’s increase in out-of-sample ﬁt varies across stocks with different ﬁrm characteristics using data from CRSP. Market capitalization is deﬁned at the close of the previous trading day. Trading volume is deﬁned as the total trading volume on the previous trading day. Return volatility is deﬁned as the volatility of one-minute returns during the previous trading day. The bid-ask spread is the average bid-ask spread during the previous trading day.

Daily Factors. Finally, to compute the abnormal returns, we use data on the daily excess returns of factor portfolios from Kenneth French’s Web site.2

### B. Out-of-Sample Fit

Before thinking about increases in out-of-sample ﬁt, let us start by asking: How much return variation can the LASSO explain? This estimate will provide

2 See http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html.


---

<!-- PDF page 12 -->

460 The Journal of Finance R ⃝

an upper bound on the LASSO’s increase in out-of-sample ﬁt because some of the return variation explained by the LASSO might already be explained by an existing benchmark model.

Econometric Approach. To answer this question, we estimate a suite of predictive regressions:

f LASSO

n,t −¯mLASSO

+ en,t+1. (9)

rn,t+1 = ¯an + ¯bn ·

n ¯sLASSO n

In equation (9), rn,t+1 is the nth stock’s realized return in minute (t + 1), f LASSO

n,t is the LASSO’s one-minute-ahead return forecast for minute (t + 1), ¯mLASSO

n and ¯sLASSO

n denote the mean and standard deviation of the LASSO’s one-minuteahead return forecasts for the nth stock on a given day, ¯an and ¯bn denote out-ofsample regression coefﬁcients, and en,t+1 is the forecasting error. We estimate a separate regression for each of the 250 randomly selected stocks on a given trading day, which means that each regression contains 356 observations. And, we normalize the LASSO’s one-minute-ahead return forecasts to have zero mean and unit variance so that we can compare the slope coefﬁcients, ¯bn, across different regressions.

For each predictive regression, we then measure the fraction of the variation in a stock’s one-minute returns on a given day that is explained by the LASSO using the adjusted-R2 statistic. At one extreme, adjusted- ¯R2

n = 100% means that the LASSO’s one-minute-ahead return forecast, f LASSO

n,t , explains all of the variation in a stock’s returns; whereas, at the other extreme, adjusted- ¯R2

n = 0% means that f LASSO

n,t explains none of this variation. Appendix A illustrates this setup with numerical simulations.

Empirical Results. Table I summarizes the results of the suite of predictive regressions that we run. On average, the LASSO’s one-minute-ahead return forecast explains 2.467% of the variation in a stock’s one-minute returns on a given day. The 95% conﬁdence interval shows that this point estimate is statistically different from zero. We two-way cluster the standard errors at the stock-day level to account for the possibility that the LASSO might do a better job of forecasting returns for particular stocks or on particular trading days. The ﬁgure to the right of Table I reveals that, while there is some time series variation in the LASSO’s out-of-sample ﬁt, the LASSO explains at least 1% of the variation in returns during every month in our sample.

### C. Increase in Out-of-Sample Fit

Of course, we are not directly interested in the LASSO’s out-of-sample ﬁt in an absolute sense. Our goal is to show that using the LASSO in addition to a benchmark model increases out-of-sample ﬁt relative to just using the benchmark model. We are interested in increases in out-of-sample ﬁt, not the level of out-of-sample ﬁt itself.

Illustrative Example. Consider an example showing why this distinction is important. Recall that the LASSO can identify a stock’s own lagged returns as


---

<!-- PDF page 13 -->

Sparse Signals in the Cross-Section of Returns 461

**Table I Out-of-Sample Fit, The LASSO**

This table presents the results of the LASSO out-of-sample ﬁt. The regressions are run on 250 randomly chosen stocks on each trading day from January 2005 to December 2012. The panel to the left reports the population averages for the regression coefﬁcients and the adjusted-R2. Numbers in parentheses are standard errors clustered by stock-day. 95% CI reports 95% conﬁdence intervals for population averages. The ﬁgure to the right plots the average adjusted-R2 each month, and the dashed line represents the time series average, ¯R2

n = 2.467%. Gray bands denote the 99.9% conﬁdence interval computed using standard errors clustered by stock-day. The results indicate that, on average, the LASSO’s one-minute-ahead return forecast explains 2.467% of the variation in a stock’s returns on a given day. And, the LASSO explains at least 1% of the variation in returns during every month in our sample.

Mean 95% CI

·

¯an [%/m] 0.002 (0.002)

¯bn [%/m] 1.433 [1.399, 1.467]

(0.017)

¯R2

n [%] 2.467 [2.414, 2.520]

(0.027)

candidate predictors. So, in principle, the LASSO could be doing nothing more than replicating the one-minute-ahead return forecast of an autoregressive model with three lags. If this were the case, then the LASSO would have signiﬁcant out-of-sample ﬁt in an absolute sense. But, it would not provide any additional information over and above what was already contained in the AR(3) model. To justify using the LASSO, we need to show that the 2.467% of the return variation explained by the LASSO is not already explained by an existing benchmark model. In other words, we need to show that using the LASSO increases out-of-sample ﬁt.

Econometric Approach. We do this by elaborating on the methodology described above. First, we estimate the out-of-sample ﬁt of a benchmark model just like we did for the LASSO:

f Bmk

n,t −¯mBmk

+ en,t+1. (10)

rn,t+1 = ¯an + ¯cn ·

n ¯sBmk n

In equation (10), rn,t+1 is the nth stock’s realized return in minute (t + 1), f Bmk

n,t is the one-minute-ahead return forecast for this stock’s minute-(t + 1) return generated by some benchmark model, ¯mBmk

n and ¯sBmk

n denote the mean and standard deviation of the benchmark model’s one-minute-ahead return forecasts,

¯an and ¯cn are out-of-sample regression coefﬁcients, and en,t+1 is the benchmark forecasting error.


---

<!-- PDF page 14 -->

462 The Journal of Finance R ⃝

Then, to see if the LASSO increases out-of-sample ﬁt relative to this benchmark model, we estimate a second speciﬁcation that includes both f LASSO

n,t and f Bmk

n,t :

f LASSO

f Bmk

n,t −¯mLASSO

n,t −¯mBmk

+ en,t+1. (11)

rn,t+1 = ¯an + ¯bn ·

+ ¯cn ·

n ¯sLASSO n

n ¯sBmk n

If including the LASSO’s one-minute-ahead return forecast increases the adjusted-R2 statistic,  ¯R2

def= ¯R2,Both

n

n −¯R2,Bmk

n , then we know that the LASSO must be capturing new information that is not already present in the benchmark model’s one-minute-ahead return forecast.

At one extreme, if the LASSO and the benchmark model are using totally different information sets to create their respective one-minute-ahead return forecasts, then we will estimate  ¯R2

n = 2.467 percentage points. At the other extreme, if the LASSO is just replicating the one-minute-ahead return forecast of the benchmark model, then we will estimate  ¯R2

n = 0 percentage points. We are working with increases, not levels. And because we are studying percentagepoint increases in adjusted-R2, we can use the analysis in Giacomini and White (2006) to evaluate statistical signiﬁcance (see Appendix B).

Empirical Results. Table II summarizes the LASSO’s increase in out-ofsample ﬁt relative to a variety of different benchmark models. The ﬁrst row reveals that one-minute-ahead return forecasts made using an AR(3) model explain ¯R2,Bmk

n = 7.365% of return variation on average. The out-of-sample ﬁt of this benchmark model is larger than the LASSO’s out-of-sample ﬁt. But we are not suggesting that researchers should use the LASSO instead of their preferred benchmark model. We are suggesting that researchers should use the LASSO in addition to their preferred benchmark model. And, by using the LASSO in addition to this benchmark model, we estimate that a researcher could explain an additional  ¯R2

n = 1.185 percentage points of the variation in returns. The Giacomini and White’s (2006) p-value shows that such a large increase in out-of-sample ﬁt is highly unlikely under the null hypothesis that  ¯R2

n = 0 percentage points. The second row of Table II performs the exact same exercise, only this time relative to a benchmark model using three lags of the market return. This market benchmark performs much worse than the AR(3) benchmark, explaining only ¯R2,Bmk

n = 0.311% of the variation in returns. And, the one-minute-ahead return forecasts coming from the market benchmark use totally different information from those coming from the LASSO. The point estimate of  ¯R2

n = 2.469 percentage points is identical to our original estimate for ¯R2,LASSO

n = 2.467% to within one part in 500. What is more, the third row shows that a combined benchmark model that uses a stock’s own returns as well as the market’s returns does not improve on the simple AR(3) benchmark.

Alternative Lag Structures. The next four rows in Table II examine the LASSO’s increase in out-of-sample ﬁt relative to alternative AR(1), AR(2), AR(4), and AR(5) benchmark models. The AR(3) benchmark has the highest out-of-sample ﬁt, so we use it in our main speciﬁcations. But the LASSO


---

<!-- PDF page 15 -->

Sparse Signals in the Cross-Section of Returns 463

**Table II Increase in Out-of-Sample Fit, Main Results**

This table presents the results on the LASSO’s increase in out-of-sample ﬁt relative to a variety of benchmark models measured as the percentage point increase in adjusted-R2. The regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012. ¯R2,Bmk

n : Out-of-sample ﬁt of a benchmark model measured using the adjusted-R2.  ¯R2

n: The LASSO’s increase in out-of-sample ﬁt. p-value: Probability of observing the realized increase in outof-sample ﬁt  ¯R2

n under the null hypothesis of no increase. Numbers in parentheses are standard errors clustered by stock-day. Numbers in square brackets represent the 95% conﬁdence interval for the mean. AR(3): three lags of a stock’s own returns. Market: three lags of the market’s returns. AR(3), Market: three lags of a stock’s own returns and three lags of the market’s returns. AR(1): one lag of a stock’s own returns. AR(2): two lags of a stock’s own returns. AR(4): four lags of a stock’s own returns. AR(5): ﬁve lags of a stock’s own returns. AR(h⋆): h⋆lags of a stock’s own returns, where h⋆is chosen within each 30-minute estimation window using the BIC. Market, Industry: three lags of the market’s returns and three lags of the stock’s industry’s returns. Market, Size, Value: three lags of the market’s returns, a size portfolio’s returns, and a value portfolio’s returns, respectively. AR(3), Market, Industry, Size, Value: three lags of the market’s returns, a stock’s industry’s returns, a size portfolio’s returns, and a value portfolio’s returns, respectively. The results indicate that a researcher could explain an additional  ¯R2

n = 1.185 percentage points of the variation in returns by using both the LASSO and an AR(3) model rather than just the AR(3) model alone.

Benchmark Model ¯R2,Bmk

n [%]  ¯R2

n [Percentage Points] p-Value

AR(3) 7.365 1.185 [1.162, 1.208] 0.000 (0.076) (0.012) Market 0.311 2.469 [2.416, 2.522] 0.000 (0.003) (0.027) AR(3), Market 0.058 1.424 [1.395, 1.453] 0.000 (0.058) (0.015) AR(1) 6.061 1.288 [1.263, 1.314] 0.000 (0.052) (0.013) AR(2) 7.309 1.165 [1.143, 1.188] 0.000 (0.071) (0.012) AR(4) 7.174 1.238 [1.214, 1.262] 0.000 (0.076) (0.012) AR(5) 6.725 1.307 [1.282, 1.332] 0.000 (0.074) (0.013) AR(h⋆) 8.031 1.134 [1.113, 1.156] 0.000 (0.080) (0.011) Market, Industry 0.314 2.436 [2.384, 2.489] 0.000 (0.007) (0.027) Market, Size, Value 0.214 2.443 [2.390, 2.496] 0.000 (0.003) (0.027) AR(3), Market, Industry, Size, Value 1.443 2.232 [2.184, 2.279] 0.000 (0.015) (0.024)

increases out-of-sample ﬁt by roughly  ¯R2

n = 1.2 percentage points regardless of the number of lags used in the benchmark model. In fact, the row labeled “AR(h⋆)” shows that the LASSO still increases out-of-sample ﬁt by  ¯R2

n = 1.1 percentage points relative to an autoregressive benchmark model where the number of lags has been optimally chosen within each 30-minute estimation window using the BIC.


---

<!-- PDF page 16 -->

464 The Journal of Finance R ⃝

Including Portfolio Returns. Finally, the last three rows in Table II show that the LASSO’s increase in out-of-sample ﬁt persists even when the benchmark model includes lagged industry and risk-factor returns. In particular, the last row examines the LASSO’s increase in out-of-sample ﬁt relative to a benchmark model that includes three lags of the market’s returns, three lags of a stock’s industry’s returns, three lags of a size portfolio’s returns, three lags of a value portfolio’s returns, and three lags of a stock’s own lagged returns. Using this benchmark model to generate one-minute-ahead return forecasts means estimating an OLS regression with 1 + 5 × 3 = 16 coefﬁcients in just 30 minutes of data. The fact that this more elaborate benchmark has a lower out-of-sample ﬁt than the simple AR(3) benchmark is evidence of overﬁtting. By contrast, the fact that using the LASSO increases out-of-sample ﬁt relative to this same AR(3) benchmark suggests the LASSO is capturing meaningful new information.

Cross-Sectional Variation. The LASSO’s increase in out-of-sample ﬁt does not appear to be explained by observable differences across stocks. For example, Figure 2 shows that the LASSO’s  ¯R2

n = 1.185-percentage-point increase relative to the AR(3) benchmark and its  ¯R2

n = 2.469-percentage-point increase relative to the market benchmark are remarkably consistent across industries. In addition, Table III shows that the LASSO’s increase in out-of-sample ﬁt is not explained by ﬁrm characteristics such as market capitalization, trading volume, return volatility, or bid-ask spread. In fact, the LASSO actually increases out-of-sample ﬁt slightly more for large, liquid, frequently traded stocks—that is, for stocks with returns that are the hardest to predict using conventional methods.

Time Series Variation. How does the LASSO’s increase in out-of-sample ﬁt vary over time? The left panel of Figure 3 shows that the LASSO increased in out-of-sample ﬁt less during the ﬁnancial crisis. This pattern is consistent with existing research showing that returns display a stronger single-factor structure during market downturns (Ferson and Harvey (1991), Dangl and Halling (2012), Kacperczyk, Van Nieuwerburgh, and Veldkamp (2014)). If there is a strong single-factor structure, then there cannot be as many unexpected, short-lived, and sparse signals in the cross-section of returns. And, if there are not many unexpected, short-lived, and sparse signals in the cross-section of returns, then using the LASSO should not increase out-of-sample ﬁt by much.

The right panel of Figure 3 looks at the intraday time series properties of the LASSO’s increase in out-of-sample ﬁt. To create this ﬁgure, we reestimated the regressions in equations (10) and (11) 356 times each trading day using the cross-section of all 250 forecasts. We then averaged the resulting adjusted-R2 statistics in each minute across trading days. The fact that the LASSO’s increase in out-of-sample ﬁt is so smooth suggests that our ﬁndings are not explained by intraday microstructure effects.


---

<!-- PDF page 17 -->

Sparse Signals in the Cross-Section of Returns 465

Figure 2. Increase in out-of-sample ﬁt, by industry. This ﬁgure shows the LASSO’s increase in out-of-sample ﬁt relative to the AR(3) and market benchmarks sorted by three-digit SIC industries. Increase in out-of-sample ﬁt is measured as the percentage point increase in adjusted-R2. Regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012. We restrict the sample to industries with at least 20 ﬁrms on average. The left panel shows the LASSO’s increase in out-of-sample ﬁt relative to a AR(3) benchmark with the dashed line representing  ¯R2

n = 1.185 percentage points. The right panel shows that the LASSO’s increase in out-of-sample ﬁt relative to a market benchmark with the dashed line representing  ¯R2

n = 2.469 percentage points. The results indicate that the LASSO increases out-of-sample ﬁt for all industries.

### D. Sharpe Ratios

We have just seen that using the LASSO leads to a statistically signiﬁcant 1.2-percentage-point increase in out-of-sample ﬁt. But, what is the economic magnitude of this gain? Because “any predictive regression can be expressed as


---

<!-- PDF page 18 -->

466 The Journal of Finance R ⃝

**Table III Increase in Out-of-Sample Fit, by Characteristics**

This table presents the result of the LASSO’s increase in out-of-sample ﬁt relative to the AR(3) and market benchmarks sorted by ﬁrm characteristics. Increase in out-of-sample ﬁt is measured as the percentage point increase in adjusted-R2. Regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012.  ¯R2

n: The LASSO’s increase in out-of-sample ﬁt relative a benchmark model. p-value: Probability of observing the realized  ¯R2

n under the null hypothesis of no increase. Numbers in parentheses are standard errors clustered by stock-day. Numbers in square brackets are 95% conﬁdence intervals. Mkt Cap: Market value at the close of the previous trading day. Volume: Trading volume on the previous trading day. Volatility: Volatility of one-minute returns during the previous trading day. Spread: Average bid-ask spread during the previous trading day. High, >50th percentile: Subset of stocks with above-median values for a given characteristic. Low, <50th percentile: Subset of stocks with below-median values for the same characteristic. The results indicate that the LASSO increases out-of-sample ﬁt slightly more for large, liquid, and frequently traded stocks.

AR(3) Benchmark

High, >50th Percentile Low, <50th Percentile

 ¯R2

n [Percentage Points] p-Value  ¯R2

n [Percentage Points] p-Value

Mkt Cap 1.341 [1.307, 1.375] 0.000 1.029 [1.007, 1.051] 0.000 0.017 0.011 Volume 1.347 [1.315, 1.380] 0.000 1.023 [1.002, 1.044] 0.000 0.017 0.011 Volatility 1.137 [1.113, 1.162] 0.000 1.234 [1.204, 1.265] 0.000 0.012 0.016 Spread 0.996 [0.975, 1.017] 0.000 1.377 [1.343, 1.410] 0.000 0.011 0.017

High, >50th Percentile Low, <50th Percentile

 ¯R2

n [Percentage Points] p-Value  ¯R2

n [Percentage Points] p-Value

Mkt Cap 2.605 [2.534, 2.675] 0.000 2.332 [2.280, 2.385] 0.000 0.036 0.027 Volume 2.518 [2.454, 2.582] 0.000 2.419 [2.360, 2.478] 0.000 0.033 0.030 Volatility 2.680 [2.626, 2.734] 0.000 2.259 [2.196, 2.321] 0.000 0.028 0.032 Spread 2.302 [2.251, 2.353] 0.000 2.639 [2.569, 2.709] 0.000 0.026 0.036

a portfolio sort” (Pedersen (2015, p. 51)), we answer this question by studying the performance of a LASSO-implied trading strategy.

Na¨ıve Starting Point. Here is the starting point for our LASSO-implied strategy. Note that the slope coefﬁcient, ¯bn, from equation (9) can be written as





f LASSO

n,t −¯mLASSO

Cov

rn,t+1,

n ¯sLASSO n



def=

 , (12)

¯bn

f LASSO

Var

n,t −¯mLASSO n ¯sLASSO n


---

<!-- PDF page 19 -->

Sparse Signals in the Cross-Section of Returns 467

Figure 3. Increase in out-of-sample ﬁt, time series. This ﬁgure plots time series variation in the LASSO’s increase in out-of-sample ﬁt relative to the AR(3) and market benchmarks. Increase in out-of-sample ﬁt is measured as the percentage point increase in adjusted-R2. Regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012. The panel on the left corresponds to the LASSO’s increase in out-of-sample ﬁt by month. The panel on the right corresponds to the LASSO’s increase in out-of-sample ﬁt by minute of the trading day. The results indicate that the LASSO increased in out-of-sample ﬁt less during the ﬁnancial crisis, but the LASSO’s increase in out-of-sample ﬁt is relatively stable over the course of the trading day.

where rn,t+1 is the nth stock’s realized return in minute (t + 1), f LASSO

n,t is the LASSO’s one-minute-ahead return forecast for minute (t + 1), ¯mLASSO

n and ¯sLASSO

n denote the mean and standard deviation of the LASSO’s one-minuteahead return forecasts for the nth stock over the course of the entire trading day, and the operators Cov[·] and Var[·] denote the covariance and variance over the same time period—that is, one observation for each minute from 10:04 am to 3:59 pm.

Because we normalize the LASSO’s one-minute-ahead return forecasts to have zero mean and unit variance within a given trading day, the denominator in equation (12) is equal to 1. Thus, we can write out the expression for ¯bn using just the covariance term as





n,t −¯mLASSO

(13a)

rn,t+1, f LASSO

¯bn = Cov

n ¯sLASSO n





356 

f LASSO

n,t+h−1 −¯mLASSO

, (13b)

(rn,t+h −¯an) ·

= 1 356 ·

n ¯sLASSO n

h=1

where ¯an denotes the nth stock’s mean return during the day.

This expression can be interpreted as an average return to a na¨ıve LASSOimplied strategy:







×

f LASSO

. (14)

rNa¨ıve

n,t −¯mLASSO

n

n,t+1 = (rn,t+1 −¯an) ×

1/¯sLASSO n

The strategy is long 1/¯sLASSO n shares of the nth stock for each 1 percentage point that the LASSO’s one-minute-ahead return forecast exceeds its mean. Likewise, it is short 1/¯sLASSO n shares of the nth stock for each 1 percentage point that the LASSO’s forecast falls below its mean for the day. The strategy will be


---

<!-- PDF page 20 -->

468 The Journal of Finance R ⃝

proﬁtable if the nth stock’s realized return in minute (t + 1) tends to be above average, rn,t+1 > ¯an, when the LASSO’s return forecast is also above average,

f LASSO

n,t > ¯mLASSO

n , and vice versa. Thus, we can interpret Table I as saying that, for a randomly selected stock-day, this na¨ıve LASSO-implied strategy has a gross return of ¯bn = 1.433% per month.

There are three problems with implementing this na¨ıve LASSO-implied strategy, though. To start with, the strategy ignores trading costs (Hasbrouck (2009), Frazzini, Israel, and Moskowitz (2017), Novy-Marx and Velikov (2015)), which are substantial when trading at the one-minute horizon. The strategy also suffers from look-ahead bias. We do not know the nth stock’s mean return,

¯an, or the mean and variance of the LASSO’s one-minute-ahead return forecasts, ¯mLASSO

n and ¯sLASSO

n , until the end of the trading day. Finally, the strategy gives no guidance on how we should combine the 250 different one-minuteahead return forecasts we make each minute. So, we modify the strategy in equation (14) in several ways to account for these problems.

Trading Costs. Let us start with the trading-cost adjustments. To account for trading costs, we make two changes. First, we change the na¨ıve LASSO-implied strategy so that it only executes an order when the LASSO’s one-minute-ahead return forecast exceeds the bid-ask spread, 1{| f LASSO

n,t |>sprdn,t}. Then, conditional on a trade taking place, we compute the strategy’s realized returns net of this bid-ask spread (rn,t+1 −¯an) · Sign[ f LASSO

n,t ] −sprdn,t. Look-Ahead Bias. Next, let us turn to the issue of look-ahead bias. To eliminate any look-ahead bias, our strategy should only use values for ¯an, ¯mLASSO

n , and ¯sLASSO

n that are known prior to trading in minute (t + 1). To make sure this is the case, we start by assuming that both realized returns and oneminute-ahead return forecasts are mean-zero variables, ¯an = ¯mLASSO

n = 0. This is a reasonable assumption at the one-minute horizon as emphasized by our point estimate of ¯an = 0.002% per month in Table I. In addition, we also estimate the standard deviation of the LASSO’s one-minute-ahead return forecast during the previous 30 minutes of trading rather than over the course of the entire trading day. We use ˜σ LASSO

n,t to denote this in-sample standard-deviation estimate.

Portfolio Construction. Finally, we come to the question of portfolio construction: how do we combine the 250 different forecasts each minute into a single portfolio? The na¨ıve strategy buys/sells more shares of the nth stock per 1-percentage-point change in the LASSO’s forecast when the LASSO’s oneminute-ahead return forecasts for the nth stock tend to be less volatile throughout the trading day. Intuitively, a one-minute-ahead return forecast that is 0.20 percentage points above/below average is a very different signal when the typical return forecast is on the order of ¯mLASSO

n ± 0.02 percentage points from when it is on the order of ¯mLASSO

n ± 2.00 percentage points. In the ﬁrst case, a 0.20-percentage-point above/below average forecast is noteworthy, garnering a large portfolio weight; whereas, in the second case, it is commonplace, garnering a small portfolio weight.


---

<!-- PDF page 21 -->

Sparse Signals in the Cross-Section of Returns 469

We want our strategy to have a similar ﬂavor. But, we also want to be able to fund the strategy by borrowing $1 at the riskless rate prior to the beginning of each trading day. Then, the strategy’s returns at the end of the trading day minus the riskless rate would represent the excess returns to a zero-cost portfolio. The complication comes from the fact that the number of LASSO forecasts that exceed the spread, 1{| f LASSO

n,t |>sprdn,t}, can change from minute to minute. So, we need a rule that determines how much we invest for each of the stocks with a forecast that exceeds the spread in a given minute.

Here is how we do this. Suppose that the LASSO generated a one-minuteahead return forecast for the nth stock that exceeds the spread in minute t. Then, the LASSO-implied strategy invests a fraction ˜ωLASSO

n,t of its assets in the nth stock:

(1/˜σ LASSO

n,t · 1{| f LASSO

n,t ) · f LASSO

def=

˜ωLASSO

. (15)

n,t

n,t |>sprdn,t} 250



 (1/˜σ LASSO

n′,t · 1{| f LASSO

n′=1

n′,t ) · f LASSO

n′,t |>sprdn′,t}

The denominator is the total investment, both long and short, dictated by the na¨ıve strategy in stocks with forecasts that exceeded the spread in minute t. The numerator is the investment dictated by the na¨ıve strategy in the nth stock. The settlement period for NYSE stocks is longer than one minute, so it does not make sense to net out offsetting short and long positions at the one-minute horizon. This is why we use the absolute-value operator in the denominator. If there are no stocks with LASSO forecasts that exceed the spread in a given minute, then ˜ωLASSO

n,t = 0 for all stocks. Consider a quick example to see what these weights imply. Suppose that there are eight stocks with LASSO forecasts that exceed the spread. And, to keep things simple, suppose further that the ﬁrst four forecasts are +1 percentage points while the second four forecasts are −1 percentage points. If all eight forecasts have a volatility of 0.02%, then the denominator will be 8 · |(1/0.02%) · 1 percentage point| = 400. And the LASSO-implied strategy will invest one-eighth of its portfolio position in each stock. But, if stocks 1, 2, 5, and 6 instead have forecast volatilities of 2%, then the denominator will be 4 · |(1/0.02%) · 1 percentage point| + 4 · |(1/2%) · 1 percentage point| = 202. This means that stocks 1, 2, 5, and 6 will have portfolio weights of ˜wLASSO

n,t = ±1/404 while stocks 3, 4, 7, and 8 will have portfolio weights of ˜wLASSO

n,t = ±100/404—that is, weights that are 100 times larger in magnitude.

LASSO-Implied Strategy. Thus, the net return each minute to our LASSOimplied strategy is

250 









f LASSO

× ˜ωLASSO

rLASSO

rn,t+1 · Sign

−sprdn,t

n,t

n,t . (16)

t+1 =

n=1

This strategy accounts for trading costs and does not suffer from look-ahead bias. In addition, if we subtract off the riskless rate from this strategy’s endof-day returns, then the resulting excess returns correspond to the returns of a zero-cost portfolio funded by borrowing $1 at the beginning of the trading day.


---

<!-- PDF page 22 -->

470 The Journal of Finance R ⃝

**Table IV Forecast-Implied Performance Net of Trading Costs**

This table presents results of the performance of forecast-implied trading strategies net of trading costs on each trading day from January 2005 to December 2012. The top panel reports annualized Sharpe ratios of forecast-implied trading strategies net of trading costs. The ﬁrst column reports results for a strategy that invests $1 in the S&P 500 at the market open on January 3, 2005 and holds that position until the market close on December 31, 2012. The second column reports results for the LASSO’s forecast-implied trading strategy over the same time period. The third column reports analogous results for an AR(3)-implied strategy with the same initial investment. The bottom panel reports net abnormal returns of the LASSO-implied strategy relative to the market, the Fama and French (1993) three-factor model, and the Carhart (1997) four-factor model. The size of the initial investment in the LASSO-implied strategy was chosen so that it has the same average excess return as the buy-and-hold S&P 500 strategy. The ﬁrst column reports annualized abnormal returns. The remaining columns report dimensionless slope coefﬁcients associated with each of the factors. The results indicate that the LASSO-implied strategy generates positive excess returns net of the spread with an annualized Sharpe ratio of 1.791, and these excess returns are not explained by the strategy’s exposures to standard risk factors.

Annualized Sharpe Ratios

S&P 500 LASSO AR(3)

0.123 1.791 −0.662

LASSO-Implied Strategy Abnormal Returns [%/Year]

α Mkt HmL SmB Mom

Market 2.709 0.004 (0.034) (0.002) Three-factor model 2.713 0.004 −0.004 0.000 (0.034) (0.002) (0.004) (0.003) Four-factor model 2.707 0.005 −0.004 0.003 0.003 (0.034) (0.002) (0.004) (0.004) (0.004)

Sharpe Ratios. Table IV compares the performance of this LASSO-implied strategy with other benchmarks. Let us start with the top panel, which provides information on annualized Sharpe ratios. The ﬁrst column reports the Sharpe ratio of an unconditional buy-and-hold S&P 500 strategy. The strategy generates an annualized Sharpe ratio of only 0.123. The Sharpe ratio is relatively low because the S&P 500’s returns were quite volatile during our sample period, which includes the ﬁnancial crisis. The next column reports the LASSO-implied strategy’s Sharpe ratio, which is 1.791. This point estimate is more than 12 times larger than the Sharpe ratio of the unconditional buy-and-hold strategy.

The last column describes the performance of an AR(3)-implied strategy that is analogous to the LASSO-implied strategy—that is, a strategy constructed by replacing f LASSO

n,t with f AR(3)

n,t in equation (16). It turns out that this AR(3)- implied strategy loses money. Even though the AR(3) benchmark had higher out-of-sample ﬁt than the LASSO, it is not possible to trade on the AR(3)


---

<!-- PDF page 23 -->

Sparse Signals in the Cross-Section of Returns 471

benchmark’s one-minute-ahead return forecasts after adjusting for the bid-ask spread and look-ahead bias.

Thus, the ¯R2,Bmk

n = 7.365% out-of-sample ﬁt for the AR(3) benchmark does not translate into economically meaningful performance. This ﬁnding is broadly consistent with the results in both Korajczyk and Sadka (2004) and Patton and Weller (2017), who give evidence that momentum proﬁts disappear after adjusting for trading costs. The forecast-implied strategy associated with the market benchmark performs even worse than the one associated with the AR(3) benchmark.

Abnormal Returns. The positive excess returns earned by the LASSO-implied strategy do not appear to be explained by standard risk factors. In the bottom panel of Table IV, we study the LASSO-implied strategy’s covariance with the daily return on the market, the daily returns on size and value portfolios (Fama and French (1993)), and the daily return on a momentum portfolio (Carhart (1997)). Because the LASSO-implied strategy is zero cost, we choose the scale of the initial investment so that it has the same average excess return as the buy-and-hold S&P 500 strategy, 2.719% per year. Because the net returns to the LASSO-implied strategy are so smooth—12 times less volatile than the returns on the S&P 500—we ﬁnd that exposure to these commonly used risk factors at the daily horizon explains almost none of the LASSO-implied strategy’s excess returns.

Increases versus Levels. If the AR(3)-implied strategy had delivered positive excess returns, then we would have examined whether a 50/50 combination of the LASSOand AR(3)-implied strategy produced an even higher Sharpe ratio than the AR(3)-implied strategy on its own (Asness, Moskowitz, and Pedersen (2013), Novy-Marx (2017)). But such a test is no longer necessary given that the AR(3)-implied strategy loses money. If the AR(3)-implied strategy delivers negative net returns, then there is no way that it could be explaining the LASSO-implied strategy’s positive net returns. The difference in signs implies a difference in the signals being used.

Trade Frequency. Finally, Table V gives summary statistics describing the rate at which both the LASSOand AR(3)-implied strategies trade. The ﬁrst row of the top panel reveals that the AR(3)-implied strategy trades roughly twice as often as the LASSO-implied strategy, 17.643 trades versus 8.624 trades per minute out of 250 possible trades. The second row shows that roughly half of each strategy’s trades are buy orders, and the third row shows that roughly a third of each strategy’s trades are proﬁtable. Finally, the bottom panel shows that the LASSO-implied strategy is more active in large, liquid, frequently traded stocks.

## III. Predictor Analysis

After seeing the increase in out-of-sample ﬁt associated with the LASSO, a natural next question is: What do the predictors selected by the LASSO look like? In this section, we give evidence that the LASSO identiﬁes predictors that are unexpected, short-lived, and sparse.


---

<!-- PDF page 24 -->

472 The Journal of Finance R ⃝

**Table V Trading Frequency of Forecast-Implied Strategies**

This table presents the results of the trading frequency of forecast-implied strategies computed using the same randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012 for which we compute one-minute-ahead return forecasts using the LASSO. The top panel reports aggregate result, the ﬁrst row reports the average number of trades per minute made by LASSOand AR(3)-implied strategies. The second row reports the number of buy orders per minute. The third row reports the number of trades per minute that made money after accounting for the bid-ask spread. The bottom panel reports results by number of trades, buy orders, and successful trades per minute for the LASSO-implied strategy among large stocks, stocks with high trading volume, stocks with high return volatility, and liquid stocks. The results indicate that the AR(3)-implied strategy trades roughly twice as often as the LASSO-implied strategy, and the LASSO-implied strategy is more active in large, liquid, and frequently traded stocks.

Aggregate [Number/Minute]

LASSO AR(3)

Trades 8.624 17.643 Buy orders 4.306 8.887 Successful 2.600 6.538

By Characteristics [Number/Minute]

>50th Percentile >50th Percentile >50th Percentile >50th Percentile Mkt Cap Volume Volatility Spread

LASSO trades 5.188 5.115 4.821 5.114 LASSO Buy orders 2.592 2.555 2.407 2.556 LASSO successful 1.578 1.533 1.467 1.550

### A. Unexpected

There are many lead-lag relationships already documented in the academic literature at the weekly and monthly horizons. For example, Lo and MacKinlay (1990) and DeMiguel, Nogales, and Uppal (2014) both show that the returns of large stocks predict the future returns of small stocks, Chordia and Swaminathan (2000) show that the returns of high-volume stocks predict the future returns of low-volume stocks, and Hou (2007) shows that the returns of larger stocks within an industry predict the future returns of smaller stocks within the same industry. We now give evidence that the LASSO’s choice of predictors does not follow these existing lead-lag relationships—in other words, the LASSO identiﬁes an unexpected collection of predictors.

Econometric Approach. Suppose that stock n is one of the randomly chosen 250 stocks for which we use the LASSO to make one-minute-ahead return forecasts on day d. For each stock n′ ∈{1, . . . , N}, we deﬁne an indicator variable that is 1 if stock n′ was ever used by the LASSO as a predictor in any of the 356 forecasts for stock n on day d and 0 otherwise. Note that for computational reasons this indicator variable summarizes the contribution of all three lags of the n′th stock’s returns. We then use a logit regression with this indicator as the dependent variable to study how the characteristics of stock n′ are related


---

<!-- PDF page 25 -->

Sparse Signals in the Cross-Section of Returns 473

**Table VI Characteristics of LASSO Predictors**

This table presents the results of the characteristics of the predictors selected by the LASSO. On each trading day, d, from January 2005 to December 2012, the data contain one observation per predictor for each of the randomly selected 250 stocks for which we make one-minute-ahead return forecasts. For example, on October 6, 2010, the LASSO could choose as predictors any of the

N = 2,191 NYSE-listed stocks. So, on that day, our data contain 250 × 2,191 = 547,750 separate observations. Each column reports results from a different logit regression. Point estimates are log-odds ratios. Numbers in parentheses are standard errors clustered by day and predictor (i.e., stock n′). Numbers in square brackets are the marginal effects implied by the log-odds ratios. Dep. Variable: An indicator variable equals to 1 if stock n′ was ever used by the LASSO as a predictor when making one-minute-ahead return forecasts for stock n on day d. Mkt Cap > 50th percentile: An indicator variable equals to 1 if stock n′ had above-median market capitalization on day d. Volume > 50th percentile: An indicator variable equals to 1 if stock n′ had above-median trading volume on day d. Volatility > 50th percentile: An indicator variable equals to 1 if stock n′ had abovemedian one-minute-return volume on day d. Spread < 50th percentile: An indicator variable equal to 1 if stock n′ had a below-median average bid-ask spread on day d. In Same Industry: An indicator variable equals to 1 if stock n and stock n′ both belonged to the same three-digit SIC industry. The results indicate that there is little correlation between the LASSO’s choice of predictors and ﬁrm size, trading volume, return volatility, and the bid-ask spread, and that the LASSO is less likely to select a stock from the same industry as a predictor.

Dep. Variable: Ever Selected

Mkt Cap > 50th percentile 0.005 0.003 (0.004) (0.007) [0.11%] [0.07%]

Volume > 50th percentile 0.004 0.001 (0.004) (0.006) [0.09%] [0.01%]

Volatility > 50th percentile −0.005 −0.004 (0.004) (0.004) [0.13%] [0.10%] Spread < 50th percentile 0.002 0.006 (0.004) (0.006) [0.05%] [0.15%] In same industry −0.046 −0.046 (0.006) (0.006) [0.15%] [0.14%]

to the probability that the LASSO identiﬁes its lagged returns as a predictor for stock n at some point during the trading day.

Empirical Results. Table VI contains the results of these logit regressions. The ﬁrst column shows that the LASSO is no more likely to select large stocks than small stocks as predictors. The second column shows that infrequently traded stocks are just as likely to be selected as predictors by the LASSO as frequently traded stocks. The third column shows that return volatility is not related to the LASSO’s choice of predictors. And, the fourth column shows that the LASSO is equally likely to use liquid and illiquid stocks as predictors. In short, these four columns document a lack of correlation between


---

<!-- PDF page 26 -->

474 The Journal of Finance R ⃝

Figure 4. The LASSO’s penalty parameter. This ﬁgure plots the monthly average (solid line) and 95% conﬁdence interval (gray bands) for the LASSO’s cross-validated penalty parameter, λn, in units of % per month. The dashed line denotes sample average over the full sample period, which is 2.5%. Regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012. The results indicate that the LASSO typically ignores all predictors weaker than λ = 2.5% per month when making its one-minute-ahead return forecasts.

ﬁrm characteristics and the LASSO’s choice of predictors. The ﬁfth column, by contrast, reveals that the LASSO is 1.15% less likely to select a stock from the same industry as a predictor. Thus, the LASSO is not just selecting predictors based off of the intraindustry lead-lag effect documented in Hou (2007). The ﬁnal column shows that all of these patterns continue to hold up when these variables are included in the same regression speciﬁcation.

Penalty Parameter. How can the LASSO increase out-of-sample ﬁt at the one-minute horizon but still be so unrelated to ﬁrm characteristics? After all, researchers know that these characteristics are correlated with returns at the weekly and monthly horizons. This seeming contradiction resolves itself when we examine the size of the LASSO’s penalty parameter, λn. The LASSO sets all coefﬁcients smaller than λn to be precisely zero—that is, it completely ignores these predictors.

Figure 4 plots the mean and 95% conﬁdence interval for λn each month during our sample period. The horizontal dashed line denotes the sample average for λn, which is 2.5% per month. In other words, the LASSO typically ignores all predictors weaker than λ = 2.5% per month when making its one-minuteahead return forecasts. This lower bound is more than twice as large as the size of well-known predictors at the weekly and monthly horizon (McLean and Pontiff (2016), Harvey, Liu, and Zhu (2016), Linnainmaa and Roberts (2017)).

This is why our implementation of the LASSO at the one-minute horizon is not identifying the existing steady long-lived predictors documented in the academic literature. If they were to last an entire month, the predictors that we identify using the LASSO would result in outlandish returns that we do not see in practice. Put differently, existing steady long-lived predictors at weekly and monthly horizons are too weak at the one-minute horizon for the LASSO to detect. This ﬁnding suggests that cross-sectional return predictability at the one-minute horizon follows a different structure from cross-sectional return predictability at the one-week and one-month horizons.


---

<!-- PDF page 27 -->

Sparse Signals in the Cross-Section of Returns 475

Figure 5. Predictor duration. This ﬁgure plots the average (solid line) and 95% conﬁdence interval (gray bands) for the usage duration of the predictors chosen by the LASSO in units of minutes. The y-axis is on a log scale and represents the probability that a predictor is used by the LASSO when making one-minute-ahead return forecasts in more than x consecutive minutes. Tick marks on the x-axis represent the duration associated with a given quantile on the y-axis. Regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012. The results indicate that less than 5% of predictors selected by the LASSO are used for more than 14.2 consecutive minutes.

### B. Short-Lived

If the predictors identiﬁed by the LASSO would lead to unrealistic amounts of predictability if scaled up to the weekly or monthly horizons, then these predictors must not last that long. They must be short-lived. And this is indeed the case. To show this, we compute the length of time that the LASSO typically uses each predictor.

Econometric Approach. Suppose that stock n is one of the 250 randomly selected stocks for which we use the LASSO to make one-minute-ahead return forecasts on day d. Now, consider the ﬁrst minute that we generate a oneminute-ahead return forecast, 10:04 am. We collect all of the predictors used by the LASSO to make this return forecast for stock n. Then, in each subsequent minute, we compute the fraction of these predictors that are still being used by the LASSO to generate one-minute-ahead return forecasts for stock n. If stock n′ was used as a predictor in the LASSO’s return forecast at minute 10:04 am but not at minute 10:05 am, then we would say that this predictor had a duration of 1 minute; whereas, if stock n′ was used as a predictor at 10:04 am as well as every subsequent minute up to but not including 10:14 am, then we say that this predictor had a duration of 10 minutes. We repeat this calculation for each of the LASSO’s remaining 355 forecasts for stock n on that day. And, we do the same thing for every other stock on day d and for every other trading day as well.

Empirical Results. Figure 5 shows the results of these calculations. We ﬁnd that less than 5% of the predictors selected by the LASSO are used when making one-minute-ahead return forecasts in more than 14.2 consecutive minutes. And, less than 1% of predictors are used by the LASSO for more than 25.2 minutes in a row. The short duration of the LASSO’s predictors helps explain the lack of correlation between these predictors and ﬁrm characteristics.

Some Intuition. Financial economists tend to study particular time scales. The ﬁeld of market microstructure analyzes intraday events. People doing


---

<!-- PDF page 28 -->

476 The Journal of Finance R ⃝

asset pricing research consider phenomena at the daily, weekly, and monthly horizons. And, research on macroﬁnance topics focuses on questions about how markets evolve from one quarter or one year to the next.

Clearly, each of these horizon-speciﬁc subﬁelds is studying different aspects of the same underlying return process. There is only one return process for the S&P 500. Its one-minute returns in a month must sum up to its monthly return. So, it might seem odd that predictability at the one-month horizon does not imply predictability at the one-minute horizon. But, as illustrated in the parable of the blind men and the elephant (Holland and Quigley (1959)), the same underlying process can manifest itself in very different ways depending on the researcher’s perspective.

What is more, we are all familiar with processes that have different dynamics at different time scales in our everyday lives. Just think about how animals grow. A caterpillar hardly appears to change from one minute to the next, but it may be a butterﬂy by this time next week. Or, think about how languages evolve. At this time last year, the word “awful” had pretty much the same meaning as it does today (very unpleasant; “an awful stench”). But, centuries ago the word had nearly the opposite meaning (inspiring wonder; “the awful majesty of God”).3

When we look at the kinds of predictors selected by the LASSO, we ﬁnd something similar. Like caterpillars and butterﬂies, these predictors have little relation to the predictors at the weekly and monthly horizons documented in the academic literature. And, we can use the functional form of the LASSO’s optimization problem to shed light on how this can be the case. On one hand, in order to identify cross-sectional predictors fast enough, the LASSO has to ignore any source of predictability weaker than λ = 2.5% per month. On the other hand, the predictors identiﬁed by the LASSO typically last less than 15 minutes, making them imperceptible to monthly investors.

### C. Sparse

Finally, the LASSO should only increase out-of-sample ﬁt if there are unexpected short-lived signals in the cross-section of returns that are also sparse. We ﬁnd that, on average, the LASSO uses only 12.7 predictors (out of a possible 3 · N ≈6,000) when making its one-minute-ahead return forecasts for each stock. Figure 6 plots the average number of predictors, Sn,λ, used by the LASSO for each of its one-minute-ahead return forecasts in a given month, and the gray bands report the 95% conﬁdence interval. We further emphasize this point in Appendix C.

## IV. Economic Origins

The LASSO uses a purely statistical rule to identify candidate predictors that are too unexpected and short-lived to be pinned down by a researcher’s

3 See OED Online, March, 2017, Oxford University Press, https://goo.gl/DGkBEl.


---

<!-- PDF page 29 -->

Sparse Signals in the Cross-Section of Returns 477

Figure 6. Predictor sparsity. This ﬁgure plots the average (solid line) and 95% conﬁdence interval (gray bands) for the number of predictors, Sn,λ, used by the LASSO for each of its oneminute-ahead return forecasts in a given month. The dashed line denotes the sample average over the course of the entire sample period, which is 12.7 predictors. Regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012. The results indicate that, on average, the LASSO uses only 12.7 predictors (out of a possible 3 · N ≈6,000) when making its one-minute-ahead return forecasts for each stock.

intuition alone. However, because it does not rely on a researcher’s intuition, the LASSO’s increase in out-of-sample ﬁt could in principle have nothing to do with economic fundamentals. But, this is not what we ﬁnd in the data. And, we conclude our analysis by showing that the LASSO tends to identify as predictors the lagged returns of stocks with news about ﬁrm fundamentals. In other words, the LASSO identiﬁes predictors that are not easy to intuit but are still economically meaningful.

### A. Ravenpack Data

To investigate the link between the LASSO’s choice of predictors and realworld events, we use data from Ravenpack. Ravenpack has a partnership with Dow Jones, giving it access to the full Dow Jones news archive. These data consist of all Dow Jones Newswire and Wall Street Journal articles. The Dow Jones news archive is used in many prior studies (Kolasinski, Reed, and Riggenberg (2013), Shroff, Verdi, and Yu (2013), Dai, Parwada, and Zhang (2015)). Ravenpack data are time-stamped to the millisecond, which allows us to examine the relative timing of news announcements and the LASSO’s choice of predictors.

Because we are particularly interested in the link between the LASSO’s choice of predictors and economically meaningful events, we look only at news articles in the Ravenpack data about a company’s revenues. In addition, we restrict attention to articles that Ravenpack has labeled as “strongly relevant” for a NYSE-listed company. To make sure that we are not looking at stale news, we narrow our focus even further and only consider articles that Ravenpack labels as “news ﬂashes” and gives the highest novelty score to. We also remove any news articles about companies that had another revenue-related news ﬂash during the previous ﬁve days. Finally, we only consider news announcements that occur from 10:04 am to 3:59 pm. We are left with a collection of novel news ﬂashes about ﬁrm revenues that occur during normal trading hours.


---

<!-- PDF page 30 -->

478 The Journal of Finance R ⃝

Figure 7. The LASSO’s selection rate around news. This ﬁgure plots the LASSO’s selection rate around two types of news. x-axis: event time relative to news ﬂash (in minutes). Vertical dashed line: minute of news ﬂash about n′th stock’s revenues, h = 0. y-axis: difference between the number of times that the LASSO selected the n′th stock as a predictor when making its one-minuteahead return forecast for minute h and the number of times it did so for minute h = 0. Each dot denotes the difference in the LASSO’s selection rate in minute h relative to minute h = 0, with the large diamond denoting a difference of 0 for h = 0 (a normalization). Gray dots denote differences that are statistically signiﬁcant at the 5% level using standard errors clustered by year. The left panel corresponds to news ﬂashes about scheduled events. The right panel corresponds to news ﬂashes about unscheduled events. Estimation results are computed using the 61-minute window around each novel news ﬂash about an NYSE-listed stock’s revenues that occurred during normal trading hours from January 2005 to December 2012. The results indicate that when there is a scheduled news ﬂash about the n′th stock’s revenues in minute t, the LASSO selects stock n′ as a predictor slightly more often when making its one-minute-ahead return forecasts for minute t, that is, for h = 0, but if the news ﬂash is unscheduled, then the LASSO selects stock n′ as a predictor much more often when making its one-minute-ahead return forecasts in the 10 minutes prior to minute t.

### B. Event Study

Does the LASSO select a stock more often in the minutes around a news ﬂash about the ﬁrm’s revenues? Yes.

Econometric Approach. Suppose that there is a new ﬂash about the n′th

stock’s revenues in minute t. We deﬁne the event time, h, as the number of minutes since minute t. So, h = 0 denotes the minute that a news ﬂash occurs, h = 10 denotes the 10th minute afterward, and h = −12 denotes the 12th minute before. We then count the number of times that the LASSO uses stock n′ as a predictor when creating its one-minute-ahead return forecasts in each minute h ∈{ −30, . . . , −1, 0, 1, . . . , 30 }. We use the LASSO to create one-minute-ahead return forecasts for a randomly selected set of 250 stocks each minute, so the maximum number of times that the n′th stock could be chosen by the LASSO in a given minute is 250.

Empirical Results. The LASSO uses a purely statistical rule to identify candidate predictors. So, the LASSO’s choice of predictors could in principle have nothing to do with economic fundamentals. If this were the case, then the number of times that the LASSO selected the n′th stock would be constant with respect to event time, h. Figure 7 shows that this is not what is going on in the data. The x-axis counts minutes in event time. The dots denote the number of additional times that the LASSO selected the n′th stock in minute h relative to minute h = 0, with red dots denoting differences that are statistically different


---

<!-- PDF page 31 -->

Sparse Signals in the Cross-Section of Returns 479

from 0 at the 5% level using standard errors that are clustered by stock. The left panel of Figure 7 reports the change in the LASSO’s selection rate around scheduled news about ﬁrm revenues, and reveals that the LASSO selects stock n′ as a predictor slightly more often on the exact minute of the news ﬂash. The right panel reports the analogous results for unscheduled news. This panel shows that the LASSO selects stock n as a predictor when making its oneminute-ahead return forecast much more often in the 10 minutes leading up to the unscheduled news ﬂash.

Timing of Results. It might seem odd that the LASSO’s selection rate increases in the 10 minutes before an unscheduled news ﬂash. But, this lag makes sense upon further inspection. For example, think about 3M’s announcement about cutting 1,800 jobs on December 8, 2008. Or, consider St. Jude’s announcement of the acquisition of AGA medical on October 18, 2010. The market did not know that these announcements were coming. And, as a result, there was a several minute lag between when these announcements were actually made and when journalists broadcast the resulting news ﬂashes. By contrast, when journalists are expecting an announcement, there should be no such gap. Consistent with this intuition, we ﬁnd that the LASSO’s selection rate only increases for the exact minute of scheduled news ﬂashes, not in the 10 minutes before.

Regression Analysis. Table VII puts precise numbers on these results. Each column reports the results from a different regression. The dependent variable in all of these regressions is the number of times the n′th stock was selected as a predictor by the LASSO when making one-minute-ahead return forecasts in a given minute. The ﬁrst column shows that the LASSO uses stock n′ to make 0.115 fewer one-minute-ahead return forecasts in each of the 30 minutes leading up to a scheduled news ﬂash than it does in the minute of the news ﬂash and that the LASSO uses stock n′ to make 0.141 fewer one-minute-ahead return forecasts in each of the subsequent 30 minutes following a scheduled news ﬂash. The ﬁfth column of Table VII reports that the LASSO uses stock n′ to make 0.203 more one-minute-ahead return forecasts in each of the 10 minutes leading up to an unscheduled news ﬂash than it does in the minute of the news ﬂash.

The third and sixth columns in Table VII present two additional robustness checks on our results. First, Ravenpack characterizes each news ﬂash’s impact on overall market volatility over the course of the next several hours, and reports this information in a variable called “market impact,” which takes values from 0 (no impact on aggregate volatility) to 1 (large impact on aggregate volatility). Consistent with our original hypothesis that the LASSO is identifying unexpected short-lived predictors, we ﬁnd that the LASSO’s selection rate for stock n′ is not related to the aggregate effect of a news announcement over the next several hours. Ravenpack also assigns each news ﬂash a sentiment score ranging from 0 (pessimistic) to 1 (optimistic). The sentiment of the news ﬂash also appears unrelated to the LASSO’s selection rate in any statistically signiﬁcant manner.


---

<!-- PDF page 32 -->

480 The Journal of Finance R ⃝

**Table VII The LASSO’s Selection Rate around News**

This table presents results of the change in the LASSO’s selection rate around news ﬂashes about a company’s revenues. Each column reports results from a different regression. Point estimates have units of number of times selected per minute. Numbers in parentheses are standard errors clustered by year. Dots denote omitted estimates for the reference category, h = 0. Dep. Variable: Number of times that the n′th stock was selected as a predictor by the LASSO in minute (t + h). Impact: A 0 (low) to 1 (high) variable summarizing the impact of a news ﬂash on overall market volatility during the next several hours. Sentiment: A 0 (very negative) to 1 (very positive) variable summarizing the sentiment of the text contained in a news ﬂash. The left columns report results of news ﬂashes about scheduled events. The right columns report results of news ﬂashes about unscheduled events. Regression are run on the 61-minute window around each novel news ﬂash about an NYSE-listed stock’s revenues that occurred during normal trading hours from January 2005 to December 2012. The results indicate that the LASSO uses stock n′ to make 0.115 fewer one-minute-ahead return forecasts in each of the 30 minutes leading up to a scheduled news ﬂash, 1−30≤h<0, than it does in the minute of the news ﬂash itself, h = 0. By contrast, the LASSO uses stock n′ to make 0.203 more one-minute-ahead return forecasts in each of the 10 minutes leading up to an unscheduled news ﬂash, 1−10≤h<0.

Dep. Variable: Times Selected [Number/Minute]

Scheduled News Unscheduled News

1{−30≤h<0} −0.115 −0.113 (0.058) (0.101) 1{h=0} · ·

1{30≥h>0} −0.141 0.026 (0.054) (0.091)

1{−30≤h<−20} −0.139 −0.139 −0.029 −0.029 (0.072) (0.073) (0.120) (0.120)

1{−20≤h<−10} −0.124 −0.123 −0.153 −0.153 (0.070) (0.070) (0.124) (0.124)

1{−10≤h<0} −0.086 −0.085 0.203 0.202 (0.056) (0.056) (0.094) (0.094) 1{h=0} · · · ·

1{10≥h>0} −0.156 −0.157 0.008 0.008 (0.050) (0.050) (0.086) (0.086)

1{20≥h>10} −0.126 −0.127 0.001 0.001 (0.063) (0.063) (0.108) (0.108)

1{30≥h>20} −0.142 −0.142 0.069 0.069 (0.066) (0.066) (0.109) (0.109)

Impact 0.201 −0.142 (0.318) (0.876)

Sentiment 0.170 −1.090 (0.209) (0.659)

Year FE Y Y Y Y Y Y


---

<!-- PDF page 33 -->

Sparse Signals in the Cross-Section of Returns 481

## V. Conclusion

In this paper, we apply the LASSO rather than intuition to identify unexpected short-lived predictors, such as the lagged returns of Family Dollar Corp. We ﬁnd that using the LASSO increases both out-of-sample ﬁt and forecastimplied Sharpe ratios, and we show that this increase in out-of-sample ﬁt comes from identifying predictors that are unexpected, short-lived, and sparse. Finally, we document that these predictors are often the lagged returns of stocks with recent news about ﬁrm fundamentals. Thus, the LASSO identiﬁes predictors that are not easy to intuit but still economically meaningful.

Initial submission: May 27, 2016; Accepted: November 17, 2017 Editors: Bruno Biais, Michael R. Roberts, and Kenneth J. Singleton

Appendix A: Numerical Simulations

In this appendix, we use the LASSO to make one-minute-ahead return forecasts in simulated data. The goal is to show that if there are sparse signals in the cross-section of returns, then the LASSO increases out-of-sample ﬁt. And, if there are not (either no signals or too many signals), then it does not.

### A. Data-Generating Process

We run 1,000 simulations. For each simulation, we generate one-minute returns for 100 stocks over the course of T = 1, 301 minutes using the following data-generating process

100 

β⋆

rn,t = 0 +

n,t. (A.1)

(n,n′),t · rn′,t−1 + 0.001 · ε⋆

n′=1

In the equation above, rn,t is the return of the nth stock in minute t, β⋆

(n,n′),t is the predictive power of the n′th stock’s lagged return in minute (t −1) when forecasting the nth stock’s return in minute t, and ε⋆

n,t

iid∼N(0, 1) is a noise term. For computational convenience, we only consider a single lag.

In our main analysis, each stock’s return in minute t is governed by its exposure to the lagged returns of a collection of ﬁve stocks in minute (t −1). We use St to denote this active set. For all 95 stocks, n′ /∈St, β⋆

(n,n′),t = 0. For all n′ ∈St, we choose the values of β⋆

(n,n′),t as follows:

t = 1: Prior to the start of trading, we initialize the model by randomly se-

lecting a set of ﬁve stocks to serve as S1. We determine the exposure of every stock n ∈{1, . . . , 100} to the lagged returns of the ﬁve stocks n′ ∈S1 using the rule



β⋆

iid∼

(n,n′),1

+0.19 w/ probability 50% −0.19 w/ probability 50% . (A.2)


---

<!-- PDF page 34 -->

482 The Journal of Finance R ⃝

t > 1: Prior to each subsequent minute, we draw ﬁve random variables zn′,t

iid∼ Unif[0, 1]—that is, one for each n′ ∈St−1. If a particular zn′,t > 0.01, then predictor n′ ∈St−1 remains in St. And, all 100 values of β⋆

(n,n′),t associated with this predictor remain the same. But, if zn′,t ≤0.01, then predictor n′ ∈St−1 is replaced at random with one of the remaining 95 stocks. And, we redraw each of the 100 stocks’ exposures to this new predictor exactly as described in equation (A.2).

Note that once a predictor gets added to St, it remains in the active set for (1 −0.01)/0.01 = 99 minutes on average. There are 100 stocks. So, the collection of ﬁve predictors in the active set is too short-lived to be estimated with an OLS regression.

### B. Estimation and Forecast Timing

We use the LASSO to make one-minute-ahead return forecasts for stock n = 1 in periods t = 302, . . . , 1, 301 exactly as we did in the main text, only using an

L = 50-minute estimation window. We burn the ﬁrst 250 periods to make sure that the initial conditions are not affecting our results. This procedure produces a total of 1,000 return forecasts per simulation. We also ﬁt two different OLS speciﬁcations to the same data. The ﬁrst is an AR(1) model that only uses a stock’s own lagged return as a predictor. The second is a market model that uses lagged values of the equally weighted market as a predictor.

### C. Out-of-Sample Fit

The dark-gray shading in the left panel of Figure A1 shows that the average out-of-sample ﬁt of the LASSO’s one-minute-ahead return forecast is 0.281%. Just like in Section II.B, we measure the LASSO’s out-of-sample ﬁt using the adjusted-R2 statistic. This explains why the out-of-sample ﬁt can sometimes be negative. By contrast, the dark-gray shading in the middle panel shows that the average out-of-sample ﬁt of the AR(1) benchmark is only 0.003%, while the dark-gray shading in the right panel shows that the average out-ofsample ﬁt of the market benchmark is only 0.004%. The light-gray shading in each of these panels displays the out-of-sample ﬁt of using both the LASSO and a benchmark model to predict future returns. In both cases, the LASSO signiﬁcantly increases the out-of-sample ﬁt, boosting the average adjusted-R2

to more than 0.300%.

### D. Oracle Regression

Is an adjusted R2 ≈0.300% big or small? To get a sense of how much outof-sample ﬁt is possible given the data-generating process in equation (A.1), we make one-minute-ahead return forecasts using two different versions of an oracle estimator. First, we estimate an OLS regression using the ﬁve true predictors governing the cross-section of returns in minute t, n′ ∈St. The left


---

<!-- PDF page 35 -->

Sparse Signals in the Cross-Section of Returns 483

Figure A1. Out-of-sample ﬁt, simulated data. The ﬁgure plots out-of-sample ﬁt of regressions using simulated data generated by equation (A.1). x-axis: adjusted-R2 in percentage. The left panel plots the distribution of adjusted-R2s in regressions involving only the LASSO’s one-minute-ahead return forecast. The vertical line denotes the average adjusted-R2 from these regressions. In the middle panel, dark-gray shading denotes the distribution of adjusted-R2s in predictive regressions involving only the AR(1) benchmark’s one-minute-ahead return forecast, while the light-gray shading denotes the distribution of adjusted-R2s in regressions involving the one-minute-ahead return forecasts from both the LASSO and the AR(1) benchmark. Vertical lines denote the average adjusted-R2s from each speciﬁcation. In the right panel, dark-gray shading denotes the distribution of adjusted-R2s in predictive regressions involving only the market benchmark’s one-minute-ahead return forecast, while the light-gray shading denotes the distribution of adjusted-R2s in predictive regressions involving the one-minute-ahead return forecasts from both the LASSO and the market benchmark. Vertical lines denote the average adjusted-R2s from each speciﬁcation. The results indicate that including the LASSO’s one-minute-ahead return forecast boosts the out-of-sample ﬁt in simulated data.

panel of Figure A2 shows that, even if you knew the correct ﬁve predictors to use each minute, the best adjusted-R2 you could hope for would be 0.525%. So, the LASSO captures a little more than half of the possible variation in returns.

This ﬁrst oracle speciﬁcation is labeled “Oracle (Exact)” in Figure A2. We use this name because this speciﬁcation knows exactly which ﬁve predictors to use when making return forecasts each minute during the 50-minute estimation window. But, during any given estimation window, the active set of ﬁve predictors could change. Even though there are only ﬁve stocks in St at any one point in time, there might be a total of six or seven stocks that were each included in St at some point in time during an estimation window. To see how accounting for these additional predictors would affect our results, we also estimate an oracle speciﬁcation that uses all stocks that belonged to St at some point during the estimation window. The right panel of Figure A2, which we label as “Oracle (All),” shows that including every stock that ever belonged to the active set drops the out-of-sample ﬁt to 0.130%.

The second version of the oracle estimator fares worse than the LASSO’s because only ﬁve predictors belong to the active set, St, that is used to generate the returns for minute t. Any additional predictors that were included in some {St−h}0<h≤50 but not in St will not add any out-of-sample predictive power. They are spurious predictors. And, the LASSO’s penalty function mitigates the problem posed by such spurious predictors.


---

<!-- PDF page 36 -->

484 The Journal of Finance R ⃝

Figure A2. Oracle out-of-sample ﬁt, simulated data. This ﬁgure plots the out-of-sample ﬁt from predictive regressions using simulated data generated by equation (A.1). x-axis: adjusted

R2 from a predictive regression in percent. The left panel plots the distribution of adjusted-R2s in predictive regressions involving an oracle speciﬁcation using the exact active set. The vertical line denotes the average adjusted-R2 from these predictive regressions. The right panel plots the distribution of adjusted-R2s in predictive regressions involving an oracle speciﬁcation using every predictor that ever belonged to the active set during the estimation window. The vertical line denotes the average adjusted-R2 from these predictive regressions. The results indicate that the maximum out-of-sample ﬁt that you could achieve—that is, if you knew exactly which ﬁve predictors to include in your OLS regression—is 0.525%.

Figure A3. Number of predictors, simulated data. The ﬁgure plots the LASSO’s choice of predictors. The left panel plots the number of predictors selected by the LASSO each minute when making its one-minute-ahead return forecasts using the data simulated from equation (A.1). The vertical line denotes the sample average across all simulations. The right panel plots the number of predictors selected by the LASSO that belong to the true active set, St. The vertical line denotes the sample average across all simulations. The results indicate that the LASSO selects a predictor in the active set roughly 80% of the time.

E. Number of Predictors

The left panel of Figure A3 shows that the LASSO typically selects 6.736 predictors when making its one-minute-ahead return forecasts each minute. The right panel of Figure A3 shows that, on average, only 0.779 of these predictors belong to the true active set, St, in any given minute. It might seem surprising that the LASSO can achieve more than half of the oracle’s out-of-sample ﬁt while correctly identifying less than one-ﬁfth of the active set. But this is another consequence of the LASSO’s penalty function, which shrinks weak predictors toward zero. The fact that the LASSO has such a high


---

<!-- PDF page 37 -->

Sparse Signals in the Cross-Section of Returns 485

Figure A4. Out-of-sample ﬁt, simulated data with no predictors. This ﬁgure plots the outof-sample ﬁt from regressions using simulated data generated by equation (A.3), which contains no predictors for the LASSO to ﬁnd. x-axis: adjusted R2 from regressions in percent. The left panel plots the distribution of adjusted-R2s in regressions involving only the LASSO’s one-minute-ahead return forecast. The vertical line denotes the average adjusted-R2 from these regressions. In the middle panel, dark-gray shading denotes the distribution of adjusted-R2s in regressions involving only the AR(1) benchmark’s one-minute-ahead return forecast, while light-gray shading denotes the distribution of adjusted-R2s in regressions involving the one-minute-ahead return forecasts from both the LASSO and the AR(1) benchmark. Vertical lines denote the average adjusted-

R2s from each speciﬁcation. In the right panel, dark-gray shading denotes the distribution of adjusted-R2s in regressions involving only the market benchmark’s one-minute-ahead return forecast, while light-gray shading denotes the distribution of adjusted-R2s in regressions involving the one-minute-ahead return forecasts from both the LASSO and the market benchmark. Vertical lines denote the average adjusted-R2s from each speciﬁcation. The results indicate that the LASSO does not increase out-of-sample ﬁt when there are no predictors.

out-of-sample ﬁt means that it is substantially shrinking the 6.736 −0.779 = 5.957 spurious predictors it selects each minute.

F. Placebo Tests

Finally, we conclude this appendix by looking at two alternative simulations where the LASSO should not increase out-of-sample ﬁt. In the ﬁrst setting, there are no predictors—that is, we simulate the returns for the 100 stocks using the data-generating process





. (A.3)

0.001 · ε⋆

rn,t = 0.125 ×

n,t

The factor of 0.125 is chosen so that the resulting time series have the same standard deviation as in equation (A.1). Figure A4 conﬁrms that, when there are no predictors for the LASSO to ﬁnd, using the LASSO does not increase out-of-sample ﬁt.

Then, in the second setting, we look at the other extreme where the predictors are dense—that is, we simulate the returns for the 100 stocks using the datagenerating process in equation (A.1) but with 75 rather than 5 stocks in the


---

<!-- PDF page 38 -->

486 The Journal of Finance R ⃝

Figure A5. Out-of-sample ﬁt, simulated data with dense predictors. The ﬁgure plots the out-of-sample ﬁt from regressions using simulated data generated by equation (A.1) with an active set containing 75 rather than ﬁve stocks. x-axis: adjusted-R2 from regression in percent. The left panel plots the distribution of adjusted-R2s in regressions involving only the LASSO’s one-minute-ahead return forecast. The vertical line denotes the average adjusted-R2 from these regressions. In the middle panel, dark-gray shading denotes the distribution of adjusted-R2s in regressions involving only the AR(1) benchmark’s one-minute-ahead return forecast, while light-gray shading denotes the distribution of adjusted-R2s in regressions involving the one-minute-ahead return forecasts from both the LASSO and the AR(1) benchmark. Vertical lines denote the average adjusted-R2s from each speciﬁcation. In the right panel, dark-gray shading denotes the distribution of adjusted-R2s in predictive regressions involving only the market benchmark’s one-minute-ahead return forecast, while light-gray shading denotes the distribution of adjusted-R2s in regressions involving the one-minute-ahead return forecasts from both the LASSO and the market benchmark. The results indicate that the LASSO does not increase out-of-sample ﬁt when there are more predictors than minutes in the estimation window.

active set. Again, to keep the standard deviation of returns constant, we choose β⋆

(n,n′),t using the rule



β⋆

(n,n′),t = 5

75 ×

+0.19 w/ probability 50% −0.19 w/ probability 50% · (A.4)

Figure A5 conﬁrms that, when there are more predictors in the active set, |St| = 75, than minutes in the estimation window, L = 50, the LASSO does not increase out-of-sample ﬁt. Thus, the LASSO really is only identifying sparse signals.

Appendix B: Signiﬁcance Test

We use the approach from Giacomini and White (2006) to assess statistical signiﬁcance using a Wald-type test outlined in Theorem 1. The results in Giacomini and White’s (2006) Theorem 1 are framed in terms of loss in forecasting power, Ln,t+1, and a test function, ht, whereas we frame our results in terms of changes in R2. Here is the connection.

First, let eBmk

n,t+1 denote the prediction error when using only the one-minuteahead return forecast from a benchmark model, and let eBoth

n,t+1 denote the prediction error when using the one-minute-ahead return forecasts from both


---

<!-- PDF page 39 -->

Sparse Signals in the Cross-Section of Returns 487

the benchmark model and the LASSO. And, let the loss in forecasting power be the increase in squared prediction error from using only the benchmark model

2

2

def=

−

eBmk

eBoth

. (B.1)

Ln,t+1

n,t+1

n,t+1

If using the LASSO in addition to the benchmark model does not increase out-of-sample ﬁt, then

E[Ln,t+1] = 0. (B.2)

This is the null hypothesis. The alternative hypothesis is that E[Ln,t+1] > 0.

Next, notice that the expected loss in forecasting power divided by the realized variation in returns can be written as the change in R2:





E

(eBmk

E

(eBoth

E[Ln,t+1]

n,t+1)2

n,t+1)2

=

−

(B.3a)

Var[rn,t+1]

Var[rn,t+1]

Var[rn,t+1]





E

(eBmk

E

(eBoth

n,t+1)2

n,t+1)2

= −1 +

+ 1 −

(B.3b)

Var[rn,t+1]

Var[rn,t+1]













E

(eBoth

E

(eBmk

n,t+1)2

n,t+1)2

=

−

1 −

1 −

(B.3c)

Var[rn,t+1]

Var[rn,t+1]

= ¯R2,Both

n −¯R2,Bmk

n (B.3d)

=  ¯R2

n . (B.3e)

Finally, assume that ht = 1. We know that  ¯R2

n →χ2

1 , so Giacomini and White’s (2006) Theorem 1 implies that we can use a standard t-test to evaluate the statistical signiﬁcance of changes in R2. The authors highlight this observation in Comment 7 of their paper.

Appendix C: Source of Gains

As noted earlier, the term “LASSO” is an acronym standing for the Least Absolute Shrinkage and Selection Operator. And, as suggested by this name, the LASSO’s penalty function is performing two separate tasks.

### A. Shrinkage without Selection

First, it is selecting coefﬁcients larger than λn. In the top panel of Table C1, we study the role of selection in the LASSO’s increase in out-of-sample ﬁt. We do this by examining the LASSO’s increase in out-of-sample ﬁt relative to alternative benchmark models that already incorporate some form of shrinkage.


---

<!-- PDF page 40 -->

488 The Journal of Finance R ⃝

Table C1 Increase in Out-of-Sample Fit, Source of Gains

This table presents the source of the LASSO’s increase in out-of-sample ﬁt relative to the AR(3) and market benchmarks. The increase in out-of-sample ﬁt is measured as the percentage point increase in adjusted-R2. Regressions are run on a randomly selected subset of 250 stocks on each trading day from January 2005 to December 2012. ¯R2,Bmk

n : Out-of-sample ﬁt of benchmark model.  ¯R2

n: Increase in out-of-sample ﬁt for the LASSO or alternative procedure. p-value: Probability of observing the realized  ¯R2

n under the null hypothesis of no increase in out-of-sample ﬁt. Numbers in parentheses are standard errors clustered by stock-day. Numbers in square brackets are 95% conﬁdence intervals. The top panel reports shows LASSO’s increase in out-of-sample ﬁt relative to alternative benchmark models that involve shrinkage but no selection. Ridge: Ridge regression estimated using three lags. Average OLS: Weighted average of AR(3) and market benchmark models. The middle panel shows LASSO’s increase in out-of-sample ﬁt for alternative procedures that involve selection but no shrinkage. Single-Best Predictor: OLS regression using the single predictor with the highest correlation during the 30-minute estimation window. Postselection OLS: OLS regression using predictors selected by the LASSO. The bottom panel shows the LASSO’s increase in out-of-sample ﬁt when using a penalty parameter that is one standard deviation too large.

No Selection

¯R2,Bmk

n [%]  ¯R2

n [Percentage Points] p-Value

Ridge 1.182 2.447 [2.395, 2.498] 0.000 (0.012) (0.026)

Average OLS 6.210 1.302 [1.276, 1.328] 0.000 (0.065) (0.013)

No Shrinkage

AR(3) Benchmark Market Benchmark

 ¯R2

n [Percentage Points] p-Value  ¯R2

n [Percentage Points] p-Value

Single-best predictor 0.474 [0.464, 0.485] 0.000 0.671 [0.658, 0.685] 0.000 (0.005) (0.007)

Postselection OLS 1.245 [1.218, 1.271] 0.000 2.544 [2.483, 2.604] 0.000 (0.013) (0.031)

Lambda Noise

AR(3) Benchmark Market Benchmark

 ¯R2

n [Percentage Points] p-Value  ¯R2

n [Percentage Points] p-Value

LASSO, λ+s.e

n 0.829 [0.807, 0.851] 0.000 1.555 [1.518, 1.592] 0.000 (0.011) (0.019)

If the LASSO’s increase in out-of-sample ﬁt were due only to coefﬁcient shrinkage and not to selection, then using the LASSO in addition to one of these benchmark models should yield  ¯R2

n = 0 percentage points. We consider two different kinds of pure-shrinkage benchmarks. To start with, we compute one-minute-ahead return forecasts using Ridge (Hastie, Tibshirani, and Friedman (2001, Section 3.4)). The ﬁrst row shows that


---

<!-- PDF page 41 -->

Sparse Signals in the Cross-Section of Returns 489

shrinkage on its own actually results in a lower out-of-sample ﬁt. And, the LASSO increases out-of-sample ﬁt relative to this pure-shrinkage benchmark.

The second row contains a weighted average of the one-minute-ahead return forecasts generated by the AR(3) and market benchmarks as suggested in Rapach, Strauss, and Zhou (2010). Consistent with their original results, we ﬁnd that averaging these forecasts generates a higher out-of-sample ﬁt than including each of the forecasts separately: ¯R2,Bmk

n = 6.210% versus ¯R2,Bmk

n = 5.553%. But, the LASSO still increases out-of-sample ﬁt relative to the weighted-average benchmark by  ¯R2

n = 1.302 percentage points.

### B. Selection without Shrinkage

Second, the LASSO is shrinking the point estimates of all selected coefﬁcients by λn. The middle panel investigates whether this shrinkage component is key to the LASSO’s increase in out-of-sample ﬁt. We do this by examining whether LASSO alternatives, which do not use any sort of shrinkage, increase out-ofsample ﬁt by more than the LASSO does.

Again, we take two different approaches. The ﬁrst row shows that using an OLS regression that only includes the single predictor with the highest insample correlation performs much worse than the LASSO. This is tantamount to applying a forward-stepwise procedure to the standard OLS-regression framework. The second row shows that using a two-step procedure that ﬁts an OLS regression to the predictors selected by the LASSO generates the same increase in out-of-sample ﬁt as using just the LASSO itself. This result suggests that there are not substantial gains to be made by postselection inference. It also implies that using an alternative sparse-selection procedure, such as the adaptive LASSO (Zou (2006)) or elastic net (Zou and Hastie (2005)), will not qualitatively affect our results because these procedures only differ from the LASSO in the amount of shrinkage.

### C. Lambda Noise

Finally, recall that our implementation of the LASSO selects the penalty parameter, λn, for each stock within each 30-minute estimation window using

K-fold cross-validation. This means that our choice of λn contains some estimation error. In the bottom panel of Table C1 we examine the effect of this estimation error on our results. We do so by testing whether the LASSO still increases out-of-sample ﬁt even when we use a penalty parameter that is one standard deviation too large in terms of the optimal λn’s cross-validation error. We ﬁnd that, while using λ+s.e.

n rather than the optimal λn reduces the LASSO’s gains, it does not eliminate them.4

4 We look only at alternative values of λn that are larger than the optimal λn. Here is why. If you take λn →∞, then the LASSO ignores all predictors and simply estimates the mean. So, conditional on the LASSO converging at the optimal λn, any alternative choice for λn that is larger than this optimal value will deliver well-deﬁned parameter estimates. However, shrinking λ →0


---

<!-- PDF page 42 -->

490 The Journal of Finance R ⃝

REFERENCES

Abadie, Alberto, and Maximilian Kasy, 2017, The risk of machine learning, Working paper, MIT

and Harvard University. Akaike, Hirotugu, 1974, A new look at the statistical model identiﬁcation, IEEE Transactions on

Automatic Control 19, 716–723. Arora, Mohit, How secure is AES against brute-force attacks? Electrical Engineering Times (newsletter), May 7, 2012. Available at https://www.eetimes.com/document.asp?doc_ id=1279619. Asness, Clifford, Tobias Moskowitz, and Lasse Pedersen, 2013, Value and momentum everywhere,

Journal of Finance 68, 929–985. Banz, Rolf, 1981, The relationship between the returns and the market values of common stocks,

Journal of Financial Economics 9, 3–18. Boyd, Stephen, and Lieven Vandenberghe, 2004, Convex Optimization (Cambridge University

Press, Cambridge). Brogaard, Jonathan, Terrence Hendershott, and Ryan Riordan, 2014, High-frequency trading and

price discovery, Review of Financial Studies 27, 2267–2306. Bryzgalova, Svetlana, 2017, Spurious factors in linear asset-pricing models, Working paper, Stan-

ford University. Campbell, John, and Samuel Thompson, 2008, Predicting excess stock returns out of sample: Can

anything beat the historical average? Review of Financial Studies 21, 1509–1531. Candes, Emmanuel, and Yaniv Plan, 2009, Near-ideal model selection by ℓ1 minimization, Annals

of Statistics 37, 2145–2177. Carhart, Mark, 1997, On persistence in mutual-fund performance, Journal of Finance 52, 57–82. Chinco, Alex, 2017, Feature-selection risk, Working paper, University of Illinois at Urbana-

Champaign. Chordia, Tarun, and Bhaskaran Swaminathan, 2000, Trading volume and cross-autocorrelations

in stock returns, Journal of Finance 55, 913–935. Cohen, Lauren, and Andrea Frazzini, 2008, Economic links and predictable returns, Journal of

Finance 63, 1977–2011. Dai, Lili, Jerry Parwada, and Bohui Zhang, 2015, The governance role of the media through news

dissemination: Evidence from insider trading, Journal of Accounting Research 53, 331–366. Dangl, Thomas, and Michael Halling, 2012, Predictive regressions with time-varying coefﬁcients,

Journal of Financial Economics 106, 157–181. DeMiguel, Victor, Lorenzo Garlappi, Francisco Nogales, and Raman Uppal, 2009, A generalized

approach to portfolio optimization: Improving performance by constraining portfolio norms, Management Science 55, 798–812. DeMiguel, Victor, Lorenzo Garlappi, and Raman Uppal, 2009, Optimal versus na¨ıve diversiﬁcation:

How inefﬁcient is the 1/n portfolio strategy? Review of Financial Studies 22, 1915–1953. DeMiguel, Victor, Francisco Nogales, and Raman Uppal, 2014, Stock-return serial dependence and

out-of-sample portfolio performance, Review of Financial Studies 27, 1031–1073. Du, Songzi, and Haoxiang Zhu, 2017, What is the optimal trading frequency in ﬁnancial markets?

Review of Economic Studies, 84, 1606–1651. Efron, Bradley, and Trevor Hastie, 2016, Computer-Age Statistical Inference (Cambridge Univer-

sity Press, Cambridge). Fama, Eugene, and Kenneth French, 1993, Common risk factors in the returns on stocks and

bonds, Journal of Financial Economics 33, 3–56. Feng, Guanhao, Stefano Giglio, and Dacheng Xiu, 2017, Taming the factor zoo, Working paper,

City University of Hong Kong, Yale University, and University of Chicago. Ferson, Wayne, and Campbell Harvey, 1991, The variation of economic risk premiums, Journal of

Political Economy 99, 385–415.

means including more predictors. So, alternative values of λn that are smaller than the best-ﬁt penalty parameter might allow for more than 30 predictors, which would yield parameter estimates that are not well deﬁned (i.e., that will depend on the details of the optimization algorithm used).


---

<!-- PDF page 43 -->

Sparse Signals in the Cross-Section of Returns 491

Foster, Dean, and Edward George, 1994, The risk inﬂation criterion for multiple regression, Annals

of Statistics 22, 1947–1975. Foucault, Thierry, Johan Hombert, and Ioanid Rosu, 2016, News trading and speed, Journal of

Finance 71, 335–382. Frazzini, Andrea, Ronen Israel, and Tobias Moskowitz, 2017, Trading costs of asset-pricing anoma-

lies, Working paper, AQR Capital Management and Yale University. Freyberger, Joachim, Andreas Neuhierl, and Michael Weber, 2017, Dissecting characteristics non-

parametrically, Working paper No. 23227, NBER. Friedman, Jerome, Trevor Hastie, and Rob Tibshirani, 2010, Regularization paths for generalized

linear models via coordinate descent, Journal of Statistical Software 33, 1–22. Gabaix, Xavier, 2014, A sparsity-based model of bounded rationality, Quarterly Journal of

Economics 129, 1661–1710. Giacomini, Raffaella, and Halbert White, 2006, Tests of conditional predictive ability, Econometrica

74, 1545–1578. Harvey, Campbell, Yan Liu, and Heqing Zhu, 2016, . . . and the cross-section of expected returns,

Review of Financial Studies 29, 5–68. Hasbrouck, Joel, 2009, Trading costs and returns for U.S. equities: Estimating effective costs from

daily data, Journal of Finance 64, 1445–1477. Hastie, Trevor, Robert Tibshirani, and Jerome Friedman, 2001, The Elements of Statistical Learn-

ing: Data Mining, Inference, and Prediction (Springer Science & Business Media, Berlin). Hoffman, Peter, 2014, A dynamic limit-order market with fast and slow traders, Journal of Finan-

cial Economics 113, 156–169. Holland, Janice, and Lillian Quigley, 1959, The Blind Men and the Elephant (Charles Scribner’s

Sons, New York). Hou, Kewei, 2007, Industry information diffusion and the lead-lag effect in stock returns, Review

of Financial Studies 20, 1113–1138. Jegadeesh, Narasimhan, and Sheridan Titman, 1993, Returns to buying winners and selling losers:

Implications for stock-market efﬁciency, Journal of Finance 48, 65–91. Kacperczyk, Marcin, Stijn Van Nieuwerburgh, and Laura Veldkamp, 2014, Time-varying fund-

manager skill, Journal of Finance 69, 1455–1484. Kolasinski, Adam, Adam Reed, and Matthew Riggenberg, 2013, A multiple-lender approach to

understanding supply and search in the equity lending market, Journal of Finance 68, 559– 595. Korajczyk, Robert, and Ronnie Sadka, 2004, Are momentum proﬁts robust to trading costs? Journal

of Finance 59, 1039–1082. Kozak, Serhiy, Stefan Nagel, and Shrihari Santosh, 2017, Shrinking the cross-section, Working

paper No. 24070, NBER. Linnainmaa, Juhani, and Michael Roberts, 2017, The history of the cross section of stock returns,

Working paper No. 22894, NBER. Lo, Andrew, and Craig MacKinlay, 1990, When are contrarian proﬁts due to stock-market overre-

action? Review of Financial Studies 3, 175–205. Manela, Asaf, and Alan Moreira, 2017, News-implied volatility and disaster concerns, Journal of

Financial Economics 123, 137–162. McLean, David, and Jeffrey Pontiff, 2016, Does academic research destroy stock-return predictabil-

ity? Journal of Finance 71, 5–32. Meinshausen, Nicolai, and Bin Yu, 2009, LASSO-type recovery of sparse representations for high-

dimensional data, Annals of Statistics 37, 246–270. Natarajan, Balas, 1995, Sparse approximate solutions to linear systems, SIAM Journal of

Computations 24, 227–234. Novy-Marx, Robert, 2017, Backtesting strategies based on multiple signals, Working paper No.

21329, NBER. Novy-Marx, Robert, and Mihail Velikov, 2015, A taxonomy of anomalies and their trading costs,

Review of Financial Studies 29, 104–147. Patton, Andrew, and Brian Weller, 2017, What you see is not what you get: The costs of trading

market anomalies, Working paper, Duke University.


---

<!-- PDF page 44 -->

492 The Journal of Finance R ⃝

Pedersen, Lasse, 2015, Efﬁciently Inefﬁcient: How Smart Money Invests and Market Prices Are

Determined (Princeton University Press, Princeton, NJ). Rapach, David, Jack Strauss, and Guofo Zhou, 2010, Out-of-sample equity-premium prediction:

Combination forecasts and links to the real economy, Review of Financial Studies 23, 821–862. Schwarz, Gideon, 1978, Estimating the dimension of a model, Annals of Statistics 6, 461–464. Shroff, Nemit, Rodrigo Verdi, and Gwen Yu, 2013, Information environment and the investment

decisions of multinational corporations, Accounting Review 89, 759–790. Tibshirani, Robert, 1996, Regression shrinkage and selection via the LASSO, Journal of the Royal

Statistical Society: Series B 58, 267–288. Ulam, Stainislaw, 1976, Adventures of a Mathematician (Scribners, New York). Zou, Hui, 2006, The adaptive LASSO and its oracle properties, Journal of the American Statistical

Association 101, 1418–1429. Zou, Hui, and Trevor Hastie, 2005, Regularization and variable selection via the elastic net, Journal

of the Royal Statistical Society: Series B 67, 301–320.

