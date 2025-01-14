import numpy as np
import pytest
import torch
import cv2

import clip


@pytest.mark.parametrize('model_name', clip.available_models())
def test_consistency(model_name):
    device = "cpu"
    jit_model, transform = clip.load(model_name, device=device, jit=True)
    py_model, _ = clip.load(model_name, device=device, jit=False)

    image = transform(cv2.imread("CLIP.png")).unsqueeze(0).to(device)
    text = clip.tokenize(["a diagram", "a dog", "a cat"]).to(device)

    with torch.no_grad():
        logits_per_image, _ = jit_model(image, text)
        jit_probs = logits_per_image.softmax(dim=-1).cpu().numpy()

        logits_per_image, _ = py_model(image, text)
        py_probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    assert np.allclose(jit_probs, py_probs, atol=0.01, rtol=0.1)
