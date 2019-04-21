import platform

if __name__ == '__main__':
    system_facts = {}

    system_facts['platform'] = platform.platform()
    system_facts['system'] = platform.system()
    system_facts['release'] = platform.release()
    system_facts['version'] = platform.version()

    print(system_facts)
