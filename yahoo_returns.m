function profile = yahoo_returns(profile,type)
prices = [];
eval(['prices = profile.',type,';']);

returns = prices(2:end) ./ prices(1:end-1) - 1;
profile.returns = returns;