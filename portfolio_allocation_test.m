function portfolio_allocation_test()

portfolio.assets = cell(2,1);

portfolio.risk_free = yahoo_load_stock('Historical/^IRX_S11-01-1993_E04-03-2003.csv');

portfolio.assets{1} = yahoo_load_stock('Historical/^GSPC_S11-01-1993_E04-03-2003.csv');
portfolio.assets{2} = yahoo_load_stock('Historical/MSFT_S11-01-1993_E04-03-2003.csv');

portfolio_allocation_model(portfolio)

