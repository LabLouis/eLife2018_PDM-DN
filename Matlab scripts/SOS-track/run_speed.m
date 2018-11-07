% Speed of Centroid During Runs
% Written by Ibrahim Tastekin
% Definition: computes the speed of the centroid only during runs.
% motorData has to be generated previously
% Run in the directory, which contains motorData
clearvars
load motorData

cm_speed=[];
turn_start=[];
turn_end=[];
mean_individual=NaN(1,length(motorData));

for i=1:length(motorData);
    
    cm_speed=motorData{i}.cmSpeed;
    
    
    cm_speed(cm_speed==0)=NaN; % get rid of tracking errors
    
    cm_speed(cm_speed>3)=NaN;  % get rid of too fast movements due to tracking errors
    
    turn_start=motorData{i}.idxTurnStart;
    turn_end=motorData{i}.idxTurnEnd;
    
    % isolate runs
    mean_run_speed=NaN(1,length(turn_end));
    
    for j=1:length(turn_end);
        
        if j==1;
            
        mean_run_speed(:,j)=nanmean(cm_speed(1:turn_start(j)-1));
        
        elseif j==length(turn_end);
            
            mean_run_speed(:,j)=nanmean(cm_speed(turn_end(j)+1):length(cm_speed));
        else
            
                mean_run_speed(:,j)=nanmean(cm_speed(turn_end(j-1)+1:turn_start(j)-1));
            
        end
        
        
    end
    
    %%% Mean of run speed for each individual
    
    mean_individual(:,i)=nanmean(mean_run_speed);
end

            

%%%Population mean and Sem


%% Mean
mean_all_runs=nanmean(mean_individual);

%% Sem

sem_all_runs=nanstd(mean_individual)/sqrt(length(mean_individual));



runspeed.mean=mean_all_runs;
runspeed.sem=sem_all_runs;
runspeed.individual_trajectories=mean_individual;
runspeed.number_of_animals=length(motorData);


% save
clearvars -except runspeed
save runspeed



  