# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import omni.ext

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class ExampleExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[intrinsic_task] startup")

        self._window = omni.ui.Window("Intrinsic Hackathon Debug", width=300, height=300)
        with self._window.frame:
            with omni.ui.VStack():
                # label = omni.ui.Label("Intrinsic Hackathon Debug")
                with omni.ui.VStack():
                    omni.ui.Button("Create Cable", clicked_fn=self.create_cable)

    def on_shutdown(self):
        print("[intrinsic_task] shutdown")

    def create_cable(self):
        print("[intrinsic_task] create_cable")

        from pxr import Usd, UsdGeom, Gf, UsdPhysics, UsdShade, Sdf, PhysxSchema
        from omni.physx.scripts import physicsUtils
        import omni.usd
        stage = omni.usd.get_context().get_stage()

        # configure ropes (all units in meters):
        linkRadius = 0.003             # e.g. 0.01 m
        linkHalfLength = linkRadius * 2.0         # capsule half-height; keeps a reasonable aspect ratio
        ropeLength = 0.3              # e.g. 1.0 m
        ropeColor = Gf.Vec3f(0.5, 0.1, 0.1)
        coneAngleLimit = 80
        rope_damping = 0.1
        rope_stiffness = 1.0
        contactOffset = linkRadius * 0.02          # small relative to link size

        # stage = get_current_stage()
        prim_path = "/World/Rope"
        # Define Xform prim for the rope
        rope_prim = UsdGeom.Xform.Define(stage, prim_path)
        # add translate op to the rope prim
        rope_prim.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0))
        # add rotate op xyz to the rope prim
        rope_prim.AddRotateXYZOp().Set(Gf.Vec3d(0, 0, 0))
        # add scale op to the rope prim
        rope_prim.AddScaleOp().Set(Gf.Vec3d(1, 1, 1))
    
        # Define PhysicsMaterial prim for the rope
        UsdShade.Material.Define(stage, f"{prim_path}/PhysicsMaterial")
        material = UsdPhysics.MaterialAPI.Apply(stage.GetPrimAtPath(f"{prim_path}/PhysicsMaterial"))
        material.CreateStaticFrictionAttr().Set(0.1)
        material.CreateDynamicFrictionAttr().Set(0.1)
        material.CreateRestitutionAttr().Set(0)

        linkLength = 2.0 * linkHalfLength - linkRadius
        numLinks = max(1, int(ropeLength / linkLength))
        xStart = 0.0 # -numLinks * linkLength * 0.5
        yStart = 0.0

        scopePath = Sdf.Path(prim_path).AppendChild("Rope")
        UsdGeom.Scope.Define(stage, scopePath)

        y = yStart
        z = 0.0
        jointX = linkHalfLength - 0.5 * linkRadius

        # Create one capsule prim per link
        linkPaths = []
        for linkInd in range(numLinks):
            linkPath = scopePath.AppendChild(f"link_{linkInd}")
            linkPaths.append(linkPath)

            capsuleGeom = UsdGeom.Capsule.Define(stage, linkPath)
            capsuleGeom.CreateHeightAttr(linkHalfLength)
            capsuleGeom.CreateRadiusAttr(linkRadius)
            capsuleGeom.CreateAxisAttr("X")
            capsuleGeom.CreateDisplayColorAttr().Set([ropeColor])

            x = xStart + linkInd * linkLength
            UsdGeom.Xformable(capsuleGeom).AddTranslateOp().Set(Gf.Vec3d(x, y, z))

            prim = capsuleGeom.GetPrim()
            UsdPhysics.CollisionAPI.Apply(prim)
            UsdPhysics.RigidBodyAPI.Apply(prim)
            massAPI = UsdPhysics.MassAPI.Apply(prim)
            massAPI.CreateDensityAttr().Set(0.0005)
            physxCollisionAPI = PhysxSchema.PhysxCollisionAPI.Apply(prim)
            physxCollisionAPI.CreateRestOffsetAttr().Set(0.0)
            physxCollisionAPI.CreateContactOffsetAttr().Set(contactOffset)
            physicsUtils.add_physics_material_to_prim(stage, prim, f"{prim_path}/PhysicsMaterial")

        # Create one joint prim per consecutive link pair
        for linkInd in range(numLinks - 1):
            jointPath = scopePath.AppendChild(f"joint_{linkInd}_{linkInd + 1}")
            joint = UsdPhysics.Joint.Define(stage, jointPath)

            joint.GetBody0Rel().SetTargets([linkPaths[linkInd]])
            joint.GetBody1Rel().SetTargets([linkPaths[linkInd + 1]])
            joint.CreateLocalPos0Attr().Set(Gf.Vec3f(jointX, 0, 0))
            joint.CreateLocalPos1Attr().Set(Gf.Vec3f(-jointX, 0, 0))
            joint.CreateLocalRot0Attr().Set(Gf.Quatf(1.0))
            joint.CreateLocalRot1Attr().Set(Gf.Quatf(1.0))

            d6Prim = joint.GetPrim()

            # Locked DOFs (low > high means locked)
            for dof in ["transX", "transY", "transZ", "rotX"]:
                limitAPI = UsdPhysics.LimitAPI.Apply(d6Prim, dof)
                limitAPI.CreateLowAttr(1.0)
                limitAPI.CreateHighAttr(-1.0)

            # Free DOFs with drives for rope dynamics
            for dof in ["rotY", "rotZ"]:
                limitAPI = UsdPhysics.LimitAPI.Apply(d6Prim, dof)
                limitAPI.CreateLowAttr(-coneAngleLimit)
                limitAPI.CreateHighAttr(coneAngleLimit)

                # driveAPI = UsdPhysics.DriveAPI.Apply(d6Prim, dof)
                # driveAPI.CreateTypeAttr("force")
                # driveAPI.CreateDampingAttr(rope_damping)
                # driveAPI.CreateStiffnessAttr(rope_stiffness)

        # Define a USD PhysicsFixedJoint 
        fixedJoint = UsdPhysics.FixedJoint.Define(stage, f"{prim_path}/fixedJoint")
        fixedJoint.GetBody0Rel().SetTargets([linkPaths[0]])
        fixedJoint.GetBody1Rel().SetTargets([Sdf.Path("/World/sc_plug_visual")])
