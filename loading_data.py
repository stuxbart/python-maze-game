import os
import xml.etree.ElementTree as ET

import numpy as np

from models import ModelData3D, Model3D, MODEL_STATIC, MODEL_DYNAMIC
from texturemanager import load_texture

BASE_OBJECTS_FOLDER = ".\\graphics\\3d_objects"
BASE_TEXTURES_FOLDER = ".\\graphics\\textures"


def load_obj_file(filename):
    if os.path.exists(filename):  # if file exists
        objects = {}
        current_obj = ''
        with open(filename, 'r') as f:
            for line in f:  # search for objects/vertices/faces
                if line.startswith('o '):
                    # New Object
                    current_obj = line[2:].strip()
                    objects[current_obj] = {'vertices': [], 'tex_coords': [], 'normals': [], 'faces': []}

                elif line.startswith('v '):
                    # New Vertex
                    x, y, z, *w = line[2:].split()
                    coords = np.array([float(x), float(y), float(z)], dtype=np.float32)
                    objects[current_obj]['vertices'].append(coords)

                elif line.startswith('vt '):
                    # Texture coord
                    u, v = line[3:].split()
                    uv = np.array([float(u), float(v)], dtype=np.float32)
                    objects[current_obj]['tex_coords'].append(uv)

                elif line.startswith('vn '):
                    # Normal
                    x, y, z = line[3:].split()
                    normal = np.array([float(x), float(y), float(z)], dtype=np.float32)
                    objects[current_obj]['normals'].append(normal)

                elif line.startswith('f '):
                    # New Face
                    vertices = line[2:].split()
                    face = []
                    for v in vertices:
                        vi, vt, vn = v.split('/')  # Vertex Index/Texture/Normal
                        face.append([int(vi) - 1, int(vt) - 1, int(vn) - 1])
                    face = np.array(face, dtype=np.uint32)
                    objects[current_obj]['faces'].append(face)

        return len(objects.items()), objects
    else:
        print(filename)
        print("File doesn't exists")
        return None, None


def load_object(name, model_type=MODEL_STATIC):
    obj_ext = ".obj"
    obj_path = os.path.join(BASE_OBJECTS_FOLDER, name)
    obj_path += obj_ext
    _, objects = load_obj_file(obj_path)
    if objects:
        k = list(objects.keys())[0]
        obj = objects[k]  # Take first object
        vertices = obj['vertices']
        texture_coordinates = obj['tex_coords']
        normals = obj['normals']
        faces = obj['faces']
        # Load Texture
        tex_ext = ".jpg"
        tex_path = os.path.join(BASE_TEXTURES_FOLDER, name)
        tex_path += tex_ext
        if os.path.exists(tex_path):
            texture_id = load_texture(tex_path)  # TEXTURES.load_texture(tex_path)
        else:
            tex_path = tex_path[:-4] + ".png"
            texture_id = load_texture(tex_path)  # TEXTURES.load_texture(tex_path)
        model = Model3D(k, True, None, model_type)
        if model_type == MODEL_STATIC:
            init = False
        elif model_type == MODEL_DYNAMIC:
            init = True
        else:
            init = False
        model_geometry = ModelData3D(
                parent=model,
                vertices=vertices,
                texture_coordinates=texture_coordinates,
                normals=normals,
                faces=faces,
                texture=texture_id,
                initialize_gl=init,
        )
        model.set_geometry(model_geometry)
        return model
    else:
        print("Cannot load File")


def load_dae_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    for geometry in root.find('library_geometries'):
        print(geometry.attrib['name'])
        # for mesh in geometry.findall('mesh'):
        #     for child in mesh:
        #         print(child.tag, child.attrib)


if __name__ == "__main__":
    load_dae_file('dodatkowe/chest.dae')
