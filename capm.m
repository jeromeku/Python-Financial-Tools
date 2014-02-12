classdef capm
    properties
        alpha;
        beta;
        critical_value;
        
        asset_market;
        asset_free;
    end
    
    
    methods (Access = private)
        
    end
    
    methods
        function self = capm(risk_free,market)
            
            if ischar(risk_free) && ischar(market)
                
                self.asset_free = stock(risk_free);
                self.asset_market = stock(market);
                
            else
                
                self.asset_free = risk_free;
                self.asset_market = market;
                
            end
            
        end
        
        function capm_results = capm_regression(self,asset)
            
            capm_results = [];
            
            if ischar(asset)
                asset = stock(asset);
            end
            market_premium = self.asset_market.statistics.returns - ...
                self.asset_free.statistics.returns;
            asset_premium = asset.statistics.returns -              ...
                self.asset_free.statistics.returns;
            
            constant = ones(size(market_premium));
            covariates = [constant,market_premium];
            
            theta = covariates \ asset_premium;
            
            residuals = asset_premium - covariates * theta;
            s_squared = (residuals' * residuals) / ...
                (length(asset.statistics.returns) - rank(covariates));
            standard_errors = sqrt(s_squared * inv(covariates'*covariates));
            
            self.critical_value = norminv(.975);
            
            capm_results.alpha.value = theta(1);
            capm_results.alpha.confidence_interval = theta(1) + ...
                [-standard_errors(1,1) * self.critical_value,   ...
                standard_errors(1,1) * self.critical_value];
            capm_results.alpha.z_value = theta(1) / standard_errors(1,1);
            capm_results.alpha.p_value = 2 * (1 - normcdf(abs(  ...
                capm_results.alpha.z_value)));
            
            capm_results.beta.value = theta(2);
            capm_results.beta.confidence_interval = theta(2) +  ...
                [-standard_errors(2,2) * self.critical_value,   ...
                standard_errors(2,2) * self.critical_value];
            capm_results.beta.z_value = theta(2) / standard_errors(2,2);
            capm_results.beta.p_value = 2 * (1 - normcdf(abs(...
                capm_results.beta.z_value)));
        end
        
        function display(self)
            
            disp(self);
            
        end
    end
    
end