% Turn rates during upgradient and downgradient runs

%Written by Ibrahim Tastekin

% Definition: Turn rate up or down gradient for single larva tracking experiments
%: Bearing is defined by reconsturcted gradient. 
%Turn rates up and downgradient are determined according to the bearing history preceding the turns
% motorData and sensoryData has to be generated and loaded.
% Run in the directory, which contains motorData and sensoryData

clearvars
load motorData
load sensoryData


%% calculate turn triggered bearings

turn_triggered_abs_bearing={};
counter=1;
% defines the time window to be analyzed
    window_start=300;
    window_end=900;
    window_length=window_end- window_start;
for i=1:length(motorData);
    
    
    
    turn_start=motorData{i}.idxTurnStart;
    turn_start=turn_start(turn_start>window_start);
    turn_start=turn_start(turn_start<window_end);
    
    bearing=180*sensoryData{i}.bearing/pi;
    
    % defines a time window preceding turns to calculate average bearing.
    % This is important to define whether the run was upgradient or
    % downgradient.
    mean_bearing_preceding_turn=NaN(1,length(turn_start));
    for j=1:length(turn_start);
        
        if turn_start(j)<5
        mean_bearing_preceding_turn(j)=nanmean(bearing(1:turn_start(j)));
        
        else
            mean_bearing_preceding_turn(j)=nanmean(bearing(turn_start(j)-4:turn_start(j)));
        end
    end
    
    turn_triggered_abs_bearing{i}=abs(mean_bearing_preceding_turn);
    counter=counter+1
end

    save  turn_triggered_abs_bearing
    
%% calculate turn rates
    
    %preallocation
    
    turn_rate_while_d=[];
    turn_rate_while_u=[];
    turn_rate_while_down=[];
    turn_rate_while_up=[];
    
    turn_rate_45=[];
    turn_rate_45_90=[];
    turn_rate_90_135=[];
    turn_rate_135_180=[];
    turn_rate_45_all=[];
    turn_rate_45_90_all=[];
    turn_rate_90_135_all=[];
    turn_rate_135_180_all=[];
    
    
for i=1:length(motorData);
    
    fs=motorData{i}.fs;
    % down gradient turn rate
    turn_rate_while_d=60*fs*length(find(turn_triggered_abs_bearing{i}>90))/window_length;
    
    % up gradient turn rate
    turn_rate_while_u=60*fs*length(find(turn_triggered_abs_bearing{i}<90))/window_length;
    
    
    % turn rate below 45 degrees bearing(absolute value)
    
    turn_rate_45=fs*length(find(turn_triggered_abs_bearing{i}<45))/window_length;
    
    % turn rate between 45-90 degrees bearing (absolute value)
    
    turn_rate_45_90=fs*length(find(turn_triggered_abs_bearing{i}>45 & turn_triggered_abs_bearing{i}<90))/window_length;
    
    % turn rate between 90-135 degrees bearing (absolute value)
    
    turn_rate_90_135=fs*length(find(turn_triggered_abs_bearing{i}>90 & turn_triggered_abs_bearing{i}<135))/window_length;
    
    % turn rate between 135-180 degrees bearing (absolute value)
    
    turn_rate_135_180=fs*length(find(turn_triggered_abs_bearing{i}>135 & turn_triggered_abs_bearing{i}<180))/window_length;
    
    
    
    
    turn_rate_while_down=[turn_rate_while_down turn_rate_while_d];
    
    turn_rate_while_up=[turn_rate_while_up turn_rate_while_u];
    
    turn_rate_45_all=[turn_rate_45_all turn_rate_45];
    turn_rate_45_90_all=[turn_rate_45_90_all turn_rate_45_90];
    turn_rate_90_135_all=[turn_rate_90_135_all turn_rate_90_135];
    turn_rate_135_180_all=[turn_rate_135_180_all turn_rate_135_180];
    
end

turnrates_recons.mean_while_down=nanmean(turn_rate_while_down);
turnrates_recons.sem_while_down=nanstd(turn_rate_while_down)/sqrt(length(turn_rate_while_down));
turnrates_recons.mean_while_up=nanmean(turn_rate_while_up);
turnrates_recons.sem_while_up=nanstd(turn_rate_while_up)/sqrt(length(turn_rate_while_up));


turnrates_recons.mean_turn_rate_45_all=nanmean(turn_rate_45_all);
turnrates_recons.sem_turn_rate_45_all=nanstd(turn_rate_45_all)/sqrt(length(turn_rate_45_all));

turnrates_recons.mean_turn_rate_45_90_all=nanmean(turn_rate_45_90_all);
turnrates_recons.sem_turn_rate_45_90_all=nanstd(turn_rate_45_90_all)/sqrt(length(turn_rate_45_90_all));

turnrates_recons.mean_turn_rate_90_135_all=nanmean(turn_rate_90_135_all);
turnrates_recons.sem_turn_rate_90_135_all=nanstd(turn_rate_90_135_all)/sqrt(length(turn_rate_90_135_all));

turnrates_recons.mean_turn_rate_135_180_all=nanmean(turn_rate_135_180_all);
turnrates_recons.sem_turn_rate_135_180_all=nanstd(turn_rate_135_180_all)/sqrt(length(turn_rate_135_180_all));




%Save
save turnrates_recons

turnrates_recons


    
    
    
    
    
    
    
    
    
    
    
    
        