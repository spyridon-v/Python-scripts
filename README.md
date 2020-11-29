""" This script can only be used in Abaqus CAE software. A crack propagation application following the LEFM method is solved.Script description:
a) A Rectangular Matrix is created
b) Random circular inclusions are created inside the matrix
c) A crack tip at the left side of the matrix is created
d) Load sets, BCs and other auxiliaries, are finally created and the CRACK PROPAGATION job is solved. 

The shape of the inclusions can be changed by modifing the part of the code which contains the inclusions characteristics.
For example, elliptical or mixed shape inclusions can be used for generating the crack propagation"""
