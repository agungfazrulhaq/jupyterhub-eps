c = get_config()  # noqa


options_form_tpl = """
    <div class="form-control">
        <input type="radio" name="image" value="{default_image}" id="image1">
        <label for="image1">Default Image</label>
    </div>
    <div class="form-control">
        <input type="radio" name="image" value="jupyter/tensorflow-notebook" id="image2">
        <label for="image2">Tensorflow Image</label>
    </div>
    <div class="form-control">
        <input type="radio" name="image" value="jupyter/gpubootcamp:v1" id="image2">
        <label for="image2">GPU Bootcamp</label>
    </div>
"""


def get_options_form(spawner):
    return options_form_tpl.format(default_image=spawner.image)


c.DockerSpawner.options_form = get_options_form

from dockerspawner import DockerSpawner
import docker
import os, nativeauthenticator
import pwd, subprocess

class CustomDockerSpawner(DockerSpawner):
    def options_from_form(self, formdata):
        options = {}
        image_form_list = formdata.get("image", [])
        if image_form_list and image_form_list[0]:
            options["image"] = image_form_list[0].strip()
            self.log.info(f"User selected image: {options['image']}")
        return options

    def load_user_options(self, options):
        image = options.get("image")
        if image:
            self.log.info(f"Loading image {image}")
            self.image = image
    
    # def pre_spawn_hook(self):
    #     username = self.user.name
    #     try:
    #         pwd.getpwnam(username)
    #     except KeyError:
    #         subprocess.check_call(['useradd', '-ms', '/bin/bash', username])
def pre_spawn_hook(spawner):
    username = spawner.user.name
    try:
        pwd.getpwnam(username)
    except KeyError:
        subprocess.check_call(['useradd', '-ms', '/bin/bash', username])


c.JupyterHub.spawner_class = CustomDockerSpawner

c.DockerSpawner.pre_spawn_hook = pre_spawn_hook
# the rest of the config is testing boilerplate
# to make the Hub connectable from the containers

# dummy for testing. Don't use this in production!
c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator"
c.Authenticator.admin_users = ['admin']
c.JupyterHub.template_paths = [f"{os.path.dirname(nativeauthenticator.__file__)}/templates/"]
# while using dummy auth, make the *public* (proxy) interface private
c.JupyterHub.ip = "0.0.0.0"

# we need the hub to listen on all ips when it is in a container
c.JupyterHub.hub_ip = "0.0.0.0"
# c.JupyterHub.hub_connect_ip = 'jupyterhub'

# may need to set hub_connect_ip to be connectable to containers
# default hostname behavior usually works, though
# c.JupyterHub.hub_connect_ip
c.DockerSpawner.network_name = 'jupyterhub'

# pick a default image to use when none is specified
c.DockerSpawner.image = "jupyter/base-notebook"
c.DockerSpawner.extra_host_config = {
    "device_requests": [
        docker.types.DeviceRequest(
            count=1,
            capabilities=[["gpu"]],
        ),
    ],
}

# delete containers when they stop
c.DockerSpawner.remove = True
