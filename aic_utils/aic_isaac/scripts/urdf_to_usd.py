import argparse
import os
from isaacsim import SimulationApp

# 1. Setup Argument Parsing BEFORE starting SimulationApp
parser = argparse.ArgumentParser(description="URDF to USD Converter for Isaac Sim")
parser.add_argument(
    "--input", type=str, required=True, help="Path to the input URDF file"
)
parser.add_argument(
    "--output", type=str, required=True, help="Path where the USD file will be saved"
)
args = parser.parse_args()

# 2. Initialize SimulationApp
# Headless is set to True as this is a conversion utility
kit = SimulationApp({"renderer": "RaytracedLighting", "headless": True})

import omni.kit.commands
import omni.usd
from isaacsim.core.prims import Articulation
from pxr import Gf, PhysicsSchemaTools, PhysxSchema, Sdf, UsdPhysics


def main():
    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        kit.close()
        return

    # Setting up import configuration
    status, import_config = omni.kit.commands.execute("URDFCreateImportConfig")
    import_config.merge_fixed_joints = False
    import_config.convex_decomp = True
    import_config.import_inertia_tensor = True
    import_config.fix_base = True
    import_config.distance_scale = 1.0

    # Import URDF
    print(f"Importing: {args.input}")
    status, prim_path = omni.kit.commands.execute(
        "URDFParseAndImportFile",
        urdf_path=args.input,
        import_config=import_config,
        get_articulation_root=True,
    )

    if not status:
        print("Failed to import URDF.")
        kit.close()
        return

    # Get stage handle
    stage = omni.usd.get_context().get_stage()

    # Enable physics and scene setup
    scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/physicsScene"))
    scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
    scene.CreateGravityMagnitudeAttr().Set(9.81)

    PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/physicsScene"))
    physxSceneAPI = PhysxSchema.PhysxSceneAPI.Get(stage, "/physicsScene")
    physxSceneAPI.CreateEnableCCDAttr(True)
    physxSceneAPI.CreateEnableStabilizationAttr(True)
    physxSceneAPI.CreateBroadphaseTypeAttr("MBP")
    physxSceneAPI.CreateSolverTypeAttr("TGS")

    # 3. Save the Stage
    print(f"Saving USD to: {args.output}")
    omni.usd.get_context().save_as_stage(args.output)

    kit.close()


if __name__ == "__main__":
    main()
