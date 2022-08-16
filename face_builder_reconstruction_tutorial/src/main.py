import pykeentools as pkt
import numpy as np
import cv2
import os


class _ConstantCameraInput(pkt.FaceBuilderCameraInputI):
    def __init__(self, fl, h_aperture, img_w, img_h):
        super().__init__()
        self._proj_mat = pkt.math.proj_mat(
            fl_to_haperture=fl / h_aperture, w=img_w, h=img_h, pixel_aspect_ratio=1.0, near=0.1, far=1000.0)
        self._img_size = (img_w, img_h)

    def projection(self, frame):
        return self._proj_mat

    def view(self, frame):
        return np.eye(4)

    def image_size(self, frame):
        return self._img_size


def _load_image(image_path: str):
    return cv2.flip(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGBA), 0) / 255.0


def _write_image(image_path: str, img: np.array):
    cv2.imwrite(image_path, cv2.flip(cv2.cvtColor((img * 255.0).astype(np.uint8), cv2.COLOR_RGBA2BGRA), 0))


def _load_images(images_dir):
    return [_load_image(os.path.join(images_dir, img_file)) for img_file in os.listdir(images_dir)]


def _write_geo_to_obj(geo: pkt.Geo, out_obj_path: str):
    assert(geo.meshes_count() == 1)
    mesh: pkt.Mesh = geo.mesh(0)
    assert(mesh.normals_attribute() == 'VERTEX_BASED')
    assert(mesh.uvs_attribute() == 'VERTEX_BASED')
    with open(out_obj_path, mode='w') as out_obj:
        for p_idx in range(mesh.points_count()):
            p = mesh.point(p_idx)
            out_obj.write('v %f %f %f\n' % (p[0], p[1], p[2]))

        for f_idx in range(mesh.faces_count()):
            for fv_idx in range(mesh.face_size(f_idx)):
                vt = mesh.uv(f_idx, fv_idx)
                out_obj.write('vt %f %f\n' % (vt[0], vt[1]))

        for f_idx in range(mesh.faces_count()):
            for fv_idx in range(mesh.face_size(f_idx)):
                vn = mesh.normal(f_idx, fv_idx)
                out_obj.write('vn %f %f %f\n' % (vn[0], vn[1], vn[2]))

        offset = 0
        for f_idx in range(mesh.faces_count()):
            face = ['/'.join([str(mesh.face_point(f_idx, v_idx) + 1), str(offset + v_idx + 1), str(offset + v_idx + 1)])
                    for v_idx in range(mesh.face_size(f_idx))]
            offset += mesh.face_size(f_idx)
            out_obj.write('f %s\n' % ' '.join(face))


def reconstruct_head_geometry(fl, h_aperture, img_w, img_h, images_dir, out_texture_path, out_obj_path):
    images = _load_images(images_dir)

    camera_input = _ConstantCameraInput(fl, h_aperture, img_w, img_h)
    fb = pkt.FaceBuilder(camera_input)

    print('Detecting faces on %d images:' % len(images))
    for image_idx, image in enumerate(images):
        face_infos = fb.detect_faces(image, pixel_aspect=1.0)
        if len(face_infos) != 1:
            print('Image %d skipped. It has %d faces detected' % (image_idx, len(face_infos)))
            continue
        detected = fb.set_detected_face_pose_keyframe(image_idx, face_infos[0])
        if detected:
            print('Successfully detected face in frame %d' % image_idx)
        else:
            print('Face box detected, but face detection failed in frame %d' % image_idx)

    added_images = fb.keyframes()
    if len(added_images) == 0:
        print('Cannot reconstruct head geometry. No faces detected')
        return

    print('Writing geometry...')
    _write_geo_to_obj(fb.applied_args_model(), out_obj_path)

    class ProgressCallback(pkt.ProgressCallback):
        def set_progress_and_check_abort(self, progress):
            return False


    def frame_data_loader(keyframe_idx: int):
        frame_data = pkt.texture_builder.FrameData()
        image_idx = added_images[keyframe_idx]
        frame_data.geo = fb.applied_args_model_at(image_idx)
        frame_data.image = images[image_idx]
        frame_data.model = fb.model_mat(image_idx)
        frame_data.view = camera_input.view(image_idx)
        frame_data.projection = camera_input.projection(image_idx)
        return frame_data

    print('Using %d frames for texture reconstruction...' % fb.keyframes_count())
    built_texture_rgba = pkt.texture_builder.build_texture(
        frames_count=len(added_images),
        frame_data_loader=frame_data_loader,
        progress_callback=ProgressCallback(),
        texture_w=2048,
        texture_h=2048
    )
    assert built_texture_rgba is not None

    print('Writing texture...')
    _write_image(out_texture_path, built_texture_rgba)


if __name__ == '__main__':
    reconstruct_head_geometry(fl=50.0, h_aperture=23.6, img_w=1800, img_h=1200, images_dir='./photos',
                              out_texture_path='face_texture.jpg', out_obj_path='head.obj')
