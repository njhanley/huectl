from argparse import ArgumentParser
from os.path import exists, expanduser
from phue import Bridge, PhueRegistrationException
from sys import exit, stderr

config_path = expanduser("~/.huectl")


def with_bridge(func):
    def decorator(*args, **kwargs):
        if not exists(config_path):
            exit("No config found. Run `huectl register`.")
        bridge = Bridge(config_file_path=config_path)
        return func(bridge, *args, **kwargs)

    return decorator


parser = ArgumentParser("huectl")
subparsers = parser.add_subparsers()


@with_bridge
def cmd_group(bridge, args):
    group = next(group for group in bridge.groups if group.name == args.name)
    group.on = {"on": True, "off": False}[args.state]


parser_light = subparsers.add_parser("group")
parser_light.add_argument("name")
parser_light.add_argument("state", choices=["on", "off"])
parser_light.set_defaults(cmd=cmd_group)


@with_bridge
def cmd_light(bridge, args):
    bridge[args.name].on = {"on": True, "off": False}[args.state]


parser_light = subparsers.add_parser("light")
parser_light.add_argument("name")
parser_light.add_argument("state", choices=["on", "off"])
parser_light.set_defaults(cmd=cmd_light)


def cmd_register(args):
    try:
        Bridge(ip=args.address, config_file_path=config_path)
        print("Success!", file=stderr)
    except PhueRegistrationException as e:
        exit("Failed: " + e.message)


parser_register = subparsers.add_parser("register")
parser_register.add_argument("address")
parser_register.set_defaults(cmd=cmd_register)


@with_bridge
def cmd_scene(bridge, args):
    scene = next(
        scene
        for scene in bridge.scenes
        if scene.name == args.name and not scene.recycle
    )
    group = next(
        group
        for group in bridge.groups
        if [light.light_id for light in group.lights] == scene.lights
    )
    bridge.activate_scene(group.group_id, scene.scene_id)


parser_scene = subparsers.add_parser("scene")
parser_scene.add_argument("name")
parser_scene.set_defaults(cmd=cmd_scene)

args = parser.parse_args()
try:
    args.cmd(args)
except AttributeError:
    parser.print_help()
