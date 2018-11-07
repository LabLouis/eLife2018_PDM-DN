% Quantification of distance the larvae to the odor sources in Multiworm Tracker (MWT) data 
% Written by Ibrahim Tastekin 
% 01/2017
% Definition: Calculates distance between larval centroids and odor sources. kinVariables and
% eventVariablas obtained from the MWT should be loaded.
clearvars
% Go to the directory where the individual experiments are
main_directory='/Users/itastekin/';
cd(main_directory)
dirlist=dir(main_directory);


distance_time={};
counter=1;
for i=1:length(dirlist);
    
    dir_individual=dirlist(i).name;
    
    dir_to=strcat(main_directory,'/',dir_individual);
    
    cd(dir_to)
    
    load kinVariables
    
distance_matrix=NaN(length(kinData),9000);
keep_counting=1;
for i=1:length(kinData);
    
    distance_matrix(keep_counting,(kinData{i}.frame))=kinData{i}.dfromsource; % distances from the odor closest odor source
    keep_counting=keep_counting+1;
end

distance_time{counter}=distance_matrix;

counter=counter+1;



end

total_traj=[];

for i=1:length(distance_time);
    
    x=size(distance_time{i});
    traj=x(1);
total_traj=[total_traj traj];

end


total_traj=sum(total_traj);


distance_time_matrix=NaN(total_traj,9000);


    counter_2=1;
    
for i=1:length(distance_time);
    data=distance_time{i};
    x=size(distance_time{i});
    traj=x(1);
    
    
    for j=1:traj;
       distance_time_matrix(counter_2,:)= data(j,:);
       counter_2=counter_2+1;
    end
        
        
end  

elements_numbers=[];
for i=300:length(distance_time_matrix);
    
    elements=length(find(distance_time_matrix(:,i)>0));
    elements_numbers=[elements_numbers elements];
end


figure(1) 

hold on

%calculate mean and SEM time series
sem=nanstd(distance_time_matrix(:,300:end))./sqrt(elements_numbers); %unfiltered
means=nanmean(distance_time_matrix(:,300:end)); %unfiltered


% distance to the odor source at 150th second
distance_150=NaN(size(distance_time_matrix,1),1);

for i=1:size(distance_time_matrix,1);
    
    distance_150(i)=nanmean(distance_time_matrix(i,4321:4350)); % use the average of a window of 10 frames
end
figure(2)
notboxplot(distance_150,1.4,0.05,'patch')

%Save
save distance_150

        