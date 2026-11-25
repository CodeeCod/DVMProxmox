import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_proxmox_kvm(mocker):
    """Мокает модуль proxmox_kvm, чтобы не обращаться к реальному API."""
    mock = mocker.patch(
        "ansible_collections.community.proxmox.plugins.modules.proxmox_kvm.main"
    )
    mock.return_value = {"changed": True, "vmid": 101}
    return mock

@pytest.fixture
def sample_host_vars():
    return {
        "vm_name": "web-01",
        "vm_vmid": 101,
        "vm_cores": 2,
        "vm_memory": 4096,
        "vm_ipconfig": "ip=192.168.1.101/24,gw=192.168.1.1",
    }