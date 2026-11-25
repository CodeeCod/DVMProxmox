# Proxmox VM Deploy — Ansible Project

Автоматизация развертывания виртуальных машин в Proxmox VE с помощью Ansible.

Проект позволяет декларативно описывать параметры каждой ВМ (имя, `vmid`, CPU, RAM, сеть) в отдельном YAML-файле и разворачивать их одной командой. Используется API Proxmox и модуль `community.proxmox.proxmox_kvm`.

---

## 📋 Требования

| Компонент | Версия / Примечание |
|-----------|---------------------|
| Ansible   | `>= 2.14`           |
| Proxmox VE | `>= 7.0` (с поддержкой cloud-init в шаблоне) |
| Python    | `>= 3.9`            |
| Коллекция | `community.proxmox` |
| Python-библиотеки | `proxmoxer`, `requests` |

### Установка зависимостей

```bash
# Коллекция Ansible
ansible-galaxy collection install community.proxmox

# Python-библиотеки
pip install proxmoxer requests
```

---

## Структура проекта

```text
proxmox-vm-deploy/
├── ansible.cfg                    # Конфигурация Ansible
├── README.md                      # Этот файл
├── inventory/
│   └── hosts.yml                  # Инвентарь (localhost, т.к. работаем через API)
├── group_vars/
│   ├── all.yml                    # Учётные данные Proxmox (шифровать через vault!)
│   └── proxmox.yml                # Общие настройки: узел, хранилище, шаблон, мост
├── host_vars/
│   ├── vm-web-01.yml              # Параметры конкретной ВМ
│   ├── vm-db-01.yml
│   └── vm-app-01.yml
├── playbooks/
│   └── deploy_vms.yml             # Точка входа — playbook развертывания
└── roles/
    └── vm_deploy/
        ├── defaults/
        │   └── main.yml           # Значения по умолчанию для роли
        └── tasks/
            └── main.yml           # Клонирование + настройка ВМ
```

### Назначение каталогов

- **`inventory/`** — список хостов. Для задач через API Proxmox достаточно `localhost`.
- **`group_vars/`** — переменные, общие для групп хостов (`all`, `proxmox`).
- **`host_vars/`** — переменные для конкретной ВМ. **Один файл = одна ВМ.**
- **`playbooks/`** — playbook-и, которые вы запускаете.
- **`roles/`** — переиспользуемая логика (клонирование, настройка).

---

## Быстрый старт

### 1. Клонируйте проект

```bash
git clone <your-repo-url> proxmox-vm-deploy
cd proxmox-vm-deploy
```

### 2. Создайте API-токен в Proxmox

1. В веб-интерфейсе Proxmox: **Datacenter → Permissions → API Tokens**.
2. Нажмите **Add**, выберите пользователя (например, `root@pam`).
3. **Снимите галочку** `Privilege Separation`, чтобы токен имел полные права.
4. Скопируйте **Token ID** и **Secret** — секрет показывается только один раз.

### 3. Настройте переменные

Отредактируйте `group_vars/all.yml`, указав данные вашего Proxmox:

```yaml
proxmox_api_host: "pve01.lab.local"
proxmox_api_user: "root@pam"
proxmox_token_id: "ansible-token"
proxmox_token_secret: "your-super-secret-token-value"
```

> **Не коммитьте секреты в открытом виде!** Зашифруйте файл:
> ```bash
> ansible-vault encrypt group_vars/all.yml
> ```

Проверьте общие настройки в `group_vars/proxmox.yml`:

```yaml
proxmox_node: "pve01"
proxmox_template: "ubuntu-2204-template"
proxmox_storage: "local-lvm"
proxmox_bridge: "vmbr0"
```

### 4. Опишите виртуальные машины

Создайте файл в `host_vars/` для каждой ВМ. Пример `host_vars/vm-web-01.yml`:

```yaml
vm_name: "web-01"
vm_vmid: 101
vm_cores: 2
vm_memory: 4096
vm_ipconfig: "ip=192.168.1.101/24,gw=192.168.1.1"
```

### 5. Запустите развертывание

```bash
# Если файл с секретами зашифрован
ansible-playbook playbooks/deploy_vms.yml --ask-vault-pass

# Иначе
ansible-playbook playbooks/deploy_vms.yml
```

---

## Параметры (переменные)

### `group_vars/all.yml`

| Переменная | Описание |
|------------|----------|
| `proxmox_api_host` | IP или FQDN Proxmox-сервера |
| `proxmox_api_user` | Пользователь API (например, `root@pam`) |
| `proxmox_token_id` | ID API-токена |
| `proxmox_token_secret` | Секрет API-токена |

### `group_vars/proxmox.yml`

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `proxmox_node` | `pve01` | Имя узла Proxmox |
| `proxmox_template` | `ubuntu-2204-template` | Имя шаблона для клонирования |
| `proxmox_storage` | `local-lvm` | Хранилище для дисков |
| `proxmox_bridge` | `vmbr0` | Сетевой мост |

### `host_vars/vm-*.yml`

| Переменная | Описание |
|------------|----------|
| `vm_name` | Имя ВМ |
| `vm_vmid` | Уникальный ID ВМ (обязательно!) |
| `vm_cores` | Количество CPU-ядер |
| `vm_memory` | Объём RAM в МБ |
| `vm_ipconfig` | Настройки сети для cloud-init |

---

##  Как это работает

1. Playbook `deploy_vms.yml` запускается на `localhost` и применяет роль `vm_deploy`.
2. Роль клонирует шаблон `proxmox_template` в новую ВМ с параметрами из `host_vars`.
3. Затем обновляет параметры ВМ (CPU, RAM, сеть) через `proxmox_kvm`.
4. Сетевые настройки передаются в гостевую ОС через **cloud-init** (`ipconfig0`).

> **Требование к шаблону:** шаблон должен быть подготовлен с поддержкой cloud-init (см. образы `cloud-image` для Debian/Ubuntu/Rocky и т.п.) и содержать настроенный `cloud-init drive`.

---

## Безопасность

- **API-токены вместо паролей.** Пароли пользователей не используются.
- **Ansible Vault** для секретов: `ansible-vault encrypt group_vars/all.yml`.
- **Права токена:** создавайте отдельного пользователя Proxmox (`ansible@pve`) с ролью `PVEVMAdmin` и ограничьте область действия токена.
- **Никогда не пушьте** незашифрованные секреты в Git.

---

## Проверка и отладка

```bash
# Проверка синтаксиса
ansible-playbook playbooks/deploy_vms.yml --syntax-check

# Dry-run (что изменится)
ansible-playbook playbooks/deploy_vms.yml --check --diff

# Подробный вывод
ansible-playbook playbooks/deploy_vms.yml -vvv
```

---

## Идемпотентность

Модуль `community.proxmox.proxmox_kvm` идемпотентен:
- Если ВМ с указанным `vmid`/`name` уже есть — повторный запуск **не создаст дубликат**, а лишь обновит конфигурацию.
- Удаление ВМ — отдельная задача (`state: absent`), не входит в текущий playbook (см. раздел «Расширение»).

---

## Расширение проекта

Идеи для развития:

- **Роль `post_configure`** — базовая настройка ОС после развертывания (SSH-ключи, hostname, пакеты).
- **Динамический инвентарь** — плагин `community.general.proxmox` для автообнаружения ВМ.
- **Playbook удаления** — отдельная задача с `state: absent`.
- **Роль `vm_snapshot`** — создание снимков перед изменениями.
- **Интеграция с `netbox`/`phpIPAM`** — автоматическое получение IP из IPAM.
- **CI/CD** — запуск playbook из GitLab CI / GitHub Actions с vault-паролем из секретов.

---

## Полезные ссылки

- [Модуль `community.proxmox.proxmox_kvm`](https://docs.ansible.com/ansible/latest/collections/community/proxmox/proxmox_kvm_module.html)
- [Документация Proxmox API](https://pve.proxmox.com/pve-docs/api-viewer/)
- [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [Cloud-init в Proxmox](https://pve.proxmox.com/wiki/Cloud-Init_Support)