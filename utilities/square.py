class Square():
    def create(structure, edge):
        s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                     sheetSize=edge*2)
        g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
        s1.setPrimaryObject(option=STANDALONE)
        s1.Spot(point=(0.0, edge*0.5))
        s1.Spot(point=(edge*0.5, edge*0.5))
        s1.Spot(point=(edge*0.5, edge*0.0))
        s1.Spot(point=(edge*1.0, edge*0.5))
        s1.Spot(point=(edge*0.5, edge*1.0))
        s1.Line(point1=(0.0, edge*0.5), point2=(edge*0.5, edge*0.5))
        s1.HorizontalConstraint(entity=g[2], addUndoState=False)
        s1.Line(point1=(edge*0.5, edge*0.5), point2=(edge*1.0, edge*0.5))
        s1.HorizontalConstraint(entity=g[3], addUndoState=False)
        s1.ParallelConstraint(entity1=g[2], entity2=g[3], addUndoState=False)
        s1.Line(point1=(edge*0.5, edge*1.0), point2=(edge*0.5, edge*0.5))
        s1.VerticalConstraint(entity=g[4], addUndoState=False)
        s1.Line(point1=(edge*0.5, edge*0.5), point2=(edge*0.5, 0.0))
        s1.VerticalConstraint(entity=g[5], addUndoState=False)
        s1.ParallelConstraint(entity1=g[4], entity2=g[5], addUndoState=False)
        p = mdb.models['Model-1'].Part(name='Part', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part']
        p.BaseWire(sketch=s1)
        s1.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part']
        del mdb.models['Model-1'].sketches['__profile__']