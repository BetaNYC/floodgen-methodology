import atexit
from argparse import ArgumentParser
from copy import deepcopy

from comet_ml import Experiment
from comet_ml.api import API
import torch

import omnigan
from omnigan.utils import get_comet_rest_api_key, flatten_opts

import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)


def set_opts(opts, str_nested_key, value):
    keys = str_nested_key.split(".")
    o = opts
    for k in keys[:-1]:
        o = o[k]
    o[keys[-1]] = value


def set_conf(opts, conf):
    for k, v in conf.items():
        if k.startswith("__"):
            continue
        set_opts(opts, k, v)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Colors:
    def _r(self, key, *args):
        return f"{key}{' '.join(args)}{bcolors.ENDC}"

    def ob(self, *args):
        return self._r(bcolors.OKBLUE, *args)

    def w(self, *args):
        return self._r(bcolors.WARNING, *args)

    def og(self, *args):
        return self._r(bcolors.OKGREEN, *args)

    def f(self, *args):
        return self._r(bcolors.FAIL, *args)

    def b(self, *args):
        return self._r(bcolors.BOLD, *args)

    def u(self, *args):
        return self._r(bcolors.UNDERLINE, *args)


def comet_handler(exp, api):
    def sub_handler():
        p = Colors()
        print()
        print(p.b(p.w("Deleting comet experiment")))
        api.delete_experiment(exp.get_key())

    return sub_handler


def print_start(desc):
    p = Colors()
    cdesc = p.b(p.ob(desc))
    title = "|  " + cdesc + "  |"
    line = "-" * (len(desc) + 6)
    print(f"{line}\n{title}\n{line}")


def print_end(desc):
    p = Colors()
    cdesc = p.b(p.og(desc))
    title = "|  " + cdesc + "  |"
    line = "-" * (len(desc) + 6)
    print(f"{line}\n{title}\n{line}")


def delete_on_exit(exp):
    rest_api_key = get_comet_rest_api_key()
    api = API(api_key=rest_api_key)
    atexit.register(comet_handler(exp, api))


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--no_delete", action="store_true", default=False)
    parser.add_argument("--no_end_to_end", action="store_true", default=False)
    args = parser.parse_args()

    global_exp = Experiment(project_name="omnigan-test")
    if not args.no_delete:
        delete_on_exit(global_exp)

    prompt = Colors()

    opts = omnigan.utils.load_opts()
    opts.data.check_samples = False
    opts.train.fid.n_images = 5
    opts.comet.display_size = 5
    opts.tasks = ["m", "s", "d"]
    opts.domains = ["r", "s"]
    opts.data.loaders.num_workers = 4
    opts.data.loaders.batch_size = 2
    opts.data.max_samples = 9
    opts.train.epochs = 1
    opts.data.transforms[-1].new_size = 256

    test_scenarios = [
        {"__comet": False, "__doc": "MSD no exp"},
        {"__doc": "MSD with exp"},
        {"tasks": ["p"], "domains": ["rf"], "__doc": "Painter"},
        {
            "tasks": ["m", "s", "d", "p"],
            "domains": ["rf", "r", "s"],
            "__doc": "MSDP no End-to-end",
        },
        {
            "tasks": ["m", "s", "d", "p"],
            "domains": ["rf", "r", "s"],
            "__pl4m": True,
            "__doc": "MSDP with End-to-end",
        },
    ]

    n_confs = len(test_scenarios)

    for test_idx, conf in enumerate(test_scenarios):
        test_opts = deepcopy(opts)
        set_conf(test_opts, conf)
        print_start(
            f"[{test_idx + 1}/{n_confs}] "
            + conf.get("__doc", "WARNING: no __doc for test scenario")
        )
        print(f"{prompt.b('Current Scenario:')}\n{conf}")

        test_exp = None
        if conf.get("__comet", True):
            test_exp = global_exp

        trainer = omnigan.trainer.Trainer(opts=test_opts, comet_exp=test_exp,)
        trainer.functional_test_mode()

        if conf.get("__pl4m", False):
            trainer.use_pl4m = True

        trainer.setup()
        trainer.train()
        print_end("Done")
