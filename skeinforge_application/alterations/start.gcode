M104 S230
M140 S120
M116
G92 E0 ;zero the extruded length
G1 Z8 F90 ;clear the bolt heads
G28 Y0 ;go home
G28 X0
G1 X135 F3000
G28 Z0
G92 Z0 ;Adjust Z height for optimum 1st layer adhesion
M113 S0.75
G1 Z0.2 F90
G1 X10 E260 F1200
G1 Z0.0 E250 F1200 
G92 E0
G1 X100.0 Y100.0 
G92 X0 ;set x 0
G92 Y0 ;set y 0
G92 Z0 ;set z 0