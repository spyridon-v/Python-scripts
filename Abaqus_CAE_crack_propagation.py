# *- encoding: utf-8 -*-
# This scripts generates random circular inclusions into a rectangular matrix. Then, a crack tip along with the load/BC sets
# are created and finally the appropriate job type is solved.

from abaqus import *
from abaqusConstants import *
import __main__
import math
import random


def random_circular_inclusions():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    
    ###n number of inclusions
    n = 20
    
    ###storing inclusions' cords to xc&yc lists
    xc = []
    yc = []
    xc.append(random.randint(-85,85))
    yc.append(random.randint(-85,85))
    j = 0
    x = random.randint(-85, 85)
    y = random.randint(-85, 85)
    while len(xc)<n :
        while j<len(xc) :
            dist= math.sqrt((x-xc[j])*(x-xc[j])+(y-yc[j])*(y-yc[j]))
            if dist<20:
                j=0
                x=random.randint(-85 ,85)
                y=random.randint(-85 ,85)
            else :
                j = j +1
        xc.append(x)
        yc.append(y)
        
    ###Profil & Model 
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',sheetSize=200.0)
    g, v, d, c =s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    #creating rectangular matrix
    s.rectangle(point1=(-100.0 , -100.0), point2 = (100.0 , 100.0 ))
    p = mdb.models['Model-1'].Part(name= 'Part-1',dimensionality=TWO_D_PLANAR,type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models[ 'Model-1' ].parts[ 'Part-1' ]
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['Model-1'].sketches['__profile__']
    p = mdb.models['Model-1'].parts['Part-1']
    f , e , d1 = p.faces , p.edges , p.datums
    t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))
    
    ###crack tip
    s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',sheetSize=565.68, gridSpacing= 14.14, transform= t)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=SUPERIMPOSE)
    p = mdb.models['Model-1'].parts['Part-1']
    p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
    s1.resetView()
    mdb.models['Model-1'].sketches['__profile__'].sketchOptions.setValues(gridSpacing=10.0, gridAuto=OFF)
    s1.Line ( point1 =(-100.00000 , 0.000000) , point2 =(-95. , 0.0 ))
    s1.HorizontalConstraint(entity=g[6], addUndoState=False)
    s1.PerpendicularConstraint(entity1=g[5], entity2=g[6], addUndoState=False )
    s1.CoincidentConstraint(entity1=v[4], entity2=g[5], addUndoState=False )
    s1.EqualDistanceConstraint(entity1=v[3], entity2=v[0], midpoint=v[4], addUndoState=False)
    
    ###creating circular elements
    i =0
    while i<n :
        s1.CircleByCenterPerimeter(center=(xc[i], yc[i]), point1=(xc[i]-10 ,yc[i]))
        i=i+1
    p = mdb.models['Model-1'].parts['Part-1']
    f=p.faces
    pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
    e1 , d2 = p.edges, p.datums
    p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
    s1.unsetPrimaryObject ()
    del mdb.models['Model-1'].sketches['__profile__']
    
    ###Materials & Sections
    mdb.models['Model-1'].Material(name='epoxy')
    mdb.models['Model-1'].materials['epoxy'].Elastic(table = ((1000.0, 0.3),))
    mdb.models['Model-1'].materials['epoxy'].MaxpsDamageInitiation (table = ((1.0,),))
    mdb.models['Model-1'].materials['epoxy'].maxpsDamageInitiation.DamageEvolution (type=ENERGY, table = ((0.0,),))
    mdb.models['Model-1'].Material(name= 'fiber')
    mdb.models['Model-1'].materials['fiber'].Elastic(table=((100000.0 ,0.3),))
    mdb.models['Model-1'].materials['fiber'].MaxpsDamageInitiation(table=((100, ),))
    mdb.models['Model-1'].materials['fiber'].maxpsDamageInitiation.DamageEvolution(type=ENERGY, table = ((0.0, ) , ))
    mdb.models['Model-1'].HomogeneousSolidSection(name='matrix', material= 'epoxy', thickness=1.0)
    mdb.models['Model-1'].HomogeneousSolidSection(name= 'inclusion', material= 'fiber', thickness =1.0 )
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    faces = f.findAt(((99, -99, 0.0), ))
    region = p.Set(faces = faces ,name= 'Set-1')
    p = mdb.models['Model-1'].parts['Part-1']
    p.SectionAssignment(region=region , sectionName='matrix',offset=0.0 ,offsetType=MIDDLE_SURFACE, offsetField = ' ' ,thicknessAssignment=FROM_SECTION)
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    
    ###tuplecontaininginclusioncoordinates
    i=0
    facestuple=()
    while i<n:
        tup=tuple([xc[i], yc[i],0])
        facestuple=facestuple + (tup, )
        i = i + 1
    faces = f.findAt(coordinates = facestuple)
    region = p.Set (faces= faces, name= 'Set-2')
    p = mdb.models['Model-1'].parts['Part-1']
    p.SectionAssignment(region=region, sectionName= 'inclusion', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField = ' ' ,thicknessAssignment=FROM_SECTION)
    
    ###Auxiliaries
    a = mdb.models['Model-1'].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    p = mdb.models['Model-1'].parts['Part-1']
    a.Instance(name= 'Part-1-1', part=p, dependent=OFF)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(adaptiveMeshConstraints=ON)
    mdb.models['Model-1'].StaticStep(name= 'Step-1', previous='Initial',maxNumInc=10000, initialInc=0.1, minInc=1e-20, maxInc =0.1)
    mdb.models['Model-1'].steps['Step-1'].control.setValues(allowPropagation=OFF,resetDefaultValues=OFF, discontinuous=ON, timeIncrementation = ( 8.0,
    10.0, 9.0, 16.0, 10.0, 4.0, 12.0, 20.0, 6.0, 3.0, 50.0))
    #Load Set
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.findAt(((50.0, -100.0, 0.0), (( -50.0, 100.0, 0.0)),))
    a.Set(edges=edges1, name='Load')
    a0=mdb.models['Model-1'].rootAssembly
    regionDef=a0.sets['Load']
    mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
    createStepName='Step-1', 
    variables=('RF1','RF2'),
    region=regionDef, frequency=1)
    
    ###Crack definition
    a = mdb.models['Model-1'].rootAssembly
    f1 = a.instances['Part-1-1'].faces
    crack_domain = facestuple + (((99, -99, 0 ) , ))
    faces1 = f1.findAt(coordinates=crack_domain)
    crackDomain = regionToolset.Region(faces= faces1 )
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.findAt(((-98.75, 0.0, 0.0) , ))
    crackLocation = regionToolset.Region(edges=edges1)
    a = mdb.models['Model-1'].rootAssembly
    a.engineeringFeatures.XFEMCrack(name='Crack-1',crackDomain=crackDomain ,
    crackLocation=crackLocation)
    mdb.models['Model-1'].XFEMCrackGrowth(name= 'Int-1', createStepName= 'Initial' ,
    crackName= 'Crack-1')    
    
    ###BCs
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.findAt(((50.0, -100.0, 0.0), (( -50.0, 100.0, 0.0)), ))
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-1'].DisplacementBC(name= 'BC-1', createStepName= 'Initial' ,
    region=region , u1=SET , u2=UNSET, ur3=UNSET, amplitude=UNSET,
    distributionType=UNIFORM, fieldName='', localCsys=None )
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.findAt(((50.0, -100.0, 0.0),))
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-1'].DisplacementBC(name= 'BC-2' , createStepName= 'Step-1',
    region=region , u1=UNSET, u2=-0.1 , ur3=UNSET, amplitude=UNSET, fixed=OFF,
    distributionType=UNIFORM, fieldName= '' , localCsys=None )
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.findAt(((-50.0 , 100.0 , 0.0), ))
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-1'].DisplacementBC(name= 'BC-3', createStepName= 'Step-1',
    region=region , u1=UNSET, u2=0.1 , ur3=UNSET, amplitude=UNSET, fixed=OFF,
    distributionType=UNIFORM, fieldName= '' , localCsys=None )
    
    ###Output Requests
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
    'S' , 'PE' , 'PEEQ' , 'PEMAG' , 'LE' , 'U', 'RF' , 'CF' , 'CSTRESS' , 'CDISP' ,
    'PHILSM' , 'PSILSM' , 'STATUS' , 'STATUSXFEM'))
    a = mdb.models['Model-1'].rootAssembly
    
    ###seeds
    partInstances=(a.instances['Part-1-1'] , )
    a.seedPartInstance(regions=partInstances, size =2 , deviationFactor =0.1 ,
    minSizeFactor =0.1 )
    a = mdb.models['Model-1'].rootAssembly
    partInstances=(a.instances['Part-1-1'] , )
    a.seedPartInstance(regions=partInstances, size=2, deviationFactor =0.1 ,
    minSizeValue =0.9)
    
    ###meshing algorithm
    a = mdb.models['Model-1'].rootAssembly
    f1=a.instances['Part-1-1'].faces
    pickedRegions = f1.findAt(((99,-99, 0.0) , ))
    a.setMeshControls(regions=pickedRegions , elemShape=QUAD, algorithm=MEDIAL_AXIS)
    a = mdb.models['Model-1'].rootAssembly
    f1 = a.instances['Part-1-1'].faces
    pickedRegions = f1.findAt(coordinates=facestuple)
    a.setMeshControls(regions=pickedRegions , elemShape=QUAD, algorithm=MEDIAL_AXIS)
    a = mdb.models['Model-1'].rootAssembly
    partInstances=(a.instances['Part-1-1'],)
    a.generateMesh(regions=partInstances)
    a = mdb.models['Model-1'].rootAssembly
    partInstances=(a.instances['Part-1-1'] , )
    a.generateMesh(regions=partInstances)
    
    ###job
    mdb.Job(name= 'Job_alpha_' , model= 'Model-1' , description= ' ' , type=ANALYSIS ,
    atTime=None , waitMinutes=0 , waitHours =0 , queue=None , memory=90 ,
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True ,
    explicitPrecision=SINGLE , nodalOutputPrecision=SINGLE , echoPrint=OFF,
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine= '' ,
    scratch= '' , resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1 ,
    numGPUs=0)

random_inclusions()
