# Wendy...
## is a UV-laser projector for printing photographic process

It's based on a 200mW UV laser, a pair of laser galvos, a Raspberry Pi and pure data.

It is mainly intended to be used to UV-print photographic alt processes like cyanotype, dichromat gum, Van Dike, and so on.

It can be used to print pictures directly from computer, and more : designed using pure data (a software aimed at musicians), it's easy to use any data to create any shape to print !

## Project layout

There are different ways to control the laser. Each mode has its own patch main patch, grouping necessary and modular tools. The patch folder contains the sub-patches used. Some have a GUI, other are just abstractions used inside sub-patches.

The position of the laser is controlled using a two channel audio streams, left and right channel beeing X and Y axis, respectively.

Majority of patches take basic settings in ther inlets, and output an audio stream correponding to the laser position. Each patch that sends audio stream has a check box to control if something is output or not.

### Necessary sub-patches
These sub patches are what is indispensable, and so usefull that every main patch should have it.
#### LaserDSP
__usefull__

Just gives an easy way to enable DSP on the control patch, so coordinates can be computed.

#### LaserAngles
__Needed__

Labelled as _Global settings_ in the sub-patch, it permits to set the distance from laser to projection support, as well as angles and DPI. These settings are used to compute maximum projection size, and send basic informations to other subatches, like max size, max angle, angle to mm ratio, dpi, and so on. DPI, distance and angles can be changed.

Each sub-patch should be connected to this one in order to compute positions.

#### LaserFormat
__usefull__

Labbelled as _support size_ on the GUI, this patch just display a rectangle which size is set by user. It's a convenient tool to check where the piece of paper should be placed in front of the laser.

Inlet has to be connected from _Laser Angles_, Outlet to LaserConnexion.

#### LaserOffset
__usefull__

This is another convenient tool that offsets the image projected. The projection defaults centered, offset can be used to move the projected data without having to move the paper.

Inlet has to be connected from _Laser Angles_, Outlet to LaserConnexion.

#### LaseConnexion
__Needed__

Is the last patch of the chain. It receives audio stream from other patches, and send it to the laser. It also provides control functions.

Audio stream is sent _via_ UDP, and control functions _via_ TCP.

There is a field for setting IP address of the laser, and another for the local computer. Thus bidirectionnal communication is possible, and laser can send information for visual feedback on the GUI.

There is a checkbox for DSP toggle on the laser, as well as the ability to set the laser OFF, ON (self-explanatory) and AUTO. In auto mode, the laser lights-up when data is received, and shuts-out as soon as the beam is immobile.

### Main patches
#### Image

This is _the_ patch the laser was designed for. it comprises two subpatches.

_LaserOpenImage_ is used to open a jpeg image. It gives image size in pixels, and default size in mm, according to DPI setting and pixel size. MM size can be changed, it will be the size the image will be projected. A threshold can be applied to the picture, so it's only black and shite with no intermediate shades.

Once the size and threshold are defined, _compute_ can be pressed, and data is sent to the following sub-patch.

Inlet should be connected from _Global settings_, outlet to _Compute image_


_LaserComputeImage_ is then used to effectively send the picture to the laser. It displays a progress bar, and a knob chich can be used to vary speed. Path speed is according to both the knob, and pixel value (white is fast, black is slow).

Inlet should be connected from _Open Image_, outlets~ to _Laser connexion_.

#### Image Wave
It does exactly the same thing as the above, but instead of scanning the file line after line, here the path follows a sine / triangle / sawtooth wave, which amplitude varies according to each pixel value. Speed is constant here.

#### Disk
It uses an audio track (.wav file), which is printed like a vinyl disk, follwing a circle or spiral path. Waveform is then added to the radius. Start radius can be sent, as well as rotation speed, spiral increment, and there is also the possibility to compensate for exposition factor (farther radii leads to fastest path, and under exposure).

Inlet should be connected from _Laser angles_, outlets~ to _Laser connexion_.

#### Gcode
This module can use (very basic !) Gcode to drive the laser by _path_ instead of _raster_. This one is really a hack : Pure Data is not made to (easilly) parse complex files like SVG, so Gcode from Inkscape extension is used here. Only G0 and G1 are understood, so every curve or circle in the original SVG file as to be changed to segments (extensions/modify paht/flatten bezier curves).

Path speed varies according to Z value in the gcode file, and global speed can be changed.

Inlet should be connected from _Laser angles_, outlets~ to _Laser connexion_

#### Sinesum
Is a tool which plays with circles and their harmonics. Main settings are base diameter and frequency.
There are eight circles that can be defined and enable, each with frequency (entire multiple of the base frequency), amplitude (same), angle offset, and the ability to reverse direction or value.

The first circle uses global size and frequency, eahc other uses the first as reference.

Each circle that is enabled is added to the output stream, and simple or more complex forms can then be formed, like epicyloids, cardioids, etc.

inlet should be connected from _Laser angles_, outlets~ to _Laser connexion_.

#### ILDA
Displays a circle inside a square. It's used for calibration purpose.