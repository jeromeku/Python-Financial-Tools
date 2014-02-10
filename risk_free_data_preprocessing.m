function processed_company = risk_free_data_preprocessing(company,treasury)
index = ismember(company.date(:),treasury.date(:));
field_names = fieldnames(company);

processed_company = [];

for i = 1:length(field_names)
    if i == length(field_names)
        index = index(2:end);
    end
    eval(['processed_company.',field_names{i},' = company.',field_names{i},'(index);']);
end




