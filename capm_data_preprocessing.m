function processed_asset_profile = capm_data_preprocessing(asset_profile,treasury)
index = ismember(asset_profile.date(:),treasury.date(:));
field_names = fieldnames(asset_profile);

processed_asset_profile = [];

for i = 1:length(field_names)
    if i == length(field_names)
        index = index(2:end);
    end
    eval(['processed_asset_profile.',field_names{i},' = asset_profile.',field_names{i},'(index);']);
end




