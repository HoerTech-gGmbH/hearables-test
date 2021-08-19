%%%%%%% Plotting Raw Accelerometer Data %%%%%%%%%
%%% author: Thalea Hoogestraat
%%% last edit: 17th august 2021
%%% Load every csv file from a given path
%%% For aech file, the name is changed by erasing "raw_accelerometer_" and
%%% "csv" to reuse it as new filename in the end of the script. Each
%%% activity is presented in a single plot, containing all three
%%% acceleration-axes of the sensor. The title is automatically generate by
%%% filename (including activity and subject no.)
%%% The plot is saved in png format to the actual folder.



clear, close all, clc

files = dir('xxx/xxx/*.csv'); %insert path, /*.csv tells matlab to look for eyerything in csv format contaied in the given folder
Temp_names = struct();

for mm=1:length(files)
    file = fullfile(files(mm).folder,files(mm).name);
    temp = readtable(file);
    temp.Properties.VariableNames = {'time', 'x', 'y', 'z', 'status', 'timestep', 'activity'};
    data(mm,1) = {temp};
    data_names(mm).name = files(mm).name;
end


%% plot data 

for idx = 1:size(data,1)
    actLabel = data_names(idx).name(1,:);
    actLabel = erase(actLabel, "raw_accelerometer_");
    actLabel = erase(actLabel, ".csv");
    plottitle = split(actLabel, '_');
    plottitle = join(plottitle, ' '); %insert space where the underscore was
    figure(idx), sgtitle(actLabel) 
    subplot(3,1,1)
    currData = data{idx}.x;
    meanData = mean(currData);
    dataPlot = data{idx}.x-meanData;
    plot(data{idx}.time, data{idx}.x)
    xlim([0, 140]) %set length of plot to 140 sec (duration of activity)
    ylabel('x-acceleration [g]');
    xlabel('time [s]')
    grid;
    title('x-axis');
    
    subplot(3,1,2)
    plot(data{idx}.time, data{idx}.y)
    xlim([0, 140])
    ylabel('Acceleration [g]');
    grid;
    title('y-axis');
    
    subplot(3,1,3)
    plot(data{idx}.time, data{idx}.z)
    xlim([0, 140])
    xlabel('Time [s]')
    ylabel('Acceleration [g]');
    title('z-axis');
    grid;
    

   filename = convertCharsToStrings(actLabel);
print(filename, '-dpng') %save figure as png
end

