# Open WebUI + skillm (MCP)

Integracja serwera MCP `mcp2skillm` z [Open WebUI](https://github.com/open-webui/open-webui).

## Wymagania

```bash
cd /home/tom/github/semcod/skillm
bash install-dev.sh
```

## Konfiguracja MCP w Open WebUI

1. Otwórz **Admin Settings → External Connections → MCP** (lub odpowiednik w Twojej wersji).
2. Dodaj serwer MCP ze stdio:

| Pole | Wartość |
|------|---------|
| Name | `skillm` |
| Command | `mcp2skillm` |
| Args | `serve` |

Alternatywnie skopiuj fragment z [`mcp-config.json`](./mcp-config.json).

3. Ustaw zmienną środowiskową (opcjonalnie), jeśli manifest nie leży w cwd:

```bash
export SKILLM_MANIFEST=/home/tom/github/semcod/skillm/app.skillm.yaml
```

## Przykładowe prompty w czacie

Po podłączeniu MCP model ma dostęp do narzędzi `skillm_*`:

```
Użyj skillm_list, żeby pokazać zarejestrowane skille.
```

```
Wywołaj skill echo-python przez skillm_invoke z args_json ["world"].
```

```
Przetłumacz na DSL: "validate manifest skillm" (skillm_to_dsl), potem wykonaj (skillm_run_command).
```

```
Zarejestruj nowy skill CLI:
skillm_run_command 'REGISTER my-tool TYPE cli WITH {"command":"date","args":["-u"]}'
```

## REST (alternatywa bez MCP)

Open WebUI może też wołać REST przez **Tools / OpenAPI**:

```bash
rest2skillm serve --port 8216
```

```bash
curl -s http://127.0.0.1:8216/health
curl -s -X POST http://127.0.0.1:8216/v1/dsl \
  -H 'Content-Type: text/plain' \
  --data 'LIST FILE app.skillm.yaml'
```

## Reużycie innych usług

W `app.skillm.yaml` każdy skill ma typ:

| Typ | Opis |
|-----|------|
| `python` | `entry: module:callable` |
| `cli` | dowolne polecenie shell |
| `docker` | `docker run image` |
| `rest` | HTTP API (np. `rest2doql` na :8210) |
| `mcp` | referencja do innego serwera MCP |

Dzięki temu jeden serwer MCP (`mcp2skillm`) agreguje Python, Docker, CLI i REST bez ręcznej integracji każdego narzędzia w Open WebUI.
