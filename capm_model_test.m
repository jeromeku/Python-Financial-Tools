function capm_model_test()
treasury = yahoo_load_stock('Historical/^IRX_S11-01-1993_E04-03-2003.csv');
market = yahoo_load_stock('Historical/^GSPC_S11-01-1993_E04-03-2003.csv');
asset_profile = yahoo_load_stock('Historical/MSFT_S11-01-1993_E04-03-2003.csv');

capm_results = capm_model_regression(asset_profile,market,treasury);
