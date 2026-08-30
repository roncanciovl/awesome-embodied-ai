md# 🏛️ Guía de depósito en Zenodo

Este documento describe el proceso para archivar una versión estable del repositorio en [Zenodo](https://zenodo.org) y obtener un **DOI** permanente.

---

## 📋 Requisitos previos

- [x] `CITATION.cff` configurado (GitHub mostrará "Cite this repository")
- [x] `LICENSE` definido (CC BY-SA 4.0)
- [x] `papers.csv` con metadatos estructurados
- [x] `research-protocol.md` con metodología reproducible
- [x] Release de GitHub creado (`v1.0.0`, 2026-08-30)
- [x] Archivo Zenodo publicado: [versión v1.0.0](https://doi.org/10.5281/zenodo.22179172) · DOI de concepto: [10.5281/zenodo.22179171](https://doi.org/10.5281/zenodo.22179171)

---

## 🔗 Paso 1: Conectar GitHub con Zenodo

1. Ir a [https://zenodo.org/account/settings/github/](https://zenodo.org/account/settings/github/)
2. Iniciar sesión con cuenta de GitHub
3. Autorizar a Zenodo para acceder a los repositorios
4. Activar el toggle para `roncanciovl/awesome-embodied-ai`

> **Documentación oficial:** [Zenodo GitHub Integration](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)

---

## 🏷️ Paso 2: Crear release en GitHub

```bash
# Desde el directorio del repositorio:
git tag -a v1.0.0 -m "Release v1.0.0: 41 papers, research protocol, gaps analysis"
git push origin v1.0.0
```

Luego en GitHub:
1. Ir a **Releases** → **Draft a new release**
2. Tag: `v1.0.0`
3. Título: `v1.0.0 — Initial Research Compendium`
4. Descripción:
   ```
   ## Awesome Embodied AI & Sim2Real v1.0.0
   
   Primera versión estable del compendio de investigación:
   - 41 papers fundamentales (2017-2026)
   - Metadatos estructurados en papers.csv
   - Protocolo de investigación reproducible
   - Análisis de brechas en 4 sublíneas
   - Propuesta experimental con burger_delivery
   
   Clasificación: Dataset / Compendio de investigación
   ```
5. Publicar release

---

## 📦 Paso 3: Verificar archivo en Zenodo

Al publicar el release, Zenodo automáticamente:
1. Archiva el contenido del repositorio
2. Asigna un **DOI** (ej. `10.5281/zenodo.XXXXXXX`)
3. Crea una página de registro con metadatos

### Metadatos recomendados en Zenodo

| Campo | Valor |
|-------|-------|
| **Upload type** | Dataset |
| **Publication type** | Other |
| **Title** | Awesome Embodied AI & Sim2Real: A Living Evidence Map for ROS 2, VLA, and Sim2Real |
| **Description** | (usar abstract de CITATION.cff) |
| **Keywords** | embodied-ai, vision-language-action, sim2real, ros2, llm |
| **License** | CC BY-SA 4.0 |
| **Communities** | Robotics, AI |

---

## 📝 Paso 4: Actualizar CITATION.cff con DOI

Una vez obtenido el DOI de Zenodo, actualizar:

```yaml
identifiers:
  - type: doi
    value: "10.5281/zenodo.XXXXXXX"
    description: "Zenodo archive DOI"
```

Y agregar badge en README.md:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

---

## 🔄 Versionado futuro

Para cada actualización mayor de la colección:
1. Incrementar versión en `CITATION.cff`
2. Crear nuevo tag (`v1.1.0`, `v2.0.0`, etc.)
3. Zenodo archivará automáticamente y asignará nuevo DOI
4. El DOI "concept" (todos los versiones) permanece estable

---

## 📊 Clasificación del depósito

| Aspecto | Clasificación |
|---------|---------------|
| **Tipo** | Dataset / Compendio de investigación |
| **No es** | Software (los scripts son auxiliares) |
| **Contenido principal** | Metadatos estructurados, protocolo reproducible y análisis de brechas; los PDF no se redistribuyen |
| **Valor de investigación** | Protocolo reproducible + análisis de brechas |

---

## 📎 Referencias

- [Zenodo GitHub Integration](https://zenodo.org/account/settings/github/)
- [GitHub: Referencing and citing content](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)
- [Citation File Format](https://citation-file-format.github.io/)
- [Zenodo DOI](https://help.zenodo.org/guides/doi/)

---

*Última actualización: 2026-08-30 — v1.0.0 archivada y verificada en Zenodo.*
