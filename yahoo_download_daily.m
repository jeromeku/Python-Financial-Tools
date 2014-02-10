function data = yahoo_download_daily(tickers,startDate,endDate,dateFormat)
if ischar(tickers)
    tickers = {tickers};
end

if nargin == 4
    startDate = datenum(startDate,dateFormat);
    endDate   = datenum(endDate,dateFormat);
end

yahoo_finance_url = 'http://ichart.finance.yahoo.com/table.csv?s=';

[start_year,start_month,start_day] = datevec(startDate);
[end_year,end_month,end_day] = datevec(endDate);

url2 = ['&a=' num2str(start_month-1, '%02u') ...
    '&b=' num2str(start_day) ...
    '&c=' num2str(start_year) ...
    '&d=' num2str(end_month-1, '%02u') ...
    '&e=' num2str(end_day) ...
    '&f=' num2str(end_year) '&g=d&ignore=.csv'];


for i = 1:length(tickers)
    stock_information = urlread([yahoo_finance_url tickers{i} url2]);
    
    c = textscan(stock_information,'%s%f%f%f%f%f%f','HeaderLines',1,'Delimiter',',');
    
    ds = table(c{1}, c{2}, c{3}, c{4}, c{5}, c{6}, c{7}, 'VariableNames', ...
        {'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'AdjClose'});
    
    ds.Date = datenum(ds.Date, 'yyyy-mm-dd');
    ds = flipud(ds);
    data.(genvarname(tickers{i})) = ds;
    
end

