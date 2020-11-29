from abaqus import *
from abaqusConstants import *
import __main__
import math
import random


def structural_fillet():
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
    #h=height of the bottom part
    h = 170.
    ###CREATING PARTS###
    #part1
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',sheetSize=200.0)
    g, v, d, c =s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(-500.0 , -h/2), point2 = (500.0 , h/2 ))
    p = mdb.models['Model-1'].Part(name= 'Part-2',dimensionality=TWO_D_PLANAR,type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-2']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models[ 'Model-1' ].parts[ 'Part-2' ]
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['Model-1'].sketches['__profile__']
    #part2       
    s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.Line(point1=(-400.0 , h/2), point2 = (-400.0 , h/2+75 ))
    s1.Line(point1=(-400.0 , h/2+75), point2 = (-70 , h/2+75 ))
    s1.ArcByCenterEnds(center = (-70,h/2+95), point1=(-70,h/2+75),point2 = (-50,h/2+95))
    s1.Line(point1=(-50 , h/2+95), point2 = (-50 , h/2 +185 ))
    s1.Line(point1=(-50 , h/2+185), point2 = (50 , h/2+185 ))
    s1.Line(point1=(50 , h/2+185), point2 = (50 , h/2+95 ))
    s1.ArcByCenterEnds(center=(70 , h/2+95),point1=(50 , h/2+95), point2 = (70 , h/2+75))
    s1.Line(point1=(70 , h/2+75), point2 = (400 , h/2+75 ))
    s1.Line(point1=(400 , h/2+75), point2 = (400 , h/2 ))
    s1.Line(point1=(400 , h/2), point2 = (-400 , h/2 ))   
    p = mdb.models['Model-1'].Part(name= 'Part-1',dimensionality=TWO_D_PLANAR,type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    p.BaseShell(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models[ 'Model-1' ].parts[ 'Part-1' ]
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['Model-1'].sketches['__profile__']
    #creating the initial crack(sketch only)
    p = mdb.models['Model-1'].parts['Part-1']
    f , e , d1 = p.faces , p.edges , p.datums
    t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))
    s2 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',sheetSize=565.68, gridSpacing= 14.14, transform= t)
    g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
    s2.setPrimaryObject(option=SUPERIMPOSE)
    p = mdb.models['Model-1'].parts['Part-1']
    p.projectReferencesOntoSketch(sketch=s2, filter=COPLANAR_EDGES)
    s2.resetView()
    mdb.models['Model-1'].sketches['__profile__'].sketchOptions.setValues(gridSpacing=10.0, gridAuto=OFF)
    s2.Line(point1=(-50.0, h/2+107.45), point2=(-45.0, h/2+107.45))
    s2.CoincidentConstraint(entity1=v[12], entity2=g[8], addUndoState=False)
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), )
    e, d2 = p.edges, p.datums
    p.PartitionFaceBySketch(faces=pickedFaces, sketch=s2)
    s2.unsetPrimaryObject()
    del mdb.models['Model-1'].sketches['__profile__']
    ###PROPERTY###
    #material
    mdb.models['Model-1'].Material(name='KA36 STEEL')
    mdb.models['Model-1'].materials['KA36 STEEL'].Elastic(table = ((200, 0.3),))
    mdb.models['Model-1'].materials['KA36 STEEL'].MaxpsDamageInitiation (table = ((0.2,),))
    mdb.models['Model-1'].materials['KA36 STEEL'].maxpsDamageInitiation.DamageEvolution (type=ENERGY, table = ((0.0,),))
    mdb.models['Model-1'].HomogeneousSolidSection(name='upper', material= 'KA36 STEEL', thickness=None)
    mdb.models['Model-1'].HomogeneousSolidSection(name= 'bottom', material= 'KA36 STEEL', thickness =None )
    #section assigment
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    faces = f.findAt(((399., h/2+1 , 0.0), ))
    region = p.Set(faces = faces ,name= 'Set-1')
    p = mdb.models['Model-1'].parts['Part-1']
    p.SectionAssignment(region=region , sectionName='upper',offset=0.0 ,offsetType=MIDDLE_SURFACE, offsetField = ' ' ,thicknessAssignment=FROM_SECTION)
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    p = mdb.models['Model-1'].parts['Part-2']
    f = p.faces
    faces = f.findAt(((499., -h/2+1 , 0.0), ))
    region = p.Set(faces = faces ,name= 'Set-2')
    p = mdb.models['Model-1'].parts['Part-2']
    p.SectionAssignment(region=region , sectionName='bottom',offset=0.0 ,offsetType=MIDDLE_SURFACE, offsetField = ' ' ,thicknessAssignment=FROM_SECTION)
    p = mdb.models['Model-1'].parts['Part-2']
    f = p.faces
    ###ASSEMBLY###
    a = mdb.models['Model-1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    a1 = mdb.models['Model-1'].rootAssembly
    a1.DatumCsysByDefault(CARTESIAN)
    p = mdb.models['Model-1'].parts['Part-1']
    a1.Instance(name='Part-1-1', part=p, dependent=OFF)
    p = mdb.models['Model-1'].parts['Part-2']
    a1.Instance(name='Part-2-1', part=p, dependent=OFF)
    ###INTERACTION###
    #crack definition
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON, 
        constraints=ON, connectors=ON, engineeringFeatures=ON)
    a = mdb.models['Model-1'].rootAssembly
    f1 = a.instances['Part-1-1'].faces
    faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
    crackDomain = regionToolset.Region(faces=faces1)
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#80 ]', ), )
    crackLocation = regionToolset.Region(edges=edges1)
    a = mdb.models['Model-1'].rootAssembly
    a.engineeringFeatures.XFEMCrack(name='Crack-1', crackDomain=crackDomain, 
        crackLocation=crackLocation)    
    #contact definition
    session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
    mdb.models['Model-1'].ContactProperty('IntProp-1')
    mdb.models['Model-1'].interactionProperties['IntProp-1'].TangentialBehavior(
        formulation=FRICTIONLESS)
    mdb.models['Model-1'].interactionProperties['IntProp-1'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=OFF, 
        constraintEnforcementMethod=DEFAULT)
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-2-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#4 ]', ), )
    region1=regionToolset.Region(side1Edges=side1Edges1)
    a = mdb.models['Model-1'].rootAssembly
    v1 = a.instances['Part-1-1'].vertices
    verts1 = v1.getSequenceFromMask(mask=('[#3 ]', ), )
    region2=regionToolset.Region(vertices=verts1)
    mdb.models['Model-1'].SurfaceToSurfaceContactStd(name='Int-2', 
        createStepName='Initial', master=region1, slave=region2, 
        sliding=FINITE, thickness=ON, interactionProperty='IntProp-1', 
        adjustMethod=NONE, initialClearance=OMIT, datumAxis=None, 
        clearanceRegion=None)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON, 
        constraints=ON, connectors=ON, engineeringFeatures=ON, 
        adaptiveMeshConstraints=OFF)
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-2-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#4 ]', ), )
    region1=regionToolset.Region(side1Edges=side1Edges1)
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-1-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
    region2=regionToolset.Region(side1Edges=side1Edges1)
    mdb.models['Model-1'].interactions['Int-2'].setValues(master=region1, 
        slave=region2, initialClearance=OMIT, adjustMethod=NONE, 
        sliding=FINITE, enforcement=SURFACE_TO_SURFACE, thickness=ON, 
        contactTracking=TWO_CONFIG, bondingSet=None)
    mdb.models['Model-1'].interactionProperties['IntProp-1'].tangentialBehavior.setValues(
        formulation=FRICTIONLESS)
    mdb.models['Model-1'].interactionProperties['IntProp-1'].normalBehavior.setValues(
        pressureOverclosure=HARD, allowSeparation=OFF, 
        constraintEnforcementMethod=DEFAULT)
    ###STEP###
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=OFF, 
        constraints=OFF, connectors=OFF, engineeringFeatures=OFF, 
        adaptiveMeshConstraints=ON)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON, 
        constraints=ON, connectors=ON, engineeringFeatures=ON, 
        adaptiveMeshConstraints=OFF)
    mdb.models['Model-1'].XFEMCrackGrowth(name='Int-1', createStepName='Initial', 
        crackName='Crack-1')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=OFF, 
        constraints=OFF, connectors=OFF, engineeringFeatures=OFF, 
        adaptiveMeshConstraints=ON)
    mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial', 
        maxNumInc=10000, initialInc=0.1, minInc=1e-20, maxInc=0.1)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    mdb.models['Model-1'].steps['Step-1'].control.setValues(allowPropagation=OFF, 
        resetDefaultValues=OFF, timeIncrementation=(4.0, 8.0, 9.0, 16.0, 10.0, 
        4.0, 12.0, 20.0, 6.0, 3.0, 50.0))
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 
        'CFORCE', 'PHILSM', 'PSILSM', 'STATUS', 'STATUSXFEM'))
    ###LOADS AND BOUNDARY CONDITIONS
    e1 = a.instances['Part-1-1'].edges
    v11 = a.instances['Part-1-1'].vertices
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-1-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#20 ]', ), )
    region = regionToolset.Region(side1Edges=side1Edges1)
    mdb.models['Model-1'].SurfaceTraction(name='Load-1', createStepName='Step-1', 
        region=region, magnitude=0.2, directionVector=(
        a.instances['Part-1-1'].InterestingPoint(edge=e1[6], rule=MIDDLE), 
        v11[6]), distributionType=UNIFORM, field='', localCsys=None, 
        traction=GENERAL)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Initial')
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#800 ]', ), )
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Initial', 
        region=region, u1=SET, u2=UNSET, ur3=UNSET, amplitude=UNSET, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-2-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#1 ]', ), )
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Initial', 
        region=region, u1=SET, u2=UNSET, ur3=UNSET, amplitude=UNSET, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models['Model-1'].rootAssembly
    v1 = a.instances['Part-2-1'].vertices
    verts1 = v1.getSequenceFromMask(mask=('[#3 ]', ), )
    region = regionToolset.Region(vertices=verts1)
    mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Initial', 
        region=region, u1=UNSET, u2=SET, ur3=UNSET, amplitude=UNSET, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    ###MESH###
    a = mdb.models['Model-1'].rootAssembly
    f1 = a.instances['Part-1-1'].faces
    faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )
    f2 = a.instances['Part-2-1'].faces
    faces2 = f2.getSequenceFromMask(mask=('[#1 ]', ), )
    pickedRegions = faces1+faces2
    a.setMeshControls(regions=pickedRegions, elemShape=QUAD, algorithm=MEDIAL_AXIS)
    session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
    a = mdb.models['Model-1'].rootAssembly
    partInstances =(a.instances['Part-1-1'], a.instances['Part-2-1'], )
    a.seedPartInstance(regions=partInstances, size=10.0, deviationFactor=0.1, 
        minSizeFactor=0.1)
    a = mdb.models['Model-1'].rootAssembly
    partInstances =(a.instances['Part-1-1'], a.instances['Part-2-1'], )
    a.generateMesh(regions=partInstances)
    session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
    session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
        meshTechnique=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    a = mdb.models['Model-1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON, 
        adaptiveMeshConstraints=OFF)
    session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
        meshTechnique=ON)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=2009.6, 
        farPlane=2069.61, width=220.267, height=123.152, viewOffsetX=0.457849, 
        viewOffsetY=6.88981)
    a = mdb.models['Model-1'].rootAssembly
    f1 = a.instances['Part-1-1'].faces
    pickedRegions = f1.getSequenceFromMask(mask=('[#1 ]', ), )
    a.deleteMesh(regions=pickedRegions)
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    pickedEdges = e1.getSequenceFromMask(mask=('[#80 ]', ), )
    a.seedEdgeByNumber(edges=pickedEdges, number=4, constraint=FINER)
    session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
    a = mdb.models['Model-1'].rootAssembly
    partInstances =(a.instances['Part-1-1'], a.instances['Part-2-1'], )
    a.generateMesh(regions=partInstances)

    ###JOB###
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
    session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
        meshTechnique=OFF)
    mdb.Job(name='Structural_Fillet', model='Model-1', description='', 
        type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
        memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
        numGPUs=0)

fillet()