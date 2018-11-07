% Plot trajectories single larva tracking
% experiments
% Written by Ibrahim Tastekin
% Definition: Plots trajectories for randomly selected larvae. Uses the
% centroid position.
% motorData has to be generated previously
% Run in the directory, which contains motorData
clearvars

load motorData

number_of_animals_to_plot=8;
random_larvae=randperm(length(motorData),number_of_animals_to_plot);

for animal=random_larvae;
    
%% Create the variables


figure(1)
hold on
x=motorData{animal}.cmXY;
h=motorData{animal}.tailXY;
c=motorData{animal}.sourceXY;
d=motorData{animal}.idxTurnEnd;

% interpolate over tracking errors
x(x==0)=NaN;
h(h==0)=NaN;

cm=inpaint_nans(x,1);
head=inpaint_nans(h,1);

y=(x(a,:));


col='k'; % define color for plotting

%% Plot interpolated centroid position


plot(cm(:,1),cm(:,2),'color',col,'Linewidth',1);


plot(cm(1,1),cm(1,2),'*','MarkerEdgeColor','r','Linewidth',1) % plot first position as a star


%% Plot source position as a circle
plot((motorData{animal}.sourceXY(:,1)),(motorData{animal}.sourceXY(:,2)),'o','MarkerFaceColor','r','MarkerEdgeColor','r')

axis equal
%Flip the axis and define the size
axis([0 128 0 85])
set(gca,'YDir','reverse')
set(gca,'XDir','Normal')
hold off
end