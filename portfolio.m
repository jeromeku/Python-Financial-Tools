classdef portfolio
    
    properties
        assets;
        optimization;
        statistics;
    end
    
    properties (Access = private)
        n_assets;
    end
    
    
    methods (Access = private)
        
        function optimization = optimize_asset_allocation(self)
            
            D = 2 * self.statistics.covariance;
            n = self.n_assets;

            expected_returns = .05:.001:.14;
            n_average_returns = length(expected_returns);
            standard_deviations = NaN(size(expected_returns));
            weights = NaN(n_average_returns,n);
            
            allocate = [];
            allocate.H = D;
            allocate.f = zeros(1,n);
            allocate.Aineq = [];
            allocate.bineq = [];
            allocate.Aeq = [ones(1,n);self.statistics.mean];
            allocate.lb = zeros(n,1);
            allocate.ub = ones(n,1);
            allocate.solver = 'quadprog';
            allocate.options = optimset('Algorithm',                ...
                'interior-point-convex','Display','off');
            
            for i = 1:n_average_returns
                allocate.beq = [1;expected_returns(i)];
                [solution,variance] = quadprog(allocate);
                
                if ~isempty(solution) && max(solution) <= 1 &&      ...
                        min(solution) >= 0
                    weights(i,:) = solution;
                    standard_deviations(i) = sqrt(variance);
                end
            end
            
            optimization.expected_returns = expected_returns;
            optimization.standard_deviations = standard_deviations;
            optimization.weights = weights;
            
            
        end
        
        function statistics = calculate_portfolio_statistics(self)
            
            asset_return_cell = cell(1,self.n_assets);
            
            for i = 1:self.n_assets
                asset_return_cell{i} = self.assets{i}.statistics.returns;
                
            end
            asset_returns = horzcat(asset_return_cell{:});
 
            statistics.mean = mean(asset_returns);
            statistics.covariance = cov(asset_returns);
            statistics.standard_deviation = sqrt(diag(              ...
                statistics.covariance));
            
            
        end
        
    end
    methods
        
        function self = portfolio(assets)
            
            self.n_assets = length(assets);
            self.assets = cell(self.n_assets,1);
            
            for i = 1:self.n_assets
                if ischar(assets{i})
                    self.assets{i} = stock(assets{i});
                else
                    self.assets{i} = assets{i};
                end
            end

            self.statistics = calculate_portfolio_statistics(self);
            self.optimization = optimize_asset_allocation(self);
            
        end
    end
end