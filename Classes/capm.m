classdef capm
    properties
        alpha;
        beta;
        critical_value;
        
        asset;
        asset_market;
        asset_free;
    end
    
    properties (Access = private)
        residuals;
        s_squared;
        standard_errors;
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
        
        function display(self)
            fprintf('================================================================================\n');
            
            fprintf('================================================================================\n');
        end
    end

end