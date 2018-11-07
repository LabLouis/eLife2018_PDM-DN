% Turn rate for individual larvae
% written by Ibrahim Tastekin
% Calculates overall turn rates for the single larva tracking experiments.
% motorData has to be generated previoulsy.
% Run in the directory, which contains motorData
clearvars

load motorData

turnstart=[];
turnfreq=[];
turnfreqall=[];
turnstart1=[];
turnstart2=[];


for i=1:length(motorData);
    
    fs=motorData{i}.fs;
    turnstart=motorData{i}.idxTurnStart;
    
    totallength=length(motorData{i}.cmXY(:,1));
    
    
    turnfreq= 60*fs*(length(turnstart)/totallength); 
    turnfreqall=[turnfreqall turnfreq];
    
end


meanrate=mean(turnfreqall)
sem=std(turnfreqall)/sqrt(length(turnfreqall))
numberofanimals=length(motorData)

turnrates={};

turnrates.meanrate=meanrate;

turnrates.turnfreqs=turnfreqall;

turnrates.sem=sem;

turnrates.numberofanimals=numberofanimals;

% Save 
clearvars -except turnrates

save turnrates


