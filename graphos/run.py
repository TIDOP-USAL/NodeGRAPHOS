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

if __name__ == '__main__':
    args = config.config()

    log.ODM_INFO('Initializing ODM %s - %s' % (graphos_version(), system.now()))

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

    #app = ODMApp(args)
    #retcode = app.execute()

    #project_dir = io.join_paths(args.project_path, args.name)
    project_dir = args.project_path
    print(project_dir)
    project_file = io.join_paths(project_dir, args.name + ".xml")
    image_dir = io.join_paths(project_dir, 'images')
    gcp_dir = io.join_paths(project_dir, 'gcp')

    # Esto lo hacen en NodeMicMac. No se si hay forma de cambiar las rutas de los directorios para evitar la copia
    # create output directories (match ODM conventions for backward compatibility, even though this is MicMac)
    odm_dirs = ['odm_orthophoto', 'odm_dem', 'dsm_tiles',
                'orthophoto_tiles', 'potree_pointcloud', 'odm_georeferencing']
    for odm_dir in odm_dirs:
            system.mkdir_p(io.join_paths(project_dir, odm_dir))

    # Controlar desde donde se vuelve a arrancae el proceso según args.rerun_from

    # Create GRAPHOS project
    stdout, stderr, retcode = run_graphos_command("createproj", ["--name", project_file, "--overwrite"])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)

    progressbc.send_update(1)

    # Add images to project
    output_file = io.join_paths(project_dir, "image_list.txt")
    list_images(image_dir, output_file)

    stdout, stderr, retcode = run_graphos_command("image_manager", ["-p", project_file, "-l", output_file])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)

    progressbc.send_update(5)

    # Features
    stdout, stderr, retcode = run_graphos_command("featextract", ["-p", project_file])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)

    progressbc.send_update(10)

    # Matching

    stdout, stderr, retcode = run_graphos_command("featmatch", ["-p", project_file])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)

    progressbc.send_update(15)

    # Load Ground Control Points
    
    gcp_file = io.join_paths(gcp_dir, "gcp_list.txt")
    print("Load Ground Control Points")
    print(gcp_file)
    if os.path.isfile(gcp_file):
        stdout, stderr, retcode = run_graphos_command("gcps", ["-p", project_file, "--cp", gcp_file])

        if retcode == 0:
            print(stdout)
        else:
            print("Error occurred:")
            print(stderr)

    progressbc.send_update(16)

    # Reconstruction
    
    if os.path.isfile(gcp_file):
        stdout, stderr, retcode = run_graphos_command("ori", ["-p", project_file, "-a"])
    else:
        stdout, stderr, retcode = run_graphos_command("ori", ["-p", project_file])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)

    progressbc.send_update(40)

    # Densification

    stdout, stderr, retcode = run_graphos_command("dense", ["-p", project_file])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)
    
    progressbc.send_update(45)

    # Exportar a las o laz en coordenadas UTM para que funcionen los postprocesos de NodeODM
    # odm_georeferencing/odm_georeferenced_model.laz o odm_georeferencing/odm_georeferenced_model.las
    # tambien valdría como ply georeferenciado "odm_filterpoints/point_cloud.ply"
    # Por ahora se añade a odm_filterpoints/point_cloud.ply
    georeferencing_point_cloud = io.join_paths(project_dir, 'odm_filterpoints/point_cloud.ply')

    stdout, stderr, retcode = run_graphos_command("export_point_cloud", ["-p", project_file, "-f", georeferencing_point_cloud])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)
    
    progressbc.send_update(5)
    
    # Mesh 

    stdout, stderr, retcode = run_graphos_command("mesh", ["-p", project_file, "--depth", str(14)])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)

    progressbc.send_update(70)

    # DEM

    stdout, stderr, retcode = run_graphos_command("dem", ["-p", project_file, "--gsd", str(0.1)])

    if retcode == 0:
        print(stdout)
    else:
        print("Error occurred:")
        print(stderr)

    dem_path = io.join_paths(project_dir, 'dtm')
    odm_dem = io.join_paths(project_dir, 'odm_dem')
    shutil.copy(io.join_paths(dem_path, 'dsm.tif'), odm_dem)
    #shutil.copy(io.join_paths(project_dir, 'dtm.tif'), odm_dem)

    progressbc.send_update(80)


    # Ortho
    progressbc.send_update(90)
    #shutil.copy(ortho/ortho.tif, odm_ortho)
    #shutil.copy(ortho/ortho.tif, odm_ortho)

    if retcode == 0:
        save_opts(opts_json, args)
    
    # Do not show ASCII art for local submodels runs
    if retcode == 0 and not "submodels" in args.project_path:
        log.ODM_INFO('GRAPHOS app finished - %s' % system.now())
    else:
        progressbc.send_update(100)
        exit(retcode)