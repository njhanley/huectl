from argparse import ArgumentParser
from os.path import exists, expanduser
from sys import exit

from phue import Bridge, PhueRegistrationException

config_path = expanduser("~/.huectl")


def with_bridge(func):
    def decorator(*args, **kwargs):
        if not exists(config_path):
            return "No config found. Run `huectl register`."
        bridge = Bridge(config_file_path=config_path)
        return func(bridge, *args, **kwargs)

    return decorator


parser = ArgumentParser("huectl")
parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")

subparsers = parser.add_subparsers()


@with_bridge
def cmd_group(bridge, args):
    group = bridge.get_group(args.name)
    if group is None:
        return "No such group."
    group.on = {"on": True, "off": False}[args.state]
    return None


parser_light = subparsers.add_parser("group")
parser_light.add_argument("name")
parser_light.add_argument("state", choices=["on", "off"])
parser_light.set_defaults(cmd=cmd_group)


@with_bridge
def cmd_light(bridge, args):
    light = bridge.get_light(args.name)
    if light is None:
        return "No such light."
    light.on = {"on": True, "off": False}[args.state]
    return None


parser_light = subparsers.add_parser("light")
parser_light.add_argument("name")
parser_light.add_argument("state", choices=["on", "off"])
parser_light.set_defaults(cmd=cmd_light)


def cmd_register(args):
    try:
        Bridge(ip=args.address, config_file_path=config_path)
        return None
    except PhueRegistrationException as e:
        return "Failed: " + e.message


parser_register = subparsers.add_parser("register")
parser_register.add_argument("address")
parser_register.set_defaults(cmd=cmd_register)


@with_bridge
def cmd_scene(bridge, args):
    try:
        scene = next(
            scene
            for scene in bridge.scenes
            if scene.name == args.name and not scene.recycle
        )
    except StopIteration:
        return "No such scene."
    group = next(
        group
        for group in bridge.groups
        if [light.light_id for light in group.lights] == scene.lights
    )
    bridge.activate_scene(group.group_id, scene.scene_id)
    return None


parser_scene = subparsers.add_parser("scene")
parser_scene.add_argument("name")
parser_scene.set_defaults(cmd=cmd_scene)


def main():
    args = parser.parse_args()
    try:
        cmd = args.cmd
    except AttributeError:
        parser.print_usage()
        return 2
    return cmd(args)


if __name__ == "__main__":
    exit(main())
