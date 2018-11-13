__author__ = 'David Tadres'
__date__ = '3rd of June, 2018'

"""
This script was used to analyze the functional imaging experiments in the study 'Sensorimotor pathway controlling
stopping behavior during chemotaxis in Drosophila melanogaster larvae'. 
The microscope used was a Ultima Multiphoton imaging system from Prairie. Stimulation of the LED was controlled using
the 'electrophysiology' tab in the software (Prairie View) which lets the user specify a voltage.
The original output of such an experiment is:
1) one .tiff image per frame recorded
2) one file called TSeries*.xml which contains metadata for general imaging settings and for each recorded frame
3) one or more files (in our case always 5) files called TSeries*Cycle*VoltageOutput*.xml. These files describe the
voltage output. One file get created per 'cycle'. A repeat is the number of repeats that were chosen to stimulate
the sample. For example we usually record 5 cycles of the following stimulus: After 3 seconds we give a 1 second
stimulus(2ms on, 31ms off, 30 times) and then no stimulus for ~16seconds. This is repeated 4 more times.
4) a folder called reference (not used in this script)
5) TSeries*Config.cfg (not used in this script)

To use this script (after doing an experiment that creates the same files as mentioned above):
1) Modify: i) the 'path' variable to point to your folder you want to analyze ii) the genotype (will be printed on
graph)
2) Run the script
3) Select and region of interest (only rectangles are possible!)
4) close the window
5) see the resulting files in the original folder

You will notice:
All the small images are gone! They have been read and put into a python-friendly format (the file 'Channel2.npy'). I've
built in an extra security against loosing the original data by saving it also as a zip (the file 'images.zip'). If you
need to get the original images back, just unzip. The reason I like to get rid of the small images is that it takes
forever to copy a lot of small files and only seconds to copy a single medium sized file.
You'll also find a couple of plots. These plots display the time on the x axis and fluorescence or dF/F on the left
y axis. The stimulation is is indicated on the right y axis.
Another file is the 'voltage_config_step.pkl' which was created by the script to not have to go through reconstructing
the stimulus if you want to chose a different ROI.
Additionally, there are csv tables with the result of the analysis. With these numbers it is possible to make plots with
different programs, such as excel. The values are identical to the plots already in the folder. 

Internally, the script does the following:
1) Try to read all the images, if the first time script is run on a dataset it will read all tiff files, sort by name,
deposit in numpy 3D (2D image + time) matrix and save both as zip and npy file. If not the first time, just read the 
npy file.
2) Organize images by cycle (e.g. image 1-154 is first cycle, 155 to 309 is second cycle etc...)
3) What's the voltage output and what is its timing?
4) The electrophysiology tab lets one define timepoints in milliseconds relative to the start of an cycle. The
images are not neatly organized in milliseconds, but as fast as the microscope can collect the data, e.g. at frame 1:
0s, at frame 2: 0.0709127078755347s etc. In order to associate each frame with a given timepoint of the stimulus the
script will associate a given frame with the closest (not the perfect!) millisecond. See details in code itself.
5) Present the user with the mean image of experiment so that an ROI can be chosen.
6) Take the mean over time of all the pixels in the ROI and save.
7) For each timepoint (in the stimulus time frame) check if an image can be assigned, if not pass, if yes take mean
of the pixel values in the ROI and save.
8) Get the mean grayscale value for the time before the stimulus. The time used was 2000 milliseconds and can be
 changed with the 'F_zero_time' variable.
9) calculate dF/F = (F(t)  - F_0)/F_0
10) plot several graphs and save the csv file with the raw ratios
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import glob
import natsort
from skimage.io import imread
import zipfile
import pandas as pd
import xml.etree.ElementTree as ET
import pickle
import matplotlib.patches as patches
from matplotlib import gridspec
from matplotlib.patches import Rectangle
import tifffile

########################################################################################################################
# you probably only need to change some things in here
path = 'C:\\Users\\David\\Desktop\\test\\TSeries-03272018-1053-001\\'
genotype = 'SS01994x75C02-lexA'
identifier = '180327 brain#1 Tseries1'
########################################################################################################################

# This is the time before the stimulus that this script takes to normalize the fluorescence
F_zero_time = 2000
# Define colormap of the single images, other valid choices can be found here:
# https://matplotlib.org/2.0.2/examples/color/colormaps_reference.html
colormap_single_image = 'magma'
# Saves plotting single graphs in png and transparent if set to 'True'. Alternative is 'False'
single_plots = True


class AnnotateRectangle(object):
    """
    This class lets the user select a rectangle on a matplotlib plot by first pressing the mouse button on one edge
    and releasing the mouse button at another edge. It saves the x and y coordinates of both x and y coordinates
    to define the region of interest.
    """
    def __init__(self):
        self.ax = plt.gca()
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.rect = Rectangle((0, 0), 1, 1, hatch='//', fill=False)  # initiate the rectangle
        self.ax.add_patch(self.rect)  # draw the rectangle
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        print('press')
        self.x0 = event.xdata
        self.y0 = event.ydata

    def on_release(self, event):
        print('released')
        if event.xdata > self.x0:
            self.x1 = event.xdata
        else:
            self.x1 = self.x0.copy()
            self.x0 = event.xdata
        if event.ydata > self.y0:
            self.y1 = event.ydata
        else:
            self.y1 = self.y0.copy()
            self.y0 = event.ydata
        self.rect.set_width(self.x1 - self.x0)
        self.rect.set_height(self.y1 - self.y0)
        self.rect.set_xy((self.x0, self.y0))
        self.ax.figure.canvas.draw()


os.chdir(path)

# The values below are measurements using the lightmeter PM100D using the light sensor S130VC (both from Thorlabs Inc.).
# The LED light was measured through the objective. The values below Volts (on the left, e.g. 0.91, the output in the
# xml file) and uW (on the right, e.g. 4.5)

light_intensity_measurement = np.zeros((2, 19))
light_intensity_measurement[:, 0] = 0.91, 4.5
light_intensity_measurement[:, 1] = 0.92, 8
light_intensity_measurement[:, 2] = 0.93, 11.5
light_intensity_measurement[:, 3] = 0.94, 14.5
light_intensity_measurement[:, 4] = 0.95, 16.5
light_intensity_measurement[:, 5] = 0.96, 20
light_intensity_measurement[:, 6] = 0.97, 22.5
light_intensity_measurement[:, 7] = 0.98, 25.5
light_intensity_measurement[:, 8] = 0.99, 28
light_intensity_measurement[:, 9] = 1.0, 31
light_intensity_measurement[:, 10] = 1.1, 59
light_intensity_measurement[:, 11] = 1.2, 95
light_intensity_measurement[:, 12] = 1.3, 123
light_intensity_measurement[:, 12] = 1.4, 147
light_intensity_measurement[:, 13] = 1.5, 166
light_intensity_measurement[:, 14] = 1.6, 188
light_intensity_measurement[:, 15] = 1.7, 209
light_intensity_measurement[:, 16] = 1.8, 230
light_intensity_measurement[:, 17] = 1.9, 251
light_intensity_measurement[:, 18] = 2.0, 271

# The value that is needed for comparison is the light intensity per area, not the absolute light intensity given above.
# The objective used for the experiments was a Olympus LUMPLFLN 60XW. It has a field number of 26.5 and a magnification
# of 60. The diamater of the field size is therefore: 26.5 / 60 = 0.441mm.
# Circle with diameter of 0.441mm is: (0.441mm/2)^2 * pi = 0.15mm^2.
# The area of the circle is calculated for the focal plane, which might differ for the neuron that was recorded from and
# the neuron that was activated.

light_intensity_measurement[1, :] /= 0.15  # light intensity is now in uW/mm2

# Read the image data and put it into memory for analysis
try:
    image_raw = np.load('Channel_2.npy')
except FileNotFoundError:
    # if we take data directly from the microscope we first have to read all the single images
    image_name = [p.replace('\\', '') for p in glob.glob('*Ch2*')]
    # sort the names 'naturally' (1,2,3...)
    image_name = natsort.natsorted(image_name)
    # make a zipfile without compression to get a single file for all the images - it takes forever to copy 1000images
    # even if only 1.5kb in size
    zf = zipfile.ZipFile('images.zip', mode='w')
    try:
        # run through all the image names, read the image file and put in the image_raw numpy array. Also put into
        # the zip file. In the interest of speed, in the first cycle, we preallocate the numpy array
        for i in range(len(image_name)):
            if i == 0:
                im = imread(image_name[i])
                image_raw = np.zeros((im.shape[0], im.shape[1], len(image_name)), dtype=im.dtype)
                image_raw[:, :, i] = im
            else:
                image_raw[:, :, i] = imread(image_name[i])
            zf.write(image_name[i])
    finally:
        # close the zip file writing process
        zf.close()
    # save the numpy array. This will be read (and is much faster) if the user want to reanalyze some data, e.g. chose
    # a different region of interest
    np.save('Channel_2.npy', image_raw)

    # After making sure that all the images have been safely stored both in a numpy array AND a zip file, run through
    # them again and remove all of the images
    for i in range(len(image_name)):
        os.remove(image_name[i])


# How many cycles of the stimulus do we have? Start by looking up the xml file coming from the microscope
xml_experiment = [p.replace('\\', '') for p in glob.glob('*xml')]
# get the root of the xml file
root_xml_experiment = ET.parse(xml_experiment[0]).getroot()
# should be third root and we look for all the 'Frame's in the third root. The length gives us the number of
# images/cycle
images_per_cycle = len(root_xml_experiment[3].findall('Frame'))
# How many cycles of the stimulus do we have? The Prairie software writes an independent xml file with 'voltageout'
# in its name for each cycle therefore the number of xml files with that indicator gives us the number of cycles
number_of_cycles = len([p.replace('\\', '') for p in glob.glob('*VoltageOut*')])

# Next we need to find the voltage output - The way I do experiments is that I don't change the stimulus between
# cycles, so we only look at the first voltage out xml file
xml_names_voltage = [p.replace('\\', '') for p in glob.glob('*VoltageOut*')]
xml = ET.parse(xml_names_voltage[0])
root = xml.getroot()


try:
    voltage_output = pickle.load(open('voltage_config.pkl', 'rb'))
except FileNotFoundError:
    # This is looking at step Stimuli. The script reads the different variables saved by the Prairie View software and
    # puts these values in a dictionary with descriptive names.
    voltage_output = {'LED': root[4].find('Name').text, 'Units': root[4].find('Units').text,
                      'PulseCount': float(root[4].find('WaveformComponent_PulseTrain').find('PulseCount').text),
                      'PulseWidth': float(root[4].find('WaveformComponent_PulseTrain').find('PulseWidth').text),
                      'PulseSpacing': float(root[4].find('WaveformComponent_PulseTrain').find('PulseSpacing').text),
                      'RestPotential': float(root[4].find('WaveformComponent_PulseTrain').find('RestPotential').text),
                      'FirstPulseDelay': float(
                          root[4].find('WaveformComponent_PulseTrain').find('FirstPulseDelay').text),
                      'Cycles': len(xml_names_voltage),
                      'Voltage': float(root[4].find('WaveformComponent_PulseTrain').find('PulsePotentialStart').text),
                      'Stimlulus Style': 'step stimulus'}
    # save all that data in the experiment folder for future reference
    pickle.dump(voltage_output, open('voltage_config.pkl', 'wb'))

# Here the frame period (how many seconds to record a frame?) is read from the microscopy data
xml_names_all = [p.replace('\\', '') for p in glob.glob('*.xml*')]
xml = ET.parse(xml_names_all[0])
root = xml.getroot()
frame_period = False
i_frame_period = 0
while not frame_period:
    if root.find('PVStateShard')[i_frame_period].get('key') == 'rastersPerFrame':
        raster_per_frame = float(root.find('PVStateShard')[i_frame_period].get('value'))
    if root.find('PVStateShard')[i_frame_period].get('key') == 'framePeriod':
        frame_period = float(root.find('PVStateShard')[i_frame_period].get('value'))
        continue
    else:
        i_frame_period += 1
        pass

frame_period = frame_period / raster_per_frame

# time of one cycle in milliseconds
time_per_cycle_in_ms = images_per_cycle * (frame_period * 1000)

# Problem: 'Real' time is defined in milliseconds using the information from the voltage output files. The resolution
# is 1 millisecond.
# Framerate is not defined precisely enough using milliseconds. In order to not have a ridiculous large array which
# will be mostly empty, each frame is rounded to the closest index in milliseconds. It usually takes more than
# 1 millisecond to record a frame (eg. a 78x64pixel images takes 63.52ms). Therefore the assignment of each frame is
# not perfect but a very good approximation.
# To make the system work the pre-allocated array needs to be large enough. Two situations can arise:
# 1) the frame_period is rounded down (e.g. it takes 13.4ms to take a frame or
# 2) the frame_period is rounded up (e.g. it takes 15.6ms to take a frame).
# In the first case one frame will be assigned to time = 0, the next frame to time = 13, the next frame to time = 26
# etc. Note: This is not optimal for long experiments because an error is introduced with the size of the decimal of
# the frame_period if smaller than .5 and (e.g. if 13.4 the error introduced is 0.4ms/frame) or 1-decimal of the
# frame_period if >= 0.5 (e.g. if 15.6 the error introduced is also 0.4ms/frame (because 1-0.6).
# For the experiments conducted here it's good enough however. A typical experiment (=1 cycle) lasts for ~20'000ms and
# consists of 200-400 frames. A typical frame period is therefore anything between 50-100. At 20'000ms there can be
# a maximum shift of 0.5*400 = 200milliseconds which equals 4 frames. For the analysis of the paper we focus on the
# first 10 seconds of the experiment, the shift is therefore a maximum of 2 frames (and much smaller in most cases) of
# a total of 200 frames.
rounding_error = np.round(frame_period * 1000) - frame_period * 1000
if rounding_error <= 0:
    rounding_error = 0
else:
    rounding_error = int(np.ceil(images_per_cycle * rounding_error))
# Initialize an array with as many indices as there are milliseconds per cycle.
stimulation_over_time = np.zeros(
    int(np.ceil(time_per_cycle_in_ms)))

# Next, we identify the number of stimulation points we get. This number is different from the image number. As we
# will always have many more stimulation points than images our reference frame will be the stimulation points
# Note: We are working in one cycle and concatenate several of those for repeats of the cycle

# We start by filling the stimulation_over_time array with the resting potential (technically this is now in voltage
# while the rest will be in uW/mm2 but the resting potential and therefore the light power will both be zero
stimulation_over_time[:] = voltage_output['RestPotential']
if voltage_output['Stimlulus Style'] == 'step stimulus':
    # then, for the amount of Pulse (usually very short, in the order of ms) spikes of voltage, e.g. the 2ms on, 31ms
    # off 30 times stimulus protocol used for our experiments
    for i in range(int(voltage_output['PulseCount'])):
        if i == 0:
            index_start = int(voltage_output['FirstPulseDelay'])
            index_end = int(voltage_output['FirstPulseDelay'] + voltage_output['PulseWidth'])
            stimulation_over_time[index_start:index_end] = light_intensity_measurement[
                1, np.where(light_intensity_measurement[0, :] == voltage_output['Voltage'])[0]]
            next_index_start = int(index_end + voltage_output['PulseSpacing'])
        else:
            index_start = next_index_start
            index_end = int(index_start + voltage_output['PulseWidth'])
            stimulation_over_time[index_start:index_end] = light_intensity_measurement[
                1, np.where(light_intensity_measurement[0, :] == voltage_output['Voltage'])[0]]
            next_index_start = int(index_start + voltage_output['PulseSpacing'])

# in an initial version more than one ROI could be chosen. Hard to interpret the graphs, though! Decided to go with
# a single ROI for now
number_of_roi = 1

# Let the user define a ROI with the mouse by clicking on one edge of the rectangle and release at the opposite side.
datatype = [('x0', float), ('x1', float), ('y0', float), ('y1', float)]
ROIs = np.zeros((int(number_of_roi)), dtype=datatype)
fig = plt.figure('Select a region of interest')
ax = fig.add_subplot(111)
ax.imshow(np.nanmean(image_raw, axis=2))
roi = AnnotateRectangle()
plt.show(block=True)
ROIs['x0'][0] = roi.x0
ROIs['x1'][0] = roi.x1
ROIs['y0'][0] = roi.y0
ROIs['y1'][0] = roi.y1

# if first ROI, pre-allocate an empty array with the number of images so that each timepoint for which we have an
# image can get a single value for the raw fluorescence measured over the whole experiment
roi_over_time = np.zeros((image_raw.shape[2]))

# Then, just take the mean of all pixel intensities in the user defined ROI and put into that array
roi_over_time[:] = np.nanmean(image_raw[int(roi.y0):int(roi.y1), int(roi.x0):int(roi.x1)], axis=(0, 1))

# Next, in order to align the image time frame to the stimulation time frame another empty array is created. This
# array has enough place to save one value per milli-second (the resolution of the voltage output). There will always
# be more space in this array than is needed for the images - therefore thew hole array is filled with NaN for now.
# Later, the appropriate indexes will be filled with values of the grayscale value of the image. Most of this array
# will always be 'nan', of course.
mean_intensity_in_stim_time_frame = np.zeros(
    (stimulation_over_time.shape[0] + rounding_error, voltage_output['Cycles']))
mean_intensity_in_stim_time_frame.fill(np.nan)

# This nested loop aligns the two time frames.
counter = 0
if voltage_output['Stimlulus Style'] == 'step stimulus':
    # the outer loop runs over each cycle (usually one cycle is around 20seconds, and there can be anything between 2
    # and 10 of those)
    for outer_i in range(voltage_output['Cycles']):
        # the inner loop goes over each frame
        os.makedirs(path + 'single_frames', exist_ok=True)
        stimulus_started = False
        during_stim_saved = False
        for i_inner in range(images_per_cycle):

            if i_inner == 0:
                # first it finds the index. Here we introduce a bit of inprecision as it usually not the case that
                # the time it takes to record a frame turns out to be an integer. We have to round as only integer
                # can be used to index.
                index = int(np.round(frame_period * 1000))
                # take the mean intensity of the ROI in question (could also take the roi_over_time array)
                mean_intensity_in_stim_time_frame[index, outer_i] = np.nanmean(
                    image_raw[int(roi.y0):int(roi.y1), int(roi.x0):int(roi.x1), counter])
                counter += 1
            else:
                # for the second and all consecutive images we just slide along the stimulus time frame and add
                # the mean fluorescence
                index += int(np.round(frame_period * 1000))
                mean_intensity_in_stim_time_frame[index, outer_i] = np.nanmean(
                    image_raw[int(roi.y0):int(roi.y1), int(roi.x0):int(roi.x1), counter])

                # The code below takes a frame just before the start of the stimulation and the last frame during the
                # stimulation. This is used to visualize the difference in recorded fluorescent intensity during the
                # experiment.
                if not stimulus_started:
                    # This checks if in the next frame there is a stimulus or not - used to check whether stimulus
                    # started
                    if (stimulation_over_time[index:int(index+np.round(frame_period*1000))] > 0).any():
                        # save that image as the reference just before the stimulus. Use Tiff to keep original grayscale
                        # values
                        tifffile.imsave('single_frames\\' + identifier + 'repeat #' + repr(int(outer_i+1)) +
                                        'before stimulus.tiff', image_raw[:, :, counter])
                        index_image_before = counter
                        before_image = image_raw[:, :, counter].copy()
                        stimulus_started = True
                elif stimulus_started and not during_stim_saved:
                    # to get the maximum response, the image before the stimulus ends, is being saved

                    if (stimulation_over_time[index::] == 0).all():
                        # again, save as tiff file to keep the grayscale values
                        tifffile.imsave('single_frames\\' + identifier + 'repeat #' + repr(int(outer_i+1)) +
                                        'last stimulus frame.tiff',image_raw[:, :, counter])

                        # Besides saving the tiff file with the true grayscale value, also save jpg for easy
                        # visualization
                        # max grayscale value could be from either image
                        max_value = np.amax(image_raw[:, :, index_image_before])
                        if np.amax(image_raw[:, :, counter]) > max_value:
                            max_value = np.amax(image_raw[:, :, counter])
                        before_image_fig = plt.figure()
                        before_image_ax = plt.Axes(before_image_fig, [0., 0., 1., 1.])
                        before_image_ax.set_axis_off()
                        before_image_fig.add_axes(before_image_ax)
                        before_image_ax.imshow(image_raw[:, :, index_image_before],
                                               vmax=max_value,
                                               cmap=colormap_single_image)
                        before_image_fig.savefig('single_frames\\' + identifier + 'repeat #' + repr(int(outer_i+1)) +
                                                 'before stimulus frame.jpg', bbox_inches='tight')

                        after_image_fig = plt.figure()
                        after_image_ax = plt.Axes(after_image_fig, [0., 0., 1., 1.])
                        after_image_ax.set_axis_off()
                        after_image_fig.add_axes(after_image_ax)
                        after_image_ax.imshow(image_raw[:, :, counter], vmax=max_value, cmap=colormap_single_image)
                        after_image_fig.savefig('single_frames\\' + identifier + 'repeat #' + repr(int(outer_i+1)) +
                                                'last stimulus frame.jpg', bbox_inches='tight')

                        plt.close(before_image_fig)
                        plt.close(after_image_fig)

                        during_stim_saved = True

                counter += 1

# calc deltaF over F: http://www.nature.com/nprot/journal/v6/n1/box/nprot.2010.169_BX1.html
# https://www.nature.com/articles/nprot.2010.169 (link above seems to be broken)

# rename some variables to be identical to the equation in the paper referenced above
F = mean_intensity_in_stim_time_frame
# pre-allocate an empty array to deposit F zero (the mean fluorescence before the stimulus)
F_zero = np.zeros((voltage_output['Cycles']))
if voltage_output['Stimlulus Style'] == 'step stimulus':
    # do that for every cycle
    for f_zero_loop in range(F_zero.shape[0]):
        F_zero[f_zero_loop] = np.nanmean(F[int(voltage_output['FirstPulseDelay'] -
                                               F_zero_time): int(voltage_output['FirstPulseDelay']), f_zero_loop])

# calculate the delta F over F (no noise filtering as in the nature protocols paper linked above)
delta_F_over_F = np.zeros((F.shape[0], F.shape[1]))
delta_F_over_F.fill(np.nan)
for f_loop in range(F.shape[1]):
    delta_F_over_F[:, f_loop] = (F[:, f_loop] - F_zero[f_loop]) / F_zero[f_loop]

# get the mean, the median and the standard deviation of dF/F over all cycles
mean_delta_F_over_F = np.nanmean(delta_F_over_F, axis=1)
median_delta_F_over_F = np.nanmedian(delta_F_over_F, axis=1)
std_delta_F_over_F = np.nanstd(delta_F_over_F, axis=1)

# save the data in a csv file to make the plots in different colorschemes and other programs.
# Save: 1) time, 2) stimulation in voltage, mean deltaF/F for each repetion. Also save median delta F/F and standard
# deviation of the mean
csv_stimulus_frame = pd.DataFrame({
                           'Time[ms]': np.arange(0, mean_delta_F_over_F[0:stimulation_over_time.shape[0]].shape[0]),
                           'Stimulation[V]': stimulation_over_time,
                           'mean delta F/F': mean_delta_F_over_F[0:stimulation_over_time.shape[0]],
                           'median delta F/F': median_delta_F_over_F[0:stimulation_over_time.shape[0]],
                           'STD delta F/F': std_delta_F_over_F[0:stimulation_over_time.shape[0]]
                           })
csv_stimulus_frame = csv_stimulus_frame[['Time[ms]', 'Stimulation[V]', 'mean delta F/F', 'median delta F/F',
                                         'STD delta F/F']]
# Also save the dF/F of each cycle
for i_cycle in range(voltage_output['Cycles']):
    current_dF_over_F = pd.DataFrame({'delta F/F repetition #' + repr(int(i_cycle+1)): delta_F_over_F[:, i_cycle]})
    csv_stimulus_frame = pd.concat([csv_stimulus_frame, current_dF_over_F], axis=1)

# now save te csv file as is
csv_stimulus_frame.to_csv(identifier + 'delta F data original.csv', header=True)
# and once without any NaNs (easier to read for humans, easy to plot)
csv_stimulus_frame[csv_stimulus_frame['mean delta F/F'].notnull()].to_csv(identifier + 'delta F data no nan.csv',
                                                                          header=True)

# now the scripts saves some plots for a quick visualization of the dF/F
# the first plot will plot the mean dF/F on the top left, the median dF/F on the bottom left, the mean image with the
# chosen ROI in the top right and an overview over the single cycles on the bottom right.
gs = gridspec.GridSpec(2, 2)
fig = plt.figure(figsize=(15, 10))
ax_top_left = fig.add_subplot(gs[0:1, 0:1])
ax_top_left_right = ax_top_left.twinx()
ax_top_right = fig.add_subplot(gs[0:1, 1:2])
ax_bottom_left = fig.add_subplot(gs[1:2, 0:1])
ax_bottom_left_right = ax_bottom_left.twinx()
ax_bottom_right = fig.add_subplot(gs[1:2, 1:2])
ax_bottom_right_right = ax_bottom_right.twinx()

# In order to plot the array that consists mostly of NaNs, a mask needs to be created that identifies the indexes with
# non-NaN values
mean_intensity_in_stim_time_frame_mask = np.isfinite(mean_intensity_in_stim_time_frame[:, 0])
# for the x-axis an array is created with just counts from zero to the time in milliseconds that one cycle lasts
time_as_range = np.arange(mean_intensity_in_stim_time_frame.shape[0])

# Plot the top left subplot (mean delta F/F)
ax_top_left.plot(time_as_range[mean_intensity_in_stim_time_frame_mask],
                 mean_delta_F_over_F[mean_intensity_in_stim_time_frame_mask],
                 label='mean ' + r'$\Delta F/F$')
ax_top_left_right.plot(stimulation_over_time, alpha=0.3, color='r', label='Stimulation [' + r'$\mu$' + 'W/mm]')
ax_top_left.set_ylabel(r'$\Delta F/F$, F zero :' + repr(F_zero_time) + 'ms')
ax_top_left.set_xlabel('Time in ms')
ax_top_left_right.set_ylabel('LED Stimulation [' + r'$\mu$' + r'$W/mm^2$]')
ax_top_left.set_title('Mean delta F over F over ' + repr(voltage_output['Cycles']) + ' cycle')
if np.nanmax(mean_delta_F_over_F) < 1:
    ax_top_left.set_ylim(-1, 1)
else:
    ax_top_left.set_ylim(-1, np.ceil(np.nanmax(mean_delta_F_over_F)))
ax_top_left.grid()
ax_top_left.legend()

# plot top right (mean image with indication of ROI
ax_top_right.imshow(np.nanmean(image_raw, axis=2), cmap='hot')
for i in range(int(number_of_roi)):
    ax_top_right.add_patch(
        patches.Rectangle(
            (ROIs['x0'][i], ROIs['y0'][i]),  # (x,y)
            ROIs['x1'][i] - ROIs['x0'][i],  # width
            ROIs['y1'][i] - ROIs['y0'][i],  # height
            fill=False,
            edgecolor='g',
            linewidth=3
        )
    )

# plot bottom left (median delta F/F)
ax_bottom_left.plot(time_as_range[mean_intensity_in_stim_time_frame_mask],
                    median_delta_F_over_F[mean_intensity_in_stim_time_frame_mask],
                    label='median ' + r'$\Delta F/F$')
ax_bottom_left_right.plot(stimulation_over_time, alpha=0.3, color='r', label='Stimulation [' + r'$\mu$' + 'W/mm]')
ax_bottom_left.set_ylabel(r'$\Delta F/F$, F zero :' + repr(F_zero_time) + 'ms')
ax_bottom_left.set_xlabel('Time in ms')
ax_bottom_left_right.set_ylabel('LED Stimulation [' + r'$\mu$' + r'$W/mm^2$]')
if np.nanmax(median_delta_F_over_F) < 1:
    ax_top_left.set_ylim(-1, 1)
else:
    ax_top_left.set_ylim(-1, np.ceil(np.nanmax(median_delta_F_over_F)))
ax_bottom_left.legend()
ax_bottom_left.grid()
ax_bottom_left.set_title('Median delta F over F over ' + repr(voltage_output['Cycles']) + ' Cycles')

# plot bottom right (display single cycles) of delta F/F
colors = ['b', 'r', 'g', 'm', 'orange']
for ax_i in range(int(number_of_cycles)):
    ax_bottom_right.plot(time_as_range[mean_intensity_in_stim_time_frame_mask],
                         mean_intensity_in_stim_time_frame[mean_intensity_in_stim_time_frame_mask, ax_i],
                         colors[ax_i],
                         alpha=0.7,
                         label=r'$\Delta F/F$, cycle: ' + repr(int(ax_i + 1)))
ax_bottom_right_right.plot(stimulation_over_time, alpha=0.3, color='r', label='Stimulation [' + r'$\mu$' + 'W/mm]')
ax_bottom_right.set_ylabel(r'$\Delta F/F$, F zero :' + repr(F_zero_time) + 'ms')
ax_bottom_right_right.set_ylabel('LED Stimulation [' + r'$\mu$' + r'$W/mm^2$]')
ax_bottom_right.legend()

if voltage_output['Stimlulus Style'] == 'step stimulus':
    ax_top_right.set_title(genotype + '\n''Stimulation: ' + repr(int(voltage_output['PulseCount'])) + ' repetitons of '
                           + repr(int(voltage_output['PulseWidth'])) + 'ms of ' + repr(float(voltage_output['Voltage']))
                           + voltage_output['Units'] + 'with interpulse Interval of ' + repr(
                            int(voltage_output['PulseSpacing'])) + 'ms')
plt.tight_layout()
plt.show(block=True)
fig.savefig('Mean delta F over F over ' + repr(voltage_output['Cycles']) + ' cycles')
