// Toolchain smoke test for the alternative CAD stack (OpenSCAD + BOSL2).
// Needs BOSL2 on OPENSCADPATH:  git clone https://github.com/BelfrySCAD/BOSL2.git
// Run headless:
//   OPENSCADPATH=<dir containing BOSL2> openscad -o pair.stl tools/toolchain-check/check_openscad.scad
//   OPENSCADPATH=... openscad -o pair.3mf tools/toolchain-check/check_openscad.scad
//   OPENSCADPATH=... xvfb-run -a openscad -o pair.png --render --viewall --autocenter tools/toolchain-check/check_openscad.scad
include <BOSL2/std.scad>
include <BOSL2/gears.scad>

mod = 1.0;        // parameter
backlash = 0.15;  // mm, BOSL2 applies it to the tooth thickness
z1 = 60; z2 = 15; face = 5;

spur_gear(mod=mod, teeth=z1, thickness=face, shaft_diam=5, backlash=backlash);
right(gear_dist(mod=mod, teeth1=z1, teeth2=z2))
  spur_gear(mod=mod, teeth=z2, thickness=face, shaft_diam=3, backlash=backlash, gear_spin=180/z2);
