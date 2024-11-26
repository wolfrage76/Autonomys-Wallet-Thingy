import psutil

def fetch_system_stats():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    return f"CPU: {cpu:.1f}% | MEM: {mem.used // (1024 ** 2)}MB/{mem.total // (1024 ** 2)}MB"

if __name__ == "__main__":
    # print(fetch_system_stats())
    fetch_system_stats()
