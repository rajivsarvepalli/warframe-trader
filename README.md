# [Warframe Trader](https://rajivsarvepalli.pythonanywhere.com/)

[Warframe trader](https://rajivsarvepalli.pythonanywhere.com/) is a website designed to analyze the data collected by [warframe market](https://warframe.market/) and make predictions for the in-game market on warframe.

The website is availbale at: https://rajivsarvepalli.pythonanywhere.com/.

## Motivation

When using warframe market to look at the prices of items, I thought it would be interesting to see more statistics collected on the prices of in-game items and see if
any prediction techniques could work on these warframe items. I hoped to add a more meaningful way of viewing the statistics collected by warframe market. Additionally,
I am working to try to keep a collection of the complete data as time goes on. As of now, warframe market only keeps the past 90 days whereas I intend to keep adding data as
they release it so that people are able to track months, and potentially even years of warframe market data.

## Graphs

The graphs are used with classic stock indicators. Many of these indicators may not provide super meaningful information since they are designed for stocks and warframe items are traded
in much smaller quantities than anything on the stock market. So there is much less data to get accurate metrics, and therefore the indicators are certainly not as helpful as with stocks.
However, I still found them interesting and worth sharing, so I worked to add them to this website.

## Prime Rankings

This is based on predicting what prime parts will go up and down in prices. This process is designed for those wanting to either buy prime parts, or to decide whether to sell
their current prime parts right now. However, this is not a perfect process and only is estimated based on the data. I would expect most people to do better if they looked up all the data
themselves, but this is an automated prediction to make it easy to view and learn from.

There are two different tables included: one for selling and one for buying. Selling means you are looking to sell prime items, and buying implies you are looking for the best prime items to buy.

### Scores

If you go and view the tables, there is a column called score which scores each prime item. This score is calculated as described below.

This score essentially generates a metric of 4 normalized metrics. The 4 metrics used are the ratio of volume bought to volume sold (in the live statistics), the price difference between now and unvaulting time, the percent price difference over between now and unvaulting time, and the date difference between now and the unvaulting time. These 4 metrics are normalized between 0 and 1, and averaged. This average of the 4 metrics is used to rank the items. When buying items, ascending order is used, otherwise, descending order is used. The function responsible for this creation can be viewed on my [GitHub](https://github.com/rajivsarvepalli/warframe-metrics/blob/main/src/warframe_metrics/market/prime.py#L167-L268) or its [documentation](https://warframe-metrics.readthedocs.io/en/latest/api_reference/_autosummary/warframe_metrics.market.prime.best_prime_complex.html) also describes its workings.


## Contributions

The main contributions of this website are to add a place to view warframe market item statistics in more depth. It also intends to add a method for predicting prime item prices.
This website is coupled with the PyPI package [`warframe-metrics`](https://pypi.org/project/warframe-metrics/), which I also developed and released. This package is used for collecting data from
warframe-market and analyzing it. If you are interested in using this package, please be respectful of warframe market be careful of how quickly you collect data from their REST API.

## Future Ideas

When I initially started this project, I was hoping for some posts from Reddit to measure the popularity and sentiment towards warframe items. I hoped that I could establish some connection
between warframe market items prices and the Reddit opinion of them. However, the sparsity of data per warframe item made this task very hard. However, perhaps there could be some work done in this direction. 
Maybe even using NLP sentiment analysis to understand the likelihood of an item being buffed or nerfed.

Additionally, some time-series prediction could be a useful addition to the graphs displayed per item. One possible algorithm for this is [Facebook's Prophet](https://github.com/facebook/prophet). However, the compute
time and lack of computational resources are why I did not implement it for this website.


## Contribute

Feel free to contribute to this website using the `dev` branch to create pull requests. Also, feel free to open an issue if there are some potential ideas or additions you would like to see. This is my first project on front-end work, so do not be surprised if the HTML/javascript code is super messy.


## Credit

All credit to [warframe market](https://warframe.market/) for the data collected and used in this website. Additionally, the charts are created using a [HighCharts demo](https://www.highcharts.com/demo/stock/all-indicators) to create the stock charts. And of course, thanks to [PythonAnywhere](https://www.pythonanywhere.com/) for enabling a way to freely host a web app. 
