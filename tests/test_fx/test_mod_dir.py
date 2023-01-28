import pytest
import torch

from siu.fx import symbolic_trace


class LinearModel(torch.nn.Module):

    def __init__(self, in_features, out_features, bias):
        super().__init__()
        self.linear = torch.nn.Linear(in_features, out_features, bias=bias)

    def forward(self, x):
        x = self.linear(x)
        return x


class ConvModel(torch.nn.Module):

    def __init__(self, in_channel, out_channels, kernel_size, bias) -> None:
        super().__init__()
        self.conv = torch.nn.Conv2d(in_channel,
                                    out_channels,
                                    kernel_size,
                                    bias=bias,
                                    padding=1,
                                    stride=2,
                                    dilation=2,
                                    groups=3)
        self.conv_transpose = torch.nn.ConvTranspose2d(out_channels,
                                                       out_channels,
                                                       kernel_size,
                                                       bias=bias,
                                                       padding=1,
                                                       stride=2,
                                                       dilation=2,
                                                       groups=3)

    def forward(self, x):
        x = self.conv(x)
        x = self.conv_transpose(x)
        return x


class AModel(torch.nn.Module):

    def __init__(self, bias) -> None:
        super().__init__()
        self.linear = LinearModel(3, 3, bias)
        self.conv = ConvModel(3, 6, 3, bias)

    def forward(self, x):
        x = self.linear(x)
        x = self.conv(x)
        return x


@pytest.mark.parametrize("bias", [True, False])
@pytest.mark.parametrize("bias_addition_split", [True, False])
@pytest.mark.parametrize("shape", [(3, 3, 3), (3, 3, 3, 3)])
def test_mod_dir(bias, bias_addition_split, shape):
    model = AModel(bias=bias)
    x = torch.rand(shape)
    gm = symbolic_trace(model, meta_args={'x': x}, bias_addition_split=bias_addition_split)
    for node in gm.graph.nodes:
        assert len(node.meta['info'].mod_dir), f"{node} should have non-trivial ``mod_dir``."
        print(node, node.meta['info'].mod_dir)


if __name__ == '__main__':
    test_mod_dir(True, True, (3, 3, 3))