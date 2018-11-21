Data presented in Figure 3J-M: 
**"Sensorimotor pathway controlling stopping behavior during chemotaxis in the Drosophila melanogaster larva", Tastekin et al., 2018.**

Data

Each folder has kinVariables.mat, which contains the kinematic variables for  individual larvae of the experimental groups indicated in the folder titles. 
Data is obtained using Close Loop Tracker (CLT, Schulze et al., 2015).


|Variables|     |
|---------    |---|
|fps         | frame rate of acquisition|
|scales      | scaling factor|
|skeL        |      skeleton points|
|led         | led stimulus intensity as percentages|
|headposition| position of the head point of the larva in the reference arena|
|tailposition| position of the tail point in the reference arena|
|centroidposition|position of the centroid in the reference arena|
|midposition| position of the middle point in the arena|
|headSpeed| speed of the head point (mm/s)|
|tailSpeed| speed of the tail point (mm/s)|
|centroidSpeed| speed of centroid (mm/s)|
|midSpeed| speed of middle point (mm/s)|
|bodyangle| Body angle|
|headangle| Head angle|
|bodyangleSpeed| Body angle speed|
|headangleSpeed| Head angle speed|
|mode| Behavioral mode classified by CLT (0=unrecognized, 1=run, 2=Turn Left, 3= Turn Right, 4= Stop, 5= Head Cast Left, 6= Head Cast Right, 7= back crawling
|fourier| Fourier coefficient for the contours|
|absX| absolute X-axis position of the CLT stage (in its own units)|
|absY| absolute Y-axis position of the CLT stage (in its own units)|
|sourceX| Position of the odor source in the X-axis.|
|SourceY|Position of the odor source in the Y-axis.|
