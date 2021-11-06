World is pixel!
But pixels wish to spawn.
So spawn them, collect them,
highlight them, scroll through the
coordinates.

Tip: How to synchronize two objects in same place with object repros
animated and with spin. Save scene with unique name and use 
"read out voxels", in dialog choose object to copy from. Both objects
need have same tessellation.

Tip: When using falloff with object that has multiple levels visible,
press 'm' first to highlight same level. Then press 'f' to refresh falloff
or set falloff in menu.

Sources in Sources directory.
---------------------------
Now "Lock Angle" detects objects with same position and sets their rotation
accordingly.

---------------------------
Now "vector animation" can be generated from UI. Its under animation sequence.
Vector animation consists of three parts, separated by commas.

---------------------------
"Randomize animation" added. This is animation feature and shifts certain
keyframes around to make "randomized" feel to the current animation.

---------------------------
New feature for animation: "animation crossfade", also "vector animation crossfade".
Crossfade fades in and out between first animation and second animation. Also it uses
setShape and setColor toggles for usual animation. Second animation can also be other size
dimensionwise than first. First however must fit object current active dimensions, else
error is generated and animation has wrong size for this division.

---------------------------
As huge renewal, "vector animation" is added. This function scans neighbouring voxels for
their movement and calculate a simple vector based on it.
Vector animation is saved into Animation directory and is picked up when user presses 'p'.

---------------------------
Horizontal banding as 2d effect is added
and is saved with scene.

---------------------------
For 'darwin' platform special rendering mode is excepted.
With DragAndDrop view open, clearcolor alpha is used.

---------------------------
Clearcolor composing added.

---------------------------
Now syncPositions and syncLevels are saved with scene.

---------------------------
syncPositions is added.

---------------------------
Now "truncate voxels" reads "truncate voxels and arrays". Invisible arrays are deleted
along invisible voxels. Also meaning they are not saved after this if not respawned.

---------------------------
Now voxels are rotated via arrays: Added rotated arrays and baked arrays.
However switching coords into baked and back needs to be done element by element.

---------------------------
Now "Noise" "Banding" "Blur" and "Median" modes are saved and loaded with scene.

---------------------------
"Noise Mode" and "Median Mode" added. Median mode turns off blur, if on.

---------------------------
Alpha premultiplication is now built into. Background color is saved with
scene and affects alpha premultiplication. Its pronounced in blur mode.
First you set background color, then load or drop images.

---------------------------
"Blur Mode". Now in surface mode (non Open GL) blur mode can be used to
achieve depth blur.

---------------------------
Drag and drop on canvas now accepts per voxel images and objects.
For SDL mode "Voxel Based repro" must be on, else "Voxel Based" must be on.
Else current object gets image or repro. In SDL_Mode textures can be
dropped to objects or collection of voxels.

---------------------------
Now arrays are dumped for objects into Arrays directory under scene.
It involves visibility, color and size.

---------------------------
Special flags, or blend modes are now saved with scene.

---------------------------
Added pygame surface special_flags in Help menu. When Raster pic is little off the
scale, blend funcs may help.

---------------------------
Big advancements: integrated arrays work now. By manipulating arrays, voxels
change. By changing voxels, arrays change. Loading frame uses array slice operation.
And in other places arrays are used. In the future i look forward to speed up
spawning maybe using arrays, but this is little unclear.

---------------------------
Now alpha is used for loaded and projected images: png file uses alpha in
"rgba" mode.

---------------------------
"Play textures directory" is added. Now ImagePlane.obj is loaded at startup.
It has uv coordinates and can project to the voxels a sequence of images
with "Play textures directory"

---------------------------
Changes in animation generation: Now FG and BG colors are picked up when
"setColor" is on in "Set Shapes" menu.

---------------------------
Short explanation for sentences: 
Xdim, Ydim, Zdim > dimensions in x, y, z axis.
cos, sin > math functions.
x, y, z > coordinates in matrix or in partial matrix.
i > frame
pi > pi
level > level is 1.0 for single voxel, 0.5 for 2x2x2 matrix, 0.25 for 4x4x4 ...
c > voxel natural size at level > 2 * level

First we use two components for a good sentence:
1. c > natural size
2. trigonometry sin and cos to produce a number varing from zero to one.

Composing the sentence:
3. Now its multiplication or division.
4. When dividing we replace multiplication with division and enclose the rest in brackets
   and add to the end: c * Xdim
5. When multiply, rest is the composition of cos and sin functions.

What is inside cos and sin functions?
6. cos((x * level - 0.5 + level / 2) * pi + i / pi)
7. sin((y * level - 0.5 + level / 2) * pi + pi * 2)

pi and i are working together to produce a loop in animations.
We could use pi / 2, but then animation jumps at the end / begin point in time.

What to do there inside?
8. Experiment with replacing variable 0.5 with a x, y, z or changing it to another value
9. Also to reverse scroll directions use minus sign in front of x, y, z ...

What is "None" ?
10. It cleans animation.

---------------------------
Now voxels are rotated using offset method. First cube is rotated and its
vectors are used to offset all the voxels into the proper place.

---------------------------
Now OBJ loading and its texture can be dragged and dropped to animpane(red).
To place them, press 'p' over animpane.

---------------------------
Now falloff 0 works with selection (yellow). After selecting zero from menu,
selection is dropped and falloff is selection. Keyframes affect falloff.
To drop falloff, have no selection and select zero again.

---------------------------
Animation files are not using cPickle any more, they use now native numpy dump method.
Also note, that animation files are written into new scenes when scene is saved.

---------------------------
Keyframes accompany scenes now. Keyframes are found in keyframes directory.

---------------------------
Several optimizations to lift speed. In loading. In selecting. In falloff.

---------------------------
Animations redesigned! Now only subset for animation cube can be generated.
Animation is generated and loaded for visible voxels for current level.

---------------------------
Now in "3d Cube Commands" menu "fill animation" and "start animation" do
not write and load Animation pickle file (pkl). This is useful for
temporary animation.

---------------------------
In "Select array" menu now is a toggle for "Zipped spawn".
Zipped means that voxel has underlying info. By using "Zipped spawn"
you can constrain refinement only to these voxels. Refinement is done
by pressing (+) and what to refine can be selected by a rectangle or by "m".

---------------------------
Now OBJ Mode uses textures and mtl files to place and pick texture colors.
To clean already loaded OBJ texture, be in "OBJ Mode" and use "Clean Texture"
in "Load OBJ" menu.

---------------------------
Now in SDL mode keys "q" and "a" act as left Ctrl and Shift modifyer keys.
Enough to tap once and perform rectangle selection. To get mouse focus to the
frame containing 3d view, move to a ui element and back to the embed frame.

---------------------------
Now "sync levels" switch says to objects to subdivide synchronously,
if the voxels have same location in current space.
To subdivide press (+), to collect press (-). To select same level 
press (m) and to collapse them press button named "collapse".

---------------------------
Now canvas interaction is improved in SDL mode (Open GL embed).
Keypresses come through.

---------------------------
Saving new scene, copys over Animation files from old scene.

---------------------------
Change in animations system. Now animation files have two digits in their
names. Last digit shows the animation dimension. Load according animations
to the corresponding levels. With "sync animation" on, objects show animation
of current object when "p" is pressed and generated animation is displayed
for all objects, when level is less.

---------------------------
"spawn_to_voxels" and "span_out_voxels" added to avoid spaning to
minor level every voxel in object.

---------------------------
Now filling animation when "sync animation" is on, fills neighbouring objects
only if their subdivision (by level of highlighted) is equal or less.

---------------------------
Elliminated hardtofind bug in voxels renumbering while saving.
(added renumber_invisible function)

---------------------------
Sync voxels is limited to visible voxels in objects.

---------------------------
New option - checkbox - "minor level". What is minor level?
This option affects saving and loading. With saving this option
says that for objects minor level or dimension is saved.
Program finds smallest divisions in hierarchys (also hidden voxels).
Hierarchys are saved anyway, if exsist, but minor level affects
reading and writing hidden or "Zipped" data.
When loading, when on, first objects are subdivided to the saved
level and then collapsed and then respawned. When objects are saved
with hidden data and minor level is off when loading them, they
are not collapsed and respawned, only subdivided.
By default minor level is on. This means bigger files.
To save still compacted files, you can discard hidden data
with "truncate voxels".
Q: When to turn off "minor level" (in "Select array" menu)?
A: When you load a file with hidden levels to fine for whole
objects to be refined to by span_recursive function. 
When you need to open such scene, then you need to control the natural 
spawn level manually by modifying actual file. 
Objects 1 dimension is in "object" -> "object1_pos.txt" for object1.
To avoid such files, control spawn level with "truncate voxels" to
get rid of hidden subdivisions no longer needed.
And save with "minor level" off.


---------------------------
"Zipped" marker in "About This Voxel". When new scene is loaded, user can open
this dialog and check if something should be under a certain voxel (Zipped - Yes),
if yes subdivide and reload if not already loaded into.

---------------------------
"truncate voxels" was moved from saving to loading.
This means, that voxels are not truncated before saving.
So files are bigger and consist hidden voxel data.
Hidden means collapsed or removed voxels.
When loading one can recreate hidden data by subdividing
to the granuality of hidden voxels and then loading.

---------------------------
To avoid memory consumption, before loading new files,
clean up scene with "truncate repros". After this the
repro and all its polygons are erased from memory.

---------------------------
Finally multilevel formats work.

---------------------------
Normals in VBO are now also interpolated with Tween on.

---------------------------
Now filenames are resolved with search if not found.

---------------------------
Now refinement level in objects is incorporated in saved 
objects and is loaded and used.

---------------------------
Oscillate state is saved for voxels.

---------------------------
Finally Load OBJ -> "Set Repro Pos Scale' is integrated into
scene format.

---------------------------
Now obj frames are saved and recovered at object level.
(Tip: avoid having static repro somewhere and animated repro,
with same name or path.)

---------------------------
Now individual voxels are saved and loaded with test "if animated".

---------------------------
After struggle now OBJ sequences are enabled in VBO mode.
Choose "Load Animated Repro" to point to a sequence with
numbers in filenames. All files in sequence need have equal
vertex count and also normal data.

---------------------------
With background, now alpha compositing is used instead of
paste through alpha when saveBackground is enabled.

---------------------------
VBO routines are incorporated. VBO is switched on and loaded
objects pass through VBO setup in obj_loader.py.

---------------------------
Now 'arrange Animated Cube' is automated for current level,
however, if matrix is partial, it returns false.

---------------------------
Now 'voxelBased' and 'voxelBasedRepro' are overloaded by selection.
If selection exsists for current object, selectionBased action
is done.

---------------------------
'None' is built into sentences. Scroll sentence to choose
different prepared animations. None is used to freeze the frame
as is.

---------------------------
Change to PICC file there for encapsulating objects texture.
Now if mtl is off or not found, objects texture is used and
saved with picc.

---------------------------
Now same type textures can be loaded at once from a directory.

---------------------------
'Reload OBJ Repro' reloads OBJ repros. When Voxelbased is on,
collection is reloaded or current voxel is reloaded. If useMtl
is on and useLoaded is off while reloading, mtl texture is reloaded.

---------------------------
Now textures use also useLoaded variable. Some loaded texture
can be renewed when this variable is set off from 'Load OBJ'
menu. Else it uses already compiled textures.

---------------------------
Now filling animation sentence is selection based.

---------------------------
Navigation pane got symmetry features for x y and z mirroring

---------------------------
Now animation files are pickled with cPickle. Changed:
voxel repro save and load in 'Load OBJ' menu are now scenebased.
This means that 'read voxels repro' loads voxel repros for
current scene.

---------------------------
New feature: navigation pane. User can move white cubes and
press 'p' to place transformed object. Loaded OBJ file is
scanned and placed. Scroll timeline to the next point in
time and place again.

---------------------------
Removed memory leak in cube drawing routine. It was caused
by unnecessary line of code that was a hanger-line from
pasted chunk.

---------------------------
Now alpha in textures is used to blend away parts of the
objects. Good choise for alpha enabled texture is PNG.

---------------------------
Now obj files can be loaded into active objects matrix.
Choose OBJ directory and go. Only thing to watch is that
they should be not very heavy in polycounts. Loader uses
also mtl files to place individual textures. Keep texture
sizes also small 512x512 for example.

---------------------------
Now scene saving features nice progressbar stating what
is going on. When hit Escape or press 'x' button to close it,
progress quits on next step.

---------------------------
Now repro files encapsulate also individual textures
for voxels set in 'Voxel Based Repro' mode.

---------------------------
Now there is a 'truncate voxels' feature in 'Select array'
menu. This command truncates not visible voxels in visible
objects hierarchys belonging not to visible objects.
It is usable for keeping possible saved files small, but
erases voxels, so that when respawned, they loose style
and settings.

---------------------------
Now for voxel repros also individual textures can
be loaded. When loaded, a line is added to the mtl file
into OBJ directory. This line adds texture path.

---------------------------
Now SDL mode reads and writes voxel repros to disk.
This is because exiting SDL mode erases Open GL display
lists.

---------------------------
Now OBJ files can be loaded for individual repros.
'Voxel Based pic' affects this setting and also
'random rotation amount' affects OBJ repros.
Also 'propagate' propagates object level voxels
to individual voxels.

---------------------------
Adding OBJ repro for voxels. Voxels may now have
shape at will. Unit cube represents a good size for
this object. Textures from OBJ files are loaded, if
not, another loaded texture is used by these voxels.
This is visible in SDL mode.

---------------------------
Now loaded OBJ files use display lists when
possible. When playing OBJ directory, they use simple
GL drawing routine.

---------------------------
Added texture support for Open GL view.

---------------------------
As a result of intense rework, now scene files can
be saved to individual folders. As Scene name one can
give a path to a directory. All scene loading looks
also for that path. Images are at relative paths and
use forward slash in pathnames.

---------------------------
Now canvas size and background pic are loaded
along with sync, rot amount, rot combine,
local mode and object list.

---------------------------
Now load and save treat voxel based image pic.

---------------------------
Added object voxel image propagate function. By toggling
it user propagates object image to voxels in canvas.

---------------------------
Added voxel based pic treatment. In 'Set Canvas Size' menu
there is now 'Voxel Based Pic' check toggle. It respects
also collections.

---------------------------
Added scene save and load functions. PICC file is required
to load pic raster into voxels.

---------------------------
Added objects data write and load functions in 'List Commands'
menu.

---------------------------
Added "sync animation". This toggle enables to synchronize
active objects when filling in Animations.

---------------------------
Now animations are per object. They are generated for
objects separately and written and loaded for objects
individually.

---------------------------
"write objects" and "place config" enable to write
and load object data for active objects in worldpixel.
Data is loaded if cubes active resolution matches the
data dimension in config file.
They are in '3d Cube Commands' menu.

---------------------------
"write objects pic" and "place pic config" enable to write
and load raster pic for active objects in worldpixel.

---------------------------
Now "Use Image Combo" enables to load similar named images
as image set for objects. They differ in numbers and have
same extension.

---------------------------
Now people can choose different image per active object.
This is done with "Set Canvas Size" - > "Choose Raster pic"

---------------------------
Now three objects are for use. Remade were some communications.
Select slice tests all visible objects and creates slice between
them.

---------------------------
Added shadow drawing mode. Shadow is semitransparent
on windows. You can turn shadows on and off from menu
"List Commands".

---------------------------
Now cube3d can draw into pic_map. User can pick cube line
and select object.

---------------------------
Added into 'Set Canvas Size' menu, sprite raster image functions.
People can load prepared images and set the rotation amount to
randomize their rotation in world matrix cube.

---------------------------

Now people can raster OBJ files directory ('Play OBJ files directory').
It uses same variables as revolve. If one wishes obj files
be in place and not revolve, he can set Turns to zero in
'Configure Raster' dialog.

---------------------------
Several changes to transformer and principles. Now
vectors are found and transformed correctly. Also
baking is integrated. But again, its up to program
when and what to bake. Added into menu GL_Lights,
Added GL_Wire mode for object.

---------------------------

Now fg and bg colors alpha affects also rasterizing
through obj 3d files. BG color grows its size when
alpha values are dismantled, FG colored particles
grow its size in opposition and loose size when raised.

---------------------------
Now after some overhaul, transformer is integrated,
some varaibles were thrown away, something was established.
Now objects have parent named "world", and LOCAL mode.
Also world rotation around world vector is done
before coordinates baking in objects.
This however may change. Also objects release angle and
local and vector variables based on condition.

---------------------------
Quick quiz: What objects are suitable in Worldpixel
program for rasterizing in Worldpixel matrix?
Answer: OBJ files with solid uv, normal and vertex
data. If not sure that all polygons are planar, non-
planar polys need to be tripled in order to pass
cull test in scan. Cull uses tolerance, but if poly
is skewed to much, cull is no manifested and ray passes
trough. This results voxels out of order for this
particular ray.
What means solid uv, normal and vertex data?
This means that, if object has uv-s, it needs them to
be set for all vertexes. Same also for normals.
Currently only normals are used to set face normal.
This is done using first vertex in face, assuming
all normal in face point in same direction.
Also object needs sit in origin and fit into 2x2x2 units
cube. Faces not fit, are sorted away. If at least
one vertex in face lands in this cube, whole face
qualifies.
---------------------------

You need to exit OBJ mode if you wish to refine or
raise levels, or spawn or collect voxels. This is
because in OBJ mode objects do not update voxels
position. They display OBJ grid or OBJ file.
Also to note: OBJ file is displayed only in SDL mode.
Then gl functions are used to rotate and position it.
SDL mode works only with MS Windows.

You can rotate loaded object with revolving it
as many times as it is configured. This happens around
current displayed UI vector. You need visit OBJ mode
for this to work. Being in 'local center' mode helps.

Now OBJ mode can be entered also without SDL being
active. It works as proxy for loaded object and rotation
enables placing transformed OBJ file into matrix.
It is better to have 'local center' active with OBJ
mode and not use arrows to move current object.

added two modules: obj_loader.py and scan_object.py
In menu one can load a obj file. And place it as
keyframe with place. I also raised possible voxel count.

Now SDL view displays in drawing voxels as cubes.

6 - 5
  2 - 1
7 + 4 +
  3 - 0

Switched neighbour finding to faster algorithm,
but this requires voxels to be arranged from menu
'Select array' -> 'arrange animated cube'. Neighbours
are used and found when using falloff. Falloff can
be renewed with canvas in focus and pressing f.

In SDL view local mode is not working. Maybe i
change to orthogonal mode and use my own 3d engine,
but then depth testing needs overhaul.

With trial and error managed to establish rendering
for OpenGL view also, but only on windows.
Mac cannot bind this view, so it is disabled there.

As current enchancement, SDL mode activates Open GL.
In draft mode this view draws gl points. In this mode
canvas functions respond only when canvas was not set
out of focus.

Now as a result of intensive rewrite, screen
blitting is pygame surface based. Also SDL mode is
added. This ties view to embed frame. A while
canvas focus remains and when user is not clicking
on frame, one can use canvas keybindings nonetheless.

Added draft mode to speed up objects drawing.
Also added bounding box toggle for objects.

Several bugs fixed, time and keyframe functions
improved.

Raveled around with selecting by coordinates.
Now they work also in local centers mode.
Only thing to note is, that pasting selections is
not cross local compatible. In local mode you can
move in conformed manner and this position is
remembered as you step out of local mode and
again step in into local mode. In local mode
first world rotation is made, then conformed
movement, then local rotation and then local conformed
movement. So reset position affects this final
conform. In addition to this is view pan and zoom,
but this is not affecting global worldpixel
state.

Few fundamental changes: now setup_numpy rearranges
indexes so that they propagate through cube shape
in ordered manner. This however makes possible repetitions
in the array of voxels. To overcome it, i use sets
everywere were voxels are iterated, but they need to
retain these empty slots in the beginning of voxels.
If for every voxel in grid position is found, there is
no empty space. This not proper index occurs, when 
not all voxels in current level are filled.

Now right-click on keyframe and choosing shape
from popupmenu writes keyframe shape
at keyframe time, independent of time marker.

Next steps: Enable multiobject modes where user
can insert many objects into objectList.

Todo: integrate some item list, that lists
some items. Currently there are two objects
object1 and object2. They can be selected from
menu and isolated. In connection with item
list, a add and remove menu items need be
integrated. Maybe some cutom buttons next to
list. Basicly item or object is a piece of
world grid. They all lay ideally in world grid
and ideally align to it. In scene build mode,
there is a change mode, where objects
inherit local alignement vectors from world.
So locally as effect they can be oriented or
rotate in individual manners. But join to the
world alignement vector.

So lets try it out first without adding
many objects. Already in render mode it has
distinct center mode. Maybe this mode can be
used to implement this feature. First lets find
AnimSequence_render function, where rendering
is started. There it lays like that:

if self.object_centers:
 j.rotate3d_vector(center = (0, 0, 0), vector = self.vector, angle = self.c)
 c = j.give_center_parent(0)
 j.bake_xyz_rotation()
 j.rotate3d_vector(center = c, vector = self.vector, angle = C)
 j.restore_xyz_baked()

There we see that to achieve local rotation baking mechanism is used.
This mechanism bakes voxel coordinates into baked coordinates and used
for coordinates rotated coordinates. So this way secondary rotation
around local center and vector can happen. Restore baked then moves
baked coordiantes back to voxel coordiantes, but transform remains.
Now the voxel coordinates just offset these transformed positions.
As in give_depth transformed _rotated coordinates are used.

So to use a custom axis per object, local rotation vector must be in
object. There it is: self.vector, but it is currently unused. Only give_center
claims that it uses it, but it is not used, because, it is called with
vector from Fclass. And there it uses global tk_App vector, that is world
vector. This world vector is set in ui with three components.
As object lays at origin, it has effect of rotating around its center.
But as soon, it has been moved away, it inherits all the world rotation
and lands onscreen all the way off. These are the conform_position
coordinates in 3d object. This means, that they still lay in grid in
discrete amounts off. This can be proven also with slicing. One
can find slices with intersecting objects that have same current level.
Then slice locates copositioned voxels and highlights them as
collection.

Lets see where self.vector in Fclass is. We are interested in self.vector
that belongs to tk_App. There it is initialized with (1, 1, 0). Points
right and up at 45 degree angle. Then in z_sort_objects is next use of
this vector. There it is used to give center to the object. Why z_sort
through rotation? It is more precise at giving objects position in space.
Other ways to find out objects position? give_center and give_center_parent.
They use already exsisting coordinates, but loose precision in give_center
and are not effective in give_center_parent and loose also precision.
Primary conclusion is to make that dont use rotated coordinates as base
for giving new coordinates, calculate center point by rotating conform_
position same amount over same axis as the world rotation wants.

Self.vector is used also in undo_view, zoom_to_selected, update_object_frame
and everywhere where it asks for center of object or rotates world.
But self.vector in tk_App is not necessarily self.vector in 3d objects.

Now in making these secondary rotations there needs to be a local rotation
mode somewhere in menu. In this mode vector slot in ui sets current
objects self.vector. While world vector and rotation remain as they were
when local mode was entered. Currently rotation is driven by a slot
or by idle animation. As soon as local rotation mode is entered, slot
begins to drive local rotation. So there it is: self.angle in object 3d and
it is again unused. give_center again claims to use it, but actually
it gets angle always from Fclass calls. Lets think what happens when
give_center should use this local angle. It results in displacement of
object off the world grid. This is not wanted. But let it be there,
and lets not use it.

Another tought: maybe use isolate mode to place this local centers mode.
Question remains only what happens when we exit this mode and display again
all objects in scene. Then all rotations jump to null as soon as global
rotation angle or rotation vector is used. Actually every update results
in being this rotation null. So this is not good. Maybe still special
mode for it, not connected to isolate mode. And when we exit this special
mode, then rotations jump to null. When rendering, then rendering uses
this scene as startup point. One more thing: also rotation direction
needs localized variable. It may be clockwise or counterclockwise. It
comes to use when user presses space to play rotation and when rendering.

There we go: added direction variable and its getmethods in Classy
and local end in Fclass.

Only job it has, is refining this pixel.
There you go. Spawn pixels, adjust their
size, set up animations.

Now timeline is up,
it features keyframes,
and play with 'p'.

...About AnimSequence_fill function.
This function uses eval(self.sentence)
to generate self.AnimSequence. This
is animation object in memory and is
central to animation. For example keyframes
are collected into this object when user
presses 'p' on timeline. Animation is
played frame by frame, each frame consisting
dimension power three entrys of voxels.
Each voxel is built up of two parts:
shape and color. Shape is pixel size and
can be tought as alpha component.
So size has number as float and color
consists three int numbers R G B.

There is a function write_AnimSequence_file.
This function writes all AnimSequence
frames into file named anim0.txt in Folders.
It uses tolist() by doing this. When Worldpixel
loads this file, it translates contents
through N[:][:] = n[:][:]. This means that
N being initialized as array to proper dimensions,
has not to worry about having in final
slot on left hand single value and on right
hand tuple of values.

Now back to AnimSequence_fill.
If we wish to fill in shape changes, we need
setShape being set. Else shape is None.
This happens also with color, color is None
if setColor is off. These values can be set in
Set Shapes menu.

These None values are visible also in keyframes
files in Folders\key_frame folder. And in anim0.txt
file in Folders\ folder. Now interesting part is,
how to interpret these None values.

When keyframes are loaded list(eval(f.read())) is
the form, it converts these tuples. With single
keyframe this 'list' clause is not needed. This
frame frame0000.txt in Folders\ folder has already
lists for color positions.

Writing frames is done with write_frame function.
Function with this name is in Fclass and in Classy.
Classy hands over these function addresses to local
Fclass object, named current_Object. Functions
react to call and use parentheses (). This same
goes to the class variables. also a name and () are
used. They are in Classy as gettobjects defined.
Locally not very much initialization is done with
this current_Object, but it takes all values in the
course of the program. Then to query a value these
getobjects are used.

Back to writing frames. So locally in Fclass before
continuing to file write in Folders/ or Folders/key_frame
folders, contents of this file are requested from
Classy instance. In Classy it is done with function
with the same name. write_frame.

This function has two parameters: shape and color.
Classy features also second function load_frame.
This function sets object3d properties, and write_frame
gets these properties.

So properties are set, and we come to query them.
With these two parameters Classy sends back new array.
If shape is None, shape value is None in this new
array. Same happens to color.

As said these values are all that there is to animation.
Size or shape or scale are interpretation of this
property that can be tought of also as alpha component
handled separately.

By knowing this one can use this knowledge to use
animation and keyframe formats to create own
interpretations or conversions for 3d array with color
and shape.

So on one side write_frame writes these None values,
and on the other side load_frame sets these None values.
When animating and None value is met, it cannot be
interpolated, so in AnimSequence_fill_frames procedure
prev[x, y, z][0] != None and frame[x, y, z][0] != None
clause is used to prevent these calculations.

Now you know what to do!
Next steps are to enable modes where we can say
animate shape and save only shape frames and animate
color and save only color frames.

When loaded, these files are merged with
self.AnimSequence object filling only one of the
columns in ndarray.

Seems complicated, but maybe it could be controlled
with a state of shape and color variables.

Say if 'p' is pressed and shape is on, from keyframes
shape data is extracted and filled to the animation.
This filling is done in AnimSequence_fill_frames.
So basically we need a mode where 'merge' happens.
Currently it writes these None values into
AnimSequence. But 'merge' mode prevents this write
and trys to aquire necessay value from exsisting
AnimSequence. This way setShape and setColor
define this situation, where 'merge' happens.

When both are on, overwrite happens. When only one
is on, 'merge' happens. To put this up.
query questions None state. If it is None, then
from self.AnimSequence at these coordinates value
is queryd. It may happen that old AnimSequence
has no value there or it is out of scope. Then it
puts None, else it takes old value to new
AnimSequence.

And done!

How to test it?
First this is new situation. We need first a simple
reckognizeable animation. Luckily without keyframes
on timeline and pressing 'p', generated animation
launches. Press 'p' again to stop it.
It has only 25 frames, so lets turn off color first
in Set Shapes menu. Because shape and color
keyframes are distinct, we can colorize and put
keyframes knowing, that we are not destroing shape
animation. Shape and color information is picked
up when 'p' is pressed and depending of what state
they had.

Now turn color on and shape off and start adding
color with and without falloffs. Renew falloff with 'f'.
Restore matrix with 'reset matrix' command.
While shape is off, this is not affecting shape or
color keyframes, but makes all voxels pickable.

falloff uses selected sphere for center. So renewing
is necessary when putting down new influence set.
Scroll timeline, select more spheres and colorize
with clicking on color marks above color palettes.
v and b can be used to set colors when over color
palette. Click colors, use 'n' to pick up colors.

Now purpose is to set keyframes with these colors.
As you pick colors, keyframe is put down when
'writeKeyFrame' is on. Press 'p' for play ...

Lets have little keyframe fun.
Now keyframes have copy_keyframe and paste_keyframe
functions. Also a pasteframe class is added.
This PasteFrame class has setter, getter and two variables.
First is image, and second is data. Image defines
keyframe image. Image means four possibilitys that
keyframe can have: color key, shape key, both or none.
When pasting a keyframe, file in disk is overwritten,
if exsists.