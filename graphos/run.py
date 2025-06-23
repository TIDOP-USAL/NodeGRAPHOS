#!/usr/bin/python3

# Basic check
import sys
if sys.version_info.major < 3:
    print("Ups! ODM needs to run with Python 3. It seems you launched it with Python 2. Try using: python3 run.py ... ")
    sys.exit(1)

import os
import shutil
from opendm import log
from opendm import config
from opendm import system
from opendm import io
from opendm.progress import progressbc
#from opendm.utils import get_processing_results_paths, rm_r
from opendm.arghelpers import args_to_dict, save_opts, compare_args, find_rerun_stage

#from stages.odm_app import ODMApp


import subprocess
 #pueba para OpenMVS que parece que termina el proceso y sigue escribiendose...
import time
from collections import OrderedDict

def run_graphos_command(command, args):
    """
    Executes a system command with a list of arguments.

    :param command: The command to be executed (e.g., 'ls', 'python', etc.).
    :param args: A list of arguments to pass to the command.
    :return: A tuple containing (stdout, stderr, returncode).
    """
    try:
        # Build the full command by concatenating the command with its arguments
        full_command = ['graphos', command] + args

        # Execute the command
        result = subprocess.run(full_command, capture_output=True, text=True)

        # Return the standard output, standard error, and return code
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        return None, f"Command '{command}' not found.", -1
    except Exception as e:
        return None, str(e), -1
    

def graphos_version():
    try:
        with open("VERSION") as f:
            return f.read().split("\n")[0].strip()
    except:
        return "?"

def list_images(image_dir, output_file):
    """
    Writes the full paths of all files in a directory to a text file.

    :param image_dir: The directory containing the images.
    :param output_file: The path of the output text file to save the image paths.
    """
    # Open the output file in write mode
    with open(output_file, "w") as file:
        # List all files in the directory
        for image in os.listdir(image_dir):
            # Get the full path of the image
            image_path = os.path.join(image_dir, image)
            # Write the full path to the output file
            file.write(image_path + "\n")

# --------------------- CLASE BASE ---------------------
class ProcessStep:
    def __init__(self, args, project_file):
        self.args = args
        self.project_file = project_file

    def run(self):
        raise NotImplementedError("Each step must implement the run method.")

# --------------------- SUBCLASES DE ETAPAS ---------------------
class CreateProject(ProcessStep):
    def run(self):
        return run_graphos_command("createproj", ["--name", self.project_file, "--overwrite"])

class AddImages(ProcessStep):
    def run(self):
        image_list = os.path.join(self.args.project_path, "image_list.txt")
        list_images(os.path.join(self.args.project_path, "images"), image_list)
        cmd = ["-p", self.project_file, "-l", image_list, "--progress_bar", "DISABLE"]
        if self.args.camera_lens: cmd += ["--camera", self.args.camera_lens]
        return run_graphos_command("image_manager", cmd)

class FeatExtract(ProcessStep):
    def run(self):
        cmd = ["-p", self.project_file, "--progress_bar", "DISABLE"]
        for k in ["max_image_size", "max_features_number", "octave_resolution", "contrast_threshold", "edge_threshold"]:
            v = getattr(self.args, k, None)
            if v: cmd += [f"--{k}", str(v)]
        if self.args.no_gpu: cmd += ["--disable_cuda"]
        return run_graphos_command("featextract", cmd)

class FeatMatch(ProcessStep):
    def run(self):
        cmd = ["-p", self.project_file, "--progress_bar", "DISABLE"]
        for k in ["ratio", "distance", "max_error", "confidence"]:
            v = getattr(self.args, k, None)
            if v: cmd += [f"--{k}", str(v)]
        if self.args.cross_check: cmd += ["--cross_check"]
        if self.args.exhaustive_matching: cmd += ["--exhaustive_matching"]
        if self.args.no_gpu: cmd += ["--disable_cuda"]
        return run_graphos_command("featmatch", cmd)

class GCPS(ProcessStep):
    def run(self):
        gcp_file = os.path.join(self.args.project_path, 'gcp', "gcp_list.txt")
        return run_graphos_command("gcps", ["-p", self.project_file, "--cp", gcp_file]) if os.path.isfile(gcp_file) else (None, None, 0)

class Ori(ProcessStep):
    def run(self):
        cmd = ["-p", self.project_file, "-a"]
        if self.args.use_gcp: cmd += ["--use_gcp", str(self.args.use_gcp)]
        if self.args.use_poses: cmd += ["--use_poses", str(self.args.use_poses)]
        return run_graphos_command("ori", cmd)

class Dense(ProcessStep):
    def run(self):
        cmd = ["-p", self.project_file]
        for k in ["resolution_level", "min_resolution", "max_resolution", "number_views", "number_views_fuse"]:
            v = getattr(self.args, k, None)
            if v: cmd += [f"--mvs:{k}", str(v)]
        if self.args.estimate_colors: cmd += ["--estimate_colors"]
        if self.args.estimate_normals: cmd += ["--estimate_normals"]
        if self.args.segment: cmd += ["--segment"]
        if self.args.no_gpu: cmd += ["--disable_cuda"]
        return run_graphos_command("dense", cmd)

class ExportPointCloud(ProcessStep):
    def run(self):
        f = os.path.join(self.args.project_path, 'odm_georeferencing', 'odm_georeferenced_model.laz')
        cmd = ["-p", self.project_file, "-f", f]
        if self.args.save_colors: cmd += ["--save_colors", str(self.args.save_colors)]
        if self.args.save_normals: cmd += ["--save_normals", str(self.args.save_normals)]
        return run_graphos_command("export_point_cloud", cmd)

class Mesh(ProcessStep):
    def run(self):
        cmd = ["-p", self.project_file]
        if self.args.depth: cmd += ["--depth", str(self.args.depth)]
        if self.args.boundary_type: cmd += ["--boundary_type", self.args.boundary_type]
        return run_graphos_command("mesh", cmd)

class DEM(ProcessStep):
    def run(self):
        cmd = ["-p", self.project_file]
        if self.args.dem_resolution: cmd += ["--gsd", str(self.args.dem_resolution)]
        return run_graphos_command("dem", cmd)

class Ortho(ProcessStep):
    def run(self):
        cmd = ["-p", self.project_file]
        if self.args.orthophoto_resolution: cmd += ["--gsd", str(self.args.orthophoto_resolution)]
        if self.args.no_gpu: cmd += ["--disable_cuda"]
        return run_graphos_command("ortho", cmd)

# --------------------- PIPELINE ---------------------
class GraphosPipeline:
    def __init__(self, args, project_file):
        self.steps = [
            ('create_project', CreateProject(args, project_file), 1),
            ('add_images', AddImages(args, project_file), 5),
            ('featextract', FeatExtract(args, project_file), 10),
            ('featmatch', FeatMatch(args, project_file), 15),
            ('gcps', GCPS(args, project_file), 16),
            ('ori', Ori(args, project_file), 40),
            ('dense', Dense(args, project_file), 45),
            ('export_point_cloud', ExportPointCloud(args, project_file), 50),
            ('mesh', Mesh(args, project_file), 70),
            ('dem', DEM(args, project_file), 80),
            ('ortho', Ortho(args, project_file), 90)
        ]

    def run(self, rerun_from=None):
        start_idx = next((i for i, (n,_,__) in enumerate(self.steps) if rerun_from and n in rerun_from), 0)
        for name, step, progress in self.steps[start_idx:]:
            stdout, stderr, retcode = step.run()
            progressbc.send_update(progress)
            if retcode != 0:
                print(stdout or '', f"ERROR: {name}", stderr or '')
                progressbc.send_update(100)
                sys.exit(retcode)
            print(stdout or '')

# --------------------- MAIN ---------------------
if __name__ == '__main__':
    args = config.config()
    log.ODM_INFO(f'Initializing NodeGRAPHOS {graphos_version()} - {system.now()}')
    
    progressbc.set_project_name(args.name)
    args.project_path = os.path.join(args.project_path, args.name)
    if not io.dir_exists(args.project_path):
        log.ODM_ERROR(f'Directory {args.name} does not exist.')
        sys.exit(1)

    project_file = io.join_paths(args.project_path, args.name + ".xml")
    opts_json = os.path.join(args.project_path, "options.json")
    auto_rerun_stage, opts_diff = find_rerun_stage(opts_json, args, config.rerun_stages, config.processopts)
    rerun_from = auto_rerun_stage or args.rerun_from or []

    args_dict = args_to_dict(args)
    for k,v in args_dict.items():
        log.ODM_INFO(f'{k}: {v} {"[changed]" if k in opts_diff else ""}')

    #for d in ['odm_orthophoto', 'odm_dem', 'dsm_tiles', 'orthophoto_tiles', 'potree_pointcloud', 'odm_georeferencing']:
    for d in ['odm_orthophoto', 'odm_dem', 'odm_georeferencing']:
        system.mkdir_p(io.join_paths(args.project_path, d))
    list_images(os.path.join(args.project_path, 'images'), os.path.join(args.project_path, "image_list.txt"))

    pipeline = GraphosPipeline(args, project_file)
    pipeline.run(rerun_from)

    shutil.copy(io.join_paths(args.project_path, 'dem', 'dsm.tif'), io.join_paths(args.project_path, 'odm_dem'))
    shutil.copy(io.join_paths(args.project_path, 'ortho', 'ortho.tif'), io.join_paths(args.project_path, 'odm_orthophoto', 'odm_orthophoto.tif'))
    output_path = io.join_paths(args.project_path, "cameras.json")
    subprocess.run([
        "python3",
        os.path.join(os.path.dirname(__file__), "export_cameras.py"),
        project_file,
        output_path
    ], check=True)

    save_opts(opts_json, args)
    log.ODM_INFO(f'GRAPHOS app finished - {system.now()}')
