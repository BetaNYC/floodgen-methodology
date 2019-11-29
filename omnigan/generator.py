import torch.nn as nn
from torch.nn import init


# --------------------------------------------------------------------------
# -----  For now no network structure, just project in a 64 x 32 x 32  -----
# -----   latent space and decode to (3 or 1) x 256 x 256              -----
# --------------------------------------------------------------------------


def get_gen(opts):
    G = OmniGenerator(opts)
    G.init_weights()
    return G


class Encoder(nn.Module):
    def __init__(self, opts):
        super().__init__()
        self.project = nn.Conv2d(3, 64, 1)
        self.downsample = nn.AdaptiveMaxPool2d(32)

    def forward(self, x):
        return self.project(self.downsample(x))


class OmniGenerator(nn.Module):
    def __init__(self, opts):
        """Creates the generator. All decoders listed in opts.gen will be added
        to the Generator.decoders ModuleDict if opts.gen.DecoderInitial is not True.
        Then can be accessed as G.decoders.T or G.decoders["T"] for instance,
        for the image Translation decoder

        Args:
            opts (addict.Dict): configuration dict
        """
        super().__init__()

        self.E = Encoder(opts)

        self.decoders = {}

        if "A" in opts.tasks and not opts.gen.A.ignore:
            self.decoders["A"] = nn.ModuleDict(
                {"r": AdapatationDecoder(opts), "s": AdapatationDecoder(opts)}
            )

        if "D" in opts.tasks and not opts.gen.D.ignore:
            self.decoders["D"] = DepthDecoder(opts)

        if "H" in opts.tasks and not opts.gen.H.ignore:
            self.decoders["H"] = HeightDecoder(opts)

        if "T" in opts.tasks and not opts.gen.T.ignore:
            self.decoders["T"] = nn.ModuleDict(
                {"f": TranslationDecoder(opts), "n": TranslationDecoder(opts)}
            )

        if "W" in opts.tasks and not opts.gen.W.ignore:
            self.decoders["W"] = WaterDecoder(opts)

        self.decoders = nn.ModuleDict(self.decoders)

    def init_weights(self, init_type="normal", init_gain=0.02):
        """Initialize network weights.
        Parameters:
            net (network)     -- network to be initialized
            init_type (str)   -- the name of an initialization method:
                                 normal | xavier | kaiming | orthogonal
            init_gain (float) -- scaling factor for normal, xavier and orthogonal.

        We use 'normal' in the original pix2pix and CycleGAN paper.
        But xavier and kaiming might work better for some applications.
        Feel free to try yourself.
        """

        def init_func(m):  # define the initialization function
            classname = m.__class__.__name__
            if hasattr(m, "weight") and (
                classname.find("Conv") != -1 or classname.find("Linear") != -1
            ):
                if init_type == "normal":
                    init.normal_(m.weight.data, 0.0, init_gain)
                elif init_type == "xavier":
                    init.xavier_normal_(m.weight.data, gain=init_gain)
                elif init_type == "kaiming":
                    init.kaiming_normal_(m.weight.data, a=0, mode="fan_in")
                elif init_type == "orthogonal":
                    init.orthogonal_(m.weight.data, gain=init_gain)
                else:
                    raise NotImplementedError(
                        "initialization method [%s] is not implemented" % init_type
                    )
                if hasattr(m, "bias") and m.bias is not None:
                    init.constant_(m.bias.data, 0.0)
            elif classname.find("BatchNorm2d") != -1:
                # BatchNorm Layer's weight is not a matrix;
                # only normal distribution applies.
                init.normal_(m.weight.data, 1.0, init_gain)
                init.constant_(m.bias.data, 0.0)

        print("initialize network with %s" % init_type)
        self.apply(init_func)


class Decoder(nn.Module):
    """generic class for decoders
    """

    def __init__(self, opts):
        super().__init__()

    def forward(self, x):
        return self.layers(x)


class HeightDecoder(Decoder):
    def __init__(self, opts):
        super().__init__(opts)
        self.layers = []
        self.layers.append(nn.Conv2d(64, 1, 1))
        self.layers.append(nn.UpsamplingNearest2d(256))
        self.layers = nn.Sequential(*self.layers)


class WaterDecoder(Decoder):
    def __init__(self, opts):
        super().__init__(opts)
        self.layers = []
        self.layers.append(nn.Conv2d(64, 1, 1))
        self.layers.append(nn.UpsamplingNearest2d(256))
        self.layers = nn.Sequential(*self.layers)


class DepthDecoder(Decoder):
    def __init__(self, opts):
        super().__init__(opts)
        self.layers = []
        self.layers.append(nn.Conv2d(64, 1, 1))
        self.layers.append(nn.UpsamplingNearest2d(256))
        self.layers = nn.Sequential(*self.layers)


class TranslationDecoder(Decoder):
    def __init__(self, opts):
        super().__init__(opts)
        self.layers = []
        self.layers.append(nn.Conv2d(64, 3, 1))
        self.layers.append(nn.UpsamplingNearest2d(256))
        self.layers = nn.Sequential(*self.layers)


class AdapatationDecoder(Decoder):
    def __init__(self, opts):
        super().__init__(opts)
        self.layers = []
        self.layers.append(nn.Conv2d(64, 3, 1))
        self.layers.append(nn.UpsamplingNearest2d(256))
        self.layers = nn.Sequential(*self.layers)