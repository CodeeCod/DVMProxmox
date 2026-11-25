import pytest
from unittest.mock import patch, MagicMock
# Предположим, у вас есть модуль utils/ip_validator.py
from utils.ip_validator import validate_ipconfig

def test_valid_ipconfig():
    """Тестирует корректный формат строки ipconfig."""
    valid_config = "ip=192.168.1.101/24,gw=192.168.1.1"
    assert validate_ipconfig(valid_config) is True

def test_invalid_ipconfig_missing_gw():
    """Тестирует строку без шлюза (должна быть невалидной)."""
    invalid_config = "ip=192.168.1.101/24"
    assert validate_ipconfig(invalid_config) is False

def test_invalid_ipconfig_bad_ip_format():
    """Тестирует строку с некорректным IP."""
    invalid_config = "ip=999.999.999.999/24,gw=192.168.1.1"
    assert validate_ipconfig(invalid_config) is False

# Пример мокирования вызова AnsibleModule, если у вас есть кастомный модуль
@patch('ansible.module_utils.basic.AnsibleModule')
def test_custom_module_logic(mock_ansible_module):
    """Пример тестирования логики кастомного Ansible-модуля."""
    # Настройка мока
    mock_instance = mock_ansible_module.return_value
    mock_instance.params = {'vm_name': 'test-vm', 'vmid': 101}
    mock_instance.exit_json = MagicMock()
    
    # Вызов вашей функции модуля
    # from plugins.modules.my_custom_module import main
    # main()
    
    # Проверка, что exit_json был вызван с ожидаемыми аргументами
    # mock_instance.exit_json.assert_called_once_with(changed=True, vm_id=101)