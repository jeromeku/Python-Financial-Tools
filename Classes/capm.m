classdef capm
    properties
        alpha;
        beta;
        critical_value;
        
        asset;
        market;
        risk_free;
    end
    
    properties (Access = private)
        residuals;
        s_squared;
        standard_errors;
    end
    
    
    
    
    
end