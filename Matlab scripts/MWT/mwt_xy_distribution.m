% Quantification of distribution of the larvae in Multiworm Tracker (MWT) data 
% Written by Ibrahim Tastekin 
% 01/2017
% Definition: Distributions of larvaL centroid positions on x and y axes are computed. kinVariables and
% eventVariablas obtained from the MWT should be loaded.


clearvars
% Go to the directory where the individual experiments are
main_directory='/Users/itastekin/'

cd(main_directory)
dirlist=dir(main_directory);



c_time={};
counter=1;
for i=1:length(dirlist);
    
    dir_individual=dirlist(i).name;
    
    dir_to=strcat(main_directory,'/',dir_individual);
    
    cd(dir_to)
    
    load kinVariables
    
centroidpos=NaN(length(kinData),9000); % centroid positionss
keep_counting=1;
for i=1:length(kinData);
    % Uncomment either Line 34 or 35 to compute distribution on the x or y
    % axis, respectively,
    centroidpos(keep_counting,(kinData{i}.frame))=kinData{i}.cx; % distribution of the centroid position on the x-axis
    %centroidpos(keep_counting,(kinData{i}.frame))=kinData{i}.cy; %distribution of the centroid position on the y-axis 
    keep_counting=keep_counting+1;
end

c_time{counter}=centroidpos; 

counter=counter+1;



end

total_traj=[];

for i=1:length(c_time);
    
    x=size(c_time{i});
    traj=x(1);
total_traj=[total_traj traj];

end


total_traj=sum(total_traj);


c_time_matrix=NaN(total_traj,9000);


counter_2=1;
    
for i=1:length(c_time);
    data=c_time{i};
    x=size(c_time{i});
    traj=x(1);
    
    
    for j=1:traj;
       c_time_matrix(counter_2,:)= data(j,:);
       counter_2=counter_2+1;
    end
        
        
end  

% create a vector with all positions from all experiments
cx_vector_all=[];
for i=1:size(c_time_matrix,1);
    
    
    cx_vector=c_time_matrix(i,:);
    
    
   cx_vector_all=[cx_vector_all cx_vector];
   
   
end

% bin the centroid positions
bins=0:10:250;
[b,a]=hist(cx_vector_all,bins);

% plot the distribution
hold on
plot(a,b/sum(b),'k')