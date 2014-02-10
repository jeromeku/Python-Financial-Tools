function profile = yahoo_load_stock(path)
fid = fopen(path);

% 
data.headers = textscan(fid,'%s %s %s %s %s %s %s',1, 'delimiter',',');
data.information = textscan(fid,'%s %f %f %f %f %f %f','delimiter',',');
fclose(fid);
profile = [];

for i = 1:length(data.headers)
    header.cell = lower(data.headers{i});
    header.name = header.cell{1};
    header.name(isspace(header.name)) = '_';
    eval(['profile.',header.name,' = data.information{',num2str(i),'};']);
end

profile = yahoo_returns(profile,'close');


