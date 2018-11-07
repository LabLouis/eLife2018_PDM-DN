% Number of turns per mm  for individual larvae
% written by Ibrahim Tastekin
% Calculates number of turns per mm distance travelled by the larva for the single larva tracking experiments.
% motorData has to be generated previoulsy.
% Run in the directory, which contains motorData
clearvars
load motorData


turnstart=[];
turnfreq=[];
turnfreqall=[];
turnstart1=[];
turnstart2=[];

distanceall=[];



for i=1:length(motorData);
    
    fs=motorData{i}.fs;
    bot_lim=1; % first frame of analysis
    up_lim=1200; % last frame of analysis
   
    
    turnstart_bot_lim=motorData{i}.idxTurnStart(motorData{i}.idxTurnStart>=bot_lim);
    turnstart_up_lim=motorData{i}.idxTurnStart(motorData{i}.idxTurnStart<=up_lim);
    turnstart=intersect(turnstart_bot_lim,turnstart_up_lim);

 % define the centroid position and interpolate over the tracking errors.
 x=(motorData{i}.cmXY);
   x(x==0)=NaN; %tag tracking errors as NaN

   x=inpaint_nans(x,1); % interpolation with inpaint_nans function
    
   
 % Compute the distance between consecutive points

distance=NaN(1,up_lim-1);

for j=2:up_lim;
       
      distance(j-1)=sqrt((x(j,1)-x(j-1,1))^2+(x(j,2)-x(j-1,2))^2);
     
end

    
sumdistance=sum(distance(1:up_lim-1));


end

distanceall=[distanceall sumdistance];
             
turnfreq=(length(turnstart)/sumdistance);
    
turnfreqall=[turnfreqall turnfreq];
    


meanrate=mean(turnfreqall);
sem=std(turnfreqall)/sqrt(length(turnfreqall));
numberofanimals=length(motorData);

turnrates_per_mm={};

turnrates_per_mm.meanrate=meanrate;

turnrates_per_mm.turnfreqs=turnfreqall;

turnrates_per_mm.sem=sem;

turnrates_per_mm.numberofanimals=numberofanimals;

% Save

clearvars -except turnrates_per_mm

save turnrates_per_mm

