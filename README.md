# freecad-legify-macros

Macros to generate 'plastic toy brick' models in FreeCAD

## Why?

This is a learning exercise undertaken to master the following:

* FreeCAD and concepts for parametric modelling: sketches, constraints, datum planes etc.
* Python and scripting with FreeCAD
* Detailed modelling of toy bricks
 
These all form the basis of a future planned project...
 
## Installation

**Tested only with FreeCAD version >= 0.18**

#### MacOS

1. Clone this repository: 

    `git clone https://github.com/vectronic/freecad-legify-macros.git`
    
1. Link the cloned folder and macro file into the FreeCAD macros directory:

    ```
    ln -s <local repository folder>/legify-brick.FCMacro <user preferences folder>/FreeCAD/Macro/
    ln -s <local repository folder>/Legify <user preferences folder>/FreeCAD/Macro/
    ```

## Usage

1. Create a new document
1. Run the `legify-brick.FCMacro`
1. Modify parameters as desired in the popup dialog 
1. Click OK
1. Wait for for a lot of sketches, constraints, pads, pockets and fillets to be rendered
1. Admire the resulting beauty 

## TODO

- [x] Confirm some dimensions
- [x] Technic Hole Rendering
- [x] Determine if the inner edge of open studs and hole studs should be filleted
- [ ] 0.25mm fillet on internal brick corners
- [ ] Determine a replacement for internal ribs if side studs exist with holes
- [ ] Determine a replacement for tube ribs if technic holes exist
- [ ] Technic Axle Hole Rendering
- [ ] Technic Pin Rendering
- [ ] Support rib variation in modern 2x1 tile and 2x1 technic brick with 2 non-offset holes
- [ ] Support modern tile where the bottom has a small outside pocket (and check if fillet is also required)

## Screenshots
![Parameters](images/parameters.png "Parameters")

![Simple](images/simple.png "Simple")

![Classic](images/classic.png "Classic")

![Odd](images/odd.png "Odd")

![Tree View](images/tree_view.png "Tree View")

![Sketch](images/sketch.png "Sketch")

## Credit

Initial drawing and dimensions used as reference for this work was done by [Nick Turo-Shields](https://grabcad.com/library/2x4-lego-brick-1)
