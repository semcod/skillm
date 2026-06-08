# skillm packages

Warstwa kontroli dla uniwersalnego reużycia skilli przez MCP/REST/CLI.

## Paczki

| Paczka | Rola |
|--------|------|
| `skillm` | Core — registry, invoke, validate |
| `dsl2skillm` | DSL + CQRS bus + Schema + Protobuf |
| `uri2skillm` | `skillm://` → linia DSL |
| `nlp2skillm` | NL → DSL |
| `cli2skillm` | Shell REPL / exec |
| `mcp2skillm` | Serwer MCP (stdio) |
| `rest2skillm` | REST API (:8216) |

## Diagram przepływu

```mermaid
flowchart TB
  subgraph adapters [Adaptery wejścia]
    NL[nlp2skillm]
    URI[uri2skillm]
    CLI[cli2skillm]
    MCP[mcp2skillm]
    REST[rest2skillm]
  end

  subgraph control [Warstwa kontroli]
    TXT[linia DSL]
    DICT[dict JSON]
    PBIN[bytes protobuf]
    SCH[JSON Schema]
    DSL[dsl2skillm.dispatch]
    Q[QueryHandler]
    C[CommandHandler]
    ES[(EventStore *.events.jsonl)]
  end

  subgraph domain [Domena skillm]
    REG[registry]
    INV[invoke]
    VAL[validate]
  end

  NL --> TXT
  URI --> TXT
  CLI --> TXT
  MCP --> TXT
  MCP --> DICT
  MCP --> PBIN
  REST --> TXT
  REST --> DICT
  REST --> PBIN

  TXT --> SCH
  DICT --> SCH
  PBIN --> DICT
  SCH --> DSL
  DSL --> Q
  DSL --> C
  Q --> REG
  Q --> INV
  C --> REG
  C --> INV
  C --> ES
```

## Instalacja dev

```bash
bash install-dev.sh
pytest packages/ -q
```
