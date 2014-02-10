function capm_results = capm_model_regression(asset_profile,market,treasury)

if length(asset_profile.returns) ~= length(treasury.returns)
    asset_profile = capm_data_preprocessing(asset_profile,treasury);
end
if length(market.returns) ~= length(treasury.returns)
    market = capm_data_preprocessing(market,treasury);
end

market_premium = market.returns - treasury.returns;
asset_premium = asset_profile.returns - treasury.returns;
constant = ones(size(market_premium));

% [b,bint,r,rint,stats] = regress(asset_premium,[constant,market_premium])

covariates = [constant,market_premium];

theta = covariates \ asset_premium;
residuals = asset_premium - covariates * theta;
s.squared = (residuals' * residuals) / (length(asset_profile.returns) - rank(covariates));
standard_errors = sqrt(s.squared * inv(covariates'*covariates));

critical_value = norminv(.975);

capm_results.alpha.value = theta(1);
capm_results.alpha.confidence_interval = theta(1) + [-standard_errors(1,1) * critical_value,standard_errors(1,1) * critical_value];

capm_results.beta.value = theta(2);
capm_results.beta.confidence_interval = theta(2) + [-standard_errors(2,2) * critical_value,standard_errors(2,2) * critical_value];

% keyboard;
