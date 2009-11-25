from yade import pack,ymport

""" This script demonstrates how to use 2 components of creating packings:

1. packing generators pack.regularHexa, pack.regularOrtho etc. generate vertices and filter them
using predicates. (Note that this will be enhanced to irregular packings in the future)

2. predicates are functors returning True/False for points that are given by the packing generator.
Their names are mostly self-explanatory, see their docstrings for meaning of their arguments.

Predicates can be combined using set arithmetics to get their Intersection (p1 & p2), union (p1 | p2),
difference (p1 - p2) and symmetric difference (XOR, p1 ^ p2). This is demontrated on the head (which
has sphere taken off at the back and also a notch) and the body (with cylidrical hole inside).

"""

rad,gap=.15,.02

#Add material
O.materials.append(GranularMat(young=1e9,poisson=.25,frictionAngle=0.5,density=1e3))

#Parameters, which will be passed into spheres and facets creators
kw={'material':0}
kwBoxes={'color':[1,0,0],'wire':False,'dynamic':False,'material':0}
kwMeshes={'color':[1,1,0],'wire':True,'dynamic':False,'material':0}

O.bodies.append(
	pack.regularHexa(
		(pack.inSphere((0,0,4),2)-pack.inSphere((0,-2,5),2)) & pack.notInNotch(centerPoint=(0,0,4),edge=(0,1,0),normal=(-1,1,-1),aperture=.2)
		,radius=rad,gap=gap,color=(0,1,0),material=0) # head
	+[utils.sphere((.8,1.9,5),radius=.2,color=(.6,.6,.6),material=0),utils.sphere((-.8,1.9,5),radius=.2,color=(.6,.6,.6),material=0),utils.sphere((0,2.4,4),radius=.4,color=(1,0,0),material=0)] # eyes and nose
	+pack.regularHexa(pack.inCylinder((-1,2.2,3.3),(1,2.2,3.3),2*rad),radius=rad,gap=gap/3,color=(0.929,0.412,0.412),material=0) #mouth
)
groundId=O.bodies.append(utils.facet([(12,0,-6),(0,12,-6,),(-12,-12,-6)],dynamic=False)) # ground

for part in [
	pack.regularHexa (
		pack.inAlignedBox((-2,-2,-2),(2,2,2))-pack.inCylinder((0,-2,0),(0,2,0),1),
		radius=1.5*rad,gap=2*gap,color=(1,0,1),**kw), # body,
	pack.regularOrtho(pack.inEllipsoid((-1,0,-4),(1,1,2)),radius=rad,gap=0,color=(0,1,1),**kw), # left leg
	pack.regularHexa (pack.inCylinder((+1,1,-2.5),(0,3,-5),1),radius=rad,gap=gap,color=(0,1,1),**kw), # right leg
	pack.regularHexa (pack.inHyperboloid((+2,0,1),(+6,0,0),1,.5),radius=rad,gap=gap,color=(0,0,1),**kw), # right hand
	pack.regularOrtho(pack.inCylinder((-2,0,2),(-5,0,4),1),radius=rad,gap=gap,color=(0,0,1),**kw) # left hand
	]: O.bodies.appendClumped(part)



q1 = Quaternion(Vector3(0,0,1),(3.14159/3))
o1,o_angl = q1.ToAxisAngle()
O.bodies.append(utils.facetBox((12,0,-6+0.9),(1,0.7,0.9),(o1[0],o1[1],o1[2],o_angl),**kwBoxes))
q1 = Quaternion(Vector3(0,0,1),(3.14159/2))
o1,o_angl = q1.ToAxisAngle()
O.bodies.append(utils.facetBox((0,12,-6+0.9),(1,0.7,0.9),(o1[0],o1[1],o1[2],o_angl),**kwBoxes))
q1 = Quaternion(Vector3(0,0,1),(3.14159))
o1,o_angl = q1.ToAxisAngle()
O.bodies.append(utils.facetBox((-12,-12,-6+0.9),(1,0.7,0.9),(o1[0],o1[1],o1[2],o_angl),**kwBoxes))


"""Import regular-sphere-pack.mesh into the YADE simulation"""
O.bodies.append(ymport.gmsh('regular-sphere-pack.mesh',**kwMeshes))#generates facets from the mesh file

"""Import regular-sphere-pack-LSMGenGeo.geo into the YADE simulation"""
O.bodies.append(ymport.gengeo('regular-sphere-pack-LSMGenGeo.geo',moveTo=[-7.0,-7.0,-5.9],scale=15.0,color=(1,0,1),**kw))


try:
	from yade import qt
	qt.Controller()
	qt.View()
except ImportError: pass

O.engines=[
	BexResetter(),
	BoundingVolumeMetaEngine([InteractingSphere2AABB(),InteractingFacet2AABB(),MetaInteractingGeometry2AABB()]),
	InsertionSortCollider(),
	InteractionDispatchers(
		[ef2_Sphere_Sphere_Dem3DofGeom(),ef2_Facet_Sphere_Dem3DofGeom()],
		[SimpleElasticRelationships()],
		[Law2_Dem3Dof_Elastic_Elastic()],
	),
	GravityEngine(gravity=(1e-2,1e-2,-1000)),
	NewtonsDampedLaw(damping=.1)
]
# we don't care about physical accuracy here, (over)critical step is fine as long as the simulation doesn't explode
O.dt=utils.PWaveTimeStep()
O.saveTmp()
O.timingEnabled=True
O.run(10000,True)
from yade import timing
timing.stats()
quit()
