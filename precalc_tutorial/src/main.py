import pykeentools as pkt
import cv2
import os


def _load_image_for_precalc(image_path: str):
    rgb_image = cv2.flip(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB), 0) / 255.0
    return pkt.prepare_for_precalc(rgb_image)


def _read_sequence(sequence_dir: str):
    frame_to_image = dict()
    for img_file in os.listdir(sequence_dir):
        img_name, _ = os.path.splitext(img_file)
        frame_number = int(img_name)
        img_path = os.path.join(sequence_dir, img_file)
        frame_to_image[frame_number] = _load_image_for_precalc(img_path)

    frame_from, frame_to = min(frame_to_image.keys()), max(frame_to_image.keys())
    assert len(frame_to_image) == (frame_to - frame_from + 1)
    return frame_to_image, frame_from, frame_to


class _CalculationClient(pkt.precalc.CalculationClient):
    def __init__(self, frame_to_image):
        super().__init__()
        self.frame_to_image = frame_to_image

    def on_progress(self, progress, progress_message):
        print('Precalc calculation %.1f%% done (%s)' % (progress * 100, progress_message))
        return True  # return False to stop

    def load_image_at(self, frame):
        assert frame in self.frame_to_image
        return self.frame_to_image[frame]


def _compute_precalc(sequence_dir: str, out_precalc_path: str):
    frame_to_image, frame_from, frame_to = _read_sequence(sequence_dir)
    calculation_client = _CalculationClient(frame_to_image)
    lm = pkt.GeoTracker.license_manager()
    img_shape = frame_to_image[frame_from].shape
    pkt.precalc.calculate(
        out_precalc_path,
        img_shape[1],
        img_shape[0],
        frame_from,
        frame_to,
        calculation_client,
        lm
    )


def _print_precalc_info(precalc_file: str):
    precalc_info: pkt.precalc.Info = pkt.precalc.Loader(precalc_file).load_info()
    print('Precalc "%s" info:' % precalc_file)
    print('\tframe range: [%d, %d]' % (precalc_info.left_precalculated_frame, precalc_info.right_precalculated_frame))
    print('\timg format: %dx%d' % (precalc_info.image_w, precalc_info.image_h))


def compute_precalc(sequence_dir: str, out_precalc_path: str):
    _compute_precalc(sequence_dir, out_precalc_path)
    print('Precalc calculation finished!')
    _print_precalc_info(out_precalc_path)


if __name__ == '__main__':
    compute_precalc('./sequence', 'example.precalc')
