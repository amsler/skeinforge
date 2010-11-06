M106
G91                        ;relative positioning
G1 F50                     ;set move speed to suit Z-axes
G1 Z2 F50                  ;move up a bit from the finished object
G90                        ;absolute positioning
G1 F2300                   ;set move speed to suit XY-axes
G1 X0 Y150 F2300        
M140 S0
M141 S0
