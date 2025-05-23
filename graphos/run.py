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

def create_project(args, project_file, progressbc):
    stdout, stderr, retcode = run_graphos_command("createproj", ["--name", project_file, "--overwrite"])
    progressbc.send_update(1)
    return stdout, stderr, retcode

def add_images(args, project_file, progressbc):
    images_file = io.join_paths(args.project_path, "image_list.txt")
    image_dir = io.join_paths(args.project_path, 'images')
    list_images(image_dir, images_file)

    cmd_args = ["-p", project_file]
    cmd_args += ["-l", images_file]
    if getattr(args, "camera_lens", None) is not None:
        cmd_args += ["--camera", str(args.camera_lens)]

    stdout, stderr, retcode = run_graphos_command("image_manager", cmd_args)
    progressbc.send_update(5)
    return stdout, stderr, retcode

def featextract(args, project_file, progressbc):
    cmd_args = ["-p", project_file]

    if getattr(args, "max_image_size", None) is not None:
        cmd_args += ["--max_image_size", str(args.max_image_size)]

    if getattr(args, "max_features_number", None) is not None:
        cmd_args += ["--max_features_number", str(args.max_features_number)]

    if getattr(args, "octave_resolution", None) is not None:
        cmd_args += ["--octave_resolution", str(args.octave_resolution)]

    if getattr(args, "contrast_threshold", None) is not None:
        cmd_args += ["--contrast_threshold", str(args.contrast_threshold)]

    if getattr(args, "edge_threshold", None) is not None:
        cmd_args += ["--edge_threshold", str(args.edge_threshold)]

    if getattr(args, "no_gpu", None) is not None:
        cmd_args += ["--disable_cuda"]

    stdout, stderr, retcode = run_graphos_command("featextract", cmd_args)
    progressbc.send_update(10)
    
    return stdout, stderr, retcode

def featmatch(args, project_file, progressbc):
    cmd_args = ["-p", project_file]

    if getattr(args, "ratio", None) is not None:
        cmd_args += ["--ratio", str(args.ratio)]

    if getattr(args, "distance", None) is not None:
        cmd_args += ["--distance", str(args.distance)]    

    if getattr(args, "max_error", None) is not None:
        cmd_args += ["--max_error", str(args.max_error)]

    if getattr(args, "confidence", None) is not None:
        cmd_args += ["--confidence", str(args.confidence)]

    if getattr(args, "cross_check", None):
        cmd_args += ["--cross_check"]

    if getattr(args, "exhaustive_matching", None):
        cmd_args += ["--exhaustive_matching"]

    if getattr(args, "no_gpu", None) is not None:
        cmd_args += ["--disable_cuda"]

    stdout, stderr, retcode = run_graphos_command("featmatch", cmd_args)
    progressbc.send_update(15)

    return stdout, stderr, retcode

def gcps(args, project_file, progressbc):
    gcp_dir = io.join_paths(args.project_path, 'gcp')
    gcp_file = io.join_paths(gcp_dir, "gcp_list.txt")

    if os.path.isfile(gcp_file):
        stdout, stderr, retcode = run_graphos_command("gcps", ["-p", project_file, "--cp", gcp_file])
        progressbc.send_update(16)
        return stdout, stderr, retcode
    return (None, None, 0)

def ori(args, project_file, progressbc):
    cmd_args = ["-p", project_file]
    cmd_args += ["-a"]

    # if getattr(args, "fix_calibration", None) is not None:
    #     cmd_args += ["--fix_calibration", str(args.fix_calibration)]

    # if getattr(args, "use_rtk_accuracy", None) is not None:
    #     cmd_args += ["--use_rtk_accuracy", str(args.use_rtk_accuracy)]

    # if getattr(args, "use_gcp", None) is not None:
    #     cmd_args += ["--use_gcp", str(args.use_gcp)]

    # if getattr(args, "use_poses", None) is not None:
    #     cmd_args += ["--use_poses", str(args.use_poses)]

    
    if args.use_gcp is not None:
        cmd_args += ["--use_gcp", str(args.use_gcp)]

    if args.use_poses is not None:
        cmd_args += ["--use_poses", str(args.use_gcp)]

    stdout, stderr, retcode = run_graphos_command("ori", cmd_args)
    progressbc.send_update(40)
    return stdout, stderr, retcode

def dense(args, project_file, progressbc):
    cmd_args = ["-p", project_file]

    if getattr(args, "resolution_level", None) is not None:
        cmd_args += ["--mvs:resolution_level", str(args.resolution_level)]

    if getattr(args, "min_resolution", None) is not None:
        cmd_args += ["--mvs:min_resolution", str(args.min_resolution)]

    if getattr(args, "max_resolution", None) is not None:
        cmd_args += ["--mvs:max_resolution", str(args.max_resolution)]

    if getattr(args, "number_views", None) is not None:
        cmd_args += ["--mvs:number_views", str(args.number_views)]

    if getattr(args, "number_views_fuse", None) is not None:
        cmd_args += ["--mvs:number_views_fuse", str(args.number_views_fuse)]

    if getattr(args, "estimate_colors", None) is not None:
        cmd_args += ["--estimate_colors"]

    if getattr(args, "estimate_normals", None) is not None:
        cmd_args += ["--estimate_normals"]

    if args.segment:
        cmd_args += ["--segment"]

    if getattr(args, "no_gpu", None) is not None:
        cmd_args += ["--disable_cuda"]

    stdout, stderr, retcode = run_graphos_command("dense", cmd_args)
    progressbc.send_update(45)
    return stdout, stderr, retcode

def export_point_cloud(args, project_file, progressbc):
    georeferencing_point_cloud = io.join_paths(args.project_path, 'odm_georeferencing/odm_georeferenced_model.las')

    cmd_args = ["-p", project_file]
    cmd_args += ["-f", georeferencing_point_cloud]

    if getattr(args, "save_colors", None) is not None:
        cmd_args += ["--save_colors", str(args.save_colors)]
    
    if getattr(args, "save_normals", None) is not None:
        cmd_args += ["--save_normals", str(args.save_normals)]

    stdout, stderr, retcode = run_graphos_command("export_point_cloud", cmd_args)
    progressbc.send_update(5)    
    return stdout, stderr, retcode

def mesh(args, project_file, progressbc):
    cmd_args = ["-p", project_file]

    if getattr(args, "depth", None) is not None:
        cmd_args += ["--depth", str(args.depth)]

    if getattr(args, "boundary_type", None) is not None:
        cmd_args += ["--boundary_type", str(args.boundary_type)]

    stdout, stderr, retcode = run_graphos_command("mesh", cmd_args)
    progressbc.send_update(70)
    return stdout, stderr, retcode

def dem(args, project_file, progressbc):
    cmd_args = ["-p", project_file]

    if getattr(args, "dem_resolution", None) is not None:
        cmd_args += ["--gsd", str(args.dem_resolution)]
    
    stdout, stderr, retcode = run_graphos_command("dem", cmd_args)
    progressbc.send_update(80)
    return stdout, stderr, retcode

def ortho(args, project_file, progressbc):
    cmd_args = ["-p", project_file]

    if getattr(args, "orthophoto_resolution", None) is not None:
        cmd_args += ["--gsd", str(args.orthophoto_resolution)]

    if getattr(args, "no_gpu", None) is not None:
        cmd_args += ["--disable_cuda"]

    stdout, stderr, retcode = run_graphos_command("ortho", cmd_args)
    progressbc.send_update(90)
    return stdout, stderr, retcode




if __name__ == '__main__':
    args = config.config()

    log.ODM_INFO('Initializing NodeGRAPHOS %s - %s' % (graphos_version(), system.now()))

    progressbc.set_project_name(args.name)
    args.project_path = os.path.join(args.project_path, args.name)

    if not io.dir_exists(args.project_path):
        log.ODM_ERROR('Directory %s does not exist.' % args.name)
        exit(1)

    opts_json = os.path.join(args.project_path, "options.json")
    auto_rerun_stage, opts_diff = find_rerun_stage(opts_json, args, config.rerun_stages, config.processopts)
    if auto_rerun_stage is not None and len(auto_rerun_stage) > 0:
        log.ODM_INFO("Rerunning from: %s" % auto_rerun_stage[0])
        args.rerun_from = auto_rerun_stage

    # Print args
    args_dict = args_to_dict(args)
    log.ODM_INFO('==============')
    for k in args_dict.keys():
        log.ODM_INFO('%s: %s%s' % (k, args_dict[k], ' [changed]' if k in opts_diff else ''))
    log.ODM_INFO('==============')
    

    # If user asks to rerun everything, delete all of the existing progress directories.
    #if args.rerun_all:
    #    log.ODM_INFO("Rerun all -- Removing old data")
    #    for d in [os.path.join(args.project_path, p) for p in get_processing_results_paths()] + [
    #              os.path.join(args.project_path, "odm_meshing"),
    #              os.path.join(args.project_path, "opensfm"),
    #              os.path.join(args.project_path, "odm_texturing_25d"),
    #              os.path.join(args.project_path, "odm_filterpoints"),
    #              os.path.join(args.project_path, "submodels")]:
    #        rm_r(d)

    #pipeline = OrderedDict([
    #    ("createproj", lambda: create_project(args, project_file)),
    #    ("image_manager", lambda: add_images(args, project_file, image_dir)),
    #    ("featextract", lambda: featextract(args, project_file)),
    #    ("featmatch", lambda: featmatch(args, project_file)),
    #    ("gcps", lambda: gcps(args, project_file, gcp_file)),
    #    ("ori", lambda: ori(args, project_file)),
    #    ("dense", lambda: dense(args, project_file)),
    #    ("export_point_cloud", lambda: export_point_cloud(args, project_file, georeferencing_point_cloud)),
    #    ("mesh", lambda: mesh(args, project_file)),
    #    ("dem", lambda: dem(args, project_file)),
    #    ("ortho", lambda: ortho(args, project_file)),
    #])


    #app = ODMApp(args)
    #retcode = app.execute()

    #project_dir = io.join_paths(args.project_path, args.name)
    project_dir = args.project_path
    #print(project_dir)
    project_file = io.join_paths(project_dir, args.name + ".xml")
    #image_dir = io.join_paths(project_dir, 'images')
    #images_file = io.join_paths(args.project_path, "image_list.txt")
    #gcp_dir = io.join_paths(project_dir, 'gcp')

    # Esto lo hacen en NodeMicMac. No se si hay forma de cambiar las rutas de los directorios para evitar la copia
    # create output directories (match ODM conventions for backward compatibility, even though this is MicMac)
    odm_dirs = ['odm_orthophoto', 'odm_dem', 'dsm_tiles',
                'orthophoto_tiles', 'potree_pointcloud', 'odm_georeferencing']
    for odm_dir in odm_dirs:
            system.mkdir_p(io.join_paths(project_dir, odm_dir))

    # Controlar desde donde se vuelve a arrancar el proceso según args.rerun_from

    # Create GRAPHOS project
    stdout, stderr, retcode = create_project(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("createproj", ["--name", project_file, "--overwrite"])

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: Create GRAPHOS project")
        print(stderr)

    #progressbc.send_update(1)

    # Add images to project
    #output_file = io.join_paths(project_dir, "image_list.txt")
    #list_images(image_dir, output_file)
    stdout, stderr, retcode = add_images(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("image_manager", ["-p", project_file, "-l", output_file])

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: Add images to project")
        print(stderr)

    #progressbc.send_update(5)

    # Features
    stdout, stderr, retcode = featextract(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("featextract", ["-p", project_file])

    if retcode == 0:
        print(stdout)
    else:
        print("ERROR: Features")
        print(stderr)

    #progressbc.send_update(10)

    # Matching
    stdout, stderr, retcode = featmatch(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("featmatch", ["-p", project_file])

    if retcode == 0:
        print(stdout)
    else:
        print("ERROR: Matching")
        print(stderr)

    #progressbc.send_update(15)

    # Load Ground Control Points
    stdout, stderr, retcode = gcps(args, project_file, progressbc)

    if retcode == 0:
        print(stdout)
    else:
        print("ERROR: Load Ground Control Points")
        print(stderr)

    #gcp_file = io.join_paths(gcp_dir, "gcp_list.txt")
    #if os.path.isfile(gcp_file):
    #    stdout, stderr, retcode = run_graphos_command("gcps", ["-p", project_file, "--cp", gcp_file])

    #    if retcode == 0:
    #        print(stdout)
    #    else:
    #        print("ERROR: Load Ground Control Points")
    #        print(stderr)

    #progressbc.send_update(16)

    # Reconstruction
    
    #if os.path.isfile(gcp_file):
    #    stdout, stderr, retcode = run_graphos_command("ori", ["-p", project_file, "-a"])
    #else:
    #    stdout, stderr, retcode = run_graphos_command("ori", ["-p", project_file])

    #stdout, stderr, retcode = run_graphos_command("ori", ["-p", project_file, "-a"])
    stdout, stderr, retcode = ori(args, project_file, progressbc)

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: Reconstruction")
        print(stderr)

    #progressbc.send_update(40)

    # Densification
    stdout, stderr, retcode = dense(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("dense", ["-p", project_file,  "--mvs:resolution_level", str(2)])

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: Densification")
        print(stderr)
    
    #progressbc.send_update(45)

    # Exportar a las o laz en coordenadas UTM para que funcionen los postprocesos de NodeODM
    # odm_georeferencing/odm_georeferenced_model.laz o odm_georeferencing/odm_georeferenced_model.las
    # tambien valdría como ply georeferenciado "odm_filterpoints/point_cloud.ply"
    # Por ahora se añade a odm_filterpoints/point_cloud.ply
    #georeferencing_point_cloud = io.join_paths(project_dir, 'odm_filterpoints/point_cloud.ply')
    #georeferencing_point_cloud = io.join_paths(project_dir, 'odm_georeferencing/odm_georeferenced_model.las')

    stdout, stderr, retcode = export_point_cloud(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("export_point_cloud", ["-p", project_file, "-f", georeferencing_point_cloud, "--save_colors", "--save_normals"])

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: Export point cloud")
        print(stderr)
    
    #progressbc.send_update(5)
    
    # Mesh 
    stdout, stderr, retcode = mesh(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("mesh", ["-p", project_file, "--depth", str(11)])

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: Mesh")
        print(stderr)

    #progressbc.send_update(70)

    # DEM
    stdout, stderr, retcode = dem(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("dem", ["-p", project_file, "--gsd", str(0.1)])

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: DSM")
        print(stderr)

    dem_path = io.join_paths(project_dir, 'dem')
    odm_dem = io.join_paths(project_dir, 'odm_dem')
    shutil.copy(io.join_paths(dem_path, 'dsm.tif'), odm_dem)

    #progressbc.send_update(80)

    # Ortho
    stdout, stderr, retcode = ortho(args, project_file, progressbc)
    #stdout, stderr, retcode = run_graphos_command("ortho", ["-p", project_file, "--gsd", str(0.05)])

    if retcode == 0:
        print(stdout)
    else:
        print(stdout)
        print("ERROR: Orthophoto")
        print(stderr)
    
    ortho_path = io.join_paths(project_dir, 'ortho')
    odm_ortho_dir = io.join_paths(project_dir, 'odm_orthophoto')
    odm_ortho_path = io.join_paths(odm_ortho_dir, 'odm_orthophoto.tif')
    shutil.copy(io.join_paths(ortho_path, 'ortho.tif'), odm_ortho_path)

    #progressbc.send_update(90)

    if retcode == 0:
        save_opts(opts_json, args)
    
    # Do not show ASCII art for local submodels runs
    if retcode == 0 and not "submodels" in args.project_path:
        log.ODM_INFO('GRAPHOS app finished - %s' % system.now())
    else:
        progressbc.send_update(100)
        exit(retcode)