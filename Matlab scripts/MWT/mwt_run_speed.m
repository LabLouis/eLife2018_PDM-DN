% Quantification of run speeds in Multiworm Tracker (MWT) data 
% Written by Ibrahim Tastekin 
% 01/2017
% Definition: Calculates the run speed for MWT data. kinVariables and
% eventVariablas obtained from the MWT should be loaded.

clearvars

% Go to the directory where the individual experiments are
main_directory='/Users/itastekin/'
dirlist=dir(main_directory);

% Compute run speeds in independent trajectories in each experiment
index_and_run_speeds={};
independent_traj_run_speed={};

% go to the folder for each experiment
counter=1;
for k=1:length(dirlist);
    
    dir_individual=dirlist(k).name;
    
    dir_to=strcat(main_directory,'/',dir_individual);
    
    cd(dir_to)
    
    load kinVariables
    load eventVariables
    
    
    traj_inx__duration_vs_run_speed=NaN(length(kinData),4);
    

    
    
    traj_inx__duration_vs_run_speed(i,1)=(kinData{i}.times(1)); %start time seconds
    traj_inx__duration_vs_run_speed(i,2)=kinData{i}.times(end); %end time in seconds
    traj_inx__duration_vs_run_speed(i,3)=(kinData{i}.times(end)-kinData{i}.times(1)); %trajectory duration in seconds
    traj_inx__duration_vs_run_speed(i,4)=nanmean(kinData{i}.speedmms); % run speed for the trajectory
    
    
end
%Following lines (Line 55-64) isolate the independent trajectories
threshold=60; % A threshold of 60 seconds enable us identify independent trajectories.

x=find(traj_inx__duration_vs_run_speed(:,3)>threshold);

y=min(traj_inx__duration_vs_run_speed(x,3)+traj_inx__duration_vs_run_speed(x,1));

z=find(traj_inx__duration_vs_run_speed(:,1)<y);

t=intersect(x,z);

independent_traj{counter}.threshold=threshold;
independent_traj{counter}.idx=t;
independent_traj{counter}.run_speed=traj_inx__duration_vs_run_speed(t,4);


index_and_run_speeds{counter}=traj_inx__duration_vs_run_speed;



counter=counter+1;

clear traj_inx_vs_run_speed 
clear x
clear y
clear y
clear t

end

% following calculates the total number of independent trajectories in the
% dataset
total_number_traj=[];
for i=1:length(independent_traj);
    
    tot=length(independent_traj{i}.run_speed);
    
    total_number_traj=[total_number_traj tot];
end
 total_number_traj=sum(total_number_traj);
 
 
 independent_run_speed_vector=[];
 for i=1:length(independent_traj);
     
     junk=independent_traj{i}.run_speed;
     independent_run_speed_vector=[independent_run_speed_vector
         junk];
 end
     
 
% Save
cd(main_directory)

clearvars -except index_and_run_speeds   independent_traj independent_run_speed_vector

save index_and_run_speeds 
save independent_traj
save independent_run_speed_vector

