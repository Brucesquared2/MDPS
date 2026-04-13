# MDPS Plugin Structure

This directory contains indicator plugins for the MDPS system.

## Structure

- `vortex/` - Vortex indicator plugin
- `clime/` - CLIME algorithm integration plugin

## Usage

Each plugin exposes a `*_run(params: dict) -> dict` function that can be called via the FastAPI endpoint `/run/{task_name}`.

Tasks are mapped in the root `tasks.yml` file.
