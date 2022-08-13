import pykeentools as pkt
import numpy as np
import math
import cv2
import typing


def _load_image(image_path: str):
    return cv2.flip(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGBA), 0)


def _write_image(image_path: str, img: np.array):
    cv2.imwrite(image_path, cv2.flip(cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA), 0))


def _build_plane_geo() -> pkt.Geo:
    mesh_builder = pkt.MeshBuilder()
    mesh_builder.add_point(np.array([0.5, -0.5, 0]))
    mesh_builder.add_point(np.array([0.5, 0.5, 0]))
    mesh_builder.add_point(np.array([-0.5, 0.5, 0]))
    mesh_builder.add_point(np.array([-0.5, -0.5, 0]))
    mesh_builder.add_face([0, 1, 2, 3])
    mesh_builder.set_uvs_attribute(
        attribute_type='POINT_BASED',
        uvs=[
            np.array([1.0, 0.0]),
            np.array([1.0, 1.0]),
            np.array([0.0, 1.0]),
            np.array([0.0, 0.0])
        ])

    geo = pkt.Geo()
    geo.add_mesh(mesh_builder.mesh())

    return geo


def build_plane_texture(rendered_card_path: str, out_path: str):
    def frame_data_loader(frame: int) -> typing.Optional[pkt.texture_builder.FrameData]:
        assert(frame == 0)  # only one frame should be requested
        frame_data = pkt.texture_builder.FrameData()
        frame_data.geo = _build_plane_geo()
        frame_data.image = _load_image(rendered_card_path)
        frame_data.model = np.eye(4)
        frame_data.view = _build_view_matrix()
        frame_data.projection = _build_proj_matrix()
        return frame_data

    class ProgressCallback(pkt.ProgressCallback):
        def set_progress_and_check_abort(self, progress):
            print('building texture ...%2.1f%% done' % (progress * 100, ))
            return False  # return True if operation should be cancelled

    built_texture_rgba = pkt.texture_builder.build_texture(
        frames_count=1,
        frame_data_loader=frame_data_loader,
        progress_callback=ProgressCallback(),
        texture_w=512,
        texture_h=512
    )

    _write_image(out_path, built_texture_rgba)


def _build_view_matrix():
    return np.array(
        [[math.cos(-math.pi / 4), -math.sin(-math.pi / 4), 0, 0],
         [math.sin(-math.pi / 4), math.cos(-math.pi / 4), 0, 0],
         [0, 0, 1, -5],
         [0, 0, 0, 1]])


def _build_proj_matrix():
    return pkt.math.proj_mat(fl_to_haperture=50.0/36, w=1280.0, h=720.0, pixel_aspect_ratio=1.0, near=0.1, far=1000.0)


if __name__ == '__main__':
    build_plane_texture(
        'rendered_plane.jpg',
        'built_texture.jpg')
