#!/usr/bin/env python

import argparse


def parser_validate(value, id_min=1, id_max=65535):
    (container, host) = value.split('=') if '=' in value else (value, value)
    (container_uid, container_gid) = container.split(':') if ':' in container else (container, container)
    (host_uid, host_gid) = host.split(':') if ':' in host else (host, host)

    if not container_uid.isdigit():
        raise argparse.ArgumentTypeError('UID "%s" is not a number' % container_uid)
    elif not container_gid.isdigit():
        raise argparse.ArgumentTypeError('GID "%s" is not a number' % container_gid)
    elif not id_min <= int(container_uid) <= id_max:
        raise argparse.ArgumentTypeError('UID "%s" is not in range %s-%s' % (container_uid, id_min, id_max))
    elif not id_min <= int(container_gid) <= id_max:
        raise argparse.ArgumentTypeError('GID "%s" is not in range %s-%s' % (container_gid, id_min, id_max))

    if not host_uid.isdigit():
        raise argparse.ArgumentTypeError('UID "%s" is not a number' % host_uid)
    elif not host_gid.isdigit():
        raise argparse.ArgumentTypeError('GID "%s" is not a number' % host_gid)
    elif not id_min <= int(host_uid) <= id_max:
        raise argparse.ArgumentTypeError('UID "%s" is not in range %s-%s' % (host_uid, id_min, id_max))
    elif not id_min <= int(host_gid) <= id_max:
        raise argparse.ArgumentTypeError('GID "%s" is not in range %s-%s' % (host_gid, id_min, id_max))
    else:
        return int(container_uid), int(container_gid), int(host_uid), int(host_gid)


# creates lxc mapping strings
def create_map(id_type, id_list):
    result = list()

    for i, (container_id, host_id) in enumerate(id_list):
        match id_type:
            case 'u':
                id_type_name = 'user'
            case 'g':
                id_type_name = 'group'
            case _:
                raise ValueError
        print(f'{id_type_name} {host_id} HOST → {container_id} CONTAINER')

        if i == 0:
            result.append(f'lxc.idmap: {id_type} 0 100000 {container_id}')
        else:
            id_range = (id_list[i - 1][0] + 1, id_list[i - 1][0] + 100001, (container_id - 1) - id_list[i - 1][0])
            result.append(f'lxc.idmap: {id_type} {id_range[0]} {id_range[1]} {id_range[2]}')

        result.append(f'lxc.idmap: {id_type} {container_id} {host_id} 1')

        if i is len(id_list) - 1:
            id_range = (container_id + 1, container_id + 100001, 65535 - container_id)
            result.append(f'lxc.idmap: {id_type} {id_range[0]} {id_range[1]} {id_range[2]}')

    return result


# collect user input
parser = argparse.ArgumentParser(description='Proxmox unprivileged container to host uid:gid mapping syntax tool.')
parser.add_argument('id', nargs='+', type=parser_validate, metavar='container_uid[:container_gid][=host_uid[:host_gid]]', help='Container uid and optional gid to map to host. If a gid is not specified, the uid will be used for the gid value.')
parser_args = parser.parse_args()

# create sorted uid/gid lists
uid_list = sorted([(i[0], i[2]) for i in parser_args.id], key=lambda tup: tup[0])
gid_list = sorted([(i[1], i[3]) for i in parser_args.id], key=lambda tup: tup[0])

uid_map = create_map('u', uid_list)
gid_map = create_map('g', gid_list)

add_to_conf_str = '# Add to /etc/pve/lxc/<container_id>.conf:'

print('\n' + '=' * (len(add_to_conf_str) + 10))

# output mapping strings
print(f'\n{add_to_conf_str}')
for i in enumerate(uid_map):
    print(uid_map[i[0]])
    print(gid_map[i[0]])

print('\n# Add to /etc/subuid:')
for uid in uid_list:
    print('root:%s:1' % uid[1])

print('\n# Add to /etc/subgid:')
for gid in gid_list:
    print('root:%s:1' % gid[1])
