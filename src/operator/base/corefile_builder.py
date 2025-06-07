def build_coredns_corefile(zones):
    corefile = ""
    for zone in zones:
        namespace = zone['metadata']['namespace']
        zone_name = zone['spec']['zone']
        records = zone['spec'].get('records', [])

        corefile += f"# Zone from namespace: {namespace}\n"
        corefile += f"{zone_name}:53 {{\n"

        hosts_entries = []
        template_entries = []

        for r in records:
            rtype = r.get('type', 'A').upper()
            name = r['name']
            ttl = r.get('ttl', 300)
            if rtype == 'A':
                ip = r['value']
                hosts_entries.append(f"{ip} {name}")
            elif rtype == 'CNAME':
                target = r['value']
                hosts_entries.append(f"CNAME {name} {target}")
            elif rtype == 'TXT':
                text = r['value']
                txt_template = f"""
{name} {{
    txt \"{text}\"
    ttl {ttl}
}}
"""
                template_entries.append(txt_template)
            elif rtype == 'SRV':
                priority = r.get('priority', 10)
                weight = r.get('weight', 10)
                port = r.get('port', 80)
                target = r['value']
                srv_template = f"""
{name} {{
    srv {priority} {weight} {port} {target}
    ttl {ttl}
}}
"""
                template_entries.append(srv_template)

        if hosts_entries:
            corefile += "    hosts {\n"
            for entry in hosts_entries:
                corefile += f"        {entry}\n"
            corefile += "        fallthrough\n    }\n"

        for tpl in template_entries:
            corefile += f"    template {tpl}\n"

        corefile += "    log\n    errors\n}\n\n"

    corefile += ".:53 {\n    forward . /etc/resolv.conf\n    log\n    errors\n}\n"
    return corefile
