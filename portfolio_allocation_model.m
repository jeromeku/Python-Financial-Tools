function portfolio_allocation_model(portfolio)


asset_characteristics = portfolio_allocation_characteristics(portfolio);


asset_characteristics.mean = [0.10713801 0.07000767 0.07788801];
asset_characteristics.covariance = [1.8821636 0.8007660 0.5270394;
    0.8007660 3.0613087 0.3588748;
    0.5270394 0.3588748 1.6702649];


n = length(asset_characteristics.mean);
D = 2 * asset_characteristics.covariance;


expected_returns = .05:.001:.14;
n_average_returns = length(expected_returns);
standard_deviations = NaN(size(expected_returns));

Aeq = [ones(1,n);asset_characteristics.mean];
weights = NaN(n_average_returns,n);

portfolio_optimization = [];
portfolio_optimization.H = D;
portfolio_optimization.f = zeros(1,n);
portfolio_optimization.Aineq = [];
portfolio_optimization.bineq = [];
portfolio_optimization.Aeq = Aeq;
portfolio_optimization.lb = zeros(n,1);
portfolio_optimization.ub = ones(n,1);
portfolio_optimization.solver = 'quadprog';
portfolio_optimization.options = optimset('Algorithm','interior-point-convex','Display','off');

for i = 1:n_average_returns
    portfolio_optimization.beq = [1;expected_returns(i)];
    [solution,variance] = quadprog(portfolio_optimization);
    
    if ~isempty(solution) && max(solution) <= 1 && min(solution) >= 0
        weights(i,:) = solution;
        standard_deviations(i) = sqrt(variance);
    end
end

% plot(standard_deviations,expected_returns);


