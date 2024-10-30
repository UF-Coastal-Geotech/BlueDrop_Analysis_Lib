# To-Do list for the BlueDrop Analysis Library - Analysis side
:thumbsup:
## Documentation that needs to be written
This includes adding paper references for the equations. There needs to be a link between the function and the work that it came from. There needs to be a significant effort to get the source from the original source and confirm that the equation is actually in the original source. Ideally there should be a reference to a page in the reference and an equation number.


### Need Sphinx docs

### Data classes
1) BinaryFile
2) dropClass
3) exceptions
4) fileClass
5) folderClass
6) TypeMixin
7) PFFPFolder
8) PFFPFile

### Folder: general_functions
1) global_constants
2) helper_functions

### machine_learning
1) RandomForestClass

### mechanincs_functions
1) white_bearing_capacity

### pffp_functions
1) basic_geometry_funcs
2) cone_area_funcs

### signal_processing
1) signal_function


## Testing that needs to be done

### Folder: data_classes
1) BinaryFile
2) dropClass
3) exceptions
4) fileClass
5) folder
6) pffpFile
7) pffpFolder
8) Type_Mixin

### Folder: general_functions
1) helper_functions

### Folder: machine_learing
1) randomForestClass

### Folder: mechanincs_functions
1) bearing_capacity_funcs
2) fluid_funcs
3) friction_angle_funcs
4) general_geotech_funcs
5) relative_density_funcs
6) soil_characteristic_funcs
7) white_bearing_capacity

### Folder: pffp_functions
1) basic_geometry_funcs
2) cone_area_funcs

### Folder: Signal Processing
1) signal_function

## Things that need to be collected
1) Need the code that generated the random forest prior model
2) Other functions that are/should be used by the group
    * Work about the pressure correction that needs to be done to the PFFP pressure module
    * Work that has been done by other students that is related
3) Equation for rope drag as a function of depth
4) Rope friction factor
   * This will depend on the rope but if we can get something in the ballpark that's a first step
 
5) Drag factor for the pffp 
    * This is going to depend on the tip type

## Code that needs to be written
1) Function to calc rope drag at current depth
2) Reference (.csv, excel, JSON, etc.) that contians the value for the rope drag as a function of rope type

## Code that needs to be reorganized
1) PffpFile Class is to messy especially the code that checks if there's a drop in the file
2) PffpFolder could also use some work


