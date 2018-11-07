%% Calcium imaging analysis for motor neurons
% written by Ibrahim Tastekin
% Reads mean fluorescent values selected within the ROIs defined by using
% fiji. The mean intensity in each ROI corresponding to each abdominal segment is written in an .xls file using Fiji
% The script computes DeltaF/F for each segment
% run the code in the directory, which contains the .xls file.

clearvars

% be careful change right and right 3 times!!!
filename = 'Experiment_003_right.xls'; %experiment 3 right abdominal segments
Experiment_003_right=xlsread(filename);
save Experiment_003_right

index=size(Experiment_003_right);
index_segments=index(2);
index_frames=index(1);
peak_distance=9;

% The time points of the light flashes (extracted in Fiji)
stimulus_start_sec=[90 130 170 240 350]; % in seconds
stimulus_end_sec=stimulus_start_sec+20;  % in seconds


 
fs=5; % frame rate of image aquisition check the info of the lif file in Fiji

%A1
A_1=Experiment_003_right(:,1);
mean_A_1=mean(A_1);
dFNormF_1=100*(A_1-mean_A_1)/mean_A_1; % compute the % change in the flourescence compared to baseline and normalized by the baseline
smooth_dFNormF_1=sgolayfilt(dFNormF_1,3,15); % smoothen the data
[pks_1,locs_1] = findpeaks(smooth_dFNormF_1,'MinPeakDistance',peak_distance,'MinPeakHeight',1);  %find local maxima to detect wave peaks


%A2
A_2=Experiment_003_right(:,2);
mean_A_2=mean(A_2);
dFNormF_2=100*(A_2-mean_A_2)/mean_A_2;
smooth_dFNormF_2=sgolayfilt(dFNormF_2,3,15);
[pks_2,locs_2] = findpeaks(smooth_dFNormF_2,'MinPeakDistance',peak_distance,'MinPeakHeight',1);  


%A3
A_3=Experiment_003_right(:,3);
mean_A_3=mean(A_3);
dFNormF_3=100*(A_3-mean_A_3)/mean_A_3;
smooth_dFNormF_3=sgolayfilt(dFNormF_3,3,15);
[pks_3,locs_3] = findpeaks(smooth_dFNormF_3,'MinPeakDistance',peak_distance,'MinPeakHeight',1);  


%A4
A_4=Experiment_003_right(:,4);
mean_A_4=mean(A_4);
dFNormF_4=100*(A_4-mean_A_4)/mean_A_4;
smooth_dFNormF_4=sgolayfilt(dFNormF_4,3,15);
[pks_4,locs_4] = findpeaks(smooth_dFNormF_4,'MinPeakDistance',peak_distance,'MinPeakHeight',1);  


%A5
A_5=Experiment_003_right(:,5);
mean_A_5=mean(A_5);
dFNormF_5=100*(A_5-mean_A_5)/mean_A_5;
smooth_dFNormF_5=sgolayfilt(dFNormF_5,3,15);
[pks_5,locs_5] = findpeaks(smooth_dFNormF_5,'MinPeakDistance',peak_distance,'MinPeakHeight',1);  


%A6
A_6=Experiment_003_right(:,6);
mean_A_6=mean(A_6);
dFNormF_6=100*(A_6-mean_A_6)/mean_A_6;
smooth_dFNormF_6=sgolayfilt(dFNormF_6,3,15);
[pks_6,locs_6] = findpeaks(smooth_dFNormF_6,'MinPeakDistance',peak_distance,'MinPeakHeight',1);  


%A7
A_7=Experiment_003_right(:,7);
mean_A_7=mean(A_7);
dFNormF_7=100*(A_7-mean_A_7)/mean_A_7;
smooth_dFNormF_7=sgolayfilt(dFNormF_7,3,15);
[pks_7,locs_7] = findpeaks(smooth_dFNormF_7,'MinPeakDistance',peak_distance,'MinPeakHeight',1);  



