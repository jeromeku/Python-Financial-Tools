classdef stock
    properties
        ticker;
        dates;
        profile;
        statistics;
    end
    
    methods (Access = private)
        function stock_profile = yahoo_download_daily(self)
            date_format = 'dd/mm/yyyy';
            start_date = datenum(self.dates.begin,date_format);
            end_date   = datenum(self.dates.end,date_format);
            yahoo_finance_url = ...
                'http://ichart.finance.yahoo.com/table.csv?s=';
            [start_year,start_month,start_day] = datevec(start_date);
            [end_year,end_month,end_day] = datevec(end_date);
            yahoo_query_url = ['&a=' num2str(start_month - 1,'%02u')   ...
                '&b=' num2str(start_day) '&c=' num2str(start_year)     ...
                '&d=' num2str(end_month - 1,'%02u') '&e='              ...
                num2str(end_day) '&f=' num2str(end_year)               ...
                '&g=d&ignore=.csv'];
            stock_information =                                        ...
                urlread([yahoo_finance_url self.ticker yahoo_query_url]);
            c = textscan(stock_information,'%s %f %f %f %f %f %f',     ...
                'HeaderLines',1,'Delimiter',',');
            stock_fields = {'date','open','high','low','close',        ...
                'volume','adj_close'};
            stock_profile = [];
            for i = 1:length(stock_fields)
                stock_profile.(genvarname(stock_fields{i})) = flipud(c{i});
            end
        end
        
        function statistics = calculate_stock_statistics(self)
            statistics.returns = calculate_stock_returns(self);
            statistics.expected_return = mean(statistics.returns);
            
        end
        
        function returns = calculate_stock_returns(self)
            returns = self.profile.close(2:end) ./ ...
                self.profile.close(1:end-1) - 1;
            
        end
        
    end
    
    methods
        function self = stock(ticker,start_date,end_date)
            self.ticker = ticker;
            
            if ~exist('start_date','var') || ~exist('end_date','var')
                self.dates.begin = datestr(datenum(date) - 100,24);
                self.dates.end = datestr(datenum(date),24);
            else
                self.dates.begin = start_date;
                self.dates.end = end_date;
            end

            self.profile = yahoo_download_daily(self);
            self.statistics = calculate_stock_statistics(self);
            
        end
        
        function parametric_value_at_risk(self)
            
        end
        
        function display(self)
            
            fprintf('Ticker: %s\n',self.ticker);
            fprintf('In time series: from %s to %s\n\n',            ...
                self.dates.begin,self.dates.end);
            fprintf('Most current performance:\n');
            fprintf(['Date\t\tOpen\tHigh\tLow\tClose\tVolume\t',    ...
                '\tAdjusted Close\n']);
            fprintf('%s\t%.2f\t%.2f\t%.2f\t%.2f\t%7e\t%.2f\n\n',    ...
                self.profile.date{end},self.profile.open(end),      ...
                self.profile.high(end),self.profile.low(end),       ...
                self.profile.close(end),self.profile.volume(end),   ...
                self.profile.adj_close(end))
            fprintf('Expected return: %.4f\n',                      ...
                self.statistics.expected_return);
            
        end
        
        function display_price(self,type)
            
            if ~exist('type','var')
                type = 'Close';
            end
            
            
            plot(datenum(self.profile.date),                    ...
                self.profile.(genvarname(lower(type))),'k-x');
            datetick('x','dd/mm/yyyy');
            
            xlabel('Daily Time Series');
            ylabel('Daily Prices');
            title(sprintf('%s %s Prices',self.ticker,type));
            
            set(gca, ...
                'Box'         , 'off'     ,     ...
                'TickDir'     , 'out'     ,     ...
                'TickLength'  , [.02 .02] ,     ...
                'XMinorTick'  , 'on'      ,     ...
                'YMinorTick'  , 'on'      ,     ...
                'YGrid'       , 'on'      ,     ...
                'XColor'      , [.3 .3 .3],     ...
                'YColor'      , [.3 .3 .3],     ...
                'FontName'    , 'Helvetica',    ...
                'FontSize'    , 12,             ...
                'LineWidth'   , 1         );
            
        end
        
        function display_returns(self)
            plot(datenum(self.profile.date(2:end)),     ...
                self.statistics.returns,'k-x');
            datetick('x','dd/mm/yyyy');
            
            xlabel('Daily Time Series');
            ylabel('Daily Returns');
            title(sprintf('%s Returns',self.ticker));
            
            set(gca, ...
                'Box'         , 'off'     ,     ...
                'TickDir'     , 'out'     ,     ...
                'TickLength'  , [.02 .02] ,     ...
                'XMinorTick'  , 'on'      ,     ...
                'YMinorTick'  , 'on'      ,     ...
                'YGrid'       , 'on'      ,     ...
                'XColor'      , [.3 .3 .3],     ...
                'YColor'      , [.3 .3 .3],     ...
                'FontName'    , 'Helvetica',    ...
                'FontSize'    , 12,             ...
                'LineWidth'   , 1         );
        end
        
    end
end