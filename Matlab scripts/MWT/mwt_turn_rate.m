% Quantification of turn rates in Multiworm Tracker (MWT) data 
% Written by Ibrahim Tastekin 
% 01/2017
% Definition: Calculates the turn rate for MWT data. kinVariables and
% eventVariablas obtained from the MWT should be loaded.

clearvars

% Go to the directory where the individual experiments are
main_directory='/Users/itastekin/'; 
dirlist=dir(main_directory);

% Compute turn rates in independent trajectories in each experiment
index_and_turn_rates={};
independent_traj_turn_rate={};

counter=1;
% go to the folder for each experiment
for k=1:length(dirlist);
    
    dir_individual=dirlist(k).name; 
    
    dir_to=strcat(main_directory,'/',dir_individual);
    
    cd(dir_to)
    
    load kinVariables
    load eventVariables
    
    
    traj_inx__duration_vs_turn_rate=NaN(length(kinData),4);
    

for i=1:length(kinData);
    
    trajectory_duration=(kinData{i}.times(end)-kinData{i}.times(1))/60; %minutes
    
    if isempty(eventData{i}.schmittTurn)==1;
  
    number_of_turns=0;
    
    else 
        number_of_turns=length(eventData{i}.schmittTurn);
        
    end
    
    
    traj_inx__duration_vs_turn_rate(i,1)=(kinData{i}.times(1)); %trajectory start time seconds
    traj_inx__duration_vs_turn_rate(i,2)=kinData{i}.times(end); %trajectory end time in seconds
    traj_inx__duration_vs_turn_rate(i,3)=(kinData{i}.times(end)-kinData{i}.times(1)); %trajectory duration in seconds
    traj_inx__duration_vs_turn_rate(i,4)=number_of_turns/trajectory_duration; % turn rate for the trajectory
    
    
end

%Following lines (Line 55-64) isolate the independent trajectories 
threshold=60; % A threshold of 60 seconds enable us identify independent trajectories.

x=find(traj_inx__duration_vs_turn_rate(:,3)>threshold);

y=min(traj_inx__duration_vs_turn_rate(x,3)+traj_inx__duration_vs_turn_rate(x,1));

z=find(traj_inx__duration_vs_turn_rate(:,1)<y);

t=intersect(x,z);

independent_traj{counter}.threshold=threshold;
independent_traj{counter}.idx=t;
independent_traj{counter}.turn_rate=traj_inx__duration_vs_turn_rate(t,4);


index_and_turn_rates{counter}=traj_inx__duration_vs_turn_rate;



counter=counter+1;

clear traj_inx_vs_turn_rate 
clear x
clear y
clear y
clear t

end

% following calculates the total number of independent trajectories in the
% dataset
total_number_traj=[];
for i=1:length(independent_traj);
    
    tot=length(independent_traj{i}.turn_rate);
    
    total_number_traj=[total_number_traj tot];
end
 total_number_traj=sum(total_number_traj);
 
% Following generates a vector of turn rates for independent trajectories
 independent_turn_rate_vector=[];
 for i=1:length(independent_traj);
     
     junk=independent_traj{i}.turn_rate;
     independent_turn_rate_vector=[independent_turn_rate_vector
         junk];
 end
     
 
% Save data
cd(main_directory)

clearvars -except index_and_turn_rates   independent_traj independent_turn_rate_vector

save index_and_turn_rates 
save independent_traj
save independent_turn_rate_vector
notboxplot(independent_turn_rate_vector,0.8,0.05,'patch')
