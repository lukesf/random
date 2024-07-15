# parametric enclosure with posts and side holes

import cadquery as cq
# parameter definitions
p_outerWidth = 120.0  # Outer width of box enclosure
p_outerLength = 100.0  # Outer length of box enclosure
p_outerHeight = 40.0  # Outer height of box enclosure

p_thickness = 2.4  # Thickness of the box walls
p_sideRadius = 4.0  # Radius for the curves around the sides of the box
p_topAndBottomRadius = (
    2.0  # Radius for the curves on the top and bottom edges of the box
)

p_flipLid = True  # Whether to place the lid with the top facing down or not.
p_lipHeight = 2.0  # Height of lip on the underside of the lid.\nSits inside the box body for a snug fit.

# outer shell
oshell = (
    cq.Workplane("XY")
    .rect(p_outerWidth, p_outerLength)
    .extrude(p_outerHeight + p_lipHeight)
)

# weird geometry happens if we make the fillets in the wrong order
if p_sideRadius > p_topAndBottomRadius:
    oshell = oshell.edges("|Z").fillet(p_sideRadius)
    oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
else:
    oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
    oshell = oshell.edges("|Z").fillet(p_sideRadius)

# inner shell
ishell = (
    oshell.faces("<Z")
    .workplane(p_thickness, True)
    .rect((p_outerWidth - 2.0 * p_thickness), (p_outerLength - 2.0 * p_thickness))
    .extrude(
        (p_outerHeight - 2.0 * p_thickness), False
    )  # set combine false to produce just the new boss
)
ishell = ishell.edges("|Z").fillet(p_sideRadius - p_thickness)

# make the box outer box
box = oshell.cut(ishell)


# Make the screw posts
p_posts= [
#    {"ws":"<Z", "OD":8., "ID":3., "H":6., "loc":(+24,-6),"pnts":[(0,0),(0, 48)]},
    {"ws":"<Z", "OD":4., "ID":2., "H":6., "loc":(-52,+8),"pnts":[(16,0),(0, 30)]},
    {"ws":"<Z", "OD":4., "ID":2., "H":6., "loc":(-40,-40),"pnts":[(0,0),(37, 0),(37, 37),(0, 37)]},
    {"ws":"<Z", "OD":4., "ID":2., "H":6., "loc":(-40,-40),"pnts":[(0,0),(37, 0),(37, 37),(0, 37)]},
    {"ws":"<Z", "OD":4., "ID":2., "H":6., "loc":(10,-40),"pnts":[(0,0),(37, 0),(37, 37),(0, 37)]},

    ]

for p in p_posts:
    # make the screw posts
    box = (
        box.faces(p["ws"])
        .workplane(-p_thickness,origin=(0,0,0))
        .pushPoints([(i[0]+p["loc"][0],i[1]+p["loc"][1]) for i in p["pnts"]])
        .circle(p["OD"] / 2.0)
        .circle(p["ID"] / 2.0)
        .extrude(-p["H"])
        )

# Make the side holes
p_sideholes= [
    {"ws":">X", "dia":30., "loc":(-20, 15+p_thickness)},
    {"ws":">Y", "dia":16., "loc":(20, +p_outerHeight/2.+5)},
    {"ws":">Y", "dia":16., "loc":(0, +p_outerHeight/2.+5)},
    {"ws":"<Y", "dia":11., "loc":(-30, +p_outerHeight/2.+5)},
#    {"ws":"<X", "dia":11., "loc":(-10, +p_outerHeight/2.+5)},
    ]

keys = []
for h in p_sideholes:
    box = (box.faces(h["ws"])
           .workplane(0,origin=(0,0,0))
           .pushPoints([h["loc"]])
           .hole(h["dia"], 10)
    )       
    # make slot
    y0 = p_outerHeight-p_thickness-h["loc"][1]
    sW = 6

    if (h["ws"]==">X"):
        wp = "YZ"
        trans = (p_outerWidth/2-p_thickness, h["loc"][0], h["loc"][1] + y0/2.)
    if (h["ws"]=="<X"):
        wp = "YZ"
        trans = (-p_outerWidth/2, -h["loc"][0], h["loc"][1] + y0/2.)

    if (h["ws"]==">Y"):
        wp = "XZ"
        trans = (-h["loc"][0], p_outerLength/2., h["loc"][1] + y0/2.)
    if (h["ws"]=="<Y"):
        wp = "XZ"
        trans = (h["loc"][0], -p_outerLength/2.+p_thickness, h["loc"][1] + y0/2.)


    cutshape = (
        cq.Workplane(wp)
        .rect(sW, y0)
        .extrude(p_thickness)
    )
    cutshape = cutshape.translate(trans)

    key = box.intersect(cutshape)
    keys.append(key)
    box = box.cut(cutshape)


# Tabs
p_tabW = p_thickness
p_tabWa = p_thickness/3.
p_tabH = -10.
p_tabL = 12.
tab_profile = [(0,0), (p_tabW,0), (p_tabW, p_tabH), (0, p_tabH), (-p_tabWa, 3*p_tabH/4.), (0, p_tabH/2.)]
#Tab locations (mirrored about center):
p_tabs = [{"wp":"YZ", "trans":(-p_outerWidth*3/8., -p_outerLength/2.+p_thickness, p_outerHeight)},
#          {"wp":"YZ", "trans":(+p_outerWidth*5/16., -p_outerLength/2.+p_thickness, p_outerHeight)},
          ]
tabs = []
for t in p_tabs:
    tabshape = (
        cq.Workplane(t["wp"])
        .polyline(tab_profile).close()
        .extrude(p_tabL/2., both= True)
    )
    # make slightly larger shape for slot
    tabshape2 = (
        cq.Workplane(t["wp"])
        .polyline(tab_profile).close()
        .extrude(p_tabL/2.+1, both= True)
    )
    # Make 4 symmetric tabs
    tabshape = tabshape.translate(t["trans"])
    tabshape2 = tabshape2.translate(t["trans"])
    tabslot = box.intersect(tabshape2)
    box = box.cut(tabslot)
    tabs.append(tabshape)

    tabshape = tabshape.mirror("XZ")
    tabshape2 = tabshape2.mirror("XZ")
    tabslot = box.intersect(tabshape2)
    box = box.cut(tabslot)
    tabs.append(tabshape)

    tabshape = tabshape.mirror("YZ")
    tabshape2 = tabshape2.mirror("YZ")
    tabslot = box.intersect(tabshape2)
    box = box.cut(tabslot)
    tabs.append(tabshape)

    tabshape = tabshape.mirror("XZ")
    tabshape2 = tabshape2.mirror("XZ")
    tabslot = box.intersect(tabshape2)
    box = box.cut(tabslot)
    tabs.append(tabshape)



# split lid into top and bottom parts
(lid, bottom) = (
    box.faces(">Z")
    .workplane(-p_thickness - p_lipHeight)
    .split(keepTop=True, keepBottom=True)
    .all()
)  # splits into two solids

# translate the lid, and subtract the bottom from it to produce the lid inset
lowerLid = lid.translate((0, 0, -p_lipHeight))
cutlip = lowerLid.cut(bottom)
#cutlip = cutlip.translate((0, 0, p_lipHeight))


# Add keys
for k in keys:
    cutlip = cutlip.union(k)

# Add tabs
for t in tabs:
    cutlip = cutlip.union(t)




cutlip2 = cutlip.translate(
    (p_outerWidth + p_thickness, 0, p_thickness - p_outerHeight)
)

top = cutlip2

# flip lid upside down if desired
if p_flipLid:
    top = top.rotateAboutCenter((1, 0, 0), 180)

# return the combined result
#result = topOfLid.union(bottom)

# Comment out to debug intermediate shapes
del oshell,ishell, box

del cutshape, key, k
del tabslot, tabshape, tabshape2, t
del lid, lowerLid, cutlip, cutlip2




'''
# Code to add boreholes in lid
p_boreDiameter = 8.0  # Diameter of the counterbore hole, if any
p_boreDepth = 1.0  # Depth of the counterbore hole, if
p_countersinkDiameter = 0.0  # Outer diameter of countersink. Should roughly match the outer diameter of the screw head
p_countersinkAngle = 90.0  # Countersink angle (complete angle between opposite sides, not from center to one side)

# compute centers for screw holes
topOfLidCenters = (
    cutlip.faces(">Z")
    .workplane(centerOption="CenterOfMass")
    .rect(POSTWIDTH, POSTLENGTH, forConstruction=True)
    .vertices()
)

# add holes of the desired type
if p_boreDiameter > 0 and p_boreDepth > 0:
    topOfLid = topOfLidCenters.cboreHole(
        p_screwpostID, p_boreDiameter, p_boreDepth, 2.0 * p_thickness
    )
elif p_countersinkDiameter > 0 and p_countersinkAngle > 0:
    topOfLid = topOfLidCenters.cskHole(
        p_screwpostID, p_countersinkDiameter, p_countersinkAngle, 2.0 * p_thickness
    )
else:
    topOfLid = topOfLidCenters.hole(p_screwpostID, 2.0 * p_thickness)
'''
