# Cry: Crear Nuevo Warrior

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Creación de Warriors (agentes especializados)

## Descripción

Comando rápido para crear un nuevo Warrior en Ahrena. Invoca `kata-create-warrior`, que consulta `codex-warriors` y el template oficial para producir un agente especializado completo en los tres idiomas obligatorios.

## Uso

```
/cry-new-warrior <rol> [dominio] [--name nombre] [--clade clade/subclade]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `rol` | Sí | Función que el Warrior desempeña | `"Arquitecto de Software"` |
| `dominio` | No | Área de actuación. Si se omite, el agente lo infiere del rol | `"decisiones arquitecturales"` |
| `--name` | No | Nombre propio del Warrior. Si se omite, el agente sugiere un nombre temático | `--name Athena` |
| `--clade` | No | Clade/subclade en la taxonomía. Si se omite, el agente lo infiere del dominio | `--clade engineering/architecture` |

## Lo que el Comando Hace

1. Lee `.ahrena/.directives` para obtener idiomas y convenciones
2. Invoca `kata-create-warrior` con los parámetros proporcionados; el Kata consulta `codex-warriors` y el template oficial y produce el Warrior
3. (El Kata) Crea el Warrior en el idioma por defecto y traduce a los demás idiomas
4. Reporta los archivos creados

## Prompt Template

```
Contexto:
- Rol: {{rol}}
- Dominio: {{dominio}} (o inferir del rol)
- Nombre: {{name}} (o sugerir nombre temático)
- Clade/Subclade: {{clade}} (o inferir del dominio)

Tarea:
Ejecute kata-create-warrior. Consulte .ahrena/.directives para obtener los
idiomas obligatorios. El Kata consulta .ahrena/.directives, codex-warriors y templates/warrior-sample.md. Cree el Warrior en el idioma por
defecto y traduzca a todos los idiomas de language.i18n.

Formato de salida:
Lista de archivos creados con confirmación de que el Warrior tiene identidad
completa, responsabilidades delimitadas y cadena de consulta definida.
```

## Ejemplo de Invocación

**Crear Warrior con rol:**

```
/cry-new-warrior "Arquitecto de Software"
```

**Output:**

```
Warrior creado con éxito.

Identidad:
- Nombre: Athena
- Rol: Arquitecto de Software
- Dominio: Decisiones arquitecturales y calidad estructural
- Persona: Analítica, rigurosa, centrada en trade-offs

Archivos creados:
1. framework/pt-BR/engineering/architecture/warriors/warrior-athena.md ✓
2. framework/es/engineering/architecture/warriors/warrior-athena.md ✓
3. framework/en/engineering/architecture/warriors/warrior-athena.md ✓
```

**Con nombre y clade explícitos:**

```
/cry-new-warrior "Revisor de Código" "calidad de código" --name Linus --clade engineering/quality
```

## Restricciones

- No crea Warriors genéricos sin alcance delimitado
- Siempre ejecuta `kata-create-warrior` (nunca crea directamente)
- Siempre crea en los tres idiomas obligatorios

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida (1 comando) | Procedimiento completo (7 pasos) |
| **Complejidad** | Baja (rol + dominio) | Alta (identidad, responsabilidades, consulta) |
| **¿Configura agente?** | No | Sí (define comportamiento) |
| **Ejemplo** | `/cry-new-warrior "Arquitecto"` | Workflow de 7 pasos con checklist |

## Referencias

- `kata-create-warrior` — Procedimiento ejecutado por este Cry (el Kata consulta los criterios de calidad aplicables; ver documentación del Kata)
- `templates/warrior-sample.md` — Template base
