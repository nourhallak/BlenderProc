from src.utility.SetupUtility import SetupUtility
SetupUtility.setup([])

from src.utility.loader.AMASSLoader import AMASSLoader
from src.utility.sampler.Sphere import Sphere
from src.utility.MathUtility import MathUtility
from src.utility.CameraUtility import CameraUtility
from src.utility.MeshObjectUtility import MeshObject
from src.utility.WriterUtility import WriterUtility
from src.utility.Initializer import Initializer
from src.utility.LightUtility import Light

from src.utility.RendererUtility import RendererUtility

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('amass_dir', nargs='?', default="resources/AMASS", help="Path to the AMASS Dataset folder")
parser.add_argument('output_dir', nargs='?', default="examples/datasets/amass_human_poses/output", help="Path to where the final files will be saved")
args = parser.parse_args()

Initializer.init()

# Load the objects into the scene
objs = AMASSLoader.load(
    args.amass_dir,
    sub_dataset_id="CMU",
    body_model_gender="male",
    subject_id="10",
    sequence_id=1,
    frame_id=600
)

# define a light and set its location and energy level
light = Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

# Find point of interest, all cam poses should look towards it
poi = MeshObject.compute_poi(objs)
# Sample five camera poses
for i in range(5):
    # Sample random camera location around the objects
    location = Sphere.sample([0, 0, 0], radius=3, mode="SURFACE")
    # Compute rotation based on vector going from location towards poi
    rotation_matrix = CameraUtility.rotation_from_forward_vec(poi - location)
    # Add homog cam pose based on location an rotation
    cam2world_matrix = MathUtility.build_transformation_mat(location, rotation_matrix)
    CameraUtility.add_camera_pose(cam2world_matrix)

# activate normal and distance rendering
RendererUtility.enable_normals_output()
RendererUtility.enable_distance_output()
# set the amount of samples, which should be used for the color rendering
RendererUtility.set_samples(350)

# render the whole pipeline
data = RendererUtility.render()

# write the data to a .hdf5 container
WriterUtility.save_to_hdf5(args.output_dir, data)