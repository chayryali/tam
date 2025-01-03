from typing import Optional

import numpy as np
from PIL import Image


def show_masks(
    image: np.ndarray,
    masks: np.ndarray,
    scores: Optional[np.ndarray],
    alpha: Optional[float] = 0.5,
    display_image: Optional[bool] = False,
    only_best: Optional[bool] = True,
    autogenerated_mask: Optional[bool] = False,
) -> Image.Image:
    if scores is not None:
        # sort masks by their scores
        sorted_ind = np.argsort(scores)[::-1]
        masks = masks[sorted_ind]

    if autogenerated_mask:
        masks = sorted(masks, key=(lambda x: x["area"]), reverse=True)
    else:
        # get mask dimensions
        h, w = masks.shape[-2:]

    if display_image:
        output_image = Image.fromarray(image)
    else:
        # create a new blank image to superimpose masks
        if autogenerated_mask:
            output_image = Image.new(
                mode="RGBA",
                size=(
                    masks[0]["segmentation"].shape[0],
                    masks[0]["segmentation"].shape[1],
                ),
                color=(0, 0, 0),
            )
        else:
            output_image = Image.new(mode="RGBA", size=(w, h), color=(0, 0, 0))

    for i, mask in enumerate(masks):
        if not autogenerated_mask:
            if mask.ndim > 2:  # type: ignore
                mask = mask.squeeze()  # type: ignore
        else:
            mask = mask["segmentation"]
        # Generate a random color with specified alpha value
        color = np.concatenate(
            (np.random.randint(0, 256, size=3), [int(alpha * 255)]), axis=0
        )

        # Create an RGBA image for the mask
        mask_image = Image.fromarray((mask * 255).astype(np.uint8)).convert("L")
        mask_colored = Image.new("RGBA", mask_image.size, tuple(color))
        mask_image = Image.composite(
            mask_colored, Image.new("RGBA", mask_image.size), mask_image
        )

        # Overlay mask on the output image
        output_image = Image.alpha_composite(output_image, mask_image)

        # Exit if specified to only display the best mask
        if only_best:
            break

    return output_image
