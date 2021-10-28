addpath(genpath(pwd))
% Get a list of all folders in this folder.
folder_list = dir('.');
ind = [folder_list.isdir];
folder_list = folder_list(ind);
folder_list = folder_list(~ismember({folder_list.name},{'.','..', '*.py'}));

figure;
hold on
for f = 1:length(folder_list)
    % load Accuracy csv
    
    %% Set up the Import Options and import the data
    opts = delimitedTextImportOptions("NumVariables", 2);

    % Specify range and delimiter
    opts.DataLines = [1, Inf];
    opts.Delimiter = ",";

    % Specify column names and types
    opts.VariableNames = ["nSamples", "Accuracy"];
    opts.VariableTypes = ["double", "double"];

    % Specify file level properties
    opts.ExtraColumnsRule = "ignore";
    opts.EmptyLineRule = "read";

    % Import the data
    tbl = readtable([pwd, filesep, folder_list(f).name, filesep, 'Accuracy.csv'], opts);

    accuracy = tbl{:,2};
    samples = tbl{:,1};
    
    plot(samples, accuracy);
    
end