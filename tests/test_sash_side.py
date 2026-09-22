"""sash_side=left moves the diagonal sash into the top-left corner, and the
quality bookmark (normally top-left) steps over to the top-right for it."""
import unittest

import numpy as np
from PIL import Image

import age_badge
import awards
import main


def _poster():
    return Image.new("RGBA", (300, 450), (0, 0, 0, 0))


def _alpha_sum(img, box):
    return int(np.asarray(img.crop(box))[..., 3].sum())


class SashSideRenderingTests(unittest.TestCase):
    def test_right_is_the_default_corner(self):
        out = awards.draw_award_sash(_poster(), "Oscar Winner")
        self.assertGreater(_alpha_sum(out, (250, 0, 300, 50)), 0)
        self.assertEqual(_alpha_sum(out, (0, 0, 50, 50)), 0)

    def test_left_mirrors_the_right(self):
        right = awards.draw_award_sash(_poster(), " ", side="right")
        left  = awards.draw_award_sash(_poster(), " ", side="left")
        self.assertGreater(_alpha_sum(left, (0, 0, 50, 50)), 0)
        self.assertEqual(_alpha_sum(left, (250, 0, 300, 50)), 0)
        # With a blank label the band is symmetric, so the two sides land on
        # mirror-image footprints.
        mirrored = right.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.assertEqual(left.getbbox(), mirrored.getbbox())


class BookmarkSideTests(unittest.TestCase):
    def test_right_side_mirrors_into_the_top_right_corner(self):
        left = _poster()
        right = _poster()
        age_badge.draw_quality_corner_bookmark(left, ["4K", "REMUX", "DV"], bookmark_size=16)
        age_badge.draw_quality_corner_bookmark(right, ["4K", "REMUX", "DV"], bookmark_size=16, side="right")
        np.testing.assert_array_equal(
            np.asarray(right.transpose(Image.Transpose.FLIP_LEFT_RIGHT)), np.asarray(left)
        )


class SashSideConfigTests(unittest.TestCase):
    def test_parses_left_and_ignores_junk(self):
        self.assertEqual(main.build_request_config({}).sash_side, "right")
        self.assertEqual(main.build_request_config({"sash_side": "Left"}).sash_side, "left")
        self.assertEqual(main.build_request_config({"sash_side": "middle"}).sash_side, "right")


if __name__ == "__main__":
    unittest.main()
