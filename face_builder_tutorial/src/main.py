import pykeentools as pkt
import numpy as np


class _FBCameraInput(pkt.FaceBuilderCameraInputI):
    def projection(self, frame):
        assert frame == 0
        return pkt.math.proj_mat(
            fl_to_haperture=50.0/36, w=1920.0, h=1080.0, pixel_aspect_ratio=1.0, near=0.1, far=1000.0)

    def view(self, frame):
        assert frame == 0
        return np.eye(4)

    def image_size(self, frame):
        assert frame == 0
        return 1920, 1080


def _try_geometry_methods(face_builder):
    # There are multiple models(topologies) available in FaceBuilder
    # Lets print them
    print('Available FaceBuilder models:')
    for topology_info in face_builder.models_list():
        print('\tTopology (name="%s", LOD="%s")' % (topology_info.name, topology_info.level_of_detail))
    # we can switch model by calling face_builder.select_model(). Let's stick with the default model for now
    print('By default "%s" model is used' % face_builder.models_list()[face_builder.selected_model()].name)

    # this method returns pkt.Geo object representing current head with current shape applied
    # as we haven't moved any pins this is a neutral head model
    neutral_model: pkt.Geo = face_builder.applied_args_model()
    print('Default FaceBuilder head model consists of %d mesh, has %d vertices and %d faces' %
          (neutral_model.meshes_count(), neutral_model.points_count(), neutral_model.faces_count()))
    assert(neutral_model.meshes_count() == 1)
    neutral_model_mesh: pkt.Mesh = neutral_model.mesh(0)
    print('FaceBuilder head model has %s uv and %s normal attributes' %
          (neutral_model_mesh.uvs_attribute(), neutral_model_mesh.normals_attribute()))

    # There is a method to get head model from specific keyframe: face_builder.applied_args_model_at(frame)
    # It is different when non-neutral expressions mode is enabled.

    # There are methods to work with head masks. You can enable/disable different parts of the model with them
    # Let's print available mask names:
    print('Available FaceBuilder masks: %s' % face_builder.mask_names())
    assert 'NeckLower' in face_builder.mask_names()
    # Let's disable NeckLower in our model
    face_builder.set_mask(face_builder.mask_names().index('NeckLower'), False)

    # There are also convenience methods:
    # - to get geometry hash
    print('Shape applied hash is "%s"' % face_builder.applied_args_model_hash())
    # - to get geometry vertices only (instead of full geometry for performance)
    # face_builder.applied_args_model_vertices_at(frame)


def _print_face_builder_licensing_information():
    fb_license_manager: pkt.LicenseManager = pkt.FaceBuilder.license_manager()

    fb_license_available = fb_license_manager.license_running(strategy=pkt.LicenseCheckStrategy.FORCE)
    print('FaceBuilder license is %s' % ('active' if fb_license_available else 'not active'))
    print('FaceBuilder license status text:')
    print(fb_license_manager.license_status_text(strategy=pkt.LicenseCheckStrategy.FORCE).replace('<br />', '\n'))


def _clone_face_builder(face_builder, camera_input):
    serialized_fb: str = face_builder.serialize()
    print('Serialized FaceBuilder string length: %d' % len(serialized_fb))

    face_builder_clone = pkt.FaceBuilder(camera_input)
    successful_deserialization = face_builder_clone.deserialize(serialized_fb)
    assert successful_deserialization

    # Let's check our mask settings are deserialized and NeckLower is disabled
    assert not face_builder_clone.masks()[face_builder.mask_names().index('NeckLower')]


def _create_keyframe(face_builder):
    # There are no keyframes in a newly created FaceBuilder
    assert len(face_builder.keyframes()) == 0

    # The easiest way to set up a keyframe is to use set_centered_geo_keyframe method
    # We are going to set up keyframe in frame 0, as expected by our _FBCameraInput implementation
    # FaceBuilder is going to create a keyframe and place head in front of the camera
    # (using view and projection matrices from our _FBCameraInput)
    face_builder.set_centered_geo_keyframe(0)

    # Let's check the position our head is in frame 0
    print('Centered head\'s translation is %s (%.1f units away from the camera and %.1f up)' %
          (face_builder.model_mat(0)[0:3, 3], face_builder.model_mat(0)[2, 3], face_builder.model_mat(0)[1, 3]))


def _add_and_move_pin(face_builder):
    # Let's try adding pin in the bottom left corner of the image
    pin = face_builder.add_pin(0, np.array([0, 0]))
    # pin wasn't added because we missed the model
    assert pin is None

    # Let's add a pin in the middle of the image
    # we know that the model is there, so we should hit the model
    pin: pkt.Pin = face_builder.add_pin(0, np.array([1920 / 2, 1080 / 2]))
    assert pin is not None
    # Pin is a connection between a 3d point on a surface of the head and a 2d point on the image
    print('Added pin:')
    print('\timage position = "%s"' % pin.img_pos)
    print('\tsurface position is specified by 3 geometry point indexes "%s" and barycentryc coordinates "%s"' %
          (pin.surface_point.geo_point_idxs, pin.surface_point.barycentric_coordinates))

    # Let's now move the pin 100 pixels right
    face_builder.move_pin(0, 0, np.array([1920 / 2 + 100, 1080 / 2]))

    # There is a convenience method to get all pins in keyframe for drawing
    for proj_pin in face_builder.projected_pins(0):
        print('Projected pin after move pin: (img position = "%s", projected surface point position = "%s")' %
              (proj_pin.img_pos, proj_pin.surface_point))

    # Notice how img position and projected surface point position doesn't match
    # this is because we need to call solve_for_current_pins method to run FaceBuilder solver
    # this will update head position in every keyframe, head shape, facial expressions (if enabled),
    # focal length (if focal length estimation is enabled)
    face_builder.solve_for_current_pins(0)

    # With only one keyframe and only one pin FaceBuilder will only move the head around.
    # Let's check the updated model matrix. It should move a little to the right:
    print('Updated head\'s translation after moving pin right is %s' % face_builder.model_mat(0)[0:3, 3])


def create_and_try_fb():
    camera_input = _FBCameraInput()
    face_builder = pkt.FaceBuilder(camera_input)
    _try_geometry_methods(face_builder)
    _print_face_builder_licensing_information()
    _clone_face_builder(face_builder, camera_input)
    _create_keyframe(face_builder)
    _add_and_move_pin(face_builder)


if __name__ == '__main__':
    create_and_try_fb()
