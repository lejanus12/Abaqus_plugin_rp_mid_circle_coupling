from abaqus import *
from abaqusConstants import *
import math
from kd_tree import KDTree


def create_coupling_from_sets(
    edges,
    edges_name,
    centers_rp,
    centers_name,
    coupling,
    model,
    assembly,
    instance,
    rMax,
    couplingType=KINEMATIC,
):

    if edges:
        circles = assembly.Set(
            edges=edges,
            name="{}_{}".format(edges_name, instance.name),
        )
    else:
        print("no ", edges_name, "found for ", instance.name)

    if centers_rp:
        centers = assembly.Set(
            referencePoints=(centers_rp,),
            name="{}_{}".format(centers_name, instance.name),
        )
    else:
        print("no ", centers_name, "found for ", instance.name)

    if edges and centers_rp and coupling:
        model.Coupling(
            name="{}_{}".format(edges_name, instance.name),
            controlPoint=centers,
            surface=circles,
            influenceRadius=rMax,
            couplingType=couplingType,
            localCsys=None,
            u1=ON,
            u2=ON,
            u3=ON,
            ur1=ON,
            ur2=ON,
            ur3=ON,
        )


def RF_on_Circle_Coupling(
    rMin,
    rMax,
    coupling,
    target_instances=None,
    target_circular=True,
    target_ovals=False,
):

    vpName = session.currentViewportName
    modelName = session.sessionState[vpName]["modelName"]
    model = mdb.models[modelName]
    assembly = model.rootAssembly
    rps = assembly.referencePoints

    rps_coord = [
        {"id": x, "coord": assembly.getCoordinates(rps[x])} for x in rps.keys()
    ]
    kd_tree = False
    if len(rps_coord) > 0:
        kd_tree = KDTree(rps_coord)

    for instance in assembly.instances.values():
        if target_instances is not None and instance not in target_instances:
            continue

        circular_edges = []
        centers_rp = []

        oval_edges = []
        oval_centers_rp = []

        circles_radius = []
        # Iterate over all edges visible in the assy
        if instance.edges:
            edges_in_cells = [e for cell in instance.cells for e in cell.getEdges()]
            print("processing part : ", instance.name)
            for edge in instance.edges:

                # Skip edges that are in the cells -- we only edge of mid surfaces
                if edge.index in edges_in_cells:
                    continue

                if target_circular:
                    # first try / catch is to target circles and half circles and get the interesting point in the middle
                    try:
                        radius = edge.getRadius()
                        edge_length = edge.getSize(printResults=False)
                        expected_circumference = 2 * math.pi * radius
                        tolerance_circle = (
                            abs(edge_length - expected_circumference)
                            / expected_circumference
                        )

                        tolerance_half_circle = abs(
                            edge_length - expected_circumference / 2
                        ) / (
                            expected_circumference / 2
                        )  # also target slot holes

                        if (
                            radius
                            and rMin <= radius <= rMax
                            and (
                                tolerance_circle <= 0.05
                                or tolerance_half_circle <= 0.05
                            )
                        ):
                            circles_radius.append(radius)
                            circular_edges.append(edge.getEdgesByEdgeAngle(30.0))
                            center = assembly.InterestingPoint(edge=edge, rule=CENTER)
                            rp = assembly.ReferencePoint(point=center)
                            new_point = assembly.getCoordinates(rps[rp.id])
                            if kd_tree:
                                nearest_id = kd_tree.distance_to_nearest(new_point, 0.1)
                                if nearest_id is not None:
                                    # add the nearest point to the set
                                    rp_ref_nearest = assembly.referencePoints[
                                        nearest_id
                                    ]
                                    centers_rp.append(rp_ref_nearest)
                                    # delete the rp we just created.
                                    feature_name = assembly.featuresById[rp.id].name
                                    assembly.deleteFeatures((feature_name,))
                                    continue

                            rp_ref = assembly.referencePoints[rp.id]
                            centers_rp.append(rp_ref)

                    except:
                        pass
                if target_ovals:
                    # second try / catch is to target ovals and create interesting point in the middle
                    # we want to fail the getRadius() method to get the curvature
                    try:
                        radius = edge.getRadius()
                    except:
                        try:
                            curvature = edge.getCurvature(0.2)["radius"]
                            if rMin <= curvature <= rMax:
                                oval_edges.append(edge.getEdgesByEdgeAngle(30.0))
                                start = edge.getCurvature(0)["evaluationPoint"]
                                end = edge.getCurvature(1)["evaluationPoint"]
                                center = assembly.DatumPointByMidPoint(
                                    point1=start,
                                    point2=end,
                                )

                                datum_center = assembly.datums[center.id]
                                rp = assembly.ReferencePoint(point=datum_center.pointOn)
                                assembly.deleteFeatures((center.name,))

                                new_point = assembly.getCoordinates(rps[rp.id])
                                nearest_id = kd_tree.distance_to_nearest(
                                    new_point, rMax
                                )
                                kd_tree.insert({"id": rp.id, "coord": new_point})
                                #  REFACTOR TO GO DRY
                                if nearest_id is not None:
                                    rp_ref_nearest = assembly.referencePoints[
                                        nearest_id
                                    ]
                                    oval_centers_rp.append(rp_ref_nearest)
                                    feature_name = assembly.featuresById[rp.id].name
                                    assembly.deleteFeatures((feature_name,))
                                    continue

                                rp_ref = assembly.referencePoints[rp.id]
                                oval_centers_rp.append(rp_ref)

                        except:
                            pass
                        pass
        if target_ovals:
            create_coupling_from_sets(
                edges=oval_edges,
                edges_name="oval_edges",
                centers_rp=oval_centers_rp,
                centers_name="oval_centers_rp",
                coupling=coupling,
                model=model,
                assembly=assembly,
                instance=instance,
                rMax=rMax,
            )
        if target_circular:
            create_coupling_from_sets(
                edges=circular_edges,
                edges_name="circular_edges",
                centers_rp=centers_rp,
                centers_name="centers_rp",
                coupling=coupling,
                model=model,
                assembly=assembly,
                instance=instance,
                rMax=rMax,
            )
