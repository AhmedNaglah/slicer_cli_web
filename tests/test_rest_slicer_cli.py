import json
import os
import pytest

from girder.api import rest
from girder.models.item import Item

from slicer_cli_web import docker_resource
from slicer_cli_web import rest_slicer_cli
from slicer_cli_web.models import CLIItem


@pytest.mark.plugin('slicer_cli_web')
def test_genHandlerToRunDockerCLI(server, admin, folder, file):
    # Make a request to allow ther eto be some lingering context to handle the
    # testing outside of a request for the actual handler.
    server.request('/system/version')
    rest.setCurrentUser(admin)

    xmlpath = os.path.join(os.path.dirname(__file__), 'data', 'ExampleSpec.xml')

    girderCLIItem = Item().createItem('data', admin, folder)
    Item().setMetadata(girderCLIItem, dict(slicerCLIType='task', type='python',
                                           image='dockerImage', digest='dockerImage@sha256:abc',
                                           xml=open(xmlpath, 'rb').read()))

    resource = docker_resource.DockerResource('test')
    item = CLIItem(girderCLIItem)
    handlerFunc = rest_slicer_cli.genHandlerToRunDockerCLI(item)
    assert handlerFunc is not None

    job = handlerFunc(resource, params={
        'inputImageFile': str(file['_id']),
        'secondImageFile': str(file['_id']),
        'outputStainImageFile_1_folder': str(folder['_id']),
        'outputStainImageFile_1': 'sample1.png',
        'outputStainImageFile_2_folder': str(folder['_id']),
        'outputStainImageFile_2_name': 'sample2.png',
        'stainColor_1': '[0.5, 0.5, 0.5]',
        'stainColor_2': '[0.2, 0.3, 0.4]',
        'returnparameterfile_folder': str(folder['_id']),
        'returnparameterfile': 'output.data',
    })

    kwargs = json.loads(job['kwargs'])
    assert 'container_args' in kwargs
    assert 'image' in kwargs
    assert 'pull_image' in kwargs

    assert kwargs['image'] == 'dockerImage@sha256:abc'
    assert kwargs['pull_image'] == 'if-not-present'
    container_args = kwargs['container_args']
    assert container_args[0] == 'data'
