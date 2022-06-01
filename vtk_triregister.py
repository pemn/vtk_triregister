#!python
# register points on surface, setting the point Z
# v1.1 2022/05 paulo.ernesto
# v1.0 2021/10 paulo.ernesto

'''
usage: $0 points*csv,xlsx flag_var=triz surface*vtk,obj,msh,00t output*csv,xlsx display@
'''
import sys
import pandas as pd
import numpy as np
import re

import os.path

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, pyd_zip_extract, pd_load_dataframe, pd_save_dataframe

pyd_zip_extract()

from pd_vtk import pv_read, vtk_df_to_mesh, pd_detect_xyz, vtk_plot_meshes, vtk_meshes_bb, vtk_Voxel, vtk_mesh_to_df, Raytracer

def vtk_triregister(points, flag_var, surface, output, display):
  mesh_s = pv_read(surface)
  df = None
  if re.fullmatch(r'[\d\.,;]+', points):
    bb = vtk_meshes_bb([mesh_s])
    grid = vtk_Voxel.from_bb_schema(bb, points, 2)
    df = vtk_mesh_to_df(grid)
  else:
    df = pd_load_dataframe(points)

  xyz = pd_detect_xyz(df)
  mesh_p = vtk_df_to_mesh(df, xyz)
  rt = Raytracer(mesh_p)
  rt.raytrace(mesh_s)

  if flag_var:
    df[flag_var] = rt.value
  else:
    df[xyz[2]] = rt.value

  if output:
    pd_save_dataframe(df.dropna(), output)

  if int(display):
    mesh_p = vtk_df_to_mesh(df, xyz)
    if flag_var:
      mesh_s.point_arrays[flag_var] = np.empty(mesh_s.n_points)
    vtk_plot_meshes([mesh_p, mesh_s], scalars=flag_var or None)

main = vtk_triregister

if __name__=="__main__":
  usage_gui(__doc__)
