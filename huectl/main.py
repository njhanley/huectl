from argparse import ArgumentParser
from os.path import exists, expanduser
from phue import Bridge, PhueRegistrationException
from sys import exit

config_path = expanduser("~/.huectl")

if exists(config_path):
    bridge = Bridge(config_file_path=config_path)
else:
    print(
        "No config found. Press the link button on your bridge before entering its address."
    )
    address = input("hue bridge address: ")
    print("Testing connection...")
    try:
        bridge = Bridge(ip=address, config_file_path=config_path)
        print("Success!")
    except PhueRegistrationException as e:
        exit(e.message)

parser = ArgumentParser("huectl")
subparsers = parser.add_subparsers()


def cmd_light(args):
    bridge[args.name].on = {"on": True, "off": False}[args.state]


parser_light = subparsers.add_parser("light")
parser_light.add_argument("name")
parser_light.add_argument("state", choices=["on", "off"])
parser_light.set_defaults(cmd=cmd_light)


def cmd_scene(args):
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
