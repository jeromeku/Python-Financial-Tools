function features = portfolio_allocation_characteristics(portfolio)

features = [];
features.risk_free = portfolio.risk_free.close(end);


assets = cell2mat(portfolio.assets);
asset_returns = horzcat(assets(:).returns);


features.mean = mean(asset_returns);
features.covariance = cov(asset_returns);
features.standard_deviation = sqrt(diag(features.covariance));





