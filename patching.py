PORT = 8501


def patching():
    from clearml import Task
    task = Task.init()
    if task._get_runtime_properties().get("_SERVICE"):
        print("already patched")
        return

    print("patching")

    import subprocess
    ip = subprocess.check_output('hostname -I', shell=True).split()[0].decode('utf-8')

    task._set_runtime_properties({"_SERVICE": "STREAMLIT", "_ADDRESS": ip, "_PORT": PORT})
    task.set_system_tags(["external_service"])

    import streamlit.config
    original_get_option = streamlit.config.get_option

    path = f"/service/{task.id}"
    print(f"path: {path}")

    def custom_get_option(key):
        return path if key == "server.baseUrlPath" else original_get_option(key)

    streamlit.config.get_option = custom_get_option

    def custom_on_server_start(server):
        def callback():
            print(f"working on http://{ip}:{PORT}{path}")
        import asyncio
        asyncio.get_running_loop().call_soon(callback)

    import streamlit.web.bootstrap
    streamlit.web.bootstrap._on_server_start = custom_on_server_start

    print("end of patching")

    import os
    import streamlit.web.bootstrap
    script = os.path.join(
        task.get_script()["working_dir"],
        task.get_script()["entry_point"]
    )
    streamlit.web.bootstrap.run(script, "", [], {})


patching()
